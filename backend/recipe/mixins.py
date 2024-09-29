from collections import Counter

from django.core.files.storage import default_storage
from rest_framework import serializers

from ingredient.models import Ingredient

from .models import Basket, Favorite, Recipe, RecipeIngredient, RecipeTag


# Вынос валидаторов, используемых в проекте.
class ValidateIDMixin:
    """Миксин для проверки существования объекта по ID"""

    def validate_id(self, value):
        model = self.Meta.model
        if model == RecipeIngredient:
            if not Ingredient.objects.filter(id=value).exists():
                raise serializers.ValidationError(
                    f"Ingredient with ID {value} - does not exist."
                )
            return value

        if not model.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f"{model.__name__} with ID {value} - does not exist."
            )
        return value


class RecipeValidationMixin:
    """Миксин для валидации тегов и ингредиентов в рецептах."""

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                "Поле 'tags' не может быть пустым."
            )

        tag_ids = [tag.id for tag in value]
        tag_counts = Counter(tag_ids)

        # Находим теги, которые повторяются
        duplicate_tags = [
            tag_id for tag_id, count in
            tag_counts.items() if count > 1
        ]

        if duplicate_tags:
            raise serializers.ValidationError(
                {"tags": f"""Обнаружены повторяющиеся
                 id тегов: {duplicate_tags}"""}
            )

        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                "Поле 'ingredients' не может быть пустым."
            )

        ingredient_ids = [ingredient["id"] for ingredient in value]
        ingredient_counts = Counter(ingredient_ids)

        # Находим ингредиенты, которые повторяются
        duplicate_ingredients = [
            ingredient_id
            for ingredient_id, count in ingredient_counts.items()
            if count > 1
        ]

        if duplicate_ingredients:
            raise serializers.ValidationError(
                {
                    "ingredients": f"""Обнаружены повторяющиеся
                    id ингредиентов: {duplicate_ingredients}"""
                }
            )

        return value


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
