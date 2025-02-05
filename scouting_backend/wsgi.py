# scouting_backend/wsgi.py
import os
import sys
from django.core.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scouting_backend.settings')

# Add error handling
try:
    application = get_wsgi_application()
    app = application  # Vercel needs this
except Exception as e:
    print(f"Error loading application: {e}")
    raise e
