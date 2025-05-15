from rest_framework import serializers
from django.shortcuts import get_object_or_404

from api.models import (
    Ingredient, Recipe, RecipeIngredient,
    Favorite, CustomUser, Subscription
)
from api.serializers.users import CustomUserSerializer
from drf_extra_fields.fields import Base64ImageField

from api.validators import validate_ingredients_data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов рецепта."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Cериализатор рецептов."""
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return obj.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return obj.shopping_cart.filter(user=user).exists()
        return False

    @staticmethod
    def validate_image(image):
        if not image:
            raise serializers.ValidationError({'image': 'Обязательное поле.'})
        return image

    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(recipe_ingredients, many=True).data

    def create(self, validated_data):
        ingredients_data = self.initial_data.get('ingredients')

        validate_ingredients_data(ingredients_data)

        validated_data['author'] = self.context['request'].user
        recipe = super().create(validated_data)

        for ingredient_data in ingredients_data:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_data['id']
            )

            amount = ingredient_data['amount']

            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = self.initial_data.get('ingredients')

        validate_ingredients_data(ingredients_data)

        instance.ingredients.clear()
        for ingredient_data in ingredients_data:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_data['id']
            )
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=amount
            )
        return super().update(instance, validated_data)


class FavAndShopCartSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного и списка покупок."""
    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)
    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(
        source='recipe.cooking_time', read_only=True
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода коротких рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода рецептов пользователя."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True, source='recipes.count'
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscription.objects.filter(
                author=user, subscriber=obj
            ).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = int(request.query_params.get('recipes_limit', '10000'))
        return ShortRecipeSerializer(
            obj.recipes.all()[:recipes_limit], many=True, context=self.context
        ).data
