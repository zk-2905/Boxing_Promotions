from django.core.management.base import BaseCommand
from box.models import BoxingEvent

class Command(BaseCommand):
    help = 'Deletes all events from the database'

    def handle(self, *args, **options):
        # Delete all events
        BoxingEvent.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All events have been deleted.'))