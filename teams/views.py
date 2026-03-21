import os
from PIL import Image

import cloudinary
import cloudinary.api
import cloudinary.uploader
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from api.tba import get_teams_list, get_team_events
from helpers import login_required
from teams.models import Teams, Team_Match_Data, Human_Player_Match
from .forms import NewHumanScoutingData
from django.db.models import Case, When, Value, IntegerField
from utils import config_loader

cloudinary.config(
    cloud_name=os.environ.get("CLOUD_NAME"),
    api_key=os.environ.get("CLOUD_API_KEY"),
    api_secret=os.environ.get("CLOUD_API_SECRET"),
    secure=True)


def home(request):
    robot_picture = None
    try:
        comp_code = request.GET.get('comp', 'testing')
        own_team = Teams.objects.filter(team_number=2073, event=comp_code).first()
        if own_team and own_team.robot_picture:
            url = str(own_team.robot_picture)
            # Only pass external HTTPS URLs (Cloudinary). Skip local dev / IP-only URLs.
            if url.startswith('https://'):
                robot_picture = url
    except Exception:
        pass
    return render(request, 'home.html', {'robot_picture': robot_picture})


@login_required
def get_events(request):
    return JsonResponse(get_team_events())


@login_required
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

@login_required
def team_page(request, team_number):
    comp_code = request.GET.get('comp')
    config = config_loader.get_config()
    
    context = {
        'team_number': team_number,
        'comp_code': comp_code,
        'config_metrics': config.get('metrics', []),
    }

    if comp_code:
        team, created = Teams.objects.get_or_create(team_number=team_number, event=comp_code)
        all_team_match_data = Team_Match_Data.objects.filter(
            team_number=team_number, 
            event=comp_code
        ).order_by('-match_number')

        context.update({
            'team': team,
            'all_team_match_data': all_team_match_data,
        })
        
    return render(request, 'teams/team_page.html', context)


@login_required
def pit_scouting(request, team_number):
    comp_code = request.GET.get('comp')
    if not comp_code:
        return HttpResponse('Competition code required. Add ?comp=EVENT_CODE to URL', status=400)
    
    config = config_loader.get_config()
    team, created = Teams.objects.get_or_create(team_number=team_number, event=comp_code)
    
    if request.method == 'POST':
        # Handle image upload (Anchor field)
        img_url = None
        logo_url = None
        allowed_types = ['image/png', 'image/jpeg', 'image/jpg']

        if 'robot_picture' in request.FILES:
            image_file = request.FILES['robot_picture']
            try:
                img = Image.open(image_file)
                img.verify()
                if img.format not in ('PNG', 'JPEG'):
                    raise ValueError("Unsupported format")
                image_file.seek(0)
            except Exception:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid file type. Only PNG and JPEG images are allowed.'
                }, status=400)

            image_response = cloudinary.uploader.upload(image_file)
            img_url = image_response["secure_url"]
            image_url_list = img_url.split("upload/")
            image_url_list.insert(1, "upload/w_0.4,c_scale/")
            img_url = "".join(image_url_list)

        # Optional team logo upload
        if 'team_logo' in request.FILES:
            logo_file = request.FILES['team_logo']
            try:
                img = Image.open(logo_file)
                img.verify()
                if img.format not in ('PNG', 'JPEG'):
                    raise ValueError("Unsupported format")
                logo_file.seek(0)
            except Exception:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid logo file type. Only PNG and JPEG images are allowed.'
                }, status=400)

            logo_response = cloudinary.uploader.upload(logo_file)
            logo_url = logo_response["secure_url"]
            # small display size
            logo_url_list = logo_url.split("upload/")
            logo_url_list.insert(1, "upload/w_0.4,c_scale/")
            logo_url = "".join(logo_url_list)

        # Handle dynamic pit data
        pit_payload = {}
        validation_errors = []
        
        for q in config.get('pit_questions', []):
            key = q['key']
            if q['type'] == 'multiselect':
                pit_payload[key] = request.POST.getlist(key)
            elif q['type'] == 'boolean':
                pit_payload[key] = request.POST.get(key) == 'on'
            else:
                pit_payload[key] = request.POST.get(key, '')
            
            # Validate number fields with min/max
            if q['type'] == 'number' and pit_payload[key]:
                try:
                    val = float(pit_payload[key])
                    if 'min' in q and val < q['min']:
                        validation_errors.append(f"{q.get('display_name', key)} must be at least {q['min']}")
                    if 'max' in q and val > q['max']:
                        validation_errors.append(f"{q.get('display_name', key)} cannot exceed {q['max']}")
                except (ValueError, TypeError):
                    validation_errors.append(f"{q.get('display_name', key)} must be a valid number")

        # Server-side required-field validation
        field_errors = {}
        for q in config.get('pit_questions', []):
            if q.get('required'):
                val = pit_payload.get(q['key'])
                if q['type'] == 'multiselect':
                    if not val:
                        field_errors[q['key']] = f"{q.get('display_name', q['key'])} is required."
                elif q['type'] in ['select', 'text', 'textarea', 'number']:
                    if val in [None, '', []]:
                        field_errors[q['key']] = f"{q.get('display_name', q['key'])} is required."
        
        # Merge validation errors
        if validation_errors:
            for err in validation_errors:
                field_errors['_general'] = field_errors.get('_general', []) if isinstance(field_errors.get('_general'), list) else []
                field_errors['_general'].append(err)

        if field_errors:
            # Return form with errors and previously entered values
            return render(request, "teams/pit_scouting.html", {
                'team_number': team_number,
                'questions': config.get('pit_questions', []),
                'existing_data': pit_payload,
                'field_errors': field_errors,
            })
        
        # Save
        team.pit_data = pit_payload
        if img_url:
            team.robot_picture = img_url
        if logo_url:
            team.logo_url = logo_url
        team.pit_scout_status = True
        team.save()
        return redirect(f'/teams/{team_number}/?comp={comp_code}')

    # Ensure existing_data is a dict (some DB rows may have JSON saved as string)
    existing_data = team.pit_data or {}
    if isinstance(existing_data, str):
        try:
            import json as _json
            existing_data = _json.loads(existing_data)
        except Exception:
            existing_data = {}

    return render(request, "teams/pit_scouting.html", {
        'team_number': team_number,
        'questions': config.get('pit_questions', []),
        'existing_data': existing_data,
        'has_robot_picture': bool(team.robot_picture),
        'comp_code': comp_code,
    })
    
@login_required
def clear_pit_data(request, team_number):
    if request.method == 'POST':
        comp_code = request.POST.get('comp_code')
        if comp_code:
            team = Teams.objects.filter(team_number=team_number, event=comp_code).first()
            if team:
                team.pit_data = {}
                team.pit_scout_status = False
                team.robot_picture = None
                team.save()
        return redirect(f'/teams/{team_number}/?comp={comp_code}')
    return redirect(f'/teams/{team_number}/')

@login_required
def human_player_submit(request, team_number):
    comp_code = request.GET.get('comp')
    if request.method == 'POST':
        form = NewHumanScoutingData(request.POST)
        if form.is_valid():
            Human_Player_Match.objects.create(team_number=team_number,
                                              event=comp_code,
                                              match_number=form.cleaned_data.get('match_number'),
                                              human_player_comment=form.cleaned_data.get('human_player_comment'))

            return redirect("team_page", team_number=team_number)
    else:
        form = NewHumanScoutingData()
    return render(request, "teams/human_player_scout.html", {'form': form, 'team_number': team_number})

