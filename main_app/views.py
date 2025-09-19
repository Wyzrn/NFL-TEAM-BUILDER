from django.shortcuts import render, get_object_or_404
from .models import Player
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def player_index(request):
    players = Player.objects.all()
    return render(request, 'players/index.html', {'players': players})

def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    return render(request, 'players/detail.html', {'player': player})

class PlayerCreate(CreateView):
    model = Player
    fields = '__all__'

class PlayerUpdate(UpdateView):
    model = Player
    # Let's disallow the renaming of a player by excluding the name field!
    fields = ['position', 'description', 'age']

class PlayerDelete(DeleteView):
    model = Player
    success_url = '/players/'
