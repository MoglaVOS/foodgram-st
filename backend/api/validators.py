from rest_framework import serializers
from .models import Ingredient


def validate_ingredients_data(ingredients_data):
    """Валидация создания/обновления ингредиентов."""
    if ingredients_data is None:
        raise serializers.ValidationError({
            'ingredients': 'Поле "Ингредиенты" обязательно.'
        })
    if not isinstance(ingredients_data, list) or len(ingredients_data) == 0:
        raise serializers.ValidationError({
            'ingredients': 'У рецепта должен быть хотя бы один ингредиент.'
        })
    try:
        ingredients_id_list = [
            ingredient['id'] for ingredient in ingredients_data
        ]
    except KeyError:
        raise serializers.ValidationError({
            'ingredients': 'Каждый ингредиент должен содержать поле id.'
        })
    existing_ids = set(
        Ingredient.objects.filter(
            id__in=ingredients_id_list).values_list('id', flat=True)
    )
    if len(existing_ids) != len(ingredients_id_list):
        raise serializers.ValidationError({
            'ingredients': 'Некоторые ингредиенты не существуют.'
        })
    if len(ingredients_id_list) != len(set(ingredients_id_list)):
        raise serializers.ValidationError({
            'ingredients': 'Ингредиенты не должны повторяться.'
        })
    for ingredient in ingredients_data:
        if int(ingredient.get('amount', 0)) <= 0:
            raise serializers.ValidationError({
                'ingredients': 'Количество ингредиента должно быть больше 0.'
            })
    return ingredients_data
