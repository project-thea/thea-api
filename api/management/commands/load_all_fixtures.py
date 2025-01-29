from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Load all fixtures'

    def handle(self, *args, **kwargs):
        fixtures = [
            'users.json', 
            'locations.json', 
            'diseases.json', 
            'tests.json', 
            'results.json', 
            'hotspots.json',
            'hotspotusermaps.json',
        ]
        for fixture in fixtures:
            call_command('loaddata', fixture)
            self.stdout.write(self.style.SUCCESS(f'Loaded fixture: {fixture}'))
