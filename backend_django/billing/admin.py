from django.contrib import admin
from .models import Payment, Bonus


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'tariff', 'amount', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'tariff']
    search_fields = ['user__username', 'external_id']
    raw_id_fields = ['user', 'tariff']
    readonly_fields = ['created_at', 'completed_at']


@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    list_display = ['user', 'source_user', 'bonus_type', 'amount', 'payment', 'created_at']
    list_filter = ['bonus_type']
    search_fields = ['user__username', 'source_user__username']
    raw_id_fields = ['user', 'source_user', 'payment']
    readonly_fields = ['created_at']

