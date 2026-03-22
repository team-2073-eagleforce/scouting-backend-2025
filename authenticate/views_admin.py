from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from authenticate.models import AuthorizedUser
from teams.models import Team_Match_Data
from django.db.models import Count
import json
from pathlib import Path
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
        if not AuthorizedUser.objects.filter(email=email).exists():
            return HttpResponseRedirect('/auth/unauthorized/')
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
        metadata = _extract_plugin_info(plugins_dir / name)
        plugin_info.append({
            'name': name,
            'enabled': is_enabled,
            'has_requirements': has_req,
            'version': metadata.get('version', ''),
            'description': metadata.get('description', ''),
            'author': metadata.get('author', ''),
            'requested_permissions': metadata.get('requested_permissions', {}),
            'has_custom_urls': metadata.get('has_custom_urls', False),
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
        email = request.POST.get('email', '').strip().lower()
        if email:
            try:
                validate_email(email)
                AuthorizedUser.objects.get_or_create(email=email)
            except ValidationError:
                pass  # silently reject malformed addresses
    return redirect('/admin-panel/')

@admin_required
@require_POST
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
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def plugins_enable(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    name = request.POST.get('name')
    enable = request.POST.get('enable') == 'true'
    cleanup_requested = request.POST.get('cleanup') == 'true'
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
    cleanup_count = 0
    # If disabling and cleanup requested, remove namespaced plugin data
    if not enable and cleanup_requested:
        try:
            cleanup_count = plugin_manager.cleanup_plugin_data(name)
        except Exception:
            cleanup_count = 0
    if _is_ajax(request):
        return JsonResponse({'status': 'success', 'enabled': enabled, 'cleanup_updated': cleanup_count})
    return redirect('admin_panel')


def _extract_plugin_info(plugin_dir: Path) -> dict:
    """Extract metadata and permission requests from a plugin.
    
    Returns dict with name, version, description, author, and requested_permissions.
    """
    info = {
        'name': plugin_dir.name,
        'version': 'unknown',
        'description': '',
        'author': '',
        'requested_permissions': {},
        'has_custom_urls': False,
        'has_requirements': False,
    }
    
    plugin_file = plugin_dir / 'plugin.py'
    if not plugin_file.exists():
        return info
    
    try:
        # Read plugin.py and extract class attributes
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"temp_plugin_{plugin_dir.name}", plugin_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'Plugin'):
                plugin_class = module.Plugin
                info['version'] = getattr(plugin_class, 'version', 'unknown')
                info['description'] = getattr(plugin_class, 'description', '')
                info['author'] = getattr(plugin_class, 'author', '')
                info['requested_permissions'] = getattr(plugin_class, 'requested_permissions', {})
                
                # Check if plugin has URLs
                try:
                    instance = plugin_class()
                    info['has_custom_urls'] = bool(getattr(instance, 'urls', []))
                except Exception:  # nosec B110
                    pass
    except Exception as e:  # nosec B110
        # If we can't load it, that's okay - just return basic info
        pass
    
    # Check for requirements.txt
    info['has_requirements'] = (plugin_dir / 'requirements.txt').exists()
    
    return info


@admin_required
def plugins_upload(request):
    # Plugin uploads are disabled for security - plugins must be installed manually on the server.
    return JsonResponse({'status': 'error', 'message': 'Plugin uploads are disabled. Install plugins manually on the server.'}, status=403)


@admin_required
def plugins_install_deps(request):
    # Dependency installation via UI is disabled for security - install dependencies manually on the server.
    return JsonResponse({'status': 'error', 'message': 'Dependency installation is disabled. Install dependencies manually on the server.'}, status=403)


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
    except Exception:
        if _is_ajax(request):
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'}, status=400)
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
    except Exception:
        if _is_ajax(request):
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'}, status=400)
        return redirect('admin_panel')
