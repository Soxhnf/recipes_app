from django import forms
from .models import Recipe, Category, Ingredient, Review


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


class ReviewForm(forms.ModelForm):
    # Définir les choix pour le widget
    STAR_CHOICES = [(i, str(i)) for i in range(1, 6)]

    rating = forms.TypedChoiceField(
        choices=STAR_CHOICES,
        coerce= int,  # S'assure que la valeur est un entier
        widget=forms.RadioSelect(attrs={'class': 'star-radio'}),  # On stylera cette classe
        label="Note",
        required=False  # Rendu optionnel DANS LE FORMULAIRE
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Partagez votre avis sur cette recette...',
                 'class': 'form-control'
            }),
        }
        labels = {
            'comment': 'Commentaire (optionnel)'
        }