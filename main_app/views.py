from django.shortcuts import render, get_object_or_404, redirect
from .models import Player, Team, RosterSpot
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
from .forms import TeamCreateForm
from .models import Team, RosterSpot, ROSTER_SLOTS
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

@login_required
def player_index(request):
    players = Player.objects.all()
    return render(request, 'players/index.html', {'players': players})

@login_required
def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    return render(request, 'players/detail.html', {'player': player})

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
    if request.method == 'POST':
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.owner = request.user
            team.save()
            for slot, _ in ROSTER_SLOTS:
                player = form.cleaned_data.get(f'player_{slot}')
                RosterSpot.objects.create(team=team, slot=slot, player=player)
            return redirect('team-detail', pk=team.pk)
    else:
        form = TeamCreateForm()

    # build roster_fields only for fields that actually exist on the form
    roster_fields = []
    for slot, label in ROSTER_SLOTS:
        field_name = f'player_{slot}'
        bound_field = form[field_name] if field_name in form.fields else None
        roster_fields.append((slot, label, bound_field))

    return render(request, 'main_app/team_form.html', {'form': form, 'roster_fields': roster_fields})

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
