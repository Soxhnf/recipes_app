from django.shortcuts import render, get_object_or_404
from .models import Recipe, Category, Ingredient

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RecipeForm



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
    return render(request, 'recipe_detail.html', {'recipe': recipe})





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