from django.core.management.base import BaseCommand
from box.models import EventRegistration, Fight

class Command(BaseCommand):
    help = 'Deletes all events from the database'

    def handle(self, *args, **options):
        # Delete all events
        EventRegistration.objects.all().delete()
        Fight.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All registrations have been deleted.'))