from django.core.management.base import BaseCommand
from main_app.models import Player
from espn_api.football import League

class Command(BaseCommand):
    help = 'Import NFL players from ESPN'

    def handle(self, *args, **kwargs):
        # Replace with a real league ID and year
        league = League(league_id=123456, year=2024)
        count = 0
        for player in league.free_agents:
            Player.objects.update_or_create(
                name=player.name,
                defaults={
                    'position': player.position,
                    'nfl_team': player.proTeam,
                    'photo_url': getattr(player, 'headshot', ''),
                }
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Imported/updated {count} players.'))