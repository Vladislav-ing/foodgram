# Generated by Django 5.1.1 on 2024-09-30 15:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("recipe", "0002_alter_basket_options_alter_recipeingredient_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="basket",
            options={
                "ordering": ("user",),
                "verbose_name": "Рецепт в корзине",
                "verbose_name_plural": "Рецепты в корзине",
            },
        ),
        migrations.AlterModelOptions(
            name="favorite",
            options={
                "ordering": ("user",),
                "verbose_name": "Избранный рецепт",
                "verbose_name_plural": "Избранные рецепты",
            },
        ),
        migrations.AlterModelOptions(
            name="recipeingredient",
            options={
                "ordering": ("recipe",),
                "verbose_name": "Ингредиент в рецепте",
                "verbose_name_plural": "Ингредиенты в рецепте",
            },
        ),
        migrations.AlterModelOptions(
            name="recipetag",
            options={
                "ordering": ("recipe",),
                "verbose_name": "Тэги связанные с рецептом",
                "verbose_name_plural": "Тэги связанные с рецептами",
            },
        ),
    ]