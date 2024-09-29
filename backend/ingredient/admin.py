from django.contrib import admin

from .models import Ingredient, Tag


class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
