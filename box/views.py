from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from allauth.account.views import LoginView
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
    
    return render(request, 'box/profile.html', {'user_form': user_form, 'profile_form': profile_form, 'user': request.user, 'user_profile': user_profile})


@login_required
def events_list(request):
    events = BoxingEvent.objects.all()
    return render(request, 'box/events_list.html', {'events': events})

def register_event(request, event_id):
    event = get_object_or_404(BoxingEvent, id=event_id)
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if profile_form.is_valid():
            profile_form.save()
            matching_user = find_matching_user(request.user, event)
            if matching_user:
                return True ### Need to send email to user to notify an opponent is found. Then on the event it must be on the event details where his name and opponent is alongside with othe oppponents ###
            return redirect('box:events_list')
    else:
        profile_form = UserProfileForm(instance=user_profile)
   
    return render(request, 'box/register_event.html', {'event': event, 'profile_form': profile_form})


def find_matching_user(current_user, event):
    current_user_profile = current_user.profile

    if calculate_points(current_user_profile) == 0: ### for new boxers ###
        zero_points_user = event.registered_users.filter(profile__wins=0, profile__draws=0, profile__losses=0, profile__weight__range=(current_user_profile.weight - 1, current_user_profile.weight + 1)).exclude(id=current_user.id)
        if zero_points_user.exists():
            return zero_points_user.first()

    for registered_user in event.registered_users.all(): ### for boxers who has fought before ###
        if registered_user != current_user:
            registered_user_profile = registered_user.profile
            current_user_points = calculate_points(current_user_profile)
            registered_user_points = calculate_points(registered_user_profile)

            points_difference = abs(current_user_points - registered_user_points)
            weight_difference = abs(current_user_profile.weight - registered_user_profile.weight)
            if (points_difference >= 0 and points_difference <= 5 and weight_difference <= 1 and weight_difference >= -1):
                return registered_user
    return None

def calculate_points(user_profile):
    return (user_profile.wins * 3) + (user_profile.draws * 2) + user_profile.losses