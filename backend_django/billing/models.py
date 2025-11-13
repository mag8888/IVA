"""
Billing models for Equilibrium System.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    """
    Платеж пользователя.
    """
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', _('Ожидает')
        COMPLETED = 'COMPLETED', _('Завершен')
        FAILED = 'FAILED', _('Ошибка')
        CANCELLED = 'CANCELLED', _('Отменен')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Пользователь')
    )
    tariff = models.ForeignKey(
        'mlm.Tariff',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Тариф')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Сумма')
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name=_('Статус')
    )
    external_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Внешний ID')
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Метаданные')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата завершения')
    )
    
    class Meta:
        verbose_name = _('Платеж')
        verbose_name_plural = _('Платежи')
        ordering = ['-created_at']
    
    def mark_completed(self):
        """Пометить платеж как завершенный."""
        from django.utils import timezone
        self.status = self.PaymentStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.get_status_display()})"


class Bonus(models.Model):
    """
    Начисленный бонус.
    """
    class BonusType(models.TextChoices):
        GREEN = 'GREEN', _('Зеленый бонус')
        YELLOW = 'YELLOW', _('Желтый бонус')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bonuses',
        verbose_name=_('Получатель')
    )
    source_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='source_bonuses',
        verbose_name=_('Источник бонуса')
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='bonuses',
        verbose_name=_('Платеж')
    )
    bonus_type = models.CharField(
        max_length=20,
        choices=BonusType.choices,
        verbose_name=_('Тип бонуса')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Сумма')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата начисления')
    )
    
    class Meta:
        verbose_name = _('Бонус')
        verbose_name_plural = _('Бонусы')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.get_bonus_type_display()})"

