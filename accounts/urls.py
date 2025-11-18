
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
app_name = 'accounts'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),


    path('my-recipes/', views.my_recipes, name='my_recipes'),

    path('my-favorites/', views.my_favorites, name='my_favorites'),


    path('edit-profile/', views.edit_profile, name='edit_profile'),
]