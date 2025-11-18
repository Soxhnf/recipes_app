from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('create-recipe/', views.create_recipe, name='create_recipe'),
    path('my-recipes/', views.my_recipes, name='my_recipes'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('recipe/<int:recipe_id>/delete/', views.delete_recipe, name='delete_recipe'),
path('toggle_favorite/<int:recipe_id>/', views.toggle_favorite, name='toggle_favorite'),
path('recipe/<int:recipe_id>/edit/', views.edit_recipe, name='edit_recipe'),
]