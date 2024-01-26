from django.urls import path
from .views import HomePage, update_profile, event_detail, events_list,events_management,edit_event,create_event

app_name = "box"

urlpatterns = [
    path('', HomePage, name='home'),
    path("accounts/profile/", update_profile, name='profile'),
    path("events/", events_list, name='events_list'),
    path("events/<int:event_id>/detail/", event_detail, name='event_detail'),
    path('manage-events/', events_management, name='manage_events'),
    path('edit-event/<int:event_id>/', edit_event, name='edit_event'),
    path('create-event/', create_event, name='create_event'),
]