"""
WSGI config for Equilibrium MLM Backend.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equilibrium_backend.settings')

application = get_wsgi_application()

