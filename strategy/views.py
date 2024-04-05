import json

from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render

from api.tba import get_single_match, get_teams_list
from teams import models

from helpers import login_required


# @login_required
def rankings(request):
    comp_code = request.GET.get('comp')
    teams = models.Teams.objects.filter(event=comp_code).order_by("team_number")
    team_averages = {}
    for team in teams:
        team_averages[team.team_number] = fetch_team_match_averages(team.team_number, comp_code)

    return render(request, "strategy/rankings.html", {'team_averages': team_averages})

# @login_required
def picklist(request):
    comp_code = request.GET.get('comp')
    teams = []
    if comp_code == None or comp_code == 'Testing':
        return render(request, "strategy/picklist.html", {'teams': teams})
    else:
        teams_data = get_teams_list(comp_code)
        for team in teams_data:

            teams.append(team["team_number"])
            teams.sort()
        return render(request, "strategy/picklist.html", {'teams': teams, 'comp_code' : comp_code})
    
def picklist_submit(request):
    comp_code = request.GET.get('comp')
    teams = []
    if comp_code == None or comp_code == 'Testing':
        return render(request, "strategy/picklist.html", {'teams': teams})
    else:
        teams_data = get_teams_list(comp_code)
        for team in teams_data:

            teams.append(team["team_number"])
            teams.sort()
        return render(request, "strategy/picklist.html", {'teams': teams, 'comp_code' : comp_code})

# @login_required
def dashboard(request):
    comp_code = request.GET.get('comp')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        match_number = json.load(request)
        match = get_single_match(comp_code, "qm" + str(match_number))
        red_json = {}
        red_teams = []
        blue_json = {}
        blue_teams = []
        for red_team in match['red']:
            red_json[red_team] = fetch_team_match_averages(red_team, comp_code)
            red_teams.append(red_team)
        for blue_team in match['blue']:
            blue_json[blue_team] = fetch_team_match_averages(blue_team, comp_code)
            blue_teams.append(blue_team)

        response = {'red': red_json, 'blue': blue_json, 'red_teams': red_teams, 'blue_teams': blue_teams}
        return JsonResponse(response)

    return render(request, "strategy/dashboard.html")


def fetch_team_match_averages(team_number, comp_code):
    team_match_data = models.Team_Match_Data.objects.filter(team_number=team_number, event=comp_code, match_number__lt=100)
    team_match_averages = team_match_data.aggregate(Avg('auto_amp', default=0),
                                                    Avg('auto_speaker_make', default=0),
                                                    Avg('teleop_amp', default=0),
                                                    Avg('teleop_speaker_make', default=0),
                                                    Avg('trap', default=0),
                                                    Avg('climb', default=0),
                                                    Avg('defense_ranking', default=0))

    return {'auto': round(team_match_averages['auto_amp__avg'] + team_match_averages['auto_speaker_make__avg'], 3),
            'teleop-total': round(team_match_averages['teleop_amp__avg'] + team_match_averages['teleop_speaker_make__avg'], 3),
            'teleop-amp': round(team_match_averages['teleop_amp__avg'], 3),
            'teleop-speaker': round(team_match_averages['teleop_speaker_make__avg'], 3),
            'trap': round(team_match_averages['trap__avg'], 3),
            'climb': round(team_match_averages['climb__avg'], 3),
            'defense': round(team_match_averages['defense_ranking__avg'], 3)}