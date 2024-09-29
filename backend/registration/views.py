import os

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from recipe.mixins import delete_file
from .models import BaseUser, UserSubscription
from .serializers import CreateProfileSerializer, FullProfileSerializer, ResetPasswordUser, AvatarProfileSerializer, SubscriptionProfileSerializer
from .utils import LimitPageNumberPagination


class ProfileViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """Представление для эндпоинтов users/* """
    queryset = BaseUser.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateProfileSerializer
        
        return FullProfileSerializer
    
    def get_permissions(self):
        if self.action in ('create', 'retrieve', 'list'):
            return (AllowAny(),)
        return super().get_permissions()
    
    @action(detail=False, methods=('POST',),
            url_path='set_password')
    def reset_password_current_user(self, request):
        serializer = ResetPasswordUser(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)  
    
    @action(detail=False, methods=('GET',),
            url_path='me')
    def get_current_user(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=('PUT',),
            url_path='me/avatar')
    def set_avatar_profile(self, request):
        user = request.user
        serializer = AvatarProfileSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @set_avatar_profile.mapping.delete
    def remove_avatar_profile(self, request):
        user = request.user
        if user.avatar:
            delete_file(user.avatar.path)
            user.avatar = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=('GET',), url_path='subscriptions')
    def list_subscriptions(self, request):
        """Метод GET, для получения списка пользователей, на которых подписан текущий пользователь"""
        subscriptions = request.user.subscription.all()
        page = self.paginate_queryset(subscriptions)
        recipes_limit = request.query_params.get('recipes_limit')

        if page is not None:
            serializer = SubscriptionProfileSerializer(
                page, many=True,
                context={
                    **self.get_serializer_context(),
                    'recipes_limit': recipes_limit
                }
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionProfileSerializer(
            subscriptions, many=True,
            context={
                **self.get_serializer_context(),
                'recipes_limit': recipes_limit
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=('POST',), url_path='subscribe')
    def subscribe_to_user(self, request, pk=None):
        """Метод для подписки на пользователя методом POST"""
        to_subscribe_user = get_object_or_404(BaseUser, pk=pk)
        
        if request.user == to_subscribe_user:
            return Response({"error": "Нельзя подписаться на самого себя."}, status=status.HTTP_400_BAD_REQUEST)

        subscription, created = UserSubscription.objects.get_or_create(user=request.user, subscription=to_subscribe_user)

        if not created:
            return Response({"error": "Вы уже подписаны на этого пользователя."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SubscriptionProfileSerializer(
            to_subscribe_user,
            context={
                **self.get_serializer_context(),
                'recipes_limit': request.query_params.get('recipes_limit')
            }
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @subscribe_to_user.mapping.delete
    def unsubscribe(self, request, pk=None):
        """Метод для отписки от пользователя через DELETE"""
        to_unsubscribe_user = get_object_or_404(BaseUser, pk=pk)

        subscription = UserSubscription.objects.filter(user=request.user, subscription=to_unsubscribe_user).first()

        if not subscription:
            return Response({"error": "Вы не подписаны на этого пользователя."}, status=status.HTTP_400_BAD_REQUEST)

        subscription.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    