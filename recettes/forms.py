from django import forms
from .models import Recipe, Category, Ingredient


class RecipeForm(forms.ModelForm):
    # Champ pour sélectionner plusieurs ingrédients
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )

    # Champ pour les instructions avec une zone de texte plus grande
    instructions = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'instructions', 'preparation_time', 'category', 'ingredients', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'preparation_time': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'preparation_time': 'Temps de préparation (minutes)',
            'image': 'Image de la recette (optionnel)',
        }