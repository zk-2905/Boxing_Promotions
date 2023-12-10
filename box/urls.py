from django.urls import path
from . import views
from .views import HomePage,update_profile

app_name = "box"

urlpatterns = [
    path('', HomePage, name='home'),
    path("accounts/profile/", update_profile, name='profile'),
]