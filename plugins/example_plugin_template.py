"""
Example Plugin Template
Copy this to plugins/your_plugin_name/plugin.py and customize
"""
from django.urls import path
from django.http import JsonResponse

class Plugin:
    """Example plugin showing all features"""
    
    name = "example_plugin"
    version = "1.0.0"
    description = "Example plugin demonstrating all available features"
    author = "Your Name"
    
    # Declare what permissions this plugin needs
    requested_permissions = {
        "scanner_anchor_patch": ["start_pos", "comment"],
        "data_metrics": [],
        "read_only": False,
        "custom_urls": True,
        "accesses_external_apis": False,
    }
    
    def __init__(self):
        # Register hooks - functions called at specific points
        self.hooks = {
            # Template hooks - return HTML strings
            'team_page_header': self.add_header,
            'team_page_match_row': self.add_match_button,
            
            # Data hooks - return dict or None
            'scanner_data_process': self.process_qr_data,
            # Controlled patch to anchor fields (requires config permission)
            'scanner_anchor_patch': self.patch_anchor_fields,
        }
        
        # Register custom URL endpoints (optional)
        self.urls = [
            path('plugins/example/api/', self.api_endpoint, name='example_api'),
        ]
    
    def add_header(self, context):
        """Add content to team page header"""
        return '<div class="alert alert-info">Example Plugin Active</div>'
    
    def add_match_button(self, context):
        """Add button to each match row"""
        match = context.get('match')
        if not match:
            return ""
        
        return f'''
        <button class="btn btn-sm btn-primary" 
                onclick="alert('Match {match.match_number}')">
            Custom Action
        </button>
        '''
    
    def process_qr_data(self, context):
        """Process additional data from QR codes"""
        qr_data = context.get('qr_data', {})
        
        # Example: Extract custom field from QR code
        if 'custom_field' in qr_data:
            return {'custom_field': qr_data['custom_field']}
        
        return None

    def patch_anchor_fields(self, context):
        """Optionally patch allowed anchor fields during scan.
        Only fields whitelisted in config permissions will be applied.
        """
        current = context.get('current', {})
        qr = context.get('qr_data', {})
        patch = {}
        # Example: ensure comment includes a tag
        base_comment = current.get('comment', '')
        if 'tag' in qr:
            patch['comment'] = f"{base_comment} [tag:{qr['tag']}]"[:256]
        # Example: set start position if present in QR
        if 'startPos' in qr:
            try:
                patch['start_pos'] = int(qr['startPos'])
            except Exception:  # nosec B110
                pass
        return patch or None
    
    def api_endpoint(self, request):
        """Custom API endpoint"""
        return JsonResponse({
            'status': 'success',
            'plugin': self.name,
            'version': self.version
        })

# Dependencies
# If your plugin requires extra packages, create a requirements.txt in this folder.
# Admins can install them via Admin Panel → Plugins → Install Dependencies.
