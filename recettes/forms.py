from django import forms
from .models import Recipe, Category, Ingredient, Review


class RecipeForm(forms.ModelForm):
    # Champ caché pour la liste dynamique d'ingrédients (rempli via JS)
    ingredients_list = forms.CharField(
        label='Ingrédients',
        required=False,
        widget=forms.HiddenInput()
    )

    # Champ d’instructions (zone de texte large)
    instructions = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
        required=True,
        label="Instructions"
    )

    class Meta:
        model = Recipe
        fields = [
            'title',
            'description',
            'instructions',
            'preparation_time',
            'category',
            'image',
            'ingredients_list'
        ]

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