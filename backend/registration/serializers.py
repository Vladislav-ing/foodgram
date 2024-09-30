from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from recipe.mixins import RolledUpRecipeSerializer
from registration.models import BaseUser
from registration.utils import Base64ImageField


class AvatarProfileSerializer(serializers.ModelSerializer):
    """Серилизатор пользователя при работе с аватаром"""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = BaseUser
        fields = ("avatar",)

    def update(self, instance, validated_data):
        """
        Если у пользователя уже есть аватар и он обновляет его,
        удаляем старый файл
        """
        if instance.avatar and validated_data.get("avatar"):
            instance.avatar.delete(save=False)

        return super().update(instance, validated_data)


class CreateProfileSerializer(serializers.ModelSerializer):
    """Серилизатор пользователя при метода POST"""

    class Meta:
        model = BaseUser
        fields = (
            "email", "id", "username", "first_name",
            "last_name", "password"
        )
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        """
        Валидация пароля с использованием валидаторов из settings.py.
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = BaseUser(**validated_data)
        user.set_password(password)  # Хеширование пароля
        user.save()
        return user


class FullProfileSerializer(CreateProfileSerializer):
    """Серилизатор для полных данных о пользователе"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = BaseUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        """
        Метод проверяющий подписку пользователя сделавшего запрос, на
        пользователя в качестве obj.
        """
        current_user = self.context["request"].user
        if (
            current_user.is_authenticated
            and current_user.subscription.all()
            .filter(id=obj.id)
        ):
            return True

        return False


class ResetPasswordUser(serializers.Serializer):
    """
    Данный серилизатор обрабатывает запросы на смену пароля.
    Ожидаемые значения ввода: new_password, current_password.
    Ожидаемый ответ: response.status.HTTP_204
    """

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Действующий пароль не правильный."
            )
        return value

    def validate(self, attrs):
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")

        if current_password == new_password:
            raise serializers.ValidationError(
                "Новый пароль, не может быть равен старому."
            )

        return attrs

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()


class SubscriptionProfileSerializer(FullProfileSerializer):
    """
    Серилизатор для обработки запросов к subscribe,
    возвращает полные данные пользователя,
    а также 2 доп. поля recipes, recipes_count.
    Данные пользователя обрабатываются только в режиме чтения.
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(FullProfileSerializer.Meta):
        fields = (
            FullProfileSerializer.Meta.fields + ("recipes", "recipes_count"))
        read_only_fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        recipes = obj.author_recipes.all()  # Получаем все рецепты пользователя
        recipes_limit = self.context.get("recipes_limit")

        if recipes_limit and int(recipes_limit) > 0:
            recipes = recipes[: int(recipes_limit)]

        return RolledUpRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.author_recipes.count()
