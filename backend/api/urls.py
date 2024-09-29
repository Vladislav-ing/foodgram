from django.urls import include, path
from rest_framework import routers

from ingredient.views import TagViewSet, IngredientViewSet
from registration.views import ProfileViewSet
from recipe.views import CRUD_RecipeViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('users', ProfileViewSet, basename='user')
router_v1.register('tags', TagViewSet, basename='tag')
router_v1.register('ingredients', IngredientViewSet, basename='ingredient')
router_v1.register('recipes', CRUD_RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
