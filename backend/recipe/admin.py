from django.contrib import admin

from .models import Basket, Favorite, Recipe, RecipeIngredient, RecipeTag


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """Модель рецептов в админке"""

    model = Recipe
    list_display = ("name", "author", "is_favorited", "is_in_cart")
    search_fields = ("name", "author__username")
    list_filter = ("tags",)
    fields = (
        "name",
        "author",
        "cooking_time",
        "text",
        "image",
        "favorite_count",
        "basket_count",
    )
    readonly_fields = ("favorite_count", "basket_count")
    inlines = [RecipeTagInline, RecipeIngredientInline]

    def is_favorited(self, obj):
        return obj.favorite.exists()

    is_favorited.boolean = True
    is_favorited.short_description = "В избранном"

    def is_in_cart(self, obj):
        return obj.shopping_cart.exists()

    is_in_cart.boolean = True
    is_in_cart.short_description = "В корзине"

    def favorite_count(self, obj):
        """
        Возвращает общее количество пользователей,
        добавивших рецепт в избранное.
        """
        return obj.favorite.count()

    favorite_count.short_description = "Количество в избранном"

    def basket_count(self, obj):
        """
        Возвращает общее количество пользователей, добавивших рецепт в корзину.
        """
        return obj.shopping_cart.count()

    basket_count.short_description = "Количество в корзине"


class FavoriteAdmin(admin.ModelAdmin):
    """Модель избранных рецептов в админке"""

    model = Favorite
    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user",)


class BasketAdmin(admin.ModelAdmin):
    """Модель рецептов в корзине для админки"""

    model = Basket
    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user",)


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Basket, BasketAdmin)
admin.site.register(Recipe, RecipeAdmin)
