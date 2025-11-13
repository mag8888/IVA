from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ-панель для пользователей."""
    list_display = ['username', 'email', 'status', 'referral_code', 'invited_by', 'is_active_mlm', 'date_joined']
    list_filter = ['status', 'is_active_mlm', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'referral_code']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('MLM Information', {
            'fields': ('status', 'referral_code', 'invited_by', 'is_active_mlm')
        }),
    )

