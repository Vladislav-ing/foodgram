# Generated by Django 5.1.1 on 2024-09-29 13:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("recipe", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="basket",
            options={
                "verbose_name": "Рецепт в корзине",
                "verbose_name_plural": "Рецепты в корзине",
            },
        ),
        migrations.AlterModelOptions(
            name="recipeingredient",
            options={
                "verbose_name": "Ингредиент в рецепте",
                "verbose_name_plural": "Ингредиенты в рецепте",
            },
        ),
        migrations.AlterModelOptions(
            name="recipetag",
            options={
                "verbose_name": "Тэги связанные с рецептом",
                "verbose_name_plural": "Тэги связанные с рецептами",
            },
        ),
    ]
