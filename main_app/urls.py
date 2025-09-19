from django.urls import path
from . import views  # Import views to connect routes to view functions
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('teams/', views.TeamList.as_view(), name='team-index'),
    path('teams/create/', views.team_create, name='team-create'),
    path('teams/<int:pk>/', views.TeamDetail.as_view(), name='team-detail'),
    path('teams/<int:pk>/update/', views.TeamUpdate.as_view(), name='team-update'),
    path('teams/<int:pk>/delete/', views.TeamDelete.as_view(), name='team-delete'),
    path('teams/<int:team_id>/roster/<int:spot_id>/assign/', views.roster_spot_assign, name='roster-assign'),
    path('players/search/', views.player_search, name='player-search'),
]

# Define the home view function