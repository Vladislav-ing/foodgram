from collections import Counter

from django.core.files.storage import default_storage
from rest_framework import serializers

from ingredient.models import Ingredient

from .models import Basket, Favorite, Recipe, RecipeIngredient, RecipeTag


# Вынос валидаторов, используемых в проекте.
class ValidateIDMixin:
    """Миксин для проверки существования объекта ингредиента по ID"""

    def validate_id(self, value):
        model = self.Meta.model
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f"Model {model} with ID {value} - does not exist."
            )
        return value


class RecipeValidationMixin:
    """Миксин для валидации тегов и ингредиентов в рецептах."""

    def _validate_unique_items(self, value, item_type):
        """Общий метод для валидации на наличие и дубликаты."""
        if not value:
            raise serializers.ValidationError(
                f"Поле '{item_type}' не может быть пустым."
            )

        item_ids = (
            [item.id for item in value]
            if item_type == "tags"
            else [item.get('id') for item in value]
        )
        item_counts = Counter(item_ids)

        duplicate_items = [
            item_id for item_id, count in item_counts.items() if count > 1
        ]

        if duplicate_items:
            raise serializers.ValidationError(
                {item_type: f"""Обнаружены повторяющиеся id {item_type}:
                 {duplicate_items}"""}
            )

        return value

    def validate_tags(self, value):
        """Валидация тегов."""
        return self._validate_unique_items(value, "tags")

    def validate_ingredients(self, value):
        """Валидация ингредиентов."""
        return self._validate_unique_items(value, "ingredients")


# Вынос методов, используемых в проекте.
class Favorit_ShoppingCart_Save_MethodsMixin:
    def get_is_favorited(self, obj):
        return (
            not self.context.get("request").user.is_anonymous
            and Favorite.objects.filter(
                user=self.context["request"].user, recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            not self.context.get("request").user.is_anonymous
            and Basket.objects.filter(
                user=self.context["request"].user, recipe=obj
            ).exists()
        )

    def _save_ingredients_and_tags(self, recipe, ingredients_data, tags_data):
        """Сохраняет ингредиенты и теги для рецепта."""
        ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient_data["id"]),
                amount=ingredient_data["amount"],
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(ingredients)

        tags = [
            RecipeTag(recipe=recipe, tag=tag_obj)
            for tag_obj in set(tags_data)
        ]
        RecipeTag.objects.bulk_create(tags)


def delete_file(file_path):
    """
    Функция для безопасного удаления image in recipe/avatar in user models.
    """
    if file_path and default_storage.exists(file_path):
        default_storage.delete(file_path)


# Вынос объектов, используемых в проекте, имеющих зависимость с apps recipe.
class RolledUpRecipeSerializer(serializers.ModelSerializer):
    """Серилизатор для чтения сокращенной формы рецептов"""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_field = ("name", "image", "cooking_time")
