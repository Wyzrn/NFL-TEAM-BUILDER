from django.db import models
from django.urls import reverse

class Player(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    age = models.IntegerField()

    def __str__(self):
        return self.name

    # Define a method to get the URL for this particular player instance
    def get_absolute_url(self):
        # Use the 'reverse' function to dynamically find the URL for viewing this player's details
        return reverse('player-detail', kwargs={'player_id': self.id})