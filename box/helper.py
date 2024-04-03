from .models import UserProfile, EventRegistration

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