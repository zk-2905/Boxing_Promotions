from django import forms
from django.contrib.auth.models import User
from .models import UserProfile,BoxingEvent

class UserForm(forms.ModelForm):
    email = forms.EmailField
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("age", "nickname", "weight", "profile_picture", "boxer_type", "gender")
        widgets = {
            'weight': forms.NumberInput(attrs={'step': 'any'}),  # Allow any decimal value
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['weight'].required = True 
        self.fields['age'].required = True 
        self.fields['gender'].required = True 

class EventForm(forms.ModelForm):
    class Meta:
        model = BoxingEvent
        fields = ("title", "date", "location")