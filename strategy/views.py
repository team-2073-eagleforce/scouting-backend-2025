import json
import os
from pathlib import Path
from time import time

from django.db.models import Avg, Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.tba import get_single_match, get_teams_list
from teams import models
from helpers import login_required
from django.shortcuts import render, redirect
from strategy.models import PickList_Data
from teams.models import Team_Match_Data
from utils import config_loader

def get_json_path(comp_code):
    # Get the project root directory
    BASE_DIR = Path(__file__).resolve().parent.parent
    # Create a picklists directory if it doesn't exist
    picklist_dir = BASE_DIR / 'picklists'
    picklist_dir.mkdir(exist_ok=True)
    return picklist_dir / f'picklist_{comp_code}.json'

def read_json_picklist(comp_code):
    json_path = get_json_path(comp_code)
    if json_path.exists():
        with open(json_path, 'r') as f:
            data = json.load(f)
            # Handle both old and new format
            if isinstance(data, list):
                # Convert old format to new format
                return {
                    'timestamp': int(time() * 1000),
                    'data': data
                }
            return data
    return None

def write_json_picklist(comp_code, data):
    json_path = get_json_path(comp_code)
    json_data = {
        'timestamp': int(time() * 1000),  # Current time in milliseconds
        'data': data
    }
    with open(json_path, 'w') as f:
        json.dump(json_data, f)

# @login_required
def rankings(request):
    comp_code = request.GET.get('comp')
    quantifier = request.GET.get('quantifier', 'Quals')
    config = config_loader.get_config()
    
    teams = models.Teams.objects.filter(event=comp_code).order_by("team_number")
    team_averages = {}
    
    for team in teams:
        if models.Team_Match_Data.objects.filter(team_number=team.team_number, event=comp_code, quantifier=quantifier).exists():
            team_averages[team.team_number] = fetch_team_match_averages(team.team_number, comp_code, quantifier)
            
    return render(request, "strategy/rankings.html", {
        'team_averages': team_averages,
        'comp_code': comp_code,
        'selected_quantifier': quantifier,
        'config_metrics': config.get('metrics', [])
    })

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
    client_timestamp = request.GET.get('timestamp', '0')
    save_to_db = request.GET.get('save_to_db') == 'true'

    if request.method == 'POST':
        try:
            picklist_data = json.loads(request.body.decode('utf-8'))
            
            # Save to JSON file first
            write_json_picklist(comp_code, picklist_data)
            
            if save_to_db:
                # Save to database
                PickList_Data.objects.get_or_create(event=comp_code)
                PickList_Data.objects.filter(event=comp_code).update(
                    event=comp_code,
                    no_pick=picklist_data[0],
                    first_pick=picklist_data[1],
                    second_pick=picklist_data[2],
                    third_pick=picklist_data[3],
                    dn_pick=picklist_data[4]
                )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Data saved successfully',
                'timestamp': int(time() * 1000)
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    elif request.method == 'GET':
        json_data = read_json_picklist(comp_code)
        
        if not json_data:
            return JsonResponse({
                'status': 'no_data',
                'timestamp': int(time() * 1000)
            })

        if int(client_timestamp) >= json_data['timestamp']:
            return JsonResponse({
                'status': 'no_change',
                'timestamp': json_data['timestamp']
            })
        
        return JsonResponse({
            'status': 'updated',
            'data': json_data['data'],
            'timestamp': json_data['timestamp']
        })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

