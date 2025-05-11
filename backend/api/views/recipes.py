from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination

from api.models import Recipe
from api.serializers import RecipeSerializer
from api.permissions import IsAuthorOrReadOnly

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

