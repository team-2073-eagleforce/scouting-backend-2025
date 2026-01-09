# Plugin Development Guide

## Overview

The plugin system allows you to extend the scouting app without modifying core code.

## Plugin Structure

```
plugins/
└── your_plugin_name/
    ├── plugin.py          # Main plugin class (required)
    ├── static/            # JS/CSS files (optional)
    └── templates/         # HTML templates (optional)
```

## Basic Plugin Template

```python
# plugins/your_plugin_name/plugin.py

from django.urls import path
from django.http import JsonResponse

class Plugin:
    """Your plugin description"""
    
    name = "your_plugin_name"
    version = "1.0.0"
    
    def __init__(self):
        # Register hooks
        self.hooks = {
            'hook_name': self.your_hook_function,
        }
        
        # Register URL routes (optional)
        self.urls = [
            path('plugins/your-plugin/endpoint/', self.your_view, name='your_plugin_endpoint'),
        ]
    
    def your_hook_function(self, context):
        """Hook function that returns HTML or data"""
        return "<div>Your custom HTML</div>"
    
    def your_view(self, request):
        """Custom API endpoint"""
        return JsonResponse({'status': 'success'})
```

## Available Hooks

### Template Hooks (return HTML string)
- `team_page_header` — Top of team page
- `team_page_match_row` — Each match row (context includes `match`)
- `home_page_header` — Top of the home page content

### Data Hooks (return dict or None)
- `scanner_data_process` — Process QR code (context includes `qr_data`, identifiers)

## Using Hooks in Templates

```html
{% load plugin_tags %}

<!-- In your template -->
{% plugin_hook 'team_page_header' %}
```

## Example: Match Replay Plugin

```python
class Plugin:
    name = "match_replay"
    
    def __init__(self):
        self.hooks = {
            'team_page_match_row': self.add_replay_button,
        }
        
        self.urls = [
            path('plugins/replay/set/', self.set_replay_link),
        ]
    
    def add_replay_button(self, context):
        match = context.get('match')
        replay_url = match.data.get('replay_url', '')
        
        return f'''
        <button onclick="window.open('{replay_url}')">
            Watch Replay
        </button>
        '''
    
    def set_replay_link(self, request):
        # Save replay URL to match data
        pass
```

## Plugin Installation & Management

Option A: Admin Panel
- Go to Admin Panel → Plugins
- Upload a `.zip` containing your plugin folder (top-level directory, with `plugin.py` inside)
- Enable the plugin in the list

Option B: Manual
- Create folder in `plugins/`
- Add `plugin.py` with a `Plugin` class
- Remove `plugins/config.json` or add your plugin name to its `enabled` list
- Restart the server

## Best Practices

- Use the `data` JSONField in models for custom data
- Prefix all URLs with `plugins/your-plugin/`
- Handle errors gracefully (hooks should never crash)
- Return empty string from template hooks if no content
- Validate and sanitize any user-provided content before rendering

## Quick Start: Hello World Plugin

This demo plugin shows a banner on the home page using the `home_page_header` hook.

1) Files
- `plugins/hello_world/plugin.py`:

```python
class Plugin:
        name = "hello_world"
        version = "1.0.0"

        def __init__(self):
                self.hooks = {
                        'home_page_header': self.banner,
                }
                self.urls = []

        def banner(self, context):
                return '<div class="alert alert-success">Hello World!</div>'
```

2) Injection Point
- The app injects `home_page_header` automatically on the home page via middleware; you do not need to edit `home.html`.

3) Enable
- In Admin Panel → Plugins, enable `hello_world` if not already active.
    - Or add to `plugins/config.json` under `enabled`.

4) Verify
- Visit `/` and the banner displays at the top of the page.
