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
        if not obj.pk:
            return "$0.00"
        try:
            return format_html(
                '<span style="color: #417690; font-weight: bold; font-size: 1.1em;">${:.2f}</span>',
                obj.entry_amount
            )
        except Exception:
            return "$0.00"
    get_entry_amount_display.short_description = "Сумма"
    get_entry_amount_display.admin_order_field = 'entry_amount'
    
    def get_statistics(self, obj):
        """Статистика по тарифу."""
        if not obj.pk:
            return "Сначала сохраните тариф"
        
        try:
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
        except Exception:
            return "Ошибка загрузки статистики"
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
        if not obj.pk or not obj.user:
            return "-"
        try:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:core_user_change', args=[obj.user.id]),
                obj.user.username
            )
        except Exception:
            return obj.user.username if obj.user else "-"
    get_user_link.short_description = "Пользователь"
    get_user_link.admin_order_field = 'user__username'
    
    def get_parent_link(self, obj):
        """Ссылка на родителя."""
        if not obj.pk or not obj.parent:
            return "-"
        try:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:core_user_change', args=[obj.parent.id]),
                obj.parent.username
            )
        except Exception:
            return obj.parent.username if obj.parent else "-"
    get_parent_link.short_description = "Родитель"
    get_parent_link.admin_order_field = 'parent__username'
    
    def get_tariff_link(self, obj):
        """Ссылка на тариф."""
        if not obj.pk or not obj.tariff:
            return "-"
        try:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:mlm_tariff_change', args=[obj.tariff.id]),
                obj.tariff.name
            )
        except Exception:
            return obj.tariff.name if obj.tariff else "-"
    get_tariff_link.short_description = "Тариф"
    get_tariff_link.admin_order_field = 'tariff__name'
    
    def get_children_info(self, obj):
        """Информация о детях."""
        if not obj.pk:
            return "Сначала сохраните узел"
        
        try:
            children = obj.children.all()
            if not children.exists():
                return format_html('<p style="color: #6c757d;">Нет детей в структуре</p>')
            
            children_items = []
            for child in children:
                try:
                    url = reverse('admin:core_user_change', args=[child.user.id])
                    children_items.append(
                        f'<li><a href="{url}">{child.user.username}</a> (Позиция {child.position})</li>'
                    )
                except Exception:
                    username = child.user.username if child.user else "N/A"
                    children_items.append(f'<li>{username} (Позиция {child.position})</li>')
            
            children_html = '<ul style="margin: 5px 0; padding-left: 20px;">' + ''.join(children_items) + '</ul>'
            
            return format_html(
                '<div style="padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;">'
                '<p><strong>Дети ({})</strong></p>'
                '{}'
                '</div>',
                children.count(),
                format_html(children_html)
            )
        except Exception:
            return "Ошибка загрузки информации о детях"
    get_children_info.short_description = "Дети в структуре"
    
    def get_structure_path(self, obj):
        """Путь в структуре от корня."""
        if not obj.pk:
            return "Сначала сохраните узел"
        
        try:
            path_items = []
            current = obj
            while current.parent:
                parent_node = StructureNode.objects.filter(user=current.parent).first()
                if parent_node:
                    try:
                        url = reverse('admin:core_user_change', args=[current.parent.id])
                        path_items.insert(0, f'<a href="{url}">{current.parent.username}</a> (L{parent_node.level} P{parent_node.position})')
                    except Exception:
                        username = current.parent.username if current.parent else "N/A"
                        path_items.insert(0, f'{username} (L{parent_node.level} P{parent_node.position})')
                    current = parent_node
                else:
                    break
            
            if path_items:
                path_html = ' → '.join(path_items)
                return format_html(
                    '<div style="padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;">'
                    '<p><strong>Путь от корня:</strong></p>'
                    '<p>{}</p>'
                    '</div>',
                    format_html(path_html)
                )
            return format_html('<p style="color: #6c757d;">Корневой пользователь</p>')
        except Exception:
            return "Ошибка загрузки пути в структуре"
    get_structure_path.short_description = "Путь в структуре"
