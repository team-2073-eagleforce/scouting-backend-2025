import re
from typing import Optional

from django.utils.deprecation import MiddlewareMixin

try:
    from plugins import plugin_manager
    PLUGINS_AVAILABLE = True
except Exception:
    PLUGINS_AVAILABLE = False


class PluginInjectionMiddleware(MiddlewareMixin):
    """
    HTML post-processing middleware to inject plugin-rendered content
    into pages that do not include explicit `{% plugin_hook %}` tags.

    Currently supports the home page by inserting the `home_page_header`
    hook output after the first content container in the home template.
    """

    def process_response(self, request, response):
        # Only operate on HTML responses
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            return response
        if not PLUGINS_AVAILABLE:
            return response
        try:
            html = response.content.decode(response.charset or 'utf-8')
        except Exception:
            return response

        # Home page injection: path "" or "/"
        if request.path == '/':
            injected = self._inject_home_header(html, request)
            if injected is not None:
                response.content = injected.encode(response.charset or 'utf-8')
        return response

    def _inject_home_header(self, html: str, request) -> Optional[str]:
        # Collect plugin-rendered HTML
        try:
            banner = plugin_manager.render_template_hook('home_page_header', {'request': request})
        except Exception:
            banner = ''
        if not banner:
            return None

        # Find opening of the home content container
        # Target the first <div style="text-align:center"> from home.html
        pattern = re.compile(r"(<div[^>]*style=\"[^\"]*text-align:center[^\"]*\"[^>]*>)", re.IGNORECASE)
        match = pattern.search(html)
        if match:
            start_tag = match.group(1)
            return html.replace(start_tag, f"{start_tag}\n{banner}", 1)

        # Fallback: insert after opening <body>
        body_open = re.search(r"(<body[^>]*>)", html, re.IGNORECASE)
        if body_open:
            start_tag = body_open.group(1)
            return html.replace(start_tag, f"{start_tag}\n{banner}", 1)

        return None