# @login_required
@csrf_exempt
def dashboard(request):
    comp_code = request.GET.get('comp')
    
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            data_from_post = json.loads(request.body.decode("utf-8"))
            match_number = data_from_post.get("match_number")
            quantifier = data_from_post.get("quantifier", "Quals")

            # Map quantifier to TBA comp_level
            comp_level = {
                "Quals": "qm",
                "Playoff": "sf",
                "Prac": "pm"
            }.get(quantifier, "qm")

            # Get match with proper comp_level
            match = get_single_match(comp_code, f"{comp_level}{match_number}")

            # Existing team processing with quantifier passthrough
            red_json = {}
            red_teams = []
            blue_json = {}
            blue_teams = []

            for red_team in match['red']:
                red_json[red_team] = fetch_team_match_averages(
                    red_team, 
                    comp_code,
                    quantifier  # Pass through without changing fetch_team_match_averages
                )
                red_teams.append(red_team)

            for blue_team in match['blue']:
                blue_json[blue_team] = fetch_team_match_averages(
                    blue_team, 
                    comp_code,
                    quantifier  # Pass through without changing fetch_team_match_averages
                )
                blue_teams.append(blue_team)

            response = {
                'red': red_json,
                'blue': blue_json,
                'red_teams': red_teams,
                'blue_teams': blue_teams,
                'quantifier': quantifier
            }
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "strategy/dashboard.html")

def fetch_team_match_averages(team_number, comp_code, quantifier):
    """Dynamic calculation of team averages based on game_config.json with legacy key support"""
    config = config_loader.get_config()
    
    team_match_data = models.Team_Match_Data.objects.filter(
        team_number=team_number,
        event=comp_code,
        match_number__lt=100,
        quantifier=quantifier
    )
    
    if not team_match_data.exists():
        return {}
    
    result = {}
    
    for metric in config['metrics']:
        key = metric['key']
        aggregation = metric.get('aggregation', 'avg')
        legacy_keys = metric.get('legacy_keys', [])
        
        # Extract values with legacy key fallback
        values = []
        for match in team_match_data:
            # Try current key first
            value = match.data.get(key)
            
            # If not found, try legacy keys
            if value is None and legacy_keys:
                for legacy_key in legacy_keys:
                    value = match.data.get(legacy_key)
                    if value is not None:
                        break
            
            if value is not None:
                values.append(float(value))
        
        if values:
            if aggregation == 'avg':
                result[key] = round(sum(values) / len(values), 3)
            elif aggregation == 'sum':
                result[key] = round(sum(values), 3)
            elif aggregation == 'percent':
                result[key] = round((sum(values) / len(values)) * 100, 1)
        else:
            result[key] = 0
    
    # Add anchor field averages
    first_match = team_match_data.first()
    result['start_pos'] = first_match.start_pos if first_match else 0
    
    # Calculate composite metrics
    auto_total = sum(result.get(f'auto_{suffix}', 0) for suffix in ['L1', 'L2', 'L3', 'L4', 'net', 'processor'])
    teleop_total = sum(result.get(f'tele{suffix}', 0) for suffix in ['L1', 'L2', 'L3', 'L4', 'net', 'Processor'])
    
    result['auto_total'] = round(auto_total, 3)
    result['teleop_total'] = round(teleop_total, 3)
    result['total'] = round(auto_total + teleop_total + result.get('climb', 0), 3)
    
    return result

def get_path_data(request, team_number):
    """API endpoint for retrieving match data - auto_path removed"""
    comp_code = request.GET.get('comp')
    match_number = request.GET.get('match')
    scout_name = request.GET.get('scout')
    
    if not comp_code:
        return JsonResponse({'error': 'Competition code required'}, status=400)
    
    try:
        filters = {
            'team_number': team_number,
            'event': comp_code,
            'match_number': match_number
        }
        
        if scout_name:
            filters['scout_name'] = scout_name
        
        match_data_records = Team_Match_Data.objects.filter(**filters)
        
        if match_data_records.count() == 0:
            return JsonResponse({
                'error': f'Match data not found for team {team_number}, match {match_number}'
            }, status=404)
        
        match_data = match_data_records.first()
        
        response = {
            'data': match_data.data,
            'match_number': match_data.match_number,
            'quantifier': match_data.quantifier,
            'scout_name': match_data.scout_name
        }
        
        if match_data_records.count() > 1:
            response['multiple_records'] = True
            response['all_scouts'] = [record.scout_name for record in match_data_records]
        
        return JsonResponse(response)
        
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)