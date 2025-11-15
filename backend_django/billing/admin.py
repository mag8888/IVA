from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse
from .models import Payment, Bonus


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user_link', 'get_tariff_link', 'get_amount_display', 'get_status_display', 'created_at', 'completed_at']
    list_filter = ['status', 'tariff', 'created_at']
    search_fields = ['user__username', 'user__email', 'external_id']
    raw_id_fields = ['user', 'tariff']
    readonly_fields = ['created_at', 'completed_at', 'get_user_info']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'tariff', 'amount', 'status', 'get_user_info')
        }),
        ('Дополнительно', {
            'fields': ('external_id', 'metadata', 'created_at', 'completed_at'),
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
    
    def get_amount_display(self, obj):
        """Отображение суммы с цветом."""
        return format_html(
            '<span style="color: #28a745; font-weight: bold; font-size: 1.1em;">${:.2f}</span>',
            obj.amount
        )
    get_amount_display.short_description = "Сумма"
    get_amount_display.admin_order_field = 'amount'
    
    def get_status_display(self, obj):
        """Отображение статуса с цветом."""
        status_colors = {
            'COMPLETED': '#28a745',
            'PENDING': '#ffc107',
            'FAILED': '#dc3545',
            'CANCELLED': '#6c757d'
        }
        status_icons = {
            'COMPLETED': '✅',
            'PENDING': '⏳',
            'FAILED': '❌',
            'CANCELLED': '🚫'
        }
        color = status_colors.get(obj.status, '#000')
        icon = status_icons.get(obj.status, '')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    get_status_display.short_description = "Статус"
    get_status_display.admin_order_field = 'status'
    
    def get_user_info(self, obj):
        """Информация о пользователе."""
        if not obj.pk:
            return "Сначала сохраните платеж"
        
        balance = obj.user.balance or 0
        total_payments = Payment.objects.filter(
            user=obj.user,
            status=Payment.PaymentStatus.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return format_html(
            '<div style="padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;">'
            '<p><strong>Баланс:</strong> <span style="color: #28a745; font-weight: bold;">${:.2f}</span></p>'
            '<p><strong>Всего оплачено:</strong> <span style="color: #417690; font-weight: bold;">${:.2f}</span></p>'
            '</div>',
            balance,
            total_payments
        )
    get_user_info.short_description = "Информация о пользователе"


@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user_link', 'get_source_user_link', 'get_bonus_type_display', 'get_amount_display', 'get_payment_link', 'created_at']
    list_filter = ['bonus_type', 'created_at']
    search_fields = ['user__username', 'source_user__username', 'description']
    raw_id_fields = ['user', 'source_user', 'payment']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    def get_user_link(self, obj):
        """Ссылка на получателя."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:core_user_change', args=[obj.user.id]),
            obj.user.username
        )
    get_user_link.short_description = "Получатель"
    get_user_link.admin_order_field = 'user__username'
    
    def get_source_user_link(self, obj):
        """Ссылка на источник бонуса."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:core_user_change', args=[obj.source_user.id]),
            obj.source_user.username
        )
    get_source_user_link.short_description = "Источник"
    get_source_user_link.admin_order_field = 'source_user__username'
    
    def get_bonus_type_display(self, obj):
        """Отображение типа бонуса с цветом."""
        if obj.bonus_type == Bonus.BonusType.GREEN:
            color = '#28a745'
            icon = '💚'
        else:
            color = '#ffc107'
            icon = '💛'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.get_bonus_type_display()
        )
    get_bonus_type_display.short_description = "Тип"
    get_bonus_type_display.admin_order_field = 'bonus_type'
    
    def get_amount_display(self, obj):
        """Отображение суммы."""
        return format_html(
            '<span style="color: #417690; font-weight: bold; font-size: 1.1em;">${:.2f}</span>',
            obj.amount
        )
    get_amount_display.short_description = "Сумма"
    get_amount_display.admin_order_field = 'amount'
    
    def get_payment_link(self, obj):
        """Ссылка на платеж."""
        return format_html(
            '<a href="{}">#{}</a>',
            reverse('admin:billing_payment_change', args=[obj.payment.id]),
            obj.payment.id
        )
    get_payment_link.short_description = "Платеж"
    get_payment_link.admin_order_field = 'payment__id'
