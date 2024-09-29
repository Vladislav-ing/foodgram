from rest_framework import serializers

from .models import Tag, Ingredient


class ReadOnlyTagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов рецепта."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        
        
class ReadOnlyIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов рецепта"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        