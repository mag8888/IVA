"""
MLM models for Equilibrium System.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class Tariff(models.Model):
    """
    Тарифный план.
    Все проценты бонусов настраиваемые через переменные окружения.
    """
    code = models.SlugField(
        unique=True,
        verbose_name=_('Код тарифа')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название')
    )
    entry_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Сумма вступительного взноса')
    )
    green_bonus_percent = models.IntegerField(
        default=settings.MLM_SETTINGS['DEFAULT_GREEN_BONUS_PERCENT'],
        verbose_name=_('Процент зеленого бонуса')
    )
    yellow_bonus_percent = models.IntegerField(
        default=settings.MLM_SETTINGS['DEFAULT_YELLOW_BONUS_PERCENT'],
        verbose_name=_('Процент желтого бонуса')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    
    class Meta:
        verbose_name = _('Тариф')
        verbose_name_plural = _('Тарифы')
        ordering = ['entry_amount']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class StructureNode(models.Model):
    """
    Узел MLM структуры.
    Максимум партнеров на уровень настраивается через переменные окружения.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='structure_node',
        verbose_name=_('Пользователь')
    )
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children_nodes',
        verbose_name=_('Родитель')
    )
    position = models.IntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3')],
        verbose_name=_('Позиция')
    )
    level = models.IntegerField(
        default=0,
        verbose_name=_('Уровень')
    )
    tariff = models.ForeignKey(
        Tariff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Тариф')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    
    class Meta:
        verbose_name = _('Узел структуры')
        verbose_name_plural = _('Узлы структуры')
        unique_together = [['parent', 'position']]
        ordering = ['level', 'position']
    
    def clean(self):
        """Валидация позиции."""
        max_partners = settings.MLM_SETTINGS['MAX_PARTNERS_PER_LEVEL']
        if self.position and self.position > max_partners:
            raise ValidationError(
                f'Позиция не может быть больше {max_partners}'
            )
    
    def __str__(self):
        return f"{self.user.username} (Level {self.level}, Position {self.position})"
    
    @property
    def children(self):
        """Получить дочерние узлы."""
        return StructureNode.objects.filter(parent=self.user)

