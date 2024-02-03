from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserForm, UserProfileForm, EventForm
from .models import UserProfile, BoxingEvent, EventRegistration, EventFight, Fight
import datetime
from datetime import timezone


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
    registration = EventRegistration(user=request.user, event=event)
    registration.save()
    if EventRegistration.objects.filter(user=request.user, event=event, matched=True).exists():
        return redirect('box:already_registered')
    return render(request, 'box/event_registration_confirmation.html', {'event': event})

def register_event(request, event_id, registration):
    event = get_object_or_404(BoxingEvent, id=event_id)
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    max_fights = 6
    current_fights_count = EventFight.objects.filter(event=event).count()
    if current_fights_count >= max_fights:
        messages.error(request, "The maximum number of fights has been reached for this event.") ### change register button into event full ###
        return redirect('box:events_list')

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        matching_user = find_matching_user(request.user, event)
        if matching_user:
            create_fight(request.user, matching_user, event)
            registration.matched = True  ### shows that the user and matched user are matched and can't be matched by another ###
            registration.save()
            matching_registration = EventRegistration.objects.get(user= matching_user, event=event)
            matching_registration.matched = True
            matching_registration.save()
            return redirect('box:event_detail', event_id=event.id) ### Need to send email to user to notify an opponent is found. Then on the event it must be on the event details where his name and opponent is alongside with othe oppponents ###
        return redirect('box:events_list')
    else:
        profile_form = UserProfileForm(instance=user_profile)
   
    return redirect('box:event_detail', event_id=event.id)
def already_registered(request):
    return render(request, 'box/already_registered.html')

def find_matching_user(current_user, event):
    weight_classes = {}
    for user in user.registered_users.all():
        weight = int(user.userprofile.weight)
        weight_class = (weight // 1)
        if weight_class not in weight_classes:
            weight_classes[weight_class].append(user)

    for users in weight_classes.values():
        users.sort(key = lambda user: calculate_points(user.userprofile), reverse= True)
    
    matches = []
    matched_users = set()
    for weight_class, users in sorted(weight_classes.items(), reverse= True):
        for i in range(len(users)):
            user1 = users[i]
            if user1 in matched_users:
                continue
            for j in range(i+1, len(users)):
                user2 = users[j]
                if user2 in matched_users:
                    continue
                if user1 in matched_users:
                    continue
                if calculate_points(user1.userprofile) == 0:
                    if calculate_points(user2.userprofile) == 0:
                        matches.append((user1, user2))
                        matched_users.add(user1)
                        matched_users.add(user2)
                points_difference = abs(calculate_points(user1.userprofile) - calculate_points(user2.userprofile))
                if points_difference <= 5:
                    matches.append((user1, user2))
                    matched_users.add(user1)
                    matched_users.add(user2)
    return matches

def calculate_points(user_profile):
    return (user_profile.wins * 3) + (user_profile.draws * 2) + user_profile.losses

def create_fight(user1, user2, event):
    max_fights = 6
    current_fights_count = EventFight.objects.filter(event=event).count()
    if current_fights_count >= max_fights:
        return  # Don't create a new fight if the limit has been reached
    fight = Fight.objects.create(red_boxer=user1, blue_boxer=user2)
    order = current_fights_count + 1  # Increment the order for the new fight
    event_fight = EventFight.objects.create(event=event, fight=fight, order=order)
    return event_fight

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


@login_required
def edit_event(request,event_id):
    event = get_object_or_404(BoxingEvent,id=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            if event.date == datetime.date.today():
                update_match_results(request, event)
                update_user_records_from_results(event, get_event_results(event))
            return redirect('box:manage_events')
    else:
        form = EventForm(instance=event)
        
    return render(request, 'box/edit_event.html', {'form': form, 'event': event})


def update_match_results(request, event):
    for event_fight in event.eventfight_set.all():
        red_result = request.POST.get(f"red_result_{event_fight.id}")
        blue_result = request.POST.get(f"blue_result_{event_fight.id}")

        event_fight.red_boxer_result = red_result
        event_fight.blue_boxer_result = blue_result
        event_fight.save()




def delete_event(request, event_id):
    event = get_object_or_404(BoxingEvent,id=event_id)
    event.delete()
    return redirect('box:manage_events')

@login_required
def my_events(request):
    user_registrations = EventRegistration.objects.filter(user=request.user)
    searching_for_opponent =[]
    matched_opponent = []
    event_complete = []
    for registration in user_registrations:
        event = registration.event
        if not event.is_event_completed():
            if not registration.matched:
                searching_for_opponent.append(event)
            else:
                matched_opponent.append(event)
        else:
            event_complete.append({
                'event':event,
                'results': get_event_results(event),
            })
    
    context = {
        'searching_for_opponent': searching_for_opponent,
        'matched_opponent': matched_opponent,
        'event_completed': event_complete,
    }
    return render(request, 'box/my_events.html', context)


def get_event_results(event):
    results = []
    for event_fight in event.eventfight_set.all():
        results.append({
            'red_boxer':  event_fight.fight.red_boxer,
            'blue_boxer': event_fight.fight.blue_boxer,
            'red_result': event_fight.red_boxer_result,
            'blue_result': event_fight.blue_boxer_result,
        })
    return results

@transaction.atomic
def update_user_records_from_results(event, results):
    for event_fight,result in zip(event.eventfight_set.all(), results):
        red_boxer = event_fight.fight.red_boxer
        blue_boxer = event_fight.fight.blue_boxer

        if result['red_result'] == 'win':
            red_boxer.userprofile.wins += 1
        elif result['red_result'] == 'loss':
            red_boxer.userprofile.losses += 1
        elif result['red_boxer'] == 'draw':
            red_boxer.userprofile.draws += 1

        if result['blue_result'] == 'win':
            blue_boxer.userprofile.wins += 1
        elif result['blue_result'] == 'loss':
            blue_boxer.userprofile.losses += 1
        elif result['blue_boxer'] == 'draw':
            blue_boxer.userprofile.draws += 1

        red_boxer.userprofile.save()
        blue_boxer.userprofile.save()