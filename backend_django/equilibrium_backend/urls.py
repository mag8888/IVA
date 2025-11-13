"""
URL configuration for Equilibrium MLM Backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """Healthcheck endpoint для Railway."""
    return JsonResponse({
        "status": "ok",
        "message": "Equilibrium MLM backend is running"
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('health/', health_check, name='health'),
    path('telegram-app/', TemplateView.as_view(template_name='telegram_app/index.html'), name='telegram-app'),
    path('', include('core.urls')),
]

