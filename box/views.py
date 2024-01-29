from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserForm, UserProfileForm, EventForm
from .models import UserProfile, BoxingEvent, EventRegistration, EventFight, Fight
import datetime

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
    today = datetime.date.today()
    events = BoxingEvent.objects.filter(date__gte=today)
    return render(request, 'box/events_list.html', {'events': events})

def event_detail(request, event_id):
    event = get_object_or_404(BoxingEvent, id=event_id)
    registrations = EventRegistration.objects.filter(event=event)
    return render(request, 'box/event_detail.html', {'event': event})

@login_required
def event_registration_confirmation(request, event_id):
    event = get_object_or_404(BoxingEvent, id=event_id)
    register_event(request, event_id)
    return render(request, 'box/event_registration_confirmation.html', {'event': event})

def register_event(request, event_id):
    event = get_object_or_404(BoxingEvent, id=event_id)
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    print("hhohohohoh")

    max_fights = 6
    current_fights_count = EventFight.objects.filter(event=event).count()
    if current_fights_count >= max_fights:
        messages.error(request, "The maximum number of fights has been reached for this event.") ### change register button into event full ###
        return redirect('box:events_list')

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        existing_registration = EventRegistration.objects.filter(user=request.user, event=event)
        if existing_registration.exists():
            messages.warning(request, "You are already registered for this event.")
            return redirect('box:events_list')
            
        registration = EventRegistration(user=request.user, event=event)
        registration.save()

        matching_user = find_matching_user(request.user, event)
        if matching_user:
            create_fight(request.user, matching_user, event)
            return redirect('box:event_detail', event_id=event.id) ### Need to send email to user to notify an opponent is found. Then on the event it must be on the event details where his name and opponent is alongside with othe oppponents ###
        return redirect('box:events_list')
    else:
        profile_form = UserProfileForm(instance=user_profile)
   
    return redirect('box:event_detail', event_id=event.id)

def create_fight(user1, user2, event):
    max_fights = 6
    current_fights_count = EventFight.objects.filter(event=event).count()
    if current_fights_count >= max_fights:
        return  # Don't create a new fight if the limit has been reached
    fight = Fight.objects.create(red_boxer=user1, blue_boxer=user2)
    order = current_fights_count + 1  # Increment the order for the new fight
    event_fight = EventFight.objects.create(event=event, fight=fight, order=order)
    return event_fight

def find_matching_user(current_user, event):
    current_user_profile = current_user.userprofile

    if calculate_points(current_user_profile) == 0: ### for new boxers ###
        zero_points_user = event.registered_users.filter(userprofile__wins=0, userprofile__draws=0, userprofile__losses=0, userprofile__weight__range=(current_user_profile.weight - 1, current_user_profile.weight + 1)).exclude(id=current_user.id)
        if zero_points_user.exists():
            return zero_points_user.first()

    for registered_user in event.registered_users.all(): ### for boxers who has fought before ###
        if registered_user != current_user:
            registered_user_profile = registered_user.userprofile
            current_user_points = calculate_points(current_user_profile)
            registered_user_points = calculate_points(registered_user_profile)

            points_difference = abs(current_user_points - registered_user_points)
            weight_difference = abs(current_user_profile.weight - registered_user_profile.weight)
            if (points_difference >= 0 and points_difference <= 5 and weight_difference <= 1 and weight_difference >= -1):
                return registered_user
    return None

def events_management(request):
    events = BoxingEvent.objects.all()
    return render(request, 'box/events_management.html', {'events': events})

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, 'Event created successfully.')
            return redirect('box:manage_events')
    else:
        form = EventForm()
    
    return render(request, 'box/create_event.html', {'form': form})

def calculate_points(user_profile):
    return (user_profile.wins * 3) + (user_profile.draws * 2) + user_profile.losses

@login_required
def edit_event(request,event_id):
    event = get_object_or_404(BoxingEvent,id=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('box:manage_events')
    else:
        form = EventForm(instance=event)
        
    return render(request, 'box/edit_event.html', {'form': form, 'event': event})

def delete_event(request, event_id):
    event = get_object_or_404(BoxingEvent,id=event_id)
    event.delete()
    return redirect('box:manage_events')
