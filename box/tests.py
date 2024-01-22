from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from .models import BoxingEvent
from datetime import timedelta, date, datetime
from django.urls import reverse
from celery.result import AsyncResult
from .tasks import create_events
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

class WeeklyAutomationTest(TestCase):
    def setUp(self):
        # Create a test user for authentication
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_weekly_automation(self):
        # Call the create_events task
        result = create_events.apply_async()

        try:
            # Wait for the task to complete with a timeout (adjust as needed)
            result_value = result.get(timeout=10)
        except Exception as e:
            # Log any exceptions during task execution
            logger.error(f"An error occurred during task execution: {e}")
            raise  # Re-raise the exception to fail the test

        # Assert that the task has completed successfully
        self.assertTrue(result.successful())

        # Check if events are created and deleted
        today = datetime.now()
        next_week = today + timedelta(days=(7 - today.weekday() + 1))

        # Ensure that events are created with the expected dates and locations
        event1_date = next_week + timedelta(days=5)  # Saturday of next week
        event2_date = next_week + timedelta(days=6)  # Sunday of next week

        event1_exists = BoxingEvent.objects.filter(date=event1_date).exists()
        self.assertTrue(event1_exists)

        event2_exists = BoxingEvent.objects.filter(date=event2_date).exists()
        self.assertTrue(event2_exists)

        # Wait for a sufficient amount of time for events to be deleted in the next task run
        time.sleep(60 * 2)  # Adjust as needed

        # Check if past events are deleted
        event1_exists_after_deletion = BoxingEvent.objects.filter(date=event1_date).exists()
        event2_exists_after_deletion = BoxingEvent.objects.filter(date=event2_date).exists()

        self.assertFalse(event1_exists_after_deletion)
        self.assertFalse(event2_exists_after_deletion)