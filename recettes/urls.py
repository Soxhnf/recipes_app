from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('create-recipe/', views.create_recipe, name='create_recipe'),
    path('my-recipes/', views.my_recipes, name='my_recipes'),
]