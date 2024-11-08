import short_url
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from registration.utils import LimitPageNumberPagination

from . import constants
from .filters import RecipeFilter
from .mixins import delete_file
from .models import Basket, Favorite, Recipe
from .permissions import ReadOnlyOrAuthorOrAdmin
from .serializers import (BasketRecipeSerializer, CRUDRecipeSerializer,
                          FavoriteRecipeSerializer)


class CRUDRecipeViewSet(viewsets.ModelViewSet):
    """CRUD вьюсет для обработки запросов к recipe/"""

    queryset = Recipe.objects.all()
    serializer_class = CRUDRecipeSerializer
    permission_classes = (ReadOnlyOrAuthorOrAdmin,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination
    http_method_names = ["get", "post", "patch", "delete"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        """Удаление изображения из хранилища при удалении рецепта."""
        if instance.image:
            delete_file(instance.image.path)
        super().perform_destroy(instance)

    @action(detail=True, methods=("GET",), url_path="get-link")
    def get_link(self, request, pk=None):
        """Метод для генерации короткой ссылки на рецепт"""
        recipe = get_object_or_404(Recipe, pk=pk)

        url = short_url.encode_url(recipe.id)
        full_url = request.build_absolute_uri(recipe.get_absolute_url())
        full_url = '/'.join(full_url.split('/')[:-2])
        short_link = f"{full_url}/{url}"

        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    def _handle_add_to_list(self, request, pk, model,
                            serializer_class, error_message):
        """Добавление рецепта в избранное/корзину"""
        recipe = get_object_or_404(Recipe, pk=pk)

        with transaction.atomic():
            obj, created = model.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if not created:
                return Response(
                    error_message.format(recipe_id=recipe.id),
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = serializer_class(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _handle_remove_from_list(self, request, pk, model, error_message):
        """Удаление рецепта из избранного/корзины"""
        recipe = get_object_or_404(Recipe, pk=pk)

        with transaction.atomic():
            try:
                obj = model.objects.get(user=request.user, recipe=recipe)
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except model.DoesNotExist:
                return Response(
                    error_message.format(recipe_id=recipe.id),
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(detail=True, methods=("POST",), url_path="favorite")
    def add_recipe_to_favorite(self, request, pk=None):
        """Метод для добавления рецепта в список избранных пользователя"""
        return self._handle_add_to_list(
            request,
            pk,
            Favorite,
            FavoriteRecipeSerializer,
            """Рецепт с id-{recipe_id} уже добавлен,
             в избранные рецепты пользователя""",
        )

    @add_recipe_to_favorite.mapping.delete
    def remove_recipe_from_favorite(self, request, pk=None):
        """Метод для удаления рецепта из списка избранных пользователя"""
        return self._handle_remove_from_list(
            request,
            pk,
            Favorite,
            "Рецепт с id-{recipe_id} не найден в избранных пользователя",
        )

    @action(detail=True, methods=("POST",), url_path="shopping_cart")
    def add_recipe_to_basket(self, request, pk=None):
        """Метод для добавления рецепта в корзину пользователя"""
        return self._handle_add_to_list(
            request,
            pk,
            Basket,
            BasketRecipeSerializer,
            "Рецепт с id-{recipe_id} уже добавлен в корзину пользователя",
        )

    @add_recipe_to_basket.mapping.delete
    def remove_recipe_from_basket(self, request, pk=None):
        """Метод для удаления рецепта из корзины пользователя"""
        return self._handle_remove_from_list(
            request,
            pk,
            Basket,
            "Рецепт с id-{recipe_id} не найден в корзине пользователя",
        )

    @action(detail=False, methods=("GET",), url_path="download_shopping_cart")
    def download_shopping_cart(self, request):
        """
        Метод для скачивания списка рецептов,
        в корзине пользователя в формате PDF
        """
        shopping_cart_recipes = request.user.shopping_carts.prefetch_related(
            "recipe_ingredients__ingredient"
        )

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_cart.pdf"'
        )

        page = canvas.Canvas(response, pagesize=A4)

        pdfmetrics.registerFont(TTFont("FreeSerif", "FreeSerif.ttf"))
        page.setFont("FreeSerif", constants.HEADER_SIZE)
        page.drawString(
            constants.COORDINAT_X_TITLE,
            constants.COORDINAT_Y_TITLE,
            f"""Корзина покупок ингредиентов,
            пользователя {request.user.username}""",
        )
        page.setFont("FreeSerif", constants.ROW_SIZE)

        ingredients_with_weight = {}

        for recipe in shopping_cart_recipes:
            for recipe_ingredient in recipe.recipe_ingredients.all():
                ingredient_name = recipe_ingredient.ingredient.name
                measurement_unit = (recipe_ingredient
                                    .ingredient.measurement_unit)
                key = f"{ingredient_name}({measurement_unit})"
                ingredients_with_weight[key] = (
                    ingredients_with_weight.get(key, 0)
                    + recipe_ingredient.amount
                )

        x_row, y_row = constants.COORDINAT_X_ROW, constants.COORDINAT_Y_ROW
        for name_measure, total_amount in ingredients_with_weight.items():
            page.drawString(x_row, y_row, f"* {name_measure} - {total_amount}")
            y_row -= constants.LINE_INDENTATION

            if y_row <= constants.PAGE_MISSING:
                page.showPage()
                page.setFont("FreeSerif", constants.ROW_SIZE)
                y_row = (
                    constants.COORDINAT_Y_TITLE - constants.COORDINAT_Y_ROW
                ) + constants.COORDINAT_Y_ROW

        page.showPage()
        page.save()

        return response
