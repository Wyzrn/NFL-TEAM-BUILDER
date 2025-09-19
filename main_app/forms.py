from django import forms
from .models import Team, Player, ROSTER_SLOTS

class TeamCreateForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for slot, label in ROSTER_SLOTS:
            self.fields[f'player_{slot}'] = forms.ModelChoiceField(
                queryset=Player.objects.all(),
                required=False,
                label=label,
                widget=forms.Select(attrs={'class': 'player-select'})
            )