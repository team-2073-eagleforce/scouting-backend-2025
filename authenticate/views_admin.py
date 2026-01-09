from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from authenticate.models import AuthorizedUser
from teams.models import Team_Match_Data
from django.db.models import Count
import json
import zipfile
from pathlib import Path
import subprocess
import sys
from plugins import plugin_manager
from authenticate.models import SiteSettings
from utils import config_loader
import re
def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


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
    
    # Plugin management
    plugins_dir = plugin_manager.plugins_dir
    config_path = plugins_dir / 'config.json'

    def _read_enabled():
        if not config_path.exists():
            return None  # None means all enabled
        try:
            data = json.loads(config_path.read_text())
            enabled = data.get('enabled')
            return enabled if isinstance(enabled, list) else None
        except Exception:
            return None

    enabled_list = _read_enabled()
    available = plugin_manager.list_available_plugins()
    plugin_info = []
    for name in available:
        is_enabled = True if enabled_list is None else name in enabled_list
        has_req = (plugins_dir / name / 'requirements.txt').exists()
        plugin_info.append({
            'name': name,
            'enabled': is_enabled,
            'has_requirements': has_req
        })

    # Current theme color
    # Load DB settings (create defaults if missing)
    try:
        site_settings, _ = SiteSettings.objects.get_or_create(id=1)
    except Exception:
        site_settings = None
    theme_color = (site_settings.theme_color if site_settings else '#e74c3c')
    logo_url = (site_settings.logo_url if site_settings else '/static/images/EagleForceLogo.png')

    return render(request, 'authenticate/admin.html', {
        'users': users,
        'leaderboard': leaderboard,
        'comp_code': comp_code,
        'event_map': event_map,
        'plugins': plugin_info,
        'theme_color': theme_color,
        'logo_url': logo_url,
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


@admin_required
def plugins_enable(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    name = request.POST.get('name')
    enable = request.POST.get('enable') == 'true'
    if not name:
        return JsonResponse({'status': 'error', 'message': 'Missing plugin name'}, status=400)

    plugins_dir = plugin_manager.plugins_dir
    config_path = plugins_dir / 'config.json'

    # Validate plugin exists
    if name not in plugin_manager.list_available_plugins():
        return JsonResponse({'status': 'error', 'message': 'Unknown plugin'}, status=404)

    # Read current config
    enabled: list
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text())
            enabled = data.get('enabled') or []
        except Exception:
            enabled = []
    else:
        enabled = []

    # Update list
    if enable and name not in enabled:
        enabled.append(name)
    if not enable and name in enabled:
        enabled.remove(name)

    config_path.write_text(json.dumps({'enabled': sorted(enabled)}, indent=2))
    # Reload plugins
    plugin_manager.reload()
    if _is_ajax(request):
        return JsonResponse({'status': 'success', 'enabled': enabled})
    return redirect('admin_panel')


def _safe_extract_zip(zip_path: Path, dest_dir: Path) -> str:
    """Safely extract a plugin ZIP into dest_dir.

    Returns the top-level folder name extracted.
    Raises ValueError on unsafe paths.
    """
    with zipfile.ZipFile(zip_path) as zf:
        # Identify common top-level directory
        top_levels = set(p.split('/')[0] for p in zf.namelist() if '/' in p)
        if not top_levels:
            raise ValueError('ZIP must contain a top-level folder')
        if len(top_levels) > 1:
            raise ValueError('ZIP must contain a single top-level folder')
        top = next(iter(top_levels))

        for member in zf.infolist():
            # Prevent path traversal
            extracted_path = dest_dir / member.filename
            if not str(extracted_path.resolve()).startswith(str(dest_dir.resolve())):
                raise ValueError('Unsafe ZIP path detected')
        zf.extractall(dest_dir)
        return top


@admin_required
def plugins_upload(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    file = request.FILES.get('plugin_zip')
    if not file:
        return JsonResponse({'status': 'error', 'message': 'Missing file'}, status=400)

    # Save temp
    temp_path = Path('/tmp') / f'plugin_{file.name}'
    with temp_path.open('wb') as f:
        for chunk in file.chunks():
            f.write(chunk)

    try:
        dest_dir = plugin_manager.plugins_dir
        top = _safe_extract_zip(temp_path, dest_dir)
        # Basic validation: plugin.py exists
        if not (dest_dir / top / 'plugin.py').exists():
            if _is_ajax(request):
                return JsonResponse({'status': 'error', 'message': 'Invalid plugin package: missing plugin.py'}, status=400)
            return redirect('admin_panel')
        if _is_ajax(request):
            return JsonResponse({'status': 'success', 'plugin': top})
        return redirect('admin_panel')
    except Exception as e:
        if _is_ajax(request):
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        return redirect('admin_panel')
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass


def _sanitize_requirements(lines):
    """Return a safe list of requirements from raw file lines.

    Only allow standard `pkg`, `pkg==x.y`, `pkg>=x`, `pkg<=x`, `pkg~=x`.
    Disallow URLs, options, editable installs, and extras like `@`.
    """
    import re
    allowed = re.compile(r"^[A-Za-z0-9_.\-]+(==|>=|<=|~=)?[A-Za-z0-9_.\-]+$")
    safe = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if allowed.match(line):
            safe.append(line)
        else:
            raise ValueError(f"Disallowed requirement entry: {line}")
    return safe


@admin_required
def plugins_install_deps(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    name = request.POST.get('name')
    if not name:
        return JsonResponse({'status': 'error', 'message': 'Missing plugin name'}, status=400)
    plugins_dir = plugin_manager.plugins_dir
    req_path = plugins_dir / name / 'requirements.txt'
    if not req_path.exists():
        return JsonResponse({'status': 'error', 'message': 'No requirements.txt found for plugin'}, status=404)

    try:
        lines = req_path.read_text().splitlines()
        safe_pkgs = _sanitize_requirements(lines)
        if not safe_pkgs:
            if _is_ajax(request):
                return JsonResponse({'status': 'success', 'message': 'No dependencies to install'})
            return redirect('admin_panel')
        # Install using current venv python
        cmd = [sys.executable, '-m', 'pip', 'install'] + safe_pkgs
        subprocess_result = subprocess.run(cmd, capture_output=True, text=True)
        if subprocess_result.returncode != 0:
            if _is_ajax(request):
                return JsonResponse({
                    'status': 'error',
                    'message': subprocess_result.stderr[:5000]
                }, status=400)
            return redirect('admin_panel')
        if _is_ajax(request):
            return JsonResponse({
                'status': 'success',
                'installed': safe_pkgs,
                'output': subprocess_result.stdout[:5000]
            })
        return redirect('admin_panel')
    except Exception as e:
        if _is_ajax(request):
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        return redirect('admin_panel')


@admin_required
def admin_set_theme_color(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    color = request.POST.get('theme_color', '').strip()
    # Validate hex color #RRGGBB
    if not re.match(r'^#[0-9A-Fa-f]{6}$', color or ''):
        return JsonResponse({'status': 'error', 'message': 'Invalid color format'}, status=400)
    try:
        # Persist to DB
        settings, _ = SiteSettings.objects.get_or_create(id=1)
        settings.theme_color = color
        settings.save()
        # Redirect back to panel
        if _is_ajax(request):
            return JsonResponse({'status': 'success', 'theme_color': color})
        return redirect('admin_panel')
    except Exception as e:
        if _is_ajax(request):
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        return redirect('admin_panel')


@admin_required
def admin_set_logo_url(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    url = request.POST.get('logo_url', '').strip()
    # Allow http(s) URLs or site-relative static paths
    if not re.match(r'^(https?://[^\s]+|/static/[^\s]+)$', url or ''):
        return JsonResponse({'status': 'error', 'message': 'Invalid logo URL'}, status=400)
    try:
        settings, _ = SiteSettings.objects.get_or_create(id=1)
        settings.logo_url = url
        settings.save()
        if _is_ajax(request):
            return JsonResponse({'status': 'success', 'logo_url': url})
        return redirect('admin_panel')
    except Exception as e:
        if _is_ajax(request):
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        return redirect('admin_panel')
