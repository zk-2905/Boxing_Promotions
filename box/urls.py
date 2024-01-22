from django.urls import path
from .views import HomePage, update_profile, event_detail, events_list

app_name = "box"

urlpatterns = [
    path('', HomePage, name='home'),
    path("accounts/profile/", update_profile, name='profile'),
    path("events/", events_list, name='events_list'),
    path("events/<int:event_id>/detail/", event_detail, name='event_detail'),
]