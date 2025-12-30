from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from authenticate.models import AuthorizedUser
from teams.models import Team_Match_Data
from django.db.models import Count
import json

def admin_required(function):
    def wrapper(request, *args, **kw):
        email = request.session.get("email")
        if not email:
            return HttpResponseRedirect('/auth/')
        # Temporarily disabled - first user can add themselves
        # if not AuthorizedUser.objects.filter(email=email).exists():
        #     return HttpResponseRedirect('/auth/unauthorized/')
        return function(request, *args, **kw)
    return wrapper

@admin_required
def admin_panel(request):
    comp_code = request.GET.get('comp', 'testing')
    
    # Get all authorized users
    users = AuthorizedUser.objects.all().order_by('email')
    
    # Get unique competitions with names
    from api.tba import get_team_events
    event_map = get_team_events()  # Returns {code: name}
    
    # Get scout leaderboard for the competition
    leaderboard = Team_Match_Data.objects.filter(event=comp_code).values('scout_name').annotate(
        match_count=Count('id')
    ).order_by('-match_count')
    
    return render(request, 'authenticate/admin.html', {
        'users': users,
        'leaderboard': leaderboard,
        'comp_code': comp_code,
        'event_map': event_map
    })

@admin_required
def add_user(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            AuthorizedUser.objects.get_or_create(email=email)
    return redirect('/admin-panel/')

@admin_required
def remove_user(request, user_id):
    AuthorizedUser.objects.filter(id=user_id).delete()
    return redirect('/admin-panel/')

@admin_required
def match_data_editor(request):
    # Get unique competitions with names
    from api.tba import get_team_events
    event_map = get_team_events()  # Returns {code: name}
    
    return render(request, 'authenticate/match_editor.html', {
        'event_map': event_map
    })

@admin_required
def get_teams_for_event(request):
    """API endpoint to get teams for a competition"""
    comp_code = request.GET.get('comp')
    teams = Team_Match_Data.objects.filter(event=comp_code).values_list('team_number', flat=True).distinct().order_by('team_number')
    return JsonResponse({'teams': list(teams)})

@admin_required
def get_quantifiers_for_team(request):
    """API endpoint to get available quantifiers for a team"""
    comp_code = request.GET.get('comp')
    team_number = request.GET.get('team')
    quantifiers = Team_Match_Data.objects.filter(
        event=comp_code,
        team_number=team_number
    ).values_list('quantifier', flat=True).distinct().order_by('quantifier')
    return JsonResponse({'quantifiers': list(quantifiers)})

@admin_required
def get_matches_for_team(request):
    """API endpoint to get available matches for a team"""
    comp_code = request.GET.get('comp')
    team_number = request.GET.get('team')
    quantifier = request.GET.get('quantifier')
    matches = Team_Match_Data.objects.filter(
        event=comp_code,
        team_number=team_number,
        quantifier=quantifier
    ).values_list('match_number', flat=True).distinct().order_by('match_number')
    return JsonResponse({'matches': list(matches)})

@admin_required
def load_match_data(request):
    """API endpoint to load match data for editing"""
    comp_code = request.GET.get('comp')
    team_number = request.GET.get('team')
    match_number = request.GET.get('match')
    quantifier = request.GET.get('quantifier')
    
    match_data = Team_Match_Data.objects.filter(
        event=comp_code,
        team_number=team_number,
        match_number=match_number,
        quantifier=quantifier
    ).first()
    
    if not match_data:
        return JsonResponse({'error': 'Match not found'}, status=404)
    
    return JsonResponse({
        'id': match_data.id,
        'team_number': match_data.team_number,
        'match_number': match_data.match_number,
        'event': match_data.event,
        'quantifier': match_data.quantifier,
        'scout_name': match_data.scout_name,
        'start_pos': match_data.start_pos,
        'comment': match_data.comment,
        'is_broken': match_data.is_broken,
        'is_disabled': match_data.is_disabled,
        'is_tipped': match_data.is_tipped,
        'data': match_data.data
    })

@admin_required
def update_match_data(request):
    if request.method == 'POST':
        match_id = request.POST.get('match_id')
        data_json = request.POST.get('data_json')
        start_pos = request.POST.get('start_pos')
        quantifier = request.POST.get('quantifier')
        comment = request.POST.get('comment')
        is_broken = request.POST.get('is_broken') == 'true'
        is_disabled = request.POST.get('is_disabled') == 'true'
        is_tipped = request.POST.get('is_tipped') == 'true'
        
        try:
            match = Team_Match_Data.objects.get(id=match_id)
            match.data = json.loads(data_json)
            match.start_pos = int(start_pos) if start_pos else 0
            match.quantifier = quantifier
            match.comment = comment
            match.is_broken = is_broken
            match.is_disabled = is_disabled
            match.is_tipped = is_tipped
            match.save()
            return JsonResponse({'status': 'success', 'message': 'Match data updated'})
        except Team_Match_Data.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Match not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
