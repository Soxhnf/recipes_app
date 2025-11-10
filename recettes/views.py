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

    categories = Category.objects.all()
    ingredients = Ingredient.objects.all()

    context = {
        'recipes': recipes,
        'categories': categories,
        'ingredients': ingredients,
        'selected_category': category_name,
        'selected_ingredient': ingredient_name,
        'selected_rating': min_rating or '',
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
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            # Créer la recette sans sauvegarder tout de suite
            recipe = form.save(commit=False)
            # Assigner l'utilisateur connecté comme auteur
            recipe.author = request.user
            recipe.save()
            # Sauvegarder les ingrédients (ManyToMany)
            form.save_m2m()
            messages.success(request, 'Votre recette a été créée avec succès !')
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm()

    context = {
        'form': form,
        'title': 'Créer une nouvelle recette'
    }
    return render(request, 'add_recipes.html', context)


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