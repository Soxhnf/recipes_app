# Fichier: accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from recettes.models import Recipe
from .forms import EditProfileForm
from django.contrib.auth.forms import PasswordChangeForm  # Importe le formulaire de mot de passe


#
# VOS VUES 'register', 'login_user', 'logout_user'
# (Je les ai copiées de votre code, elles sont correctes)
#
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm']

        if password == confirm:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Nom d'utilisateur déjà pris")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Cette adresse email est déjà utilisée")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, "Compte créé avec succès !")
                return redirect('accounts:login')
        else:
            messages.error(request, "Les mots de passe ne correspondent pas")
    return render(request, 'register.html')


def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            username = None
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Email ou mot de passe incorrect")
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('home')


#
# VUES MISES À JOUR ET NOUVELLES VUES
#

@login_required
def my_recipes(request):

    recipes = Recipe.objects.filter(author=request.user)
    context = {
        'recipes': recipes,
        'page_title': "Mes Recettes",
        'view_mode': 'recipes',
    }
    return render(request, 'my_recipes.html', context)


@login_required
def my_favorites(request):

    recipes = request.user.favorite_recipes.all()
    context = {
        'recipes': recipes,
        'page_title': "Mes Favoris",
        'view_mode': 'favorites',
    }

    return render(request, 'my_recipes.html', context)


@login_required
def edit_profile(request):

    if request.method == 'POST':
        # Détermine quel formulaire a été soumis
        if 'change_profile' in request.POST:
            profile_form = EditProfileForm(request.POST, instance=request.user)
            password_form = PasswordChangeForm(request.user)  # Formulaire vide

            if profile_form.is_valid():
                if 'email' in profile_form.changed_data:
                    email = profile_form.cleaned_data['email']
                    if User.objects.filter(email=email).exclude(username=request.user.username).exists():
                        messages.error(request, 'Cet email est déjà utilisé par un autre compte.')
                    else:
                        profile_form.save()
                        messages.success(request, 'Profil mis à jour avec succès !')
                        return redirect('edit_profile')
                else:
                    profile_form.save()
                    messages.success(request, 'Profil mis à jour avec succès !')
                    return redirect('edit_profile')

        elif 'change_password' in request.POST:
            profile_form = EditProfileForm(instance=request.user)  # Formulaire vide
            password_form = PasswordChangeForm(request.user, request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Maintient l'utilisateur connecté
                messages.success(request, 'Votre mot de passe a été changé avec succès !')
                return redirect('edit_profile')
            else:
                messages.error(request,
                               'Erreur lors du changement de mot de passe. Veuillez corriger les erreurs ci-dessous.')

    else:
        # Requête GET (chargement normal)
        profile_form = EditProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'page_title': "Modifier le Profil",
        'view_mode': 'edit_profile',  # Pour la sidebar
    }
    return render(request, 'edit_profile.html', context)