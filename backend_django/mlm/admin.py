from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Tariff, StructureNode


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'get_entry_amount_display', 'green_bonus_percent', 'yellow_bonus_percent', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'get_statistics']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('code', 'name', 'entry_amount', 'is_active')
        }),
        ('Бонусы', {
            'fields': ('green_bonus_percent', 'yellow_bonus_percent')
        }),
        ('Статистика', {
            'fields': ('get_statistics',),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_entry_amount_display(self, obj):
        """Отображение суммы вступительного взноса."""
        return format_html(
            '<span style="color: #417690; font-weight: bold; font-size: 1.1em;">${:.2f}</span>',
            obj.entry_amount
        )
    get_entry_amount_display.short_description = "Сумма"
    get_entry_amount_display.admin_order_field = 'entry_amount'
    
    def get_statistics(self, obj):
        """Статистика по тарифу."""
        if not obj.pk:
            return "Сначала сохраните тариф"
        
        from billing.models import Payment
        from django.db.models import Sum, Count
        
        total_payments = Payment.objects.filter(tariff=obj).count()
        completed_payments = Payment.objects.filter(tariff=obj, status=Payment.PaymentStatus.COMPLETED).count()
        total_amount = Payment.objects.filter(
            tariff=obj,
            status=Payment.PaymentStatus.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        users_count = StructureNode.objects.filter(tariff=obj).count()
        
        return format_html(
            '<div style="padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;">'
            '<p><strong>📊 Статистика тарифа:</strong></p>'
            '<p>Всего платежей: <strong>{}</strong></p>'
            '<p>Завершено: <strong style="color: #28a745;">{}</strong></p>'
            '<p>Общая сумма: <strong style="color: #417690;">${:.2f}</strong></p>'
            '<p>Пользователей с тарифом: <strong>{}</strong></p>'
            '</div>',
            total_payments,
            completed_payments,
            total_amount,
            users_count
        )
    get_statistics.short_description = "📊 Статистика"


@admin.register(StructureNode)
class StructureNodeAdmin(admin.ModelAdmin):
    list_display = ['get_user_link', 'get_parent_link', 'level', 'position', 'get_tariff_link', 'created_at']
    list_filter = ['level', 'tariff', 'created_at']
    search_fields = ['user__username', 'parent__username']
    raw_id_fields = ['user', 'parent']
    readonly_fields = ['created_at', 'get_children_info', 'get_structure_path']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'parent', 'level', 'position', 'tariff')
        }),
        ('Структура', {
            'fields': ('get_structure_path', 'get_children_info'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_link(self, obj):
        """Ссылка на пользователя."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:core_user_change', args=[obj.user.id]),
            obj.user.username
        )
    get_user_link.short_description = "Пользователь"
    get_user_link.admin_order_field = 'user__username'
    
    def get_parent_link(self, obj):
        """Ссылка на родителя."""
        if obj.parent:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:core_user_change', args=[obj.parent.id]),
                obj.parent.username
            )
        return "-"
    get_parent_link.short_description = "Родитель"
    get_parent_link.admin_order_field = 'parent__username'
    
    def get_tariff_link(self, obj):
        """Ссылка на тариф."""
        if obj.tariff:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:mlm_tariff_change', args=[obj.tariff.id]),
                obj.tariff.name
            )
        return "-"
    get_tariff_link.short_description = "Тариф"
    get_tariff_link.admin_order_field = 'tariff__name'
    
    def get_children_info(self, obj):
        """Информация о детях."""
        if not obj.pk:
            return "Сначала сохраните узел"
        
        children = obj.children.all()
        if not children.exists():
            return format_html('<p style="color: #6c757d;">Нет детей в структуре</p>')
        
        children_html = '<ul style="margin: 5px 0; padding-left: 20px;">'
        for child in children:
            children_html += format_html(
                '<li><a href="{}">{}</a> (Позиция {})</li>',
                reverse('admin:core_user_change', args=[child.user.id]),
                child.user.username,
                child.position
            )
        children_html += '</ul>'
        
        return format_html(
            '<div style="padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;">'
            '<p><strong>Дети ({})</strong></p>'
            '{}'
            '</div>',
            children.count(),
            children_html
        )
    get_children_info.short_description = "Дети в структуре"
    
    def get_structure_path(self, obj):
        """Путь в структуре от корня."""
        if not obj.pk:
            return "Сначала сохраните узел"
        
        path = []
        current = obj
        while current.parent:
            parent_node = StructureNode.objects.filter(user=current.parent).first()
            if parent_node:
                path.insert(0, format_html(
                    '<a href="{}">{}</a> (L{} P{})',
                    reverse('admin:core_user_change', args=[current.parent.id]),
                    current.parent.username,
                    parent_node.level,
                    parent_node.position
                ))
                current = parent_node
            else:
                break
        
        if path:
            return format_html(
                '<div style="padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;">'
                '<p><strong>Путь от корня:</strong></p>'
                '<p>{}</p>'
                '</div>',
                ' → '.join(path)
            )
        return format_html('<p style="color: #6c757d;">Корневой пользователь</p>')
    get_structure_path.short_description = "Путь в структуре"
