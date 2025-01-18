import json

from django.db.models import Avg
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.tba import get_single_match, get_teams_list
from teams import models

from helpers import login_required

from django.shortcuts import render, redirect
from strategy.models import PickList_Data


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
    no_pick_teams = []
    first_pick_teams = []
    second_pick_teams = []
    third_pick_teams = []
    dn_pick_teams = []
    if comp_code == None or comp_code == 'Testing':
        return render(request, "strategy/picklist.html", {'teams': teams})
    else:
        if len(PickList_Data.objects.filter(event=comp_code)) == 0:
            teams_data = get_teams_list(comp_code)
            for team in teams_data:
                teams.append(team["team_number"])
            teams.sort()
            return render(request, "strategy/picklist.html", {'teams': teams,
                                                          'comp_code' : comp_code,
                                                          'no_pick_teams' : no_pick_teams,
                                                          'first_pick_teams' : first_pick_teams,
                                                          'second_pick_teams' : second_pick_teams,
                                                          'third_pick_teams' : third_pick_teams,
                                                          'dn_pick_teams' : dn_pick_teams,})
        
        picklist_data = PickList_Data.objects.filter(event=comp_code).values()[0]
        no_pick_teams = picklist_data['no_pick']
        first_pick_teams = picklist_data['first_pick']
        second_pick_teams = picklist_data['second_pick']
        third_pick_teams = picklist_data['third_pick']
        dn_pick_teams = picklist_data['dn_pick']
        return render(request, "strategy/picklist.html", {'teams': teams,
                                                          'comp_code' : comp_code,
                                                          'no_pick_teams' : no_pick_teams,
                                                          'first_pick_teams' : first_pick_teams,
                                                          'second_pick_teams' : second_pick_teams,
                                                          'third_pick_teams' : third_pick_teams,
                                                          'dn_pick_teams' : dn_pick_teams})
        
@csrf_exempt
def picklist_submit(request):
    comp_code = request.GET.get('comp')
    picklist_data = json.loads(request.body.decode('utf-8'))
        
    PickList_Data.objects.get_or_create(event=comp_code)

    PickList_Data.objects.filter(event=comp_code).update(
        event=comp_code,
        no_pick = picklist_data[0],
        first_pick = picklist_data[1],
        second_pick = picklist_data[2],
        third_pick = picklist_data[3],
        dn_pick = picklist_data[4]
    )
        
    return HttpResponse(status=200)

# @login_required
@csrf_exempt
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
    team_match_data = models.Team_Match_Data.objects.filter(
        team_number=team_number,
        event=comp_code,
        match_number__lt=100
    )
    
    team_match_averages = team_match_data.aggregate(
        # Auto Period
        Avg('auto_leave', default=0),
        Avg('auto_L1', default=0),
        Avg('auto_L2', default=0),
        Avg('auto_L3', default=0),
        Avg('auto_L4', default=0),
        Avg('auto_net', default=0),
        Avg('auto_processor', default=0),
        Avg('auto_removed', default=0),
        # Teleop Period
        Avg('teleL1', default=0),
        Avg('teleL2', default=0),
        Avg('teleL3', default=0),
        Avg('teleL4', default=0),
        Avg('telenet', default=0),
        Avg('teleProcessor', default=0),
        Avg('teleRemoved', default=0),
        # End Game
        Avg('climb', default=0),
        # Rankings
        Avg('defense_ranking', default=0)
    )

    auto_total = (
        team_match_averages['auto_L1__avg'] +
        team_match_averages['auto_L2__avg'] +
        team_match_averages['auto_L3__avg'] +
        team_match_averages['auto_L4__avg'] +
        team_match_averages['auto_net__avg'] +
        team_match_averages['auto_processor__avg']
    )

    teleop_total = (
        team_match_averages['teleL1__avg'] +
        team_match_averages['teleL2__avg'] +
        team_match_averages['teleL3__avg'] +
        team_match_averages['teleL4__avg'] +
        team_match_averages['telenet__avg'] +
        team_match_averages['teleProcessor__avg']
    )

    return {
    'autoleave': round(team_match_averages['auto_leave__avg'], 3),
    'auto': round(auto_total, 3),
    'L1': round(team_match_averages['auto_L1__avg'] + team_match_averages['teleL1__avg'], 3),
    'L2': round(team_match_averages['auto_L2__avg'] + team_match_averages['teleL2__avg'], 3),
    'L3': round(team_match_averages['auto_L3__avg'] + team_match_averages['teleL3__avg'], 3),
    'L4': round(team_match_averages['auto_L4__avg'] + team_match_averages['teleL4__avg'], 3),
    'net': round(team_match_averages['auto_net__avg'] + team_match_averages['telenet__avg'], 3),
    'processor': round(team_match_averages['auto_processor__avg'] + team_match_averages['teleProcessor__avg'], 3),
    'removed': round(team_match_averages['auto_removed__avg'] + team_match_averages['teleRemoved__avg'], 3),
    'climb': round(team_match_averages['climb__avg'], 3),
    'total': round(auto_total + teleop_total + team_match_averages['climb__avg'], 3),
    'defense': round(team_match_averages['defense_ranking__avg'], 3)
}

