from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import permissions
from rest_framework.decorators import action

from api.models import Recipe
from api.serializers import RecipeSerializer
from api.permissions import IsAuthorOrReadOnly

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination


    # @action(detail=True, methods=['GET'], permission_classes=[permissions.IsAuthenticated])
    # def favorite(self, request, pk=None):
