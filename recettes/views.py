import json
import requests
from django.shortcuts import render, get_object_or_404, redirect
from .models import Recipe, Category, Ingredient, Review
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
import functools
import operator
from .forms import RecipeForm, ReviewForm
from django.template.loader import render_to_string


def home(request):
    recipes = Recipe.objects.all()

    # --- Lecture des filtres de l'URL ---
    category_name = request.GET.get('category')
    ingredient_query = request.GET.get('ingredient')
    show_favorites = request.GET.get('favorites')

    # --- Logique de filtre (inchangée) ---
    if ingredient_query:
        search_terms = ingredient_query.split()
        conditions = []
        for term in search_terms:
            conditions.append(
                Q(title__icontains=term) | Q(ingredients__name__icontains=term)
            )
        if conditions:
            query = functools.reduce(operator.and_, conditions)
            recipes = recipes.filter(query)
    if category_name:
        recipes = recipes.filter(category__name=category_name)
    if show_favorites == 'true' and request.user.is_authenticated:
        recipes = recipes.filter(favorited_by=request.user)

    # --- Appel API ---
    api_recipes = []
    try:
        response = requests.get("https://www.themealdb.com/api/json/v1/1/search.php?s=")
        data = response.json()
        api_recipes = data.get("meals", [])
    except Exception as e:
        print("Erreur API:", e)
        api_recipes = []

    # --- Filtrage API ---
    if api_recipes:
        if category_name:
            api_recipes = [r for r in api_recipes if r.get('strCategory') == category_name]
        if ingredient_query:
            search_terms = ingredient_query.split()
            filtered_api_recipes = []
            for r in api_recipes:
                all_ingredients = [r.get(f'strIngredient{i}') or '' for i in range(1, 21)]
                api_ingredients_str = " ".join(all_ingredients).lower()
                recipe_title = (r.get('strMeal') or '').lower()
                search_corpus = f"{recipe_title} {api_ingredients_str}"
                if all(term.lower() in search_corpus for term in search_terms):
                    filtered_api_recipes.append(r)
            api_recipes = filtered_api_recipes

    categories = Category.objects.all()

    # --- Compteur de favoris  ---
    favorites_count = 0
    if request.user.is_authenticated:
        favorites_count = request.user.favorite_recipes.count()

    # --- Préparation du contexte (ajout de 'user') ---
    context = {
        'recipes': recipes.distinct(),
        'categories': categories,
        'selected_category': category_name,
        'selected_ingredient': ingredient_query,
        'api_recipes': api_recipes,
        'favorites_count': favorites_count,
        'user': request.user  # Important pour le partiel
    }

    # --- DÉTECTION AJAX RENVOIE DU JSON ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # 1. Génère le HTML de la grille dans une chaîne de caractères
        html = render_to_string(
            'partials/_recipe_grid.html',
            context,
            request=request
        )
        # 2. Renvoie le HTML ET le compteur à jour
        return JsonResponse({
            'html': html,
            'favorites_count': favorites_count
        })

    # Si ce n'est pas de l'AJAX, renvoie la page complète
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
            #  NOUVEL AVIS (note + commentaire optionnel)

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


@login_required
def toggle_favorite(request, recipe_id):
    # Vérifie que c'est une requête POST (pour la sécurité)
    if request.method == 'POST':
        recipe = get_object_or_404(Recipe, id=recipe_id)

        if recipe.favorited_by.filter(id=request.user.id).exists():
            recipe.favorited_by.remove(request.user)
            is_favorited = False
        else:
            recipe.favorited_by.add(request.user)
            is_favorited = True

        # Renvoie le nouveau statut et le nouveau compte
        new_count = request.user.favorite_recipes.count()
        return JsonResponse({'status': 'ok', 'is_favorited': is_favorited, 'favorites_count': new_count})

    # Si ce n'est pas POST, ne rien faire
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Sécurité : Vérifie que l'utilisateur est bien l'auteur
    if recipe.author != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette recette.")
        return redirect('home')

    if request.method == 'POST':
        # Traite le formulaire soumis
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            # Sauvegarde la recette (mais pas les M2M)
            recipe = form.save(commit=False)
            recipe.author = request.user  # Ré-assigne l'auteur (juste au cas où)
            recipe.save()

            # Logique pour les ingrédients (identique à create_recipe)
            # 1. Efface les anciens ingrédients
            recipe.ingredients.clear()

            # 2. Ajoute les nouveaux
            ingredients_json = form.cleaned_data.get('ingredients_list')
            if ingredients_json:
                ingredients = json.loads(ingredients_json)
                for name in ingredients:
                    ing, created = Ingredient.objects.get_or_create(name=name.strip().capitalize())
                    recipe.ingredients.add(ing)

            messages.success(request, 'Recette modifiée avec succès !')
            return redirect('recipe_detail', recipe_id=recipe.id)

    else:
        # Requête GET : Affiche le formulaire pré-rempli

        # 1. Récupère les ingrédients actuels de la recette
        current_ingredients = list(recipe.ingredients.all().values_list('name', flat=True))

        # 2. Convertit-les en une chaîne JSON pour le script
        ingredients_json = json.dumps(current_ingredients)

        # 3. Initialise le formulaire avec les données de la recette ET le JSON des ingrédients
        form = RecipeForm(instance=recipe, initial={'ingredients_list': ingredients_json})

    # Réutilise le template 'add_recipes.html'
    context = {
        'form': form,
        'title': 'Modifier ma Recette'
    }
    return render(request, 'add_recipes.html', context)