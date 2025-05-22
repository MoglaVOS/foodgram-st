from rest_framework import serializers

from api.models import (
    Ingredient, Recipe, RecipeIngredient, User
)
from api.serializers.users import UserSerializer
from drf_extra_fields.fields import Base64ImageField

from api.validators import validate_ingredients_data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
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
    ingredients = RecipeIngredientSerializer(
        many=True, source='ingredients_amounts'
    )
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
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
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shopping_carts.filter(user=request.user).exists()
        return False

    @staticmethod
    def validate_image(image):
        if not image:
            raise serializers.ValidationError({'image': 'Обязательное поле.'})
        return image

    @staticmethod
    def set_recipe_ingredients(recipe, ingredients):
        """Добавление ингредиентов в рецепт."""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=x['ingredient'].id,
                amount=x['amount'],
            )
            for x in ingredients
        )

    def create(self, validated_data):
        """Создание рецепта."""
        ingredients_data = validated_data.pop('ingredients_amounts')
        validate_ingredients_data(ingredients_data)
        recipe = super().create(validated_data)
        self.set_recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        ingredients_data = validated_data.pop('ingredients_amounts', None)
        validate_ingredients_data(ingredients_data)
        instance.ingredients_amounts.all().delete()
        self.set_recipe_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода коротких рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class UserRecipeSerializer(UserSerializer):
    """Сериализатор для вывода рецептов пользователя."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True, source='recipes.count'
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = int(request.query_params.get('recipes_limit', '10000'))
        return ShortRecipeSerializer(
            obj.recipes.all()[:recipes_limit], many=True, context=self.context
        ).data
