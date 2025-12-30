from utils import config_loader

def config_context(request):
    """Make config values available in all templates"""
    config = config_loader.get_config()
    return {
        'app_name': config.get('app_name', 'Scouting System'),
        'team_name': config.get('team_name', 'Team'),
    }
