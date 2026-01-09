from utils import config_loader
from authenticate.models import SiteSettings

def config_context(request):
    """Make config values available in all templates"""
    config = config_loader.get_config()
    # Fetch DB-backed settings if present
    try:
        settings = SiteSettings.objects.first()
    except Exception:
        settings = None
    return {
        'app_name': config.get('app_name', 'Scouting System'),
        'team_name': config.get('team_name', 'Team'),
        'theme_color': (settings.theme_color if settings and settings.theme_color else config.get('theme_color', '#e74c3c')),
        'logo_url': (settings.logo_url if settings and settings.logo_url else config.get('logo_url', '/static/images/EagleForceLogo.png')),
    }
