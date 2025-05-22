from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    RecipeViewSet, IngredientViewSet,
    UserViewSet, ShortLinkRedirectView
)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', UserViewSet, basename='users')
urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:pk>/get-link/', ShortLinkRedirectView.as_view(),
         name='short-link'),
]
