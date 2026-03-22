import json
import logging
import os
import re

logger = logging.getLogger(__name__)
from pathlib import Path
from time import time

from django.db.models import Avg, Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from api.tba import get_single_match, get_teams_list
from teams import models
from helpers import login_required
from django.shortcuts import render, redirect
from strategy.models import PickList_Data
from teams.models import Team_Match_Data
from utils import config_loader

_SAFE_COMP_CODE = re.compile(r'^[A-Za-z0-9_\-]{1,20}$')

def get_json_path(comp_code):
    if not comp_code or not _SAFE_COMP_CODE.match(comp_code):
        return None
    # Get the project root directory
    BASE_DIR = Path(__file__).resolve().parent.parent
    # Create a picklists directory if it doesn't exist
    picklist_dir = BASE_DIR / 'picklists'
    picklist_dir.mkdir(exist_ok=True)
    return picklist_dir / f'picklist_{comp_code}.json'

def read_json_picklist(comp_code):
    json_path = get_json_path(comp_code)
    if json_path is None:
        return None
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
    if json_path is None:
        raise ValueError("Invalid competition code")
    json_data = {
        'timestamp': int(time() * 1000),  # Current time in milliseconds
        'data': data
    }
    with open(json_path, 'w') as f:
        json.dump(json_data, f)

@login_required
def rankings(request):
    comp_code = request.GET.get('comp')
    quantifier = request.GET.get('quantifier', 'Quals')
    config = config_loader.get_config()

    VALID_SORT_FIELDS = {
        'autoScore', 'autoPass', 'autoClimb',
        'teleScore', 'telePass',
        'totalShooting', 'totalPass', 'totalTotal',
    }
    sort_by = request.GET.get('sort_by', 'totalShooting')
    if sort_by not in VALID_SORT_FIELDS:
        sort_by = 'totalShooting'

    SORT_OPTIONS = [
        ('autoScore',     'Auto Score'),
        ('autoPass',      'Auto Pass'),
        ('autoClimb',     'Auto Climb'),
        ('teleScore',     'Teleop Score'),
        ('telePass',      'Teleop Pass'),
        ('totalShooting', 'Total Score'),
        ('totalPass',     'Total Pass'),
        ('totalTotal',    'Total Total'),
    ]

    teams = models.Teams.objects.filter(event=comp_code).order_by("team_number")
    team_averages = {}

    for team in teams:
        if models.Team_Match_Data.objects.filter(team_number=team.team_number, event=comp_code, quantifier=quantifier).exists():
            stats = fetch_team_match_averages(team.team_number, comp_code, quantifier)
            stats['totalPass']     = round((stats.get('autoPass', 0) or 0) + (stats.get('telePass', 0) or 0), 3)
            stats['totalShooting'] = round((stats.get('autoScore', 0) or 0) + (stats.get('teleScore', 0) or 0), 3)
            stats['totalTotal']    = round((stats.get('totalShooting', 0) or 0) + (stats.get('totalPass', 0) or 0), 3)
            team_averages[team.team_number] = stats

    team_averages = dict(sorted(team_averages.items(), key=lambda x: x[1].get(sort_by, 0), reverse=True))

    return render(request, "strategy/rankings.html", {
        'team_averages': team_averages,
        'comp_code': comp_code,
        'selected_quantifier': quantifier,
        'config_metrics': config.get('metrics', []),
        'rankings_columns': config.get('rankings', []),
        'sort_by': sort_by,
        'sort_options': SORT_OPTIONS,
    })

@login_required
def picklist(request):
    comp_code = request.GET.get('comp')
    teams = []
    no_pick_teams = []
    first_pick_teams = []
    second_pick_teams = []
    third_pick_teams = []
    dn_pick_teams = []
    if not comp_code or comp_code.lower() == 'testing':
        return render(request, "strategy/picklist.html", {'teams': teams})
    else:
        # Read JSON timestamp so JS won't overwrite server-rendered data on first load
        json_data = read_json_picklist(comp_code)
        json_timestamp = json_data['timestamp'] if json_data else 0

        if len(PickList_Data.objects.filter(event=comp_code)) == 0:
            teams_data = get_teams_list(comp_code)
            for team in teams_data:
                teams.append(team["team_number"])
            teams.sort()
            # If JSON exists, use it to populate lists so server render matches JSON state
            if json_data and json_data.get('data'):
                d = json_data['data']
                no_pick_teams   = d[0] if len(d) > 0 else []
                first_pick_teams  = d[1] if len(d) > 1 else []
                second_pick_teams = d[2] if len(d) > 2 else []
                third_pick_teams  = d[3] if len(d) > 3 else []
                dn_pick_teams     = d[4] if len(d) > 4 else []
                # Only show teams in the pool that aren't already categorized
                categorized = set(no_pick_teams + first_pick_teams + second_pick_teams + third_pick_teams + dn_pick_teams)
                teams = [t for t in teams if str(t) not in categorized and t not in categorized]
            return render(request, "strategy/picklist.html", {'teams': teams,
                                                          'comp_code' : comp_code,
                                                          'json_timestamp': json_timestamp,
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
                                                          'json_timestamp': json_timestamp,
                                                          'no_pick_teams' : no_pick_teams,
                                                          'first_pick_teams' : first_pick_teams,
                                                          'second_pick_teams' : second_pick_teams,
                                                          'third_pick_teams' : third_pick_teams,
                                                          'dn_pick_teams' : dn_pick_teams})
        
@login_required
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
            
        except Exception:
            logger.exception("picklist_submit POST failed")
            return JsonResponse({
                'status': 'error',
                'message': 'An unexpected error occurred'
            }, status=500)

    elif request.method == 'GET':
        json_data = read_json_picklist(comp_code)
        
        if not json_data:
            return JsonResponse({
                'status': 'no_data',
                'timestamp': int(time() * 1000)
            })

        try:
            client_ts = int(client_timestamp)
        except (ValueError, TypeError):
            client_ts = 0
        if client_ts >= json_data['timestamp']:
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

@login_required
def dashboard(request):
    comp_code = request.GET.get('comp')
    config = config_loader.get_config()
    
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
            
            # Check if match data exists
            if not match or 'alliances' not in match:
                return JsonResponse({"error": "Match data not found or incomplete"}, status=404)

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
        except Exception:
            return JsonResponse({"error": "An unexpected error occurred"}, status=500)

    return render(request, "strategy/dashboard.html", {
        'config_metrics': config.get('metrics', []),
        'config_metrics_json': json.dumps(config.get('metrics', []))
    })

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
    
    # Add anchor field averages
    anchor_fields = ['driverRanking', 'defenseRanking', 'autoLeave']
    for field in anchor_fields:
        values = [getattr(match, field, 0) for match in team_match_data if getattr(match, field, 0) > 0]
        if values:
            result[field] = round(sum(values) / len(values), 3)
        else:
            result[field] = 0
    
    # Dynamic metrics from config
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
    
    # Add start_pos from first match
    first_match = team_match_data.first()
    result['start_pos'] = first_match.start_pos if first_match else 0
    
    return result

@login_required
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
        
    except Exception:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)