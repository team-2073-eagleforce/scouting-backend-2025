import json
import logging
import os
import re
from collections import defaultdict

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
from teams.models import Team_Match_Data, Teams
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
    exclude_zeros = request.GET.get('exclude_zeros', 'true') == 'true'
    min_matches = int(request.GET.get('min_matches', '0'))
    config = config_loader.get_config()

    VALID_SORT_FIELDS = {m['key'] for m in config.get('metrics', [])}
    # Add computed and anchor fields
    VALID_SORT_FIELDS |= {'totalShooting', 'totalPass', 'totalTotal', 'match_count',
                          'driverRanking', 'defenseRanking', 'autoLeave'}
    sort_by = request.GET.get('sort_by', 'totalShooting')
    if sort_by not in VALID_SORT_FIELDS:
        sort_by = 'totalShooting'

    # Build sort options from config rankings columns + computed fields
    SORT_OPTIONS = []
    for col in config.get('rankings', []):
        if col.get('sortable') and col['key'] != 'team_number':
            SORT_OPTIONS.append((col['key'], col['display_name']))
    SORT_OPTIONS.append(('match_count', 'Matches Played'))

    # Get excluded match IDs from session
    excluded_ids = set(request.session.get('excluded_match_ids', []))
    logger.warning(
        "RANKINGS user=%s session=%s excluded_ids=%s",
        request.session.get('email', '?'),
        request.session.session_key[:8] if request.session.session_key else '?',
        list(excluded_ids)
    )

    # --- Pit scouting attribute filters ---
    pit_questions = config.get('pit_questions', [])
    # Deduplicate by key (config has some dupes)
    seen_keys = set()
    filterable_pit = []
    for q in pit_questions:
        if q['type'] in ('select', 'multiselect') and q['key'] not in seen_keys:
            seen_keys.add(q['key'])
            filterable_pit.append(q)

    # Collect active pit filters from query params (pit__<key>=value)
    active_pit_filters = {}
    for q in filterable_pit:
        vals = request.GET.getlist('pit__' + q['key'])
        if vals:
            active_pit_filters[q['key']] = vals

    # Build a set of team numbers that pass pit filters
    pit_filtered_teams = None
    if active_pit_filters:
        pit_filtered_teams = set()
        for team in models.Teams.objects.filter(event=comp_code, pit_scout_status=True):
            pit_data = team.pit_data or {}
            passes = True
            for key, required_vals in active_pit_filters.items():
                team_val = pit_data.get(key)
                if isinstance(team_val, list):
                    if not any(rv in team_val for rv in required_vals):
                        passes = False
                        break
                else:
                    if str(team_val) not in required_vals:
                        passes = False
                        break
            if passes:
                pit_filtered_teams.add(team.team_number)

    teams = models.Teams.objects.filter(event=comp_code).order_by("team_number")
    team_averages = {}

    # Bulk-fetch ALL match data for this event/quantifier in ONE query
    all_matches = list(models.Team_Match_Data.objects.filter(
        event=comp_code, quantifier=quantifier, match_number__lt=100
    ).exclude(id__in=excluded_ids if excluded_ids else []))

    # Group by team number
    matches_by_team = defaultdict(list)
    for m in all_matches:
        matches_by_team[m.team_number].append(m)

    for team in teams:
        if pit_filtered_teams is not None and team.team_number not in pit_filtered_teams:
            continue
        team_matches = matches_by_team.get(team.team_number)
        if not team_matches:
            continue
        stats = _compute_team_averages(team_matches, config, exclude_zeros)
        if not stats or stats.get('match_count', 0) < min_matches:
            continue
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
        'exclude_zeros': exclude_zeros,
        'min_matches': min_matches,
        'filterable_pit': filterable_pit,
        'active_pit_filters': active_pit_filters,
        'excluded_count': len(excluded_ids),
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
        if not comp_code or not _SAFE_COMP_CODE.match(comp_code):
            return JsonResponse({'status': 'error', 'message': 'Invalid or missing competition code'}, status=400)
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

def _compute_team_averages(team_match_data_list, config, exclude_zeros=True):
    """Compute averages from a pre-fetched list of matches (no DB calls)."""
    if exclude_zeros:
        team_match_data_list = [
            m for m in team_match_data_list
            if m.data and any(float(v) != 0 for v in m.data.values() if isinstance(v, (int, float)))
        ]
    if not team_match_data_list:
        return {}

    result = {'match_count': len(team_match_data_list)}

    for field in ('driverRanking', 'defenseRanking', 'autoLeave'):
        values = [getattr(m, field, 0) for m in team_match_data_list if getattr(m, field, 0) > 0]
        result[field] = round(sum(values) / len(values), 3) if values else 0

    for metric in config['metrics']:
        key = metric['key']
        aggregation = metric.get('aggregation', 'avg')
        legacy_keys = metric.get('legacy_keys', [])
        values = []
        for match in team_match_data_list:
            value = match.data.get(key)
            if value is None:
                for lk in legacy_keys:
                    value = match.data.get(lk)
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

    result['start_pos'] = team_match_data_list[0].start_pos if team_match_data_list else 0
    return result


def fetch_team_match_averages(team_number, comp_code, quantifier, exclude_zeros=True, excluded_ids=None):
    """Dynamic calculation of team averages based on game_config.json with legacy key support"""
    config = config_loader.get_config()
    
    team_match_data = models.Team_Match_Data.objects.filter(
        team_number=team_number,
        event=comp_code,
        match_number__lt=100,
        quantifier=quantifier
    )

    # Exclude manually excluded matches
    if excluded_ids:
        team_match_data = team_match_data.exclude(id__in=excluded_ids)

    # Filter out all-zero data matches (incomplete scans)
    if exclude_zeros:
        filtered = []
        for match in team_match_data:
            if match.data:
                numeric_vals = [float(v) for v in match.data.values() if isinstance(v, (int, float))]
                if numeric_vals and any(v != 0 for v in numeric_vals):
                    filtered.append(match)
        team_match_data_list = filtered
    else:
        team_match_data_list = list(team_match_data)
    
    if not team_match_data_list:
        return {}
    
    result = {'match_count': len(team_match_data_list)}
    
    # Add anchor field averages (only count non-zero values)
    anchor_fields = ['driverRanking', 'defenseRanking', 'autoLeave']
    for field in anchor_fields:
        values = [getattr(match, field, 0) for match in team_match_data_list if getattr(match, field, 0) > 0]
        result[field] = round(sum(values) / len(values), 3) if values else 0
    
    # Dynamic metrics from config — per-metric non-zero averaging
    for metric in config['metrics']:
        key = metric['key']
        aggregation = metric.get('aggregation', 'avg')
        legacy_keys = metric.get('legacy_keys', [])
        
        values = []
        for match in team_match_data_list:
            value = match.data.get(key)
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
    result['start_pos'] = team_match_data_list[0].start_pos if team_match_data_list else 0
    
    return result


@login_required
def toggle_exclude_match(request):
    """Toggle exclusion of a specific match from rankings calculations."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        body = json.loads(request.body.decode('utf-8'))
        match_id = int(body['match_id'])
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        return JsonResponse({'error': 'Invalid match_id'}, status=400)

    user = request.session.get('email', '?')
    session_key = request.session.session_key
    before = list(request.session.get('excluded_match_ids', []))

    excluded = set(before)
    if match_id in excluded:
        excluded.discard(match_id)
        action = 'included'
    else:
        excluded.add(match_id)
        action = 'excluded'
    request.session['excluded_match_ids'] = list(excluded)

    logger.warning(
        "TOGGLE user=%s session=%s match_id=%d action=%s before=%s after=%s",
        user, session_key[:8] if session_key else '?', match_id, action, before, list(excluded)
    )

    return JsonResponse({'status': action, 'match_id': match_id, 'excluded_count': len(excluded)})


@login_required
def team_matches_detail(request, team_number):
    """Return individual match data for a team so strategists can review/exclude."""
    comp_code = request.GET.get('comp')
    quantifier = request.GET.get('quantifier', 'Quals')
    if not comp_code:
        return JsonResponse({'error': 'comp required'}, status=400)

    matches = Team_Match_Data.objects.filter(
        team_number=team_number, event=comp_code, quantifier=quantifier
    ).order_by('match_number')

    excluded = set(request.session.get('excluded_match_ids', []))
    result = []
    for m in matches:
        result.append({
            'id': m.id,
            'match_number': m.match_number,
            'start_pos': m.start_pos,
            'scout_name': m.scout_name,
            'data': m.data,
            'excluded': m.id in excluded,
        })
    return JsonResponse({'matches': result})

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


@login_required
def team_info(request, team_number):
    """Return pit scouting info + full match history for a team — used by the rankings quick-view modal."""
    comp_code = request.GET.get('comp')
    quantifier = request.GET.get('quantifier', 'Quals')
    if not comp_code:
        return JsonResponse({'error': 'comp required'}, status=400)

    team = Teams.objects.filter(team_number=team_number, event=comp_code).first()
    matches = Team_Match_Data.objects.filter(
        team_number=team_number, event=comp_code, quantifier=quantifier
    ).order_by('match_number')

    excluded = set(request.session.get('excluded_match_ids', []))
    config = config_loader.get_config()
    metrics = config.get('metrics', [])

    match_list = []
    for m in matches:
        flags = []
        if m.is_broken:   flags.append('Broken')
        if m.is_disabled: flags.append('Disabled')
        if m.is_tipped:   flags.append('Tipped')
        match_list.append({
            'id': m.id,
            'match_number': m.match_number,
            'start_pos': m.start_pos,
            'scout_name': m.scout_name,
            'autoLeave': m.autoLeave,
            'driverRanking': m.driverRanking,
            'defenseRanking': m.defenseRanking,
            'comment': m.comment,
            'flags': flags,
            'data': m.data,
            'excluded': m.id in excluded,
        })

    return JsonResponse({
        'team_number': team_number,
        'logo_url': team.logo_url if team else None,
        'robot_picture': str(team.robot_picture) if team and team.robot_picture else None,
        'pit_scout_status': team.pit_scout_status if team else False,
        'pit_data': team.pit_data if team else {},
        'metrics': [{'key': m['key'], 'display_name': m['display_name']} for m in metrics],
        'matches': match_list,
    })
