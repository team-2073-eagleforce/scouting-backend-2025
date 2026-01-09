# Plugin Development Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Overview](#overview)
3. [Plugin Structure](#plugin-structure)
4. [Available Hooks](#available-hooks)
5. [Database Access & Permissions](#database-access--permissions)
6. [Installation & Management](#installation--management)
7. [Complete Examples](#complete-examples)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

**Create your first plugin in 3 minutes:**

1. **Create the plugin folder:**
   ```bash
   mkdir -p plugins/my_plugin
   ```

2. **Create `plugins/my_plugin/plugin.py`:**
   ```python
   class Plugin:
       name = "my_plugin"
       version = "1.0.0"
       
       def __init__(self):
           self.hooks = {
               'home_page_header': self.show_message,
           }
           self.urls = []
       
       def show_message(self, context):
           return '<div class="alert alert-info">My Plugin is Active!</div>'
   ```

3. **Enable the plugin:**
   - Go to **Admin Panel → Plugins**
   - Click **Enable** next to `my_plugin`

4. **Test it:**
   - Visit the home page (`/`) and see your message!

---

## Overview

The plugin system allows you to **extend the scouting app without modifying core code**. Plugins can:
- ✅ Add custom UI elements via template hooks
- ✅ Process QR scanner data
- ✅ Modify match data fields (with permissions)
- ✅ Store custom data in the database
- ✅ Add custom API endpoints
- ✅ Be enabled/disabled without code changes

**When to use plugins:**
- Adding team-specific features
- Custom analytics or visualizations
- Integration with external services
- Experimental features that might be removed later

---

## Plugin Structure

**Minimal structure:**
```
plugins/
└── your_plugin_name/
    └── plugin.py          # Main plugin class (REQUIRED)
```

**Full structure:**
```
plugins/
└── your_plugin_name/
    ├── plugin.py          # Main plugin class (REQUIRED)
    ├── requirements.txt   # Python dependencies (optional)
    ├── static/            # JS/CSS files (optional)
    │   └── script.js
    └── templates/         # HTML templates (optional)
        └── widget.html
```

**The Plugin class must:**
- Be named exactly `Plugin`
- Have a `name` attribute (string)
- Have a `version` attribute (string, recommended)
- Have a `description` attribute (string, recommended for user clarity)
- Have a `author` attribute (string, recommended)
- Have a `requested_permissions` dict (dict, **required for transparency**)
- Have a `hooks` dict (can be empty)
- Have a `urls` list (can be empty)

**Example minimal plugin:**
```python
class Plugin:
    name = "my_plugin"
    version = "1.0.0"
    description = "What this plugin does"
    author = "Your Name"
    
    requested_permissions = {
        "scanner_anchor_patch": [],      # List of anchor fields to modify
        "data_metrics": [],               # List of root data keys to add
        "read_only": True,                # True if plugin doesn't write to DB
        "custom_urls": False,             # True if plugin adds API endpoints
        "accesses_external_apis": False,  # True if calls external services
    }
    
    def __init__(self):
        self.hooks = {}
        self.urls = []
```

### Permission Declaration

**Always declare your plugin's permissions** using the `requested_permissions` attribute. This:
- ✅ Informs users what the plugin can do before they enable it
- ✅ Creates trust through transparency
- ✅ Helps administrators assess security risks
- ✅ Documents your plugin's capabilities

**Permission fields explained:**
- `scanner_anchor_patch`: List of match fields the plugin will modify (e.g., `["start_pos", "comment"]`)
- `data_metrics`: Legacy - list of root data keys (prefer namespaced writes)
- `read_only`: Set to `true` if plugin never writes to the database (display-only plugins)
- `custom_urls`: Set to `true` if plugin adds custom API endpoints
- `accesses_external_apis`: Set to `true` if plugin calls external services (TBA API, cloud services, etc.)

---

## Available Hooks

Hooks are **functions that run at specific points** in the app. Your plugin registers hooks to inject custom behavior.

### Hook Types

| Hook Name | Type | When It Runs | Return Type | Context Available |
|-----------|------|--------------|-------------|-------------------|
| `home_page_header` | Template | Home page load | HTML string | `request` |
| `team_page_header` | Template | Team page load | HTML string | `request`, `team` |
| `team_page_match_row` | Template | Each match row | HTML string | `request`, `match` |
| `scanner_data_process` | Data | QR code scanned | dict or None | `qr_data`, `team_number`, `event`, `match_number`, `scout_name` |
| `scanner_anchor_patch` | Data | Before match save | dict or None | `current`, `qr_data`, `team_number`, `event`, `match_number`, `scout_name` |

### Template Hooks

**Purpose:** Add HTML to specific parts of the UI

**Example - Add a banner to home page:**
```python
class Plugin:
    name = "banner_plugin"
    
    def __init__(self):
        self.hooks = {
            'home_page_header': self.add_banner,
        }
    
    def add_banner(self, context):
        # context contains: request
        return '''
        <div class="alert alert-warning">
            <strong>Notice:</strong> Playoffs start tomorrow!
        </div>
        '''
```

**Example - Add button to each match row:**
```python
def add_match_button(self, context):
    # context contains: request, match
    match = context.get('match')
    if not match:
        return ""
    
    return f'''
    <button class="btn btn-sm btn-primary" 
            onclick="alert('Match {match.match_number}')">
        Details
    </button>
    '''
```

### Data Processing Hooks

**Purpose:** Process QR scanner data and add custom fields

**Example - Extract custom field from QR code:**
```python
def process_qr_data(self, context):
    # context contains: qr_data, team_number, event, match_number, scout_name
    qr_data = context.get('qr_data', {})
    
    # Extract custom field if present
    if 'defense_rating' in qr_data:
        return {
            'defense_rating': int(qr_data['defense_rating']),
            'processed_at': datetime.now().isoformat()
        }
    
    return None  # Return None if nothing to add
```

**Where the data goes:**
- Your returned dict is stored at: `Team_Match_Data.data['plugins']['your_plugin_name']`
- Automatically namespaced to prevent conflicts
- Cleaned up when plugin is disabled (if cleanup requested)

### Anchor Field Patching Hook

**Purpose:** Modify core match fields during scan (REQUIRES PERMISSIONS)

**Available anchor fields:**
- `start_pos` (int) - Starting position
- `comment` (str) - Match comment
- `scout_name` (str) - Scout name
- `quantifier` (str) - 'Quals', 'Playoff', or 'Prac'
- `is_broken` (bool) - Robot broken flag
- `is_disabled` (bool) - Robot disabled flag
- `is_tipped` (bool) - Robot tipped flag

**Example - Modify comment and start position:**
```python
def patch_anchor_fields(self, context):
    # context contains: current, qr_data, team_number, event, match_number, scout_name
    current = context.get('current', {})
    qr = context.get('qr_data', {})
    patch = {}
    
    # Add tag to comment if present in QR
    if 'tag' in qr:
        base = current.get('comment', '')
        patch['comment'] = f"{base} [tag:{qr['tag']}]"[:256]
    
    # Override start position from QR
    if 'startPos' in qr:
        patch['start_pos'] = int(qr['startPos'])
    
    return patch  # Only whitelisted fields are applied
```

---

## Database Access & Permissions

### Overview

Plugins can write to the database in **two ways**:

1. **Automatic (recommended):** Return data from `scanner_data_process` hook → automatically namespaced
2. **Manual:** Use `PluginDB` helpers in custom endpoints → requires explicit namespacing

### Permission System

Control what each plugin can do via `plugins/config.json`:

```json
{
  "enabled": ["my_plugin", "analytics_plugin"],
  "permissions": {
    "my_plugin": {
      "scanner_anchor_patch": ["start_pos", "comment"],
      "data_metrics": [],
      "read_only": false
    },
    "analytics_plugin": {
      "scanner_anchor_patch": [],
      "data_metrics": [],
      "read_only": true
    }
  }
}
```

**Permission Fields Explained:**

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `scanner_anchor_patch` | list | Anchor fields plugin can modify | `["start_pos", "comment"]` |
| `data_metrics` | list | Root data keys plugin can add (legacy) | `["custom_metric"]` |
| `read_only` | bool | Block all DB writes if true | `true` for analytics plugins |

### Data Flow Diagram

```
QR Code Scanned
      ↓
Scanner View receives data
      ↓
Builds anchor fields (team, match, scout_name, etc.)
      ↓
Calls scanner_data_process hooks
      ↓
Your plugin returns: {'my_field': 123}
      ↓
Stored at: data['plugins']['your_plugin']['my_field'] = 123
      ↓
(Optional) Calls scanner_anchor_patch hooks
      ↓
Your plugin returns: {'comment': 'Updated comment'}
      ↓
Only whitelisted fields applied to anchor data
      ↓
Single DB save with all data
```

### Method 1: Automatic Namespacing (Recommended)

Use the `scanner_data_process` hook - **no manual DB writes needed:**

```python
class Plugin:
    name = "auto_plugin"
    
    def __init__(self):
        self.hooks = {
            'scanner_data_process': self.process_data,
        }
    
    def process_data(self, context):
        qr = context.get('qr_data', {})
        
        # Just return the data you want to store
        return {
            'custom_score': int(qr.get('custom_score', 0)),
            'notes': qr.get('notes', ''),
        }
        # This automatically goes to:
        # Team_Match_Data.data['plugins']['auto_plugin']
```

**Benefits:**
- ✅ No manual DB code needed
- ✅ Automatically namespaced (no conflicts)
- ✅ Cleaned up when plugin disabled (if requested)
- ✅ Thread-safe (scanner handles the save)

### Method 2: Manual DB Writes

For custom endpoints that need to write data:

```python
from django.urls import path
from django.http import JsonResponse
from plugins.permissions import PluginDB
from datetime import datetime

class Plugin:
    name = "manual_plugin"
    
    def __init__(self):
        self.urls = [
            path('plugins/manual/save/', self.save_data, name='manual_save'),
        ]
    
    def save_data(self, request):
        # Get parameters
        team = int(request.POST.get('team'))
        event = request.POST.get('event')
        match = int(request.POST.get('match'))
        scout = request.POST.get('scout')
        
        payload = {
            'custom_field': request.POST.get('value'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Use helper to write namespaced data
        try:
            obj_id = PluginDB.set_team_match_data(
                plugin_name='manual_plugin',
                team_number=team,
                event=event,
                match_number=match,
                scout_name=scout,
                payload=payload
            )
            return JsonResponse({'status': 'success', 'id': obj_id})
        except PermissionError as e:
            return JsonResponse({'error': str(e)}, status=403)
```

**Available helpers:**

```python
from plugins.permissions import PluginDB

# Write to match data
PluginDB.set_team_match_data(
    plugin_name='your_plugin',
    team_number=1234,
    event='2025cada',
    match_number=5,
    scout_name='Alice',
    payload={'key': 'value'}
)

# Write to pit data
PluginDB.set_team_pit_data(
    plugin_name='your_plugin',
    team_number=1234,
    event='2025cada',
    payload={'pit_notes': 'Great robot'}
)
```

### Anchor Field Permissions

To modify **core match fields** (not just custom data):

**1. Configure permissions in `plugins/config.json`:**
```json
{
  "enabled": ["field_patcher"],
  "permissions": {
    "field_patcher": {
      "scanner_anchor_patch": ["start_pos", "comment"]
    }
  }
}
```

**2. Implement the hook:**
```python
def patch_anchor_fields(self, context):
    current = context.get('current', {})
    qr = context.get('qr_data', {})
    
    patch = {}
    if 'override_start' in qr:
        patch['start_pos'] = int(qr['override_start'])
    
    if 'add_note' in qr:
        patch['comment'] = current.get('comment', '') + f" | {qr['add_note']}"
    
    return patch
```

**Security features:**
- ✅ Only fields in your permission list are applied
- ✅ Type validation enforced (`int`, `str`, `bool`)
- ✅ All changes audit-logged
- ✅ Invalid values ignored

### Data Cleanup

When disabling a plugin, you can optionally remove its data:

**Via Admin Panel:**
1. Go to Plugins section
2. Check "Cleanup data on disable"
3. Click Disable
4. See count of cleaned records in confirmation

**Programmatically:**
```python
from plugins import plugin_manager
cleaned = plugin_manager.cleanup_plugin_data('your_plugin')
print(f"Cleaned {cleaned} records")
```

**What gets cleaned:**
- Data at `Team_Match_Data.data['plugins']['your_plugin']`
- Data at `Teams.pit_data['plugins']['your_plugin']`

**What stays:**
- Other plugins' data (untouched)
- Core anchor fields (untouched)
- Rows themselves (only your namespace is removed)

### Concurrency & Thread Safety

**Built-in protections:**
- All `PluginDB` helpers use `transaction.atomic`
- Existing rows locked with `select_for_update()` before update
- Scanner processes all plugins then saves once (no race between plugins)
- Cleanup locks rows during removal

**Best practices:**
- Keep transactions short
- Only merge your namespace, don't overwrite entire JSON
- For high-traffic endpoints, add retry logic
- Check plugin enabled status before writes if needed

---

## Installation & Management

### Option A: Admin Panel (Recommended)

1. **Package your plugin:**
   ```bash
   cd plugins
   zip -r my_plugin.zip my_plugin/
   ```

2. **Upload:**
   - Go to Admin Panel → Plugins
   - Click "Choose File" and select `my_plugin.zip`
   - Click "Upload Plugin"

3. **Install dependencies (if needed):**
   - If your plugin has `requirements.txt`
   - Click "Install Dependencies" button

4. **Enable:**
   - Click "Enable" button next to your plugin

### Option B: Manual Installation

1. **Copy plugin folder:**
   ```bash
   cp -r my_plugin plugins/
   ```

2. **Edit config (optional):**
   ```bash
   nano plugins/config.json
   ```
   Add your plugin to `enabled` list

3. **Restart server:**
   ```bash
   python manage.py runserver
   ```

### Managing Dependencies

If your plugin needs extra Python packages:

1. **Create `requirements.txt` in your plugin folder:**
   ```
   requests>=2.28.0
   pandas>=1.5.0
   ```

2. **Install via Admin Panel:**
   - Click "Install Dependencies" next to your plugin

3. **Or install manually:**
   ```bash
   pip install -r plugins/my_plugin/requirements.txt
   ```

---

## Complete Examples

### Example 1: Defense Rating Tracker

**Goal:** Add custom defense rating field from QR codes

```python
# plugins/defense_tracker/plugin.py

class Plugin:
    name = "defense_tracker"
    version = "1.0.0"
    
    def __init__(self):
        self.hooks = {
            'scanner_data_process': self.track_defense,
            'team_page_match_row': self.show_rating,
        }
        self.urls = []
    
    def track_defense(self, context):
        """Extract defense rating from QR code"""
        qr = context.get('qr_data', {})
        
        if 'defense_rating' in qr:
            try:
                rating = int(qr['defense_rating'])
                if 1 <= rating <= 5:
                    return {'defense_rating': rating}
            except (ValueError, TypeError):
                pass
        
        return None
    
    def show_rating(self, context):
        """Display defense rating in match row"""
        match = context.get('match')
        if not match:
            return ""
        
        rating = match.data.get('plugins', {}).get('defense_tracker', {}).get('defense_rating')
        if not rating:
            return ""
        
        stars = '★' * rating + '☆' * (5 - rating)
        return f'<span title="Defense: {rating}/5">{stars}</span>'
```

**Enable it:**
```json
{
  "enabled": ["defense_tracker"]
}
```

### Example 2: Auto-Commenter

**Goal:** Automatically add tags to comments based on QR data

**Config - Set permissions:**
```json
{
  "enabled": ["auto_commenter"],
  "permissions": {
    "auto_commenter": {
      "scanner_anchor_patch": ["comment"]
    }
  }
}
```

**Plugin code:**
```python
# plugins/auto_commenter/plugin.py

class Plugin:
    name = "auto_commenter"
    version = "1.0.0"
    
    def __init__(self):
        self.hooks = {
            'scanner_anchor_patch': self.add_tags,
        }
        self.urls = []
    
    def add_tags(self, context):
        """Add automatic tags to comments"""
        current = context.get('current', {})
        qr = context.get('qr_data', {})
        
        base_comment = current.get('comment', '')
        tags = []
        
        # Add tags based on QR data
        if qr.get('played_defense') == '1':
            tags.append('DEFENSE')
        
        if qr.get('tipped') == '1':
            tags.append('TIPPED')
        
        if int(qr.get('auto_points', 0)) > 10:
            tags.append('STRONG_AUTO')
        
        if tags:
            tag_str = ' | '.join(tags)
            new_comment = f"{base_comment} [{tag_str}]"[:256]
            return {'comment': new_comment}
        
        return None
```

### Example 3: Custom API Endpoint

**Goal:** Create a custom analytics endpoint

```python
# plugins/analytics_api/plugin.py

from django.urls import path
from django.http import JsonResponse
from teams.models import Team_Match_Data

class Plugin:
    name = "analytics_api"
    version = "1.0.0"
    
    def __init__(self):
        self.hooks = {}
        self.urls = [
            path('plugins/analytics/team/<int:team_num>/', 
                 self.team_stats, 
                 name='analytics_team_stats'),
        ]
    
    def team_stats(self, request, team_num):
        """Return custom analytics for a team"""
        event = request.GET.get('event', 'testing')
        
        matches = Team_Match_Data.objects.filter(
            team_number=team_num,
            event=event
        )
        
        if not matches.exists():
            return JsonResponse({'error': 'No data'}, status=404)
        
        # Calculate custom stats
        total_matches = matches.count()
        avg_auto = sum(m.data.get('auto_points', 0) for m in matches) / total_matches
        
        return JsonResponse({
            'team': team_num,
            'event': event,
            'matches_played': total_matches,
            'avg_auto_points': round(avg_auto, 2),
        })
```

**Use it:**
```
GET /plugins/analytics/team/1234/?event=2025cada
```

---

## Best Practices

### 1. Naming Conventions
- Plugin name: lowercase with underscores (`my_plugin`)
- URL prefix: `plugins/your-plugin/`
- Template IDs: `your-plugin-element-id`

### 2. Error Handling
```python
def your_hook(self, context):
    try:
        # Your logic
        return result
    except Exception as e:
        # Log but don't crash
        print(f"Error in {self.name}: {e}")
        return None  # or "" for template hooks
```

### 3. Data Storage
- **Always use namespaced keys** via `scanner_data_process` hook or `PluginDB` helpers
- Don't write directly to models in hooks
- Keep payload sizes reasonable (<1KB recommended)

### 4. Performance
- Template hooks should return quickly (<50ms)
- Avoid heavy computation in hooks
- Cache expensive calculations
- Use database indexes for custom queries

### 5. Security
- Validate all user input
- Escape HTML in template returns
- Use Django's template system for complex HTML
- Don't expose sensitive data in templates

### 6. Testing
```python
# Test your hook locally
plugin = Plugin()
context = {'qr_data': {'test': '123'}}
result = plugin.process_data(context)
print(result)  # Should return your expected data
```

---

## Plugin Security & Review

### For Plugin Developers

**Be transparent about what your plugin does:**
1. Declare all permissions accurately in `requested_permissions`
2. Document external API calls and data collection
3. Use descriptive names and clear descriptions
4. Provide source code or detailed documentation
5. Test thoroughly before distributing

**Security best practices:**
- Never store API keys or passwords in plugin code
- Validate and sanitize all user input
- Use Django's built-in security features
- Limit network requests to necessary operations only
- Use HTTPS for external API calls

### For System Administrators

**Before installing a plugin:**
1. **Review permissions** displayed during upload
2. **Check source code** if available (look for suspicious patterns)
3. **Verify author** - is this from a trusted source?
4. **Test in development** before deploying to production
5. **Monitor behavior** after enabling - check logs for unexpected activity

**Red flags to watch for:**
- Requests excessive permissions (modifying many anchor fields)
- Accesses external APIs without clear justification
- Obfuscated or difficult-to-read code
- No description or author information
- Asks for permissions it doesn't seem to need

**Permission safety levels:**

| Permission | Risk Level | Notes |
|------------|-----------|-------|
| `read_only: true` | ✅ Low | Cannot modify data |
| Display-only hooks | ✅ Low | Just adds UI elements |
| `scanner_data_process` | ⚠️ Medium | Adds namespaced data (easy to clean) |
| `scanner_anchor_patch` | 🔴 High | Modifies core match fields |
| `custom_urls: true` | ⚠️ Medium | Adds API endpoints (review code) |
| `accesses_external_apis: true` | 🔴 High | May leak data externally |

### Reviewing During Upload

When you upload a plugin, the system automatically shows:
- Plugin name, version, author, description
- All requested permissions with warnings
- Whether it has custom API endpoints
- Whether it requires additional dependencies
- Whether it accesses external APIs

**The plugin is uploaded but DISABLED by default** - you must manually enable it after review.

---

## Troubleshooting

### Plugin not showing up

**Check:**
1. Is plugin folder in `plugins/`?
2. Does it have `plugin.py` with a `Plugin` class?
3. Is it enabled in `plugins/config.json`?
4. Did you restart the server after adding it?

**Debug:**
```bash
# Check if plugin is discovered
python manage.py shell
>>> from plugins import plugin_manager
>>> plugin_manager.list_available_plugins()
['your_plugin', 'hello_world', ...]

>>> plugin_manager._enabled_names
['your_plugin', ...]  # Should include your plugin
```

### Hook not executing

**Check:**
1. Is hook name spelled correctly?
2. Is hook function registered in `self.hooks` dict?
3. Does function return correct type (str for templates, dict for data)?

**Debug:**
```python
# In your hook
def your_hook(self, context):
    print(f"HOOK CALLED: {context}")  # Should appear in server logs
    return result
```

### Permission errors

**Check:**
1. Is plugin name in `permissions` section of `config.json`?
2. Are field names spelled correctly?
3. For `read_only=true`, remove DB write calls

**Debug:**
```python
>>> from plugins import plugin_manager
>>> plugin_manager.get_anchor_patch_fields('your_plugin')
['start_pos', 'comment']  # Should show your allowed fields
```

### Data not being saved

**Check:**
1. Hook returns a dict (not None)?
2. Data structure is JSON-serializable?
3. For anchor patches, fields are in permissions whitelist?

**Debug:**
```python
# Check saved data
>>> from teams.models import Team_Match_Data
>>> match = Team_Match_Data.objects.first()
>>> match.data.get('plugins', {}).get('your_plugin')
{'your_field': 'value'}  # Your data should be here
```

### Dependencies not installing

**Check:**
1. Is `requirements.txt` in plugin folder root?
2. Are package names valid?
3. Does server have internet access?

**Manual install:**
```bash
pip install -r plugins/your_plugin/requirements.txt
```

---

## Additional Resources

- **Example plugin:** See `plugins/hello_world/` for a working example
- **Template plugin:** See `plugins/example_plugin_template.py` for comprehensive template
- **Models:** See `teams/models.py` for data structure
- **Config validation:** See `scanner/validation.py` for field types

**Need help?** Check the server logs for detailed error messages:
```bash
tail -f logs/django.log  # Or wherever your logs are
```
