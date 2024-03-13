"""scouting_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from scouting_backend import settings
from teams import views as team_views
from scanner import views as scanner_views
from strategy import views as strategy_views
from authenticate import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', team_views.home, name='home'),
    path('scanner/', scanner_views.scanner, name='scanner'),
    path('teams/', team_views.display_teams, name='teams'),
    path('teams/<int:team_number>', team_views.team_page, name='team_page'),
    path("teams/human-scout/ <int:team_number>", team_views.human_player_submit, name="human-scout"),
    path('get_events/', team_views.get_events),
    path('pit_scouting/<int:team_number>', team_views.pit_scouting, name='pit_scouting'),
    path('strategy/rankings', strategy_views.rankings, name='rankings'),
    path('strategy/dashboard', strategy_views.dashboard, name='dashboard'),
    path('strategy/picklist', strategy_views.picklist, name='picklist'),
    path("auth/", include("authenticate.urls")),
]
