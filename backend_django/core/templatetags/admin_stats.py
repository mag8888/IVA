from datetime import timedelta

from django import template
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q
from django.utils import timezone

from billing.models import Payment, Bonus
from mlm.models import StructureNode

register = template.Library()


@register.simple_tag
def total_users():
    User = get_user_model()
    return User.objects.count()


@register.simple_tag
def active_users():
    User = get_user_model()
    return User.objects.filter(is_active=True).count()


@register.simple_tag
def users_with_payments():
    User = get_user_model()
    return User.objects.filter(payments__status=Payment.PaymentStatus.COMPLETED).distinct().count()


@register.simple_tag
def total_payments():
    return Payment.objects.count()


@register.simple_tag
def completed_payments():
    return Payment.objects.filter(status=Payment.PaymentStatus.COMPLETED).count()


@register.simple_tag
def pending_payments():
    return Payment.objects.filter(status=Payment.PaymentStatus.PENDING).count()


@register.simple_tag
def total_revenue():
    return Payment.objects.filter(status=Payment.PaymentStatus.COMPLETED).aggregate(total=Sum('amount'))['total'] or 0


@register.simple_tag
def total_bonuses():
    return Bonus.objects.aggregate(total=Sum('amount'))['total'] or 0


@register.simple_tag
def green_bonuses():
    return (Bonus.objects.filter(bonus_type=Bonus.BonusType.GREEN)
            .aggregate(total=Sum('amount'))['total'] or 0)


@register.simple_tag
def yellow_bonuses():
    return (Bonus.objects.filter(bonus_type=Bonus.BonusType.YELLOW)
            .aggregate(total=Sum('amount'))['total'] or 0)


@register.simple_tag
def total_nodes():
    return StructureNode.objects.count()


@register.simple_tag
def recent_users(days=30):
    User = get_user_model()
    since = timezone.now() - timedelta(days=days)
    return User.objects.filter(date_joined__gte=since).count()


@register.simple_tag
def recent_payments(days=30):
    since = timezone.now() - timedelta(days=days)
    return Payment.objects.filter(created_at__gte=since).count()


@register.simple_tag
def recent_revenue(days=30):
    since = timezone.now() - timedelta(days=days)
    return (Payment.objects.filter(created_at__gte=since, status=Payment.PaymentStatus.COMPLETED)
            .aggregate(total=Sum('amount'))['total'] or 0)


@register.simple_tag
def top_users_by_balance(limit=5):
    User = get_user_model()
    return User.objects.order_by('-balance')[:limit]


@register.simple_tag
def top_users_by_bonuses(limit=5):
    User = get_user_model()
    return (User.objects
            .annotate(total_bonuses=Sum('bonuses__amount'))
            .filter(total_bonuses__gt=0)
            .order_by('-total_bonuses')[:limit])


