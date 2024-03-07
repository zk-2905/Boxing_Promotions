from django import forms
from django.contrib.auth.models import User
from .models import UserProfile,BoxingEvent

class UserForm(forms.ModelForm):
    email = forms.EmailField
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("age", "nickname", "weight", "profile_picture", "boxer_type")

class EventForm(forms.ModelForm):
    class Meta:
        model = BoxingEvent
        fields = ("title", "date", "location")