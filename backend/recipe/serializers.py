from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from ingredient.models import Tag
from ingredient.serializers import ReadOnlyTagSerializer
from registration.serializers import FullProfileSerializer
from registration.utils import Base64ImageField

from . import constants
from .mixins import (Favorit_ShoppingCart_Save_MethodsMixin,
                     RecipeValidationMixin, RolledUpRecipeSerializer,
                     ValidateIDMixin)
from .models import Recipe, RecipeIngredient


class IngredientSerializerForRecipe(
    ValidateIDMixin, serializers.ModelSerializer
):
    """Серилизатор для обработки ингредиентов в recipe"""

    id = serializers.IntegerField(required=True)
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(constants.MIN_WEIGHT),
            MaxValueValidator(constants.MAX_WEIGHT)
        ]
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")

    def to_representation(self, instance):
        """
        Переопределяем метод для корректной выдачи id ингредиента в ответе
        """
        representation = super().to_representation(instance)
        representation["id"] = instance.ingredient.id
        return representation


class TagListSerializer(serializers.ListField):
    """
    Серилизатор для обработки списка ID тэгов и их преобразования в объекты.
    """

    child = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())

    def to_representation(self, data):
        """Переопределяем метод для возврата списка объектов тэгов."""
        return ReadOnlyTagSerializer(data.all(), many=True).data


class CRUDRecipeSerializer(
    RecipeValidationMixin,
    Favorit_ShoppingCart_Save_MethodsMixin,
    serializers.ModelSerializer,
):
    """Серилизатор рецептов обрабатывающий CRUD операции представления"""

    ingredients = IngredientSerializerForRecipe(
        source="recipe_ingredients", many=True, required=True, allow_null=False
    )
    tags = TagListSerializer(required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)
    author = FullProfileSerializer(
        read_only=True,
    )
    cooking_time = serializers.IntegerField(
        required=True,
        validators=[
            MinValueValidator(constants.MIN_COOKING_TIME),
            MaxValueValidator(constants.MAX_COOKING_TIME)
        ]
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop("recipe_ingredients")
        tags_data = validated_data.pop("tags")

        recipe = Recipe.objects.create(**validated_data)

        self._save_ingredients_and_tags(recipe, ingredients_data, tags_data)
        return recipe

    def update(self, instance, validated_data):
        """Обновление валидированных данных для рецепта"""
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.save()

        if (
            not validated_data.get("recipe_ingredients")
            or not validated_data.get("tags")
        ):
            raise serializers.ValidationError(
                'Отсутствует обязательное поле "tags" или "ingredients"'
            )

        ingredients_data = validated_data.pop("recipe_ingredients")
        tags_data = validated_data.pop("tags")

        instance.recipe_ingredients.all().delete()
        instance.recipe_tags.all().delete()

        self._save_ingredients_and_tags(instance, ingredients_data, tags_data)
        return instance


class FavoriteRecipeSerializer(RolledUpRecipeSerializer):
    """Серилизатор для чтения рецептов в избранных"""


class BasketRecipeSerializer(RolledUpRecipeSerializer):
    """Серилизатор для чтения рецептов в корзине"""
