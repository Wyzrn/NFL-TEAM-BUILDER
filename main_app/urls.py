from django.urls import path
from . import views  # Import views to connect routes to view functions
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.edit import CreateView

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('players/', views.player_index, name='player-index'),
    path('players/<int:player_id>/', views.player_detail, name='player-detail'),
    path('players/create/', views.PlayerCreate.as_view(), name='player-create'),
    path('players/<int:pk>/update/', views.PlayerUpdate.as_view(), name='player-update'),
    path('players/<int:pk>/delete/', views.PlayerDelete.as_view(), name='player-delete'),
]

# Define the home view function