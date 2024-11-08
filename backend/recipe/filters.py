from django_filters.rest_framework import FilterSet, filters

from .models import BaseUser, Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all()
    )
    author = filters.ModelChoiceFilter(
        queryset=BaseUser.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        method="is_favorited_filter",
        label="Is favorited"
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="is_in_shopping_cart_filter",
        label="Is in shopping cart"
    )

    class Meta:
        model = Recipe
        fields = ("is_in_shopping_cart", "is_favorited", "author", "tags")

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return user.favorites.all()
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return user.shopping_carts.all()
        return queryset
