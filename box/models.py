from django.db import models
from django.contrib.auth.admin import User
from django.dispatch import receiver
from django.db.models.signals import post_save

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

#@receiver(post_save, sender=User)
#def save_user_profile(sender, instance, **kwargs):
 #   try:
  #      instance.profile.save()
   # except UserProfile.DoesNotExist:
    #    UserProfile.objects.create(user=instance)

class BoxingEvent(models.Model):
    date = models.DateField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.date} - {self.location}"