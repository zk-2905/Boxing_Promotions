from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group

@receiver(post_save, sender=User)
def assign_organiser_role(sender, instance, created, **kwargs):
    if created and 'organiser' in instance.email:
        organiser_group = Group.objects.get(name='organiser')
        instance.groups.add(organiser_group)
