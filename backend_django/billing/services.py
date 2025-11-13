"""
Billing Services - логика начисления бонусов.
"""
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import Payment, Bonus
from core.models import User


def calculate_bonus_amounts(tariff):
    """
    Рассчитать суммы бонусов на основе тарифа.
    
    Args:
        tariff: Tariff объект
    
    Returns:
        dict: {'green': amount, 'yellow': amount}
    """
    entry_amount = tariff.entry_amount
    green_percent = tariff.green_bonus_percent
    yellow_percent = tariff.yellow_bonus_percent
    
    green_amount = entry_amount * green_percent / 100
    yellow_amount = entry_amount * yellow_percent / 100
    
    return {
        'green': green_amount,
        'yellow': yellow_amount,
    }


@transaction.atomic
def apply_signup_bonuses(user, payment):
    """
    Начислить бонусы при регистрации нового партнера.
    
    Бонусы:
    1. Green Bonus - пригласившему (inviter)
    2. Yellow Bonus - владельцу позиции размещения (parent)
    
    Args:
        user: User объект нового партнера
        payment: Payment объект
    
    Returns:
        list: Список созданных Bonus объектов
    """
    bonuses = []
    tariff = payment.tariff
    
    if not tariff:
        return bonuses
    
    # Рассчитываем суммы бонусов
    bonus_amounts = calculate_bonus_amounts(tariff)
    
    # 1. Green Bonus - пригласившему (inviter)
    if user.invited_by:
        green_bonus = Bonus.objects.create(
            user=user.invited_by,  # Получатель - пригласивший
            source_user=user,  # Источник - новый партнер
            payment=payment,
            bonus_type=Bonus.BonusType.GREEN,
            amount=bonus_amounts['green'],
            description=f"Зеленый бонус за приглашение {user.username}"
        )
        bonuses.append(green_bonus)
    
    # 2. Yellow Bonus - владельцу позиции размещения (parent)
    from mlm.models import StructureNode
    
    try:
        structure_node = StructureNode.objects.get(user=user)
        parent_user = structure_node.parent
        
        if parent_user:
            yellow_bonus = Bonus.objects.create(
                user=parent_user,  # Получатель - владелец позиции
                source_user=user,  # Источник - новый партнер
                payment=payment,
                bonus_type=Bonus.BonusType.YELLOW,
                amount=bonus_amounts['yellow'],
                description=f"Желтый бонус за размещение {user.username} в структуре"
            )
            bonuses.append(yellow_bonus)
    except StructureNode.DoesNotExist:
        # Пользователь еще не размещен в структуре
        pass
    
    return bonuses

