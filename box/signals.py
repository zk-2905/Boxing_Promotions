from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from box.models import UserProfile, BoxingEvent
from box.views import register_event
from datetime import timezone, timedelta
import datetime

@receiver(post_save, sender=User)
def assign_organiser_role(sender, instance, created, **kwargs):
    if created and 'organiser' in instance.email:
        organiser_group = Group.objects.get(name='organiser')
        instance.groups.add(organiser_group)

@receiver(post_save, sender=BoxingEvent)
def schedule_event_registration(sender, instance, **kwargs):
    previous_day = instance.date - timedelta(1)
    today = datetime.date.today()
    if previous_day == today:
        register_event(instance.id)