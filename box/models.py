from django.db import models
from django.contrib.auth.admin import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import Group, Permission

def create_organiser_group():
    organiser_group, created = Group.objects.get_or_create(name='organiser')
    if created:
        organiser_group.permissions.set([
            Permission.objects.get(codename='add_event'),
            Permission.objects.get(codename='change_event'),
            Permission.objects.get(codename='delete_event'),
        ])
create_organiser_group()



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    nickname = models.CharField(max_length=100, null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    profile_picture = models.ImageField(null=True, blank=True, upload_to="images/")

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)



class BoxingEvent(models.Model):
    title = models.CharField(max_length=225, null=True)
    date = models.DateField()
    location = models.CharField(max_length=255)
    registered_users = models.ManyToManyField(User, through='EventRegistration')
    fights = models.ManyToManyField('Fight', through='EventFight')

    def __str__(self):
        return f"{self.title} - {self.date} - {self.location}"

class Fight(models.Model):
    red_boxer = models.ForeignKey(User, related_name='red_boxer', on_delete=models.CASCADE)
    blue_boxer = models.ForeignKey(User, related_name='blue_boxer', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.red_boxer.username} vs {self.blue_boxer.username}"

class EventFight(models.Model):
    event = models.ForeignKey(BoxingEvent, on_delete=models.CASCADE)
    fight = models.ForeignKey(Fight, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('event', 'order')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.event} - {self.fight} - Order: {self.order}"

class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(BoxingEvent, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} registered for {self.event}"