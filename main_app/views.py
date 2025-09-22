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
            login(request, user)
            messages.success(request, 'Welcome to Gridiron Fantasy!')
            return redirect('team-index')  # Redirect to all teams after signup
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
    # Disallow the renaming of a player by excluding the name field
    fields = ['position', 'description', 'age']

@method_decorator(login_required, name='dispatch')
class PlayerDelete(DeleteView):
    model = Player
    success_url = '/players/'

@method_decorator(login_required, name='dispatch')
class TeamDelete(DeleteView):
    model = Team
    success_url = '/teams/'

    def get_queryset(self):
        return Team.objects.filter(owner=self.request.user)

class TeamList(ListView):
    model = Team
    # Show all teams to all users
    def get_queryset(self):
        return Team.objects.all()

class TeamDetail(DetailView):
    model = Team

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user == self.object.owner:
            new_name = request.POST.get("team_name", "").strip()
            if new_name:
                self.object.name = new_name
                self.object.save()
                messages.success(request, "Team name updated.")
            else:
                messages.error(request, "Team name cannot be empty.")
        return redirect(self.object.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.object
        
        # Define the proper roster order
        roster_order = ['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'TE', 'FLEX', 'K', 'DEF', 
                       'BENCH1', 'BENCH2', 'BENCH3', 'BENCH4', 'BENCH5', 'BENCH6']
        
        # Get all roster spots for this team
        spots_dict = {spot.slot: spot for spot in team.roster_spots.all()}
        
        # Order them according to roster_order
        ordered_roster_spots = []
        for slot in roster_order:
            if slot in spots_dict:
                ordered_roster_spots.append(spots_dict[slot])
        
        context['ordered_roster_spots'] = ordered_roster_spots
        return context

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@login_required
def roster_spot_assign(request, team_id, spot_id):
    team = get_object_or_404(Team, id=team_id, owner=request.user)
    spot = get_object_or_404(RosterSpot, id=spot_id, team=team)
    query = request.GET.get('q', '')

    # Determine allowed positions for this spot
    slot = spot.slot
    if slot.startswith('RB'):
        allowed_positions = ['RB']
    elif slot.startswith('WR'):
        allowed_positions = ['WR']
    elif slot == 'QB':
        allowed_positions = ['QB']
    elif slot == 'TE':
        allowed_positions = ['TE']
    elif slot == 'K':
        allowed_positions = ['K']
    elif slot == 'DEF':
        allowed_positions = ['DEF']
    elif slot == 'FLEX':
        allowed_positions = ['RB', 'WR', 'TE']
    elif slot.startswith('BENCH'):
        allowed_positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
    else:
        allowed_positions = []

    # Filter players by allowed positions
    players = Player.objects.filter(position__in=allowed_positions)
    if query:
        players = players.filter(
            Q(name__icontains=query) |
            Q(position__icontains=query) |
            Q(team__icontains=query)
        )

    if request.method == 'POST':
        if 'drop' in request.POST:
            spot.player = None
            spot.save()
            return redirect('team-detail', pk=team.id)
        player_id = request.POST.get('player_id')
        if player_id:
            player = get_object_or_404(Player, id=player_id)
            if player.position in allowed_positions:
                spot.player = player
                spot.save()
            return redirect('team-detail', pk=team.id)

    # Always show roster spots in the correct order
    ordered_spots = []
    slot_order = [slot for slot, _ in ROSTER_SLOTS]
    spots_dict = {s.slot: s for s in team.roster_spots.all()}
    for slot in slot_order:
        if slot == spot.slot:
            ordered_spots.append(spot)
        elif slot in spots_dict:
            ordered_spots.append(spots_dict[slot])

    return render(request, 'main_app/roster_spot_assign.html', {
        'team': team,
        'spot': spot,
        'players': players,
        'query': query,
        'allowed_positions': allowed_positions,
        'ordered_spots': ordered_spots,
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

    unique = set()
    unique_players = []
    for p in players:
        key = (p.name, p.team, p.position)
        if key not in unique:
            unique.add(key)
            unique_players.append(p)
    players = unique_players

    if sort == "position":
        players = sorted(players, key=lambda p: (p.position, p.name))
    elif sort == "team":
        players = sorted(players, key=lambda p: (p.team, p.name))
    else:
        players = sorted(players, key=lambda p: p.name)

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
        team_name = request.POST.get("team_name")
        if team_name:
            team = Team.objects.create(name=team_name, owner=request.user)
            # Assign players to roster spots (do NOT create extra spots, only update the ones created by default)
            for slot, _ in roster_slots:
                player_id = request.POST.get(f"slot_{slot}")
                # Find the existing RosterSpot for this team and slot
                spot = RosterSpot.objects.filter(team=team, slot=slot).first()
                if not spot:
                    spot = RosterSpot.objects.create(team=team, slot=slot)
                if player_id:
                    player = Player.objects.get(id=player_id)
                    spot.player = player
                    spot.save()
            # Redirect to the new team's detail page
            return redirect(team.get_absolute_url())
        else:
            messages.error(request, "Team name is required.")

    # No form object needed, just pass None
    return render(request, "main_app/team_form.html", {
        "form": None,
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
            Q(team__icontains=query)
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
    players = resp.json()  # Adjust this if I need to change the API structure

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
        key = (p.get('name'), p.get('team'), p.get('position'))
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
