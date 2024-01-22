from celery import shared_task
from datetime import datetime, timedelta
from .models import BoxingEvent
from django.db import transaction
import logging, time

logger = logging.getLogger(__name__)

@shared_task
@transaction.atomic
def create_events():
    try:
        start_time = time.time()
        logger.info("Starting create_events task")
        
        # Delete past events
        if delete_past_events():
            logger.info("Successfully deleted events.")

        # Create new events
        result1, result2 = create_new_events()
        if result1 and result2:
            logger.info("Successfully created events.")
        else:
            logger.warning("Failed to create one or more events.")
        end_time = time.time()
        logger.info(f"Task execution time: {end_time - start_time} seconds")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

@transaction.atomic
def delete_past_events():
    today = datetime.now()
    # Delete events with dates earlier than today
    try:
        count, _ = BoxingEvent.objects.filter(date__lt=today).delete()
        return count > 0  # Return True if any events were deleted
    except Exception as e:
        logger.error(f"Error deleting past events: {e}")
        return False
    
@transaction.atomic
def create_new_events():
    try:
        today = datetime.now()
        next_week = today + timedelta(days=(7 - today.weekday() + 1))
        event1_date = next_week + timedelta(days=5)  # Saturday of next week
        event2_date = next_week + timedelta(days=6)  # Sunday of next week

        # Create new events
        event1 = BoxingEvent.objects.create(date=event1_date, location="Location 1")
        event2 = BoxingEvent.objects.create(date=event2_date, location="Location 2")
        return event1 is not None, event2 is not None  # Return True if both events were created
    except Exception as e:
        logger.error(f"Error creating new events: {e}")
        return False, False