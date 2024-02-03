from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from box.models import UserProfile, BoxingEvent
from box.views import register_event
from datetime import timezone

@receiver(post_save, sender=User)
def assign_organiser_role(sender, instance, created, **kwargs):
    if created and 'organiser' in instance.email:
        organiser_group = Group.objects.get(name='organiser')
        instance.groups.add(organiser_group)

@receiver(post_save, sender=BoxingEvent)
def schedule_event_registration(sender, instance, **kwargs):
    schedule_time = instance.date - timezone.timedelta(days=1)
    register_event(instance.id, schedule=schedule_time)