from django.urls import path
from . import views
from .views import HomePage,update_profile,CustomLoginView

app_name = "box"

urlpatterns = [
    path('', HomePage, name='home'),
    path("accounts/profile/", update_profile, name='profile'),
    path("events/", views.events_list, name='events_list'),
    path("events/<int:event_id>/register/", views.register_event, name='register_event'),
]