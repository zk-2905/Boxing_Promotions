from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from .models import BoxingEvent, UserProfile, EventRegistration
from .views import find_matching_user
from datetime import timedelta, date, datetime
from django.urls import reverse
import time
import logging

logger = logging.getLogger(__name__)

class EventsListTest(TestCase):
    def setUp(self):
        # Create a test user for authentication
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_events_list_display(self):
        # Create a test event
        event = BoxingEvent.objects.create(
            title='Test Event',
            date=date.today() + timedelta(days=7),  # Set a date in the future
            location='Test Location'
        )

        # Perform a GET request to the events_list view
        response = self.client.get(reverse('box:events_list'))

        # Print the response content for debugging
        print(response.content.decode('utf-8'))

        # Check if the event title is present in the response
        self.assertContains(response, event.title)
