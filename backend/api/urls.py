from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import RecipeViewSet, IngredientViewSet,  CustomUserViewSet

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'users', CustomUserViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
]
