from django.urls import path
from . import views # Import views to connect routes to view functions
from django.shortcuts import render
# Import HttpResponse to send text-based responses
from django.http import HttpResponse

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('cats/', views.cat_index, name='cat-index'),
]

# Define the home view function
