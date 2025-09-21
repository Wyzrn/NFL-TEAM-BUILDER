from django.shortcuts import render, get_object_or_404, redirect
from .models import Player, Team, RosterSpot, ROSTER_SLOTS
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q
from .forms import TeamCreateForm, TeamForm
import requests

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

@login_required
def player_index(request):
    players = Player.objects.all()
    return render(request, 'players/index.html', {'players': players})

@login_required
def player_detail(request, pk):
    player = Player.objects.get(pk=pk)
    return render(request, 'main_app/player_detail.html', {'player': player})

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after signup
            messages.success(request, 'Welcome to Gridiron Fantasy!')
            return redirect('player-index')  # Redirect to player list or any page you want
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

@method_decorator(login_required, name='dispatch')
class PlayerCreate(CreateView):
    model = Player
    fields = '__all__'

@method_decorator(login_required, name='dispatch')
class PlayerUpdate(UpdateView):
    model = Player
    # Let's disallow the renaming of a player by excluding the name field!
    fields = ['position', 'description', 'age']

@method_decorator(login_required, name='dispatch')
class PlayerDelete(DeleteView):
    model = Player
    success_url = '/players/'

@method_decorator(login_required, name='dispatch')
class TeamCreate(CreateView):
    model = Team
    fields = ['name']
    success_url = reverse_lazy('team-index')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        # Create empty roster spots
        for slot in ROSTER_SLOTS:
            RosterSpot.objects.create(team=self.object, slot=slot)
        return response

@method_decorator(login_required, name='dispatch')
class TeamUpdate(UpdateView):
    model = Team
    fields = ['name']

@method_decorator(login_required, name='dispatch')
class TeamDelete(DeleteView):
    model = Team
    success_url = '/teams/'

@method_decorator(login_required, name='dispatch')
class TeamList(ListView):
    model = Team

@method_decorator(login_required, name='dispatch')
class TeamDetail(DetailView):
    model = Team

@login_required
def roster_spot_assign(request, team_id, spot_id):
    team = get_object_or_404(Team, id=team_id, owner=request.user)
    spot = get_object_or_404(RosterSpot, id=spot_id, team=team)
    query = request.GET.get('q', '')
    players = []
    if query:
        players = Player.objects.filter(
            Q(name__icontains=query) |
            Q(position__icontains=query) |
            Q(nfl_team__icontains=query)
        )
    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        player = get_object_or_404(Player, id=player_id)
        spot.player = player
        spot.save()
        return redirect('team-detail', pk=team.id)
    return render(request, 'main_app/roster_spot_assign.html', {
        'team': team,
        'spot': spot,
        'players': players,
        'query': query,
    })

@login_required
def team_create(request):
    q = request.GET.get("q", "").strip()
    selected_position = request.GET.get("position", "")
    selected_team = request.GET.get("team", "")
    sort = request.GET.get("sort", "name")

    players = Player.objects.all()
    if q:
        players = players.filter(
            Q(name__icontains=q) | Q(team__icontains=q) | Q(position__icontains=q)
        )
    if selected_position:
        players = players.filter(position=selected_position)
    if selected_team:
        players = players.filter(team=selected_team)
    if sort == "position":
        players = players.order_by("position", "name")
    elif sort == "team":
        players = players.order_by("team", "name")
    else:
        players = players.order_by("name")

    positions = sorted(set(Player.objects.values_list("position", flat=True)))
    teams = sorted(set(Player.objects.values_list("team", flat=True)))

    roster_slots = [
        ("QB", "Quarterback"),
        ("WR1", "Wide Receiver 1"),
        ("WR2", "Wide Receiver 2"),
        ("RB1", "Running Back 1"),
        ("RB2", "Running Back 2"),
        ("TE", "Tight End"),
        ("FLEX", "Flex"),
        ("K", "Kicker"),
        ("DEF", "Defense"),
        ("BENCH1", "Bench 1"),
        ("BENCH2", "Bench 2"),
        ("BENCH3", "Bench 3"),
        ("BENCH4", "Bench 4"),
        ("BENCH5", "Bench 5"),
        ("BENCH6", "Bench 6"),
    ]

    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("teams:list")
    else:
        form = TeamForm()

    return render(request, "main_app/team_form.html", {
        "form": form,
        "players": players,
        "positions": positions,
        "teams": teams,
        "roster_slots": roster_slots,
        "selected_position": selected_position,
        "selected_team": selected_team,
        "sort": sort,
        "q": q,
    })

@login_required
def player_search(request):
    query = request.GET.get('q', '')
    players = []
    if query:
        players = Player.objects.filter(
            Q(name__icontains=query) |
            Q(position__icontains=query) |
            Q(nfl_team__icontains=query)
        )
    return render(request, 'main_app/player_search.html', {'players': players, 'query': query})

RAPIDAPI_KEY = 'YOUR_RAPIDAPI_KEY'
RAPIDAPI_HOST = 'nfl-api-data.p.rapidapi.com'

def player_search_api(request):
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'name')
    position = request.GET.get('position', '')
    team = request.GET.get('team', '')

    url = 'https://nfl-api-data.p.rapidapi.com/nfl-player-stats/v1/data'
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    }
    resp = requests.get(url, headers=headers)
    players = resp.json()  # Adjust this if the API structure is different

    # Filter by search query
    if query:
        players = [p for p in players if query.lower() in p.get('name', '').lower()]

    # Filter by position
    if position:
        players = [p for p in players if p.get('position', '').lower() == position.lower()]

    # Filter by team
    if team:
        players = [p for p in players if p.get('team', '').lower() == team.lower()]

    # Sort
    if sort == 'name':
        players = sorted(players, key=lambda x: x.get('name', ''))
    elif sort == 'position':
        players = sorted(players, key=lambda x: x.get('position', ''))
    elif sort == 'team':
        players = sorted(players, key=lambda x: x.get('team', ''))

    # Get unique positions and teams for filter dropdowns
    positions = sorted(set(p.get('position', '') for p in players if p.get('position')))
    teams = sorted(set(p.get('team', '') for p in players if p.get('team')))

    unique = set()
    unique_players = []
    for p in players:
        key = (p.name, p.team, p.position)
        if key not in unique:
            unique.add(key)
            unique_players.append(p)
    players = unique_players

    return render(request, 'main_app/player_search_api.html', {
        'players': players,
        'query': query,
        'sort': sort,
        'positions': positions,
        'teams': teams,
        'selected_position': position,
        'selected_team': team,
    })
