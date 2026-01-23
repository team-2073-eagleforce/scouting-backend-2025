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
