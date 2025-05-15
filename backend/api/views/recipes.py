from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.db.models import F, Sum
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from io import BytesIO

from api.models import (
    Recipe, Ingredient, Favorite,
    ShoppingCart, RecipeIngredient
)
from api.serializers.recipes import (
    RecipeSerializer, IngredientSerializer,
    FavAndShopCartSerializer
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

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            obj, is_created = Favorite.objects.get_or_create(
                user=user, recipe=recipe
            )
            if not is_created:
                return Response(
                    {'detail': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                FavAndShopCartSerializer(obj).data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            deleted, _ = Favorite.objects.filter(
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
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            obj, is_created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe
            )
            if not is_created:
                return Response({'detail': 'Рецепт уже в списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(FavAndShopCartSerializer(obj).data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            deleted, _ = ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).delete()
            if deleted:
                return Response(
                    {'detail': 'Рецепт успешно удален из списка покупок'},
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response({'detail': 'Рецепт не найден в списке покупок'},
                            status=status.HTTP_400_BAD_REQUEST
                            )

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        relative_url = f'/api/recipes/{recipe.id}/'
        absolute_url = request.build_absolute_uri(relative_url)
        return Response(
            {'short-link': absolute_url},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit')
        ).annotate(amount=Sum('amount')).order_by('name')

        content = '\n'.join(
            f"{i}. {item['name'].capitalize()} "
            f"— {item['amount']} {item['unit']}"
            for i, item in enumerate(ingredients, 1)
        ) or 'Empty list.'

        buffer = BytesIO(content.encode('utf-8'))
        return FileResponse(
            buffer,
            filename='shopping_list.txt',
            as_attachment=True,
            content_type='text/plain'
        )
