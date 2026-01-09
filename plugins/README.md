# Plugins

This directory hosts drop-in plugin packages to extend the scouting app without touching core code.

How it works:
- Each plugin lives in a subfolder: `plugins/<your_plugin>/`.
- Inside the folder, implement `plugin.py` defining a `Plugin` class.
- Plugins can expose template hooks, data processing hooks, and custom URL endpoints.

Hooks available:
- `team_page_header`: return HTML to render at the top of the team page.
- `team_page_match_row`: return HTML for each match row; the context contains `match`.
- `scanner_data_process`: receive QR JSON and return a dict to merge into stored `data`.

Enable/disable:
- Admins can manage plugins in the Admin Panel (Plugins section): upload `.zip`, enable or disable.
- Configuration is stored in `plugins/config.json`. If `enabled` is empty, all plugins are disabled. If the file is deleted or `enabled` is omitted, all plugins are enabled.

Minimal example (`plugins/replay_link/plugin.py`):

```python
from django.urls import path

class Plugin:
	name = "replay_link"
	version = "1.0.0"

	def __init__(self):
		self.hooks = {
			'team_page_match_row': self.row_button,
			'scanner_data_process': self.capture_replay_id,
		}
		self.urls = []

	def row_button(self, context):
		match = context.get('match')
		link = (match.data or {}).get('replay_url')
		if not link:
			return ""
		return f'<a class="btn btn-sm btn-secondary" target="_blank" href="{link}">Replay</a>'

	def capture_replay_id(self, context):
		qr = context.get('qr_data', {})
		url = qr.get('replay_url')
		return {'replay_url': url} if url else None
```

Packaging a plugin:
- Zip the plugin folder (top-level must be the plugin directory), e.g. `replay_link/` containing `plugin.py`.
- Upload via Admin Panel → Plugins → Upload.

Dependencies:
- If your plugin needs extra packages, add `requirements.txt` inside the plugin folder with lines like `requests==2.31.0`.
- Admins can install them per plugin from the Admin Panel (Install Dependencies button).
- For security, only simple pinned specs are allowed (e.g., `pkg`, `pkg==x.y`, `pkg>=x`, `pkg<=x`, `pkg~=x`). URLs, editable installs, and options are blocked.

Notes:
- Plugins run in-process and have full access to Django; only install code you trust.
- Handle errors gracefully in hooks; returning `None` skips output.
