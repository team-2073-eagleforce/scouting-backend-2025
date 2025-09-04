from django.http import HttpResponseRedirect
from django.urls import reverse


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Paths that don't require authentication
        public_paths = ['/auth/', '/auth/oauth2callback/']
        
        # Check if user is authenticated
        if not request.session.get('email') and request.path not in public_paths:
            return HttpResponseRedirect('/auth/')
        
        response = self.get_response(request)
        return response