# Generated by Django 5.1.1 on 2024-09-25 10:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0005_auto_20240919_1110'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='baseuser',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='avatar',
            field=models.ImageField(blank=True, help_text='Картинка закодированная в Base64', upload_to='users/', verbose_name='Main foto profile'),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='role',
            field=models.CharField(blank=True, choices=[('user', 'Пользователь'), ('admin', 'Администратор')], default='user', max_length=5, verbose_name='Role'),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='subscription',
            field=models.ManyToManyField(db_index=True, through='registration.UserSubscription', to=settings.AUTH_USER_MODEL, verbose_name='User subscriptions'),
        ),
    ]
