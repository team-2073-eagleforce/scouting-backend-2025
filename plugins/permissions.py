"""
Plugin permissions and safe DB helper.

This module provides a small API for plugins to write data to the DB
in a namespaced way so it can be audited and cleaned up on uninstall.

Convention: store plugin contributions under JSON field key
    data['plugins'][plugin_name] = {...}
"""
from typing import Dict, Any, Optional
from django.db import transaction

class PluginDB:
    """Helper for namespaced plugin DB writes.

    Use this from plugin views to persist data safely under a namespace.
    """

    @staticmethod
    @transaction.atomic
    def set_team_match_data(plugin_name: str,
                            team_number: int,
                            event: str,
                            match_number: int,
                            scout_name: str,
                            payload: Dict[str, Any]) -> int:
        """Upsert namespaced plugin payload into Team_Match_Data.data.

        Returns affected object ID.
        Raises PermissionError if plugin is marked read_only.
        """
        from . import plugin_manager
        if plugin_manager.is_read_only(plugin_name):
            raise PermissionError(f"Plugin '{plugin_name}' is marked read-only and cannot write to DB")
        
        from teams.models import Team_Match_Data
        # Try to lock existing row for update to avoid races
        obj = (
            Team_Match_Data.objects
            .filter(team_number=team_number, event=event, match_number=match_number, scout_name=scout_name)
            .select_for_update()
            .first()
        )
        if obj is None:
            obj, _ = Team_Match_Data.objects.get_or_create(
                team_number=team_number,
                event=event,
                match_number=match_number,
                scout_name=scout_name,
                defaults={'data': {}}
            )
        data = obj.data or {}
        plugins_blob = data.get('plugins') or {}
        plugins_blob[plugin_name] = payload
        data['plugins'] = plugins_blob
        obj.data = data
        obj.save(update_fields=['data'])
        return obj.id

    @staticmethod
    @transaction.atomic
    def set_team_pit_data(plugin_name: str,
                          team_number: int,
                          event: str,
                          payload: Dict[str, Any]) -> int:
        """Upsert namespaced plugin payload into Teams.pit_data.

        Returns affected object ID.
        Raises PermissionError if plugin is marked read_only.
        """
        from . import plugin_manager
        if plugin_manager.is_read_only(plugin_name):
            raise PermissionError(f"Plugin '{plugin_name}' is marked read-only and cannot write to DB")
        
        from teams.models import Teams
        obj = (
            Teams.objects
            .filter(team_number=team_number, event=event)
            .select_for_update()
            .first()
        )
        if obj is None:
            obj, _ = Teams.objects.get_or_create(
                team_number=team_number,
                event=event,
                defaults={'pit_data': {}}
            )
        pit = obj.pit_data or {}
        plugins_blob = pit.get('plugins') or {}
        plugins_blob[plugin_name] = payload
        pit['plugins'] = plugins_blob
        obj.pit_data = pit
        obj.save(update_fields=['pit_data'])
        return obj.id

def cleanup_plugin(plugin_name: str) -> int:
    """Remove namespaced plugin entries from known JSON fields.

    Returns number of records updated.
    """
    from . import plugin_manager
    return plugin_manager.cleanup_plugin_data(plugin_name)
