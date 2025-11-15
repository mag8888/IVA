"""
Custom admin views for dashboard and statistics.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.urls import path
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from core.models import User
from mlm.models import Tariff, StructureNode
from billing.models import Payment, Bonus


@staff_member_required
def dashboard(request):
    """Кастомный dashboard с статистикой."""
    # Общая статистика
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    users_with_payments = User.objects.filter(
        payments__status=Payment.PaymentStatus.COMPLETED
    ).distinct().count()
    
    # Статистика по платежам
    total_payments = Payment.objects.count()
    completed_payments = Payment.objects.filter(status=Payment.PaymentStatus.COMPLETED).count()
    pending_payments = Payment.objects.filter(status=Payment.PaymentStatus.PENDING).count()
    total_revenue = Payment.objects.filter(
        status=Payment.PaymentStatus.COMPLETED
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Статистика по бонусам
    total_bonuses = Bonus.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    green_bonuses = Bonus.objects.filter(bonus_type=Bonus.BonusType.GREEN).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    yellow_bonuses = Bonus.objects.filter(bonus_type=Bonus.BonusType.YELLOW).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Статистика по структуре
    total_nodes = StructureNode.objects.count()
    max_level = StructureNode.objects.aggregate(max_level=Count('level')) or {'max_level': 0}
    
    # Статистика по тарифам
    tariffs_stats = []
    for tariff in Tariff.objects.filter(is_active=True):
        tariff_payments = Payment.objects.filter(
            tariff=tariff,
            status=Payment.PaymentStatus.COMPLETED
        )
        tariffs_stats.append({
            'tariff': tariff,
            'count': tariff_payments.count(),
            'total': tariff_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        })
    
    # Статистика за последние 30 дней
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_users = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    recent_payments = Payment.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_revenue = Payment.objects.filter(
        created_at__gte=thirty_days_ago,
        status=Payment.PaymentStatus.COMPLETED
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Топ пользователей по балансу
    top_users_balance = User.objects.order_by('-balance')[:10]
    
    # Топ пользователей по бонусам
    top_users_bonuses = User.objects.annotate(
        total_bonuses=Sum('bonuses__amount')
    ).filter(total_bonuses__gt=0).order_by('-total_bonuses')[:10]
    
    from django.contrib import admin
    
    context = {
        **admin.site.each_context(request),
        'title': 'Dashboard - Статистика',
        'total_users': total_users,
        'active_users': active_users,
        'users_with_payments': users_with_payments,
        'total_payments': total_payments,
        'completed_payments': completed_payments,
        'pending_payments': pending_payments,
        'total_revenue': total_revenue,
        'total_bonuses': total_bonuses,
        'green_bonuses': green_bonuses,
        'yellow_bonuses': yellow_bonuses,
        'total_nodes': total_nodes,
        'tariffs_stats': tariffs_stats,
        'recent_users': recent_users,
        'recent_payments': recent_payments,
        'recent_revenue': recent_revenue,
        'top_users_balance': top_users_balance,
        'top_users_bonuses': top_users_bonuses,
    }
    
    return TemplateResponse(request, 'admin/dashboard.html', context)


# URL patterns для dashboard
urlpatterns = [
    path('', dashboard, name='admin_dashboard'),
]

