"""
URL configuration for Equilibrium MLM Backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from integrations.telegram import telegram_webhook

# Настройка админки Django
admin.site.site_header = "Equilibrium MLM Admin"
admin.site.site_title = "Equilibrium MLM"
admin.site.index_title = "Панель управления"

@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """Healthcheck endpoint для Railway."""
    return JsonResponse({
        "status": "ok",
        "message": "Equilibrium MLM backend is running"
    })

urlpatterns = [
    path('admin/dashboard/', include('core.admin_views')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('health/', health_check, name='health'),
    path('telegram-app/', TemplateView.as_view(template_name='telegram_app/index.html'), name='telegram-app'),
    path('telegram/webhook/', telegram_webhook, name='telegram-webhook'),
    path('', include('core.urls')),
]

