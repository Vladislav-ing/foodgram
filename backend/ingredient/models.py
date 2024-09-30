from django.db import models

from .constants import (INGREDIENT_MEASURE_LENGTH, INGREDIENT_NAME_LENGTH,
                        TAG_LENGTH)


class Tag(models.Model):
    """Модель-Tag, для подборки рецептов пользователей."""

    name = models.CharField(
        verbose_name="Name",
        help_text="Тэги для группирования рецептов",
        max_length=TAG_LENGTH,
    )
    slug = models.SlugField(
        unique=True, verbose_name="Slug",
        help_text="Slug тэга", max_length=TAG_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ("slug",)

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """Модель ингредиентов"""

    name = models.CharField(
        verbose_name="Name",
        help_text="Название ингредиента",
        max_length=INGREDIENT_NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name="Measure",
        help_text="Мера измерения",
        max_length=INGREDIENT_MEASURE_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)

    def __str__(self):
        return self.name
