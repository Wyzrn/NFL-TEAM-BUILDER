from django.urls import path
from . import views  # Import views to connect routes to view functions
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LogoutView
from .views import PlayerCreate, PlayerUpdate, PlayerDelete

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('teams/', views.TeamList.as_view(), name='team-index'),
    path('teams/create/', views.team_create, name='team_create'),
    path('teams/<int:pk>/', views.TeamDetail.as_view(), name='team-detail'),
    path('teams/<int:pk>/delete/', views.TeamDelete.as_view(), name='team-delete'),
    path('teams/<int:team_id>/roster/<int:spot_id>/assign/', views.roster_spot_assign, name='roster-assign'),
    path('players/search/api/', views.player_search_api, name='player-search-api'),
    path('players/', views.player_index, name='players_index'),
    path('players/<int:pk>/', views.player_detail, name='player-detail'),
    path('signup/', views.signup, name='signup'),
    path('players/create/', PlayerCreate.as_view(), name='player-create'),
    path('players/<int:pk>/update/', PlayerUpdate.as_view(), name='player-update'),
    path('players/<int:pk>/delete/', PlayerDelete.as_view(), name='player-delete'),
]