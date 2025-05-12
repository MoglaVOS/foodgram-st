from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from .models import Ingredient, Recipe, CustomUser, Follow


class CustomUserCreateSerializer(UserCreateSerializer):
    password = serializers.CharField(write_only=True, label='Пароль')

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True, label='Подписан')
    avatar = Base64ImageField(required=False, label='Аватар')

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(user=user, following=obj).exists() 
        return False

class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=CustomUser.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=CustomUser.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Follow
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Подписка уже существует'
            )
        ]

    def validate(self, attrs):
        if attrs['user'] == attrs['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return attrs

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'
