from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from .forms import UserForm, UserProfileForm
from .models import UserProfile, BoxingEvent

def HomePage(request):
    return render(request,'box/home.html')

@login_required
@transaction.atomic
def update_profile(request):
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('box:profile')
    else: 
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)

    return render(request, 'box/profile.html', {'user_form': user_form, 'profile_form': profile_form})

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    if not user.last_login:
        messages.success(request, "Welcome! You have successfully logged in.")
        redirect_url = reverse('user:events_list')
        return redirect(redirect_url)

@login_required
def events_list(request):
    events = BoxingEvent.objects.all()
    return render(request, 'box/events_list.html', {'events': events})

def register_event(request, event_id):
    event = get_object_or_404(BoxingEvent, id=event_id)
    return render(request, 'box/register_event.html', {'event': event})