"""
ASGI config for Equilibrium MLM Backend.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equilibrium_backend.settings')

application = get_asgi_application()

