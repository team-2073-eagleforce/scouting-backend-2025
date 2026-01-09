"""
Hello World Demo Plugin
Displays a banner on the home page via a template hook.
"""

class Plugin:
    name = "hello_world"
    version = "1.0.0"
    description = "Simple demo plugin that displays a banner on the home page"
    author = "Scouting System"
    
    # Declare permissions - this plugin is read-only and safe
    requested_permissions = {
        "scanner_anchor_patch": [],  # Does not modify match fields
        "data_metrics": [],           # Does not add custom data
        "read_only": True,            # Read-only, no DB writes
        "custom_urls": False,         # No custom API endpoints
        "accesses_external_apis": False,  # No external API calls
    }

    def __init__(self):
        self.hooks = {
            'home_page_header': self.banner,
        }
        self.urls = []

    def banner(self, context):
        return (
            '<div class="alert alert-success" role="alert" '
            'style="max-width:800px;margin:10px auto">'
            'Hello World!'
            '</div>'
        )
