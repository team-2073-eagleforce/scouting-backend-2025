from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Usage: {{ mydict|get_item:key }}
    Allows dynamic dictionary lookup in templates.
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
