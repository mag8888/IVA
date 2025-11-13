from django.contrib import admin
from .models import Tariff, StructureNode


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'entry_amount', 'green_bonus_percent', 'yellow_bonus_percent', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(StructureNode)
class StructureNodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'parent', 'level', 'position', 'tariff', 'created_at']
    list_filter = ['level', 'tariff']
    search_fields = ['user__username', 'parent__username']
    raw_id_fields = ['user', 'parent']

