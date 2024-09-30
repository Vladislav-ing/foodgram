# Generated by Django 5.1.1 on 2024-09-30 15:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipe", "0004_alter_recipe_cooking_time_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipeingredient",
            name="amount",
            field=models.PositiveSmallIntegerField(
                default=1,
                help_text="Количество/Вес для ингредиентов",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(32000),
                ],
                verbose_name="Amount",
            ),
        ),
    ]