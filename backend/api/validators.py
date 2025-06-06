from rest_framework import serializers


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
    ingredients_id_list = [
        ingredient['ingredient'].id for ingredient in ingredients_data
    ]
    if len(ingredients_id_list) != len(set(ingredients_id_list)):
        raise serializers.ValidationError({
            'ingredients': 'Ингредиенты не должны повторяться.'
        })
