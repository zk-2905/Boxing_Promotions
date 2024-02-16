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

    one_day_before_event = datetime.date.today() >= (event.date - datetime.timedelta(days=1))
    context = {
        'event': event,
        'registrations': registrations,
        'one_day_before_event': one_day_before_event,
    }
    return render(request, 'box/event_detail.html', context)

@login_required
def event_registration_confirmation(request, event_id):
    event = get_object_or_404(BoxingEvent, id=event_id)
    registration = EventRegistration(user=request.user, event=event)
    if EventRegistration.objects.filter(user=request.user, event=event, registered=True).exists():
        return redirect('box:already_registered')
    registration.registered = True
    registration.save()
    return render(request, 'box/event_registration_confirmation.html', {'event': event})

def register_event(request, event_id):
    event = get_object_or_404(BoxingEvent, id=event_id)
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    registration = EventRegistration(user=request.user, event=event)
    
    max_fights = 6
    current_fights_count = EventFight.objects.filter(event=event).count()
    if current_fights_count >= max_fights:
        messages.error(request, "The maximum number of fights has been reached for this event.") ### change register button into event full ###
        return redirect('box:events_list')

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        matches = find_matches(request.user, event)
        if matches:
            create_fight(matches, event)
            update_not_matched_counters(event)
            return redirect('box:event_detail', event_id=event.id) ### Need to send email to user to notify an opponent is found. Then on the event it must be on the event details where his name and opponent is alongside with othe oppponents ###
        return redirect('box:events_list')
    else:
        profile_form = UserProfileForm(instance=user_profile)
   
    return redirect('box:event_detail', event_id=event.id)
def already_registered(request):
    return render(request, 'box/already_registered.html')

def find_matches(current_user, event):
    weight_classes = {}
    for user_registration in EventRegistration.objects.filter(event=event, matched=False):
        user = user_registration.user
        weight = int(user.userprofile.weight)
        weight_class = (weight // 1)
        if weight_class not in weight_classes:
            weight_classes[weight_class] = []
        weight_classes[weight_class].append(user)

    for users in weight_classes.values():
        users.sort(key = lambda user: (user.userprofile.not_matched_counter, calculate_points(user.userprofile)), reverse= True)
    matches = []
    matched_users = set()
    max_fights_per_class = 6
    for weight_class, users in sorted(weight_classes.items(), reverse= True):
        fights_created = 0
        for i in range(len(users)):
            user1 = users[i]
            if user1 in matched_users or fights_created == max_fights_per_class:
                continue
            for j in range(i+1, len(users)):
                user2 = users[j]
                if user2 in matched_users or user1 in matched_users or user1 == user2:
                    continue
                if calculate_points(user1.userprofile) == 0:
                    if calculate_points(user2.userprofile) == 0:
                        matches.append((user1, user2))
                        matched_users.add(user1)
                        matched_users.add(user2)
                        reset_user_not_matched_counter(user1, event)
                        reset_user_not_matched_counter(user2, event)
                        fights_created += 1
                points_difference = abs(calculate_points(user1.userprofile) - calculate_points(user2.userprofile))
                if user1 not in matched_users and user2 not in matched_users and points_difference <= 5 and points_difference >= -5:
                    matches.append((user1, user2))
                    matched_users.add(user1)
                    matched_users.add(user2)
                    reset_user_not_matched_counter(user1, event)
                    reset_user_not_matched_counter(user2, event)
                    fights_created += 1

    return matches


def reset_user_not_matched_counter(user, event):
    registration = UserProfile.objects.get(user=user)
    registration.not_matched_counter = 0
    registration.save()

def update_not_matched_counters(event):
    not_matched_users = EventRegistration.objects.filter(event=event, matched=False)
    for registration in not_matched_users:
        user_profile = registration.user.userprofile
        user_profile.not_matched_counter += 1
        user_profile.save()

def calculate_points(user_profile):
    return (user_profile.wins * 3) + (user_profile.draws * 2) + user_profile.losses

def create_fight(matches, event):
    current_fights_count = EventFight.objects.filter(event=event).count()
    
    for i, (user1, user2) in enumerate(matches):
        order = current_fights_count + i + 1  # Increment the order for the new fight
        fight = Fight.objects.create(red_boxer=user1, blue_boxer=user2)
        event_fight = EventFight.objects.create(event=event, fight=fight, order=order)
    
        registration_user1 = EventRegistration.objects.get(user=user1, event=event)
        registration_user1.matched = True
        registration_user1.save()

        registration_user2 = EventRegistration.objects.get(user=user2, event=event)
        registration_user2.matched = True
        registration_user2.save()

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
    today = datetime.date.today()
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
        if event.date == today:
            update_match_results(request, event)
            update_user_records_from_results(event, get_event_results(request,event))
        return redirect('box:manage_events')
    else:
        form = EventForm(instance=event)

    match_results_allowed = (event.date == today)
    context = {
        'form': form,
        'event': event,
        'match_results_allowed': match_results_allowed,
    }
        
    return render(request, 'box/edit_event.html', context)


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
        print(registration)
        event = registration.event
        print(event)
        if not event.is_event_completed():
            if not registration.matched:
                searching_for_opponent.append(event)
            else:
                matched_opponent.append(event)
        else:
            event_complete.append({
                'event':event,
                'results': get_event_results(request, event),
            })
    
    context = {
        'searching_for_opponent': searching_for_opponent,
        'matched_opponent': matched_opponent,
        'event_completed': event_complete,
    }
    return render(request, 'box/my_events.html', context)


def get_event_results(request, event):
    results = []
    current_user = request.user
    for event_fight in event.eventfight_set.filter(fight__red_boxer=current_user) | event.eventfight_set.filter(fight__blue_boxer=current_user):
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