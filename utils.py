import json
import os
from pathlib import Path
from threading import Lock

class ConfigLoader:
    """Smart cache for game_config.json with hot-reload capability"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._config = None
                    cls._instance._last_modified = None
        return cls._instance
    
    def _get_config_path(self):
        return Path(__file__).resolve().parent / 'game_config.json'
    
    def _load_config(self):
        """Load config from file"""
        config_path = self._get_config_path()
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def get_config(self):
        """Get config with hot-reload check"""
        config_path = self._get_config_path()
        
        if not config_path.exists():
            raise FileNotFoundError(f"game_config.json not found at {config_path}")
        
        current_modified = os.path.getmtime(config_path)
        
        # First load or file changed
        if self._config is None or self._last_modified != current_modified:
            self._config = self._load_config()
            self._last_modified = current_modified
        
        return self._config
    
    def validate_data(self, data, metric_key):
        """Validate incoming data against config schema"""
        config = self.get_config()
        
        # Find metric definition
        metric = next((m for m in config['metrics'] if m['key'] == metric_key), None)
        if not metric:
            return True, None  # Unknown metrics pass through
        
        value = data.get(metric_key)
        if value is None or value == "":
            return True, None  # Allow empty values
        
        # Type validation
        if metric['type'] == 'number':
            try:
                value = float(value)
                if 'min' in metric and value < metric['min']:
                    return False, f"{metric_key} below minimum ({metric['min']})"
                if 'max' in metric and value > metric['max']:
                    return False, f"{metric_key} above maximum ({metric['max']})"
            except (ValueError, TypeError):
                return False, f"{metric_key} must be a number"
        
        elif metric['type'] == 'boolean':
            if not isinstance(value, bool) and value not in [0, 1, '0', '1', 'true', 'false']:
                return False, f"{metric_key} must be boolean"
        
        return True, None

# Singleton instance
config_loader = ConfigLoader()
