"""
Plugin System for FRC Scouting
Allows dynamic loading of custom features without modifying core code.

Improvements:
- Enable/disable plugins via config file
- Safer logging instead of prints
- Utility methods for discovery and reload
- Error isolation for hooks
"""
import importlib
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from django.utils.safestring import mark_safe

class PluginManager:
    """Singleton manager for loading and executing plugins"""

    _instance: Optional["PluginManager"] = None
    _plugins: Dict[str, Any] = {}
    _hooks: Dict[str, List] = {}
    _enabled_names: Optional[List[str]] = None
    _permissions: Dict[str, Any] = {}
    _logger = logging.getLogger("plugins")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_enabled_config()
            cls._instance._load_plugins()
        return cls._instance

    @property
    def plugins_dir(self) -> Path:
        return Path(__file__).parent

    @property
    def config_path(self) -> Path:
        return self.plugins_dir / "config.json"

    def _load_enabled_config(self) -> None:
        """Load list of enabled plugin names from config.json (optional)."""
        try:
            if self.config_path.exists():
                data = json.loads(self.config_path.read_text())
                enabled = data.get("enabled")
                if isinstance(enabled, list):
                    # Normalize names
                    self._enabled_names = [str(n).strip() for n in enabled if n]
                else:
                    self._enabled_names = None
                perms = data.get("permissions")
                if isinstance(perms, dict):
                    self._permissions = perms
                else:
                    self._permissions = {}
            else:
                self._enabled_names = None
                self._permissions = {}
        except Exception as e:
            self._logger.warning("Failed to read plugin config: %s", e)
            self._enabled_names = None
            self._permissions = {}

    def _is_enabled(self, name: str) -> bool:
        if self._enabled_names is None:
            return True
        return name in self._enabled_names

    def _register_hooks(self, plugin_instance: Any) -> None:
        """Register hook functions exposed by a plugin instance.

        Stores metadata so callers can attribute results to a plugin when needed.
        """
        hooks = getattr(plugin_instance, "hooks", None)
        if not isinstance(hooks, dict):
            return
        for hook_name, hook_func in hooks.items():
            if hook_name not in self._hooks:
                self._hooks[hook_name] = []
            # Store dict with metadata but keep backward compatibility for execute_hook
            self._hooks[hook_name].append({
                'plugin': getattr(plugin_instance, 'name', 'unknown'),
                'func': hook_func,
            })

    def _load_plugins(self) -> None:
        """Discover and load all enabled plugins from plugins/ directory."""
        self._plugins.clear()
        self._hooks.clear()

        for item in self.plugins_dir.iterdir():
            if not (item.is_dir() and not item.name.startswith("_")):
                continue
            if not self._is_enabled(item.name):
                self._logger.info("Plugin disabled: %s", item.name)
                continue
            try:
                plugin_module = importlib.import_module(f"plugins.{item.name}.plugin")
                if hasattr(plugin_module, "Plugin"):
                    plugin_instance = plugin_module.Plugin()
                    self._plugins[item.name] = plugin_instance
                    self._register_hooks(plugin_instance)
                    self._logger.info("Loaded plugin: %s", item.name)
            except Exception as e:
                self._logger.error("Failed to load plugin %s: %s", item.name, e)
    
    def execute_hook(self, hook_name: str, context: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Execute all registered hooks for a given hook point.

        Returns a list of results produced by hooks.
        """
        if hook_name not in self._hooks:
            return []
        ctx = context or {}
        results: List[Any] = []
        for entry in self._hooks[hook_name]:
            hook_func = entry['func'] if isinstance(entry, dict) else entry
            try:
                result = hook_func(ctx)
                if result is not None:
                    results.append(result)
            except Exception as e:
                self._logger.error("Hook '%s' error in %s: %s", hook_name, getattr(hook_func, "__qualname__", hook_func), e)
        return results

    def execute_hook_with_meta(self, hook_name: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute hooks and include plugin metadata with each result.

        Returns list of {'plugin': name, 'result': value} dicts.
        """
        if hook_name not in self._hooks:
            return []
        ctx = context or {}
        outputs: List[Dict[str, Any]] = []
        for entry in self._hooks[hook_name]:
            plugin_name = entry['plugin'] if isinstance(entry, dict) else 'unknown'
            hook_func = entry['func'] if isinstance(entry, dict) else entry
            try:
                result = hook_func(ctx)
                if result is not None:
                    outputs.append({'plugin': plugin_name, 'result': result})
            except Exception as e:
                self._logger.error("Hook '%s' error in %s: %s", hook_name, getattr(hook_func, "__qualname__", hook_func), e)
        return outputs
    
    def get_plugin_urls(self):
        """Collect URL patterns from all plugins"""
        url_patterns = []
        for plugin_name, plugin in self._plugins.items():
            urls = getattr(plugin, "urls", None)
            if urls:
                for url_pattern in urls:
                    url_patterns.append(url_pattern)
        return url_patterns
    
    def render_template_hook(self, hook_name: str, context: Dict[str, Any]):
        """Render HTML from template hooks.

        Concatenates string-like results. Non-string results are ignored.
        """
        rendered: List[str] = []
        for res in self.execute_hook(hook_name, context):
            if isinstance(res, str):
                rendered.append(res)
        return mark_safe("".join(rendered))

    def list_available_plugins(self) -> List[str]:
        """Return all plugin package directory names (including disabled)."""
        names: List[str] = []
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                names.append(item.name)
        return sorted(names)

    def reload(self) -> None:
        """Reload enabled config and re-import plugins."""
        self._load_enabled_config()
        self._load_plugins()

    def cleanup_plugin_data(self, plugin_name: str) -> int:
        """Remove namespaced JSON entries for a plugin from known models.

        Returns number of records updated.
        """
        try:
            from django.db import transaction
            from teams.models import Teams, Team_Match_Data
        except Exception:
            # Models may not be ready in certain contexts
            return 0

        updated = 0
        # Remove under 'plugins'[plugin_name] convention
        with transaction.atomic():
            for model, field in ((Teams, 'pit_data'), (Team_Match_Data, 'data')):
                # Lock rows as they are processed to avoid concurrent writes
                for obj in model.objects.select_for_update().only('id', field):
                    data = getattr(obj, field) or {}
                    plugins_blob = data.get('plugins')
                    if isinstance(plugins_blob, dict) and plugin_name in plugins_blob:
                        try:
                            plugins_blob.pop(plugin_name, None)
                            data['plugins'] = plugins_blob
                            setattr(obj, field, data)
                            obj.save(update_fields=[field])
                            updated += 1
                        except Exception:
                            continue
        return updated

    def get_anchor_patch_fields(self, plugin_name: str) -> List[str]:
        """Return allowed anchor fields a plugin may patch during scan.

        Reads from config.json → permissions[plugin]['scanner_anchor_patch'].
        """
        try:
            entries = self._permissions.get(plugin_name, {})
            fields = entries.get('scanner_anchor_patch', [])
            if isinstance(fields, list):
                return [str(f) for f in fields if f]
        except Exception:
            pass
        return []

    def is_read_only(self, plugin_name: str) -> bool:
        """Check if plugin is marked read-only (cannot write to DB).

        Reads from config.json → permissions[plugin]['read_only'].
        """
        try:
            entries = self._permissions.get(plugin_name, {})
            return bool(entries.get('read_only', False))
        except Exception:
            pass
        return False

    def get_data_metrics(self, plugin_name: str) -> List[str]:
        """Return allowed root-level data keys plugin may add.

        Reads from config.json → permissions[plugin]['data_metrics'].
        Use sparingly; prefer namespaced writes.
        """
        try:
            entries = self._permissions.get(plugin_name, {})
            metrics = entries.get('data_metrics', [])
            if isinstance(metrics, list):
                return [str(m) for m in metrics if m]
        except Exception:
            pass
        return []

# Singleton instance
plugin_manager = PluginManager()
