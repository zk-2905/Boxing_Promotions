from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path("accounts/profile/", views.update_profile, name='profile')
]