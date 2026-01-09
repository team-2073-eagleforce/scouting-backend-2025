from django import template

try:
    from plugins import plugin_manager
    PLUGINS_AVAILABLE = True
except ImportError:
    PLUGINS_AVAILABLE = False

register = template.Library()

@register.simple_tag(takes_context=True)
def plugin_hook(context, hook_name):
    """Render plugin content at specified hook point"""
    if not PLUGINS_AVAILABLE:
        return ""
    return plugin_manager.render_template_hook(hook_name, context)
