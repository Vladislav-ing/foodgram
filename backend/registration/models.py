from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models

from .constants import LENGTH_EMAIL_USER, LENGTH_NAME_USER
from .managers import CustomBaseUserManager


class BaseUser(AbstractUser):
    """Базовая модель пользователя"""

    class Roles(models.TextChoices):
        USER = "user", "Пользователь"
        ADMIN = "admin", "Администратор"

    username = models.CharField(
        unique=True,
        max_length=LENGTH_NAME_USER,
        blank=False,
        validators=[UnicodeUsernameValidator()],
        help_text="Уникальный username",
        verbose_name="Username",
    )

    first_name = models.CharField(
        max_length=LENGTH_NAME_USER,
        blank=False,
        help_text="Имя пользователя",
        verbose_name="Name",
    )

    last_name = models.CharField(
        max_length=LENGTH_NAME_USER,
        blank=False,
        help_text="Фамилия пользователя",
        verbose_name="Last name",
    )

    email = models.EmailField(
        unique=True,
        max_length=LENGTH_EMAIL_USER,
        blank=False,
        help_text="Адрес электронной почты",
        verbose_name="Email",
    )

    role = models.CharField(
        max_length=max(map(len, Roles.values)),
        blank=True,
        verbose_name="Role",
        choices=Roles.choices,
        default=Roles.USER,
    )

    avatar = models.ImageField(
        blank=True,
        help_text="Картинка закодированная в Base64",
        verbose_name="Main foto profile",
        upload_to="users/",
    )

    subscription = models.ManyToManyField(
        to="self",
        db_index=True,
        through="UserSubscription",
        verbose_name="User subscriptions",
    )

    objects = CustomBaseUserManager()

    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN or self.is_staff

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("date_joined",)


class UserSubscription(models.Model):
    """Отношение пользователя к подпискам на др. пользователей."""

    user = models.ForeignKey(
        BaseUser, on_delete=models.CASCADE, related_name="subscriptions"
    )
    subscription = models.ForeignKey(
        BaseUser, on_delete=models.CASCADE, related_name="subscribers"
    )

    def __str__(self):
        return f"{self.user}: {self.subscription}"

    class Meta:
        verbose_name = "Подписки пользователя"
        verbose_name_plural = "Подписки пользователя"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "subscription"],
                name="unique_user_subscription"
            )
        ]

    def clean(self):
        if self.user == self.subscription:
            raise ValidationError("Нельзя подписаться на самого себя.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
