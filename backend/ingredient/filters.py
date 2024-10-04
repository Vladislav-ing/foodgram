import django_filters
from django.forms import TextInput

from .models import Ingredient


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для представления ингредиентов"""
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
        widget=TextInput(
            attrs={'placeholder': 'Поиск по названию ингредиента'}
        )
    )

    class Meta:
        model = Ingredient
        fields = ['name']
