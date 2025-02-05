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
        all_team_match_data = Team_Match_Data.objects.filter(
            team_number=team_number, 
            event=comp_code
        ).order_by("-quantifier", "-match_number")
        
        # Debug: Print auto_path data
        for match in all_team_match_data:
            print(f"Match {match.match_number} auto_path: {match.auto_path}")
            print(f"Auto path type: {type(match.auto_path)}")
        
        # Extract paths with match numbers for dropdown
        paths_data = [
            {
                'match_number': match.match_number,
                'quantifier': match.quantifier,
                'path': match.auto_path
            }
            for match in all_team_match_data if match.auto_path
        ]
        
        # Debug: Print paths_data
        print("Paths data:", paths_data)

        context = {
            'team': team,
            'all_team_match_data': all_team_match_data,
            'team_number': team_number,
            'paths_data': paths_data,
            'comp_code': comp_code
        }
        return render(request, 'teams/team_page.html', context)
    
    return render(request, 'teams/team_page.html', {'team_number': team_number})


def pit_scouting(request, team_number):
    comp_code = request.GET.get('comp')
    print(f"Method: {request.method}")  # Check if POST
    print(f"Competition Code: {comp_code}")  # Check if comp_code exists
    
    if request.method == 'POST' and comp_code is not None:
        form = NewPitScoutingData(request.POST, request.FILES)
        print(f"Form is valid: {form.is_valid()}")
        
        if not form.is_valid():
            print(f"Form errors: {form.errors}")  # Print validation errors
        
        if form.is_valid():
            try:
                # Handle image upload
                if 'robot_picture' in request.FILES:
                    image_file = request.FILES['robot_picture']
                    # Validate file type (optional)
                    allowed_types = ['image/png', 'image/jpeg', 'image/jpg']
                    if image_file.content_type not in allowed_types:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Invalid file type. Only PNG, JPEG, and JPG are allowed.'
                        }, status=400)

                    # Upload to Cloudinary
                    image_response = cloudinary.uploader.upload(image_file)
                    img_url = image_response["secure_url"]

                    # Resize image (optional)
                    image_url_list = img_url.split("upload/")
                    image_url_list.insert(1, "upload/w_0.4,c_scale/")
                    img_url = "".join(image_url_list)
                else:
                    img_url = None  # No image provided

                # Get or create team
                team, created = Teams.objects.get_or_create(
                    team_number=team_number,
                    event=comp_code
                )
                print(f"Team created: {created}")  # Check if team was created

                # Process multi-select fields
                intake_locations_char = ", ".join(form.cleaned_data.get('intake_locations', []))
                scoring_locations_char = ", ".join(form.cleaned_data.get('scoring_locations', []))
                auto_positions_char = ", ".join(form.cleaned_data.get('auto_positions', []))
                cage_positions_char = ", ".join(form.cleaned_data.get('cage_positions', []))

                # Update team data
                update_result = Teams.objects.filter(
                    team_number=team_number,
                    event=comp_code
                ).update(
                    drivetrain=form.cleaned_data.get('drivetrain'),
                    weight=form.cleaned_data.get('weight'),
                    length=form.cleaned_data.get('length'),
                    width=form.cleaned_data.get('width'),
                    intake_design=form.cleaned_data.get('intake_design'),
                    intake_locations=intake_locations_char,
                    scoring_locations=scoring_locations_char,
                    cage_positions=cage_positions_char,
                    under_shallow=form.cleaned_data.get('under_shallow'),
                    algae_picker=form.cleaned_data.get('algae_picker'),
                    auto_positions=auto_positions_char,
                    auto_leave=form.cleaned_data.get('auto_leave'),
                    auto_algae_max=form.cleaned_data.get('auto_algae_max'),
                    auto_coral_max=form.cleaned_data.get('auto_coral_max'),
                    robot_picture=img_url,  # Save the image URL
                    additional_info=form.cleaned_data.get('additional_info'),
                    pit_scout_status=True
                )
                print(f"Update result: {update_result}")  # Check if update was successful
                print(f"Cleaned data: {form.cleaned_data}")  # Print the form data

                return redirect('team_page', team_number=team_number)
            except Exception as e:
                print(f"Error occurred: {str(e)}")  # Print any errors
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)
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

def get_path_data(request, team_number):
    comp_code = request.GET.get('comp')
    if not comp_code:
        return HttpResponse('Competition code required', status=400)
    
    try:
        match_number = request.GET.get('match')
        match_data = Team_Match_Data.objects.get(
            team_number=team_number,
            event=comp_code,
            match_number=match_number
        )
        
        return HttpResponse(match_data.auto_path, content_type='text/plain')
    except Team_Match_Data.DoesNotExist:
        return HttpResponse('Match data not found', status=404)