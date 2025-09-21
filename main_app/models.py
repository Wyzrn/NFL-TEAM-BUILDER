from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

ROSTER_SLOTS = [
    ('QB', 'Quarterback'),
    ('WR1', 'Wide Receiver 1'),
    ('WR2', 'Wide Receiver 2'),
    ('RB1', 'Running Back 1'),
    ('RB2', 'Running Back 2'),
    ('TE', 'Tight End'),
    ('FLEX', 'Flex'),
    ('K', 'Kicker'),
    ('DEF', 'Defense'),
    ('BENCH1', 'Bench 1'),
    ('BENCH2', 'Bench 2'),
    ('BENCH3', 'Bench 3'),
    ('BENCH4', 'Bench 4'),
    ('BENCH5', 'Bench 5'),
    ('BENCH6', 'Bench 6'),
]

class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.CharField(max_length=50)
    position = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} - {self.team} ({self.position})"

class Team(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('team-detail', kwargs={'pk': self.pk})

class RosterSpot(models.Model):
    SLOT_CHOICES = ROSTER_SLOTS
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='roster_spots')
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    slot = models.CharField(max_length=10, choices=SLOT_CHOICES)

    def __str__(self):
        return f"{self.team.name} - {self.get_slot_display()}: {self.player}"