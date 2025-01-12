import os

import cloudinary
import cloudinary.api
import cloudinary.uploader
from django.http import JsonResponse
from django.shortcuts import render, redirect

from api.tba import get_teams_list, get_team_events
from helpers import login_required
from teams.models import Teams, Team_Match_Data, Human_Player_Match
from .forms import NewPitScoutingData, NewHumanScoutingData

cloudinary.config(
    cloud_name=os.environ.get("CLOUD_NAME"),
    api_key=os.environ.get("CLOUD_API_KEY"),
    api_secret=os.environ.get("CLOUD_API_SECRET"),
    secure=True)


def home(request):
    return render(request, 'home.html')


def get_events(request):
    return JsonResponse(get_team_events())


# @login_required
def display_teams(request):
    comp_code = request.GET.get('comp', "testing")
    pit_scouted = []
    for team in Teams.objects.filter(event=comp_code, pit_scout_status=True):
        pit_scouted.append(team.team_number)

    all_teams = []
    if comp_code == "testing":
        for team in Teams.objects.filter(event=comp_code):
            all_teams.append(team.team_number)
    else:
        for team in get_teams_list(comp_code):
            all_teams.append(team["team_number"])
    all_teams.sort()

    return render(request, 'teams/view_teams.html', {'all_teams': all_teams, "pit_scouted": pit_scouted})


# @login_required
def team_page(request, team_number):
    comp_code = request.GET.get('comp')
    if comp_code is not None:
        team, created = Teams.objects.get_or_create(team_number=team_number, event=comp_code)
        all_team_match_data = Team_Match_Data.objects.filter(team_number=team_number, event=comp_code).order_by("-quantifier", "-match_number")
        human_player_matches = Human_Player_Match.objects.filter(team_number=team_number, event=comp_code)

        return render(request, 'teams/team_page.html', {'team': team, 'all_team_match_data': all_team_match_data, "team_number": team_number, "human_player_matches": human_player_matches})

    return render(request, 'teams/team_page.html', {"team_number": team_number})


# @login_required
def pit_scouting(request, team_number):
    comp_code = request.GET.get('comp')
    if request.method == 'POST' and comp_code is not None:
        form = NewPitScoutingData(request.POST, request.FILES)
        if form.is_valid():
            image_response = cloudinary.uploader.upload(request.FILES['robot_picture'])
            img_url = image_response["secure_url"]
            image_url_list = img_url.split("upload/")
            image_url_list.insert(1, "upload/w_0.4,c_scale/")
            img_url = "".join(image_url_list)

            Teams.objects.get_or_create(team_number=team_number, event=comp_code)

            intake_design_char = form.cleaned_data.get('intake_design')
            intake_locations_char = ", ".join(form.cleaned_data.get('intake_locations'))
            scoring_locations_char = ", ".join(form.cleaned_data.get('scoring_locations'))
            shooting_positions_char = ", ".join(form.cleaned_data.get('shooting_positions'))
            auto_positions_char = ", ".join(form.cleaned_data.get('auto_positions'))
            Teams.objects.filter(team_number=team_number, event=comp_code).update(
                drivetrain=form.cleaned_data.get('drivetrain'),
                weight=form.cleaned_data.get('weight'),
                length=form.cleaned_data.get('length'),
                width=form.cleaned_data.get('width'),
                intake_design=intake_design_char,
                intake_locations=intake_locations_char,
                scoring_locations=scoring_locations_char,
                shooting_positions=shooting_positions_char,
                auto_positions=auto_positions_char,
                auto_leave=form.cleaned_data.get('auto_leave'),
                auto_total_notes=form.cleaned_data.get('auto_total_notes'),
                auto_amp_notes=form.cleaned_data.get('auto_amp_notes'),
                robot_picture=img_url,
                additional_info=form.cleaned_data.get('additional_info'),
                pit_scout_status=True)

            return redirect("team_page", team_number=team_number)
    else:
        form = NewPitScoutingData()
    return render(request, "teams/pit_scouting.html", {'form': form, 'team_number': team_number})


# @login_required
def human_player_submit(request, team_number):
    comp_code = request.GET.get('comp')
    if request.method == 'POST':
        form = NewHumanScoutingData(request.POST)
        print(form)
        if form.is_valid():
            Human_Player_Match.objects.create(team_number=team_number,
                                              event=comp_code,
                                              match_number=form.cleaned_data.get('match_number'),
                                              human_player_comment=form.cleaned_data.get('human_player_comment'))

            return redirect("team_page", team_number=team_number)
    else:
        form = NewHumanScoutingData()
    return render(request, "teams/human_player_scout.html", {'form': form, 'team_number': team_number})
