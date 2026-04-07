from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Usage: {{ mydict|get_item:key }}
    Allows dynamic dictionary lookup in templates.
    Robust: if dictionary is a JSON string, try to parse it; if it's not a mapping, return None.
    """
    if dictionary is None:
        return None
    # If someone stored JSON as a string in the DB, try to decode it
    if isinstance(dictionary, str):
        try:
            import json as _json
            dictionary = _json.loads(dictionary)
        except Exception:
            return None
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None

@register.filter
def prettify_key(value):
    """Turn snake_case keys into Title Case labels: drive_type → Drive Type"""
    return str(value).replace('_', ' ').title()

@register.filter
def format_pit_value(value):
    """Render pit data values cleanly: join lists with ', ', pass everything else through."""
    if isinstance(value, list):
        return ', '.join(str(v) for v in value) if value else '—'
    if value is None or value == '':
        return '—'
    return value
