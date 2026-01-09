"""
Hello World Demo Plugin
Displays a banner on the home page via a template hook.
"""

class Plugin:
    name = "hello_world"
    version = "1.0.0"

    def __init__(self):
        self.hooks = {
            'home_page_header': self.banner,
        }
        self.urls = []

    def banner(self, context):
        return (
            '<div class="alert alert-success" role="alert" '
            'style="max-width:800px;margin:10px auto">'
            'Hello World!'
            '</div>'
        )
