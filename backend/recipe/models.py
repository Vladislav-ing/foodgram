from django.db import models
from django.core import validators
from django.urls import reverse

from .constants import RECIPE_NAME_LENGTH
from ingredient.models import Ingredient, Tag
from registration.models import BaseUser


class Favorite(models.Model):
    """Модель рецептов добавленных в избранное для пользователя"""
    user = models.ForeignKey(
        to=BaseUser,
        verbose_name='User',
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
    )
    recipe = models.ForeignKey(
        to='Recipe',
        verbose_name='Recipe',
        on_delete=models.CASCADE,
        related_name='recipe_users',
    )
    
    def __str__(self):
        return f'{self.user.username} добавлен - {self.recipe.name}'

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_user_recipe_favorite')
        ]
        
        
class Basket(models.Model):
    """Модель рецептов добавленных в покупки"""
    user = models.ForeignKey(
        to=BaseUser,
        verbose_name='User',
        on_delete=models.CASCADE,
        related_name='user_purchases',
    )
    recipe = models.ForeignKey(
        to='Recipe',
        verbose_name='Recipe',
        on_delete=models.CASCADE,
        related_name='purchasing_users',
    )
    
    def __str__(self):
        return f'{self.user.username}: {self.recipe.name}'

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_user_recipe_basket')
        ]
        

class RecipeIngredient(models.Model):
    """Модель связывающая рецепты и ингредиенты"""
    recipe = models.ForeignKey(
        to='Recipe',
        verbose_name='Recipe',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        verbose_name='Ingredients to recipe',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    amount = models.DecimalField(
        verbose_name='Amount',
        help_text='Количество/Вес для ингредиентов',
        max_digits=8,
        decimal_places=2,
        default=1,
        validators=[validators.MinValueValidator(1)]
    )
    
    def __str__(self):
        return f'{self.recipe.name}: {self.ingredient.name}'
    
    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient')
        ]
        
        
class RecipeTag(models.Model):
    """Модель связывающая рецепты и тэги"""
    recipe = models.ForeignKey(
        to='Recipe',
        verbose_name='Recipe',
        on_delete=models.CASCADE,
        related_name='recipe_tags',
    )
    tag = models.ForeignKey(
        to=Tag,
        verbose_name='Tag',
        on_delete=models.CASCADE,
        related_name='tag_recipes',
    )
    
    def __str__(self):
        return f'{self.recipe.name}: {self.tag.name}'
    
    class Meta:
        verbose_name = 'Тэги связанные с рецептом'
        verbose_name_plural = 'Тэги связанные с рецептами'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag')
        ]


class Recipe(models.Model):
    """Модель рецептов"""
    name = models.CharField(
        verbose_name='Название рецепта',
        help_text='Максимальная длинна 256 символов',
        max_length=RECIPE_NAME_LENGTH
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through=RecipeIngredient,
    )
    tags = models.ManyToManyField(
        to=Tag,
        through=RecipeTag,
    )
    text = models.TextField(
        verbose_name='Recipe description',
        help_text='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Cooking time',
        help_text='время приготовления(в минутах)',
        validators=[validators.MinValueValidator(1)]
    )
    image = models.ImageField(
        help_text='Картинка рецепта, закодированная в Base64',
        upload_to='recipes/images/'
    )
    author = models.ForeignKey(
        to=BaseUser,
        verbose_name='Author',
        help_text='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='author_recipes',
    )
    pub_date = models.DateTimeField(
        verbose_name='Время публикации',
        auto_now_add=True
    )
    favorite = models.ManyToManyField(
        to=BaseUser,
        through=Favorite,
        related_name='favorites'
    )
    shopping_cart = models.ManyToManyField(
        to=BaseUser,
        through=Basket,
        related_name='shopping_carts'
    )
    
    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.pk})
    
    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
    
