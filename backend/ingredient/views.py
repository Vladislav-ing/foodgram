from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Ingredient, Tag
from .serializers import ReadOnlyIngredientSerializer, ReadOnlyTagSerializer


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для чтения тэгов."""

    queryset = Tag.objects.all()
    serializer_class = ReadOnlyTagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для чтения ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = ReadOnlyIngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("name",)
