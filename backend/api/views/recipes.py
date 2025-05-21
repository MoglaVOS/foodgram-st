from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.db.models import F, Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import now

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from api.models import (
    Recipe, Ingredient, Favorite,
    ShoppingCart, RecipeIngredient
)
from api.serializers import ShortRecipeSerializer
from api.serializers.recipes import (
    RecipeSerializer, IngredientSerializer
)
from api.filter import IngredientSearchFilter, RecipeSearchFilter
from api.permissions import IsAuthorOrReadOnly


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeSearchFilter

    def perform_create(self, serializer):
        """Создать рецепт и присовить автора"""
        serializer.save(author=self.request.user)

    def check_recipe_exists(self, model, request, recipe_id):
        """Добавление/удаление рецепта в избранное/список покупок."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.method == 'POST':
            obj, is_created = model.objects.get_or_create(
                user_id=user.id, recipe_id=recipe.id
            )
            if not is_created:
                return Response({'detail': 'Рецепт уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(ShortRecipeSerializer(recipe).data,
                            status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            deleted, _ = model.objects.filter(
                user=user, recipe=recipe
            ).delete()
            if deleted:
                return Response(
                    {'detail': 'Рецепт успешно удален из избранного'},
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response({'detail': 'Рецепт не найден в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        """Для добавления/удаления рецепта в избранное."""
        return self.check_recipe_exists(Favorite, request, pk)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        """Добавление/удаление рецепта в список покупок."""
        return self.check_recipe_exists(ShoppingCart, request, pk)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        url = f'{request.get_host()}/recipes/{recipe.id}/'
        return Response({'short-link': url}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit')
        ).annotate(amount=Sum('amount')).order_by('name')

        recipes = Recipe.objects.filter(
            shopping_carts__user=user
        ).select_related('author')

        content = '\n'.join([
            f"Список покупок для: {user.get_full_name() or user.username}",
            f"Дата: {now().strftime('%d.%m.%Y')}",
            '',
            'Рецепты:',
            *(
                f"- {recipe.name} (автор:"
                f" {recipe.author.get_full_name() or recipe.author.username})"
                for recipe in recipes),
            '',
            'Ингредиенты:',
            *(f"{i}. {item['name'].capitalize()} — "
              f"{item['amount']} {item['unit']}"
              for i, item in enumerate(ingredients, 1))
        ]) or 'Список покупок пуст.'

        return FileResponse(
            content,
            filename='shopping_list.txt',
            as_attachment=True,
            content_type='text/plain'
        )
