from datetime import timedelta

from django import template
from django.apps import apps
from django.db.models import Sum
from django.utils import timezone

register = template.Library()


def _m(app_label: str, model_name: str):
    """Safe model getter to avoid ImportError at import time on cold start."""
    try:
        return apps.get_model(app_label, model_name)
    except Exception:
        return None


@register.simple_tag
def total_users():
    User = _m('core', 'User') or _m('auth', 'User')
    return User.objects.count() if User else 0


@register.simple_tag
def active_users():
    User = _m('core', 'User') or _m('auth', 'User')
    return User.objects.filter(is_active=True).count() if User else 0


@register.simple_tag
def users_with_payments():
    User = _m('core', 'User') or _m('auth', 'User')
    Payment = _m('billing', 'Payment')
    if not (User and Payment):
        return 0
    return (
        User.objects.filter(payments__status=Payment.PaymentStatus.COMPLETED)
        .distinct()
        .count()
    )


@register.simple_tag
def total_payments():
    Payment = _m('billing', 'Payment')
    return Payment.objects.count() if Payment else 0


@register.simple_tag
def completed_payments():
    Payment = _m('billing', 'Payment')
    if not Payment:
        return 0
    return Payment.objects.filter(status=Payment.PaymentStatus.COMPLETED).count()


@register.simple_tag
def pending_payments():
    Payment = _m('billing', 'Payment')
    if not Payment:
        return 0
    return Payment.objects.filter(status=Payment.PaymentStatus.PENDING).count()


@register.simple_tag
def total_revenue():
    Payment = _m('billing', 'Payment')
    if not Payment:
        return 0
    return (
        Payment.objects.filter(status=Payment.PaymentStatus.COMPLETED)
        .aggregate(total=Sum('amount'))
        .get('total')
        or 0
    )


@register.simple_tag
def total_bonuses():
    Bonus = _m('billing', 'Bonus')
    return (Bonus.objects.aggregate(total=Sum('amount')).get('total') or 0) if Bonus else 0


@register.simple_tag
def green_bonuses():
    Bonus = _m('billing', 'Bonus')
    if not Bonus:
        return 0
    return (
        Bonus.objects.filter(bonus_type=Bonus.BonusType.GREEN)
        .aggregate(total=Sum('amount'))
        .get('total')
        or 0
    )


@register.simple_tag
def yellow_bonuses():
    Bonus = _m('billing', 'Bonus')
    if not Bonus:
        return 0
    return (
        Bonus.objects.filter(bonus_type=Bonus.BonusType.YELLOW)
        .aggregate(total=Sum('amount'))
        .get('total')
        or 0
    )


@register.simple_tag
def total_nodes():
    Node = _m('mlm', 'StructureNode')
    return Node.objects.count() if Node else 0


@register.simple_tag
def recent_users(days=30):
    User = _m('core', 'User') or _m('auth', 'User')
    if not User:
        return 0
    since = timezone.now() - timedelta(days=days)
    return User.objects.filter(date_joined__gte=since).count()


@register.simple_tag
def recent_payments(days=30):
    Payment = _m('billing', 'Payment')
    if not Payment:
        return 0
    since = timezone.now() - timedelta(days=days)
    return Payment.objects.filter(created_at__gte=since).count()


@register.simple_tag
def recent_revenue(days=30):
    Payment = _m('billing', 'Payment')
    if not Payment:
        return 0
    since = timezone.now() - timedelta(days=days)
    return (
        Payment.objects.filter(created_at__gte=since, status=Payment.PaymentStatus.COMPLETED)
        .aggregate(total=Sum('amount'))
        .get('total')
        or 0
    )


@register.simple_tag
def top_users_by_balance(limit=5):
    User = _m('core', 'User') or _m('auth', 'User')
    return User.objects.order_by('-balance')[:limit] if User else []


@register.simple_tag
def top_users_by_bonuses(limit=5):
    User = _m('core', 'User') or _m('auth', 'User')
    if not User:
        return []
    try:
        return (
            User.objects
            .annotate(total_bonuses=Sum('bonuses__amount'))
            .filter(total_bonuses__gt=0)
            .order_by('-total_bonuses')[:limit]
        )
    except Exception:
        return []


