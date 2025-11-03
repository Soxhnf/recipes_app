from django.contrib import admin
from .models import Category, Ingredient, Recipe, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'rating', 'preparation_time', 'created_at']
    list_filter = ['category', 'rating', 'created_at']
    search_fields = ['title', 'description']
    filter_horizontal = ['ingredients']  # Permet de mieux gérer les ingrédients

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['recipe__title', 'user__username']