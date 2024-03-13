from django.urls import path
from . import views

urlpatterns = [
    path("", views.authorize),
    path("oauth2callback/", views.oauth2callback, name="oauth2callback")
]