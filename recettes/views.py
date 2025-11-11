import json

import requests
from django.shortcuts import render, get_object_or_404, redirect
from .models import Recipe, Category, Ingredient, Review

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RecipeForm, ReviewForm


def home(request):
    recipes = Recipe.objects.all()

    # Filtres
    category_name = request.GET.get('category')
    ingredient_name = request.GET.get('ingredient')
    min_rating = request.GET.get('min_rating')

    if category_name:
        recipes = recipes.filter(category__name=category_name)

    if ingredient_name:
        recipes = recipes.filter(ingredients__name__icontains=ingredient_name)

    if min_rating:
        recipes = recipes.filter(rating__gte=float(min_rating))

    # --- Charger les données de l’API ---
    api_recipes = []
    try:
        response = requests.get("https://www.themealdb.com/api/json/v1/1/search.php?s=")
        data = response.json()
        api_recipes = data.get("meals", [])
    except Exception as e:
        print("Erreur API:", e)
        api_recipes = []

    # --- Appliquer les filtres aussi sur les recettes API ---
    if api_recipes:
        if category_name:
            api_recipes = [r for r in api_recipes if r.get('strCategory') == category_name]
        if ingredient_name:
            api_recipes = [
                r for r in api_recipes
                if ingredient_name.lower() in (
                    f"{r.get('strIngredient1', '')} {r.get('strIngredient2', '')} {r.get('strIngredient3', '')}"
                ).lower()
            ]

    categories = Category.objects.all()
    ingredients = Ingredient.objects.all()

    context = {
        'recipes': recipes,
        'categories': categories,
        'ingredients': ingredients,
        'selected_category': category_name,
        'selected_ingredient': ingredient_name,
        'selected_rating': min_rating or '',
        'api_recipes': api_recipes,
    }
    return render(request, 'home.html', context)


def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    top_level_reviews = recipe.reviews.filter(parent=None)
    review_form = ReviewForm()

    if request.method == 'POST' and request.user.is_authenticated:
        form_data = ReviewForm(request.POST)
        parent_id = request.POST.get('parent_id')

        if parent_id:
            # C'est une RÉPONSE (commentaire seul)
            if form_data.is_valid():
                try:
                    parent_review = Review.objects.get(id=parent_id)
                    new_review = form_data.save(commit=False)
                    new_review.recipe = recipe
                    new_review.user = request.user
                    new_review.parent = parent_review
                    new_review.rating = parent_review.rating  # Une réponse hérite la note
                    new_review.save()
                    messages.success(request, 'Votre réponse a été ajoutée.')
                except Review.DoesNotExist:
                    messages.error(request, 'Commentaire parent introuvable.')
                return redirect('recipe_detail', recipe_id=recipe.id)

        else:
            # C'est un NOUVEL AVIS (note + commentaire optionnel)

            # --- VÉRIFICATION MANUELLE DE LA NOTE ---
            rating_value = request.POST.get('rating')
            if not rating_value:
                messages.error(request, 'Veuillez sélectionner une note (étoiles) pour laisser un avis.')

            elif form_data.is_valid():
                new_review = form_data.save(commit=False)
                new_review.recipe = recipe
                new_review.user = request.user
                # La note est déjà dans form_data.cleaned_data['rating']
                new_review.save()
                messages.success(request, 'Votre avis a été ajouté.')
                return redirect('recipe_detail', recipe_id=recipe.id)

    # Contexte pour le GET ou si le formulaire POST échoue
    context = {
        'recipe': recipe,
        'reviews': top_level_reviews,
        'review_form': review_form,  # Toujours un formulaire vide en cas d'échec
    }
    return render(request, 'recipe_detail.html', context)



@login_required
def create_recipe(request):
    storage = messages.get_messages(request)
    storage.used = True

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()

            # Handle custom ingredients
            ingredients_json = form.cleaned_data.get('ingredients_list')
            if ingredients_json:
                ingredients = json.loads(ingredients_json)
                for name in ingredients:
                    ing, created = Ingredient.objects.get_or_create(name=name.strip().capitalize())
                    recipe.ingredients.add(ing)

            messages.success(request, 'Votre recette a été créée avec succès !')
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm()

    return render(request, 'add_recipes.html', {'form': form, 'title': 'Créer une nouvelle recette'})


@login_required
def my_recipes(request):
    # Afficher les recettes de l'utilisateur connecté
    recipes = Recipe.objects.filter(author=request.user)
    context = {
        'recipes': recipes
    }
    return render(request, 'my_recipes.html', context)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    recipe_id = review.recipe.id

    # Seul l'auteur de la recette peut supprimer les commentaires
    if request.user == review.recipe.author:
        review.delete()
        messages.success(request, 'Le commentaire a été supprimé.')
    else:
        messages.error(request, "Vous n'avez pas la permission de faire cela.")

    return redirect('recipe_detail', recipe_id=recipe_id)
@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if recipe.author != request.user:
        messages.error(request, "Vous n'avez pas la permission de supprimer cette recette.")
        return redirect('home')

    if request.method == 'POST':
        recipe.delete()
        messages.success(request, "Recette supprimée avec succès.")
        return redirect('home')

    return redirect('recipe_detail', recipe_id=recipe.id)