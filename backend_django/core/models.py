"""
Core models for Equilibrium MLM System.
"""
import secrets
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Расширенная модель пользователя Django.
    Все поля статуса и реферальной системы.
    """
    
    class UserStatus(models.TextChoices):
        PARTICIPANT = 'PARTICIPANT', _('Участник')
        PARTNER = 'PARTNER', _('Партнер')
        ADMIN = 'ADMIN', _('Администратор')
    
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.PARTICIPANT,
        verbose_name=_('Статус')
    )
    
    referral_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        verbose_name=_('Реферальный код')
    )
    
    invited_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_users',
        verbose_name=_('Пригласивший')
    )
    
    is_active_mlm = models.BooleanField(
        default=True,
        verbose_name=_('Активен в MLM')
    )
    
    telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name=_('Telegram ID'),
        help_text=_('ID пользователя в Telegram')
    )
    
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Баланс'),
        help_text=_('Баланс пользователя в долларах')
    )
    
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['-date_joined']
    
    def save(self, *args, **kwargs):
        """Автоматическая генерация referral_code при создании."""
        if not self.referral_code:
            # Генерируем уникальный код
            while True:
                code = secrets.token_urlsafe(8).upper()[:8]
                if not User.objects.filter(referral_code=code).exists():
                    self.referral_code = code
                    break
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} ({self.get_status_display()})"

