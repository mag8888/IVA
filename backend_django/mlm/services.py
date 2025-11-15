"""
MLM Services - логика размещения пользователей в структуре.
"""
from collections import deque
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import StructureNode, Tariff
from core.models import User


def get_active_tariff(tariff_code=None):
    """
    Получить активный тариф.
    
    Args:
        tariff_code: Код тарифа (опционально)
    
    Returns:
        Tariff объект или None
    """
    if tariff_code:
        try:
            return Tariff.objects.get(code=tariff_code, is_active=True)
        except Tariff.DoesNotExist:
            return None
    
    # Возвращаем первый активный тариф по умолчанию
    return Tariff.objects.filter(is_active=True).first()


def find_parent_for_new_partner(user):
    """
    Найти родителя для размещения нового партнера используя BFS.
    
    Алгоритм:
    1. Начинаем с корня структуры (Level 0)
    2. Используем BFS (обход в ширину)
    3. Ищем первого пользователя с менее чем MAX_PARTNERS_PER_LEVEL партнерами
    4. Возвращаем найденного родителя и свободную позицию
    
    Args:
        user: User объект для размещения
    
    Returns:
        tuple: (parent_user, position) или (None, None) если не найдено
    """
    max_partners = settings.MLM_SETTINGS['MAX_PARTNERS_PER_LEVEL']
    
    # Если это первый пользователь - он становится корнем
    if not StructureNode.objects.exists():
        return None, None  # Корень не имеет parent
    
    # Находим корневой узел (Level 0, parent=None)
    root_nodes = StructureNode.objects.filter(level=0).select_related('user')
    
    if not root_nodes.exists():
        # Если нет корня, но есть узлы - берем первого пользователя
        first_node = StructureNode.objects.select_related('user').first()
        if first_node:
            return first_node.user, 1
    
    # BFS: очередь для обхода
    queue = deque()
    
    # Добавляем все корневые узлы в очередь
    for root_node in root_nodes:
        queue.append(root_node.user)
    
    # Множество посещенных пользователей (для избежания циклов)
    visited = set()
    
    while queue:
        current_user = queue.popleft()
        
        if current_user.id in visited:
            continue
        
        visited.add(current_user.id)
        
        # Получаем узел текущего пользователя
        try:
            current_node = StructureNode.objects.get(user=current_user)
        except StructureNode.DoesNotExist:
            continue
        
        # Проверяем количество партнеров у текущего пользователя
        children_count = StructureNode.objects.filter(parent=current_user).count()
        
        if children_count < max_partners:
            # Нашли свободное место!
            # Определяем свободную позицию (1, 2 или 3)
            existing_positions = set(
                StructureNode.objects.filter(parent=current_user)
                .values_list('position', flat=True)
            )
            
            # Находим первую свободную позицию
            for pos in range(1, max_partners + 1):
                if pos not in existing_positions:
                    return current_user, pos
        
        # Если место не найдено, добавляем детей в очередь для дальнейшего поиска
        children = StructureNode.objects.filter(parent=current_user).select_related('user')
        for child_node in children:
            if child_node.user.id not in visited:
                queue.append(child_node.user)
    
    # Если не нашли место (не должно произойти в нормальных условиях)
    return None, None


@transaction.atomic
def place_user(user, payment):
    """
    Разместить пользователя в MLM структуре.
    
    Args:
        user: User объект для размещения
        payment: Payment объект (должен быть COMPLETED)
    
    Returns:
        StructureNode объект
    
    Raises:
        ValidationError: если размещение невозможно
    """
    # Проверяем, что пользователь еще не размещен
    if StructureNode.objects.filter(user=user).exists():
        raise ValidationError(f"Пользователь {user.username} уже размещен в структуре")
    
    # Проверяем статус платежа
    if payment.status != payment.PaymentStatus.COMPLETED:
        raise ValidationError("Платеж должен быть завершен перед размещением")
    
    # Получаем тариф
    tariff = payment.tariff
    if not tariff:
        raise ValidationError("Платеж должен иметь тариф")
    
    # Находим родителя для размещения
    parent_user, position = find_parent_for_new_partner(user)
    
    # Проверяем, найдено ли место для размещения
    # Если есть узлы в структуре, но не найден parent, значит структура заполнена
    if StructureNode.objects.exists() and parent_user is None and position is None:
        raise ValidationError("Структура заполнена. Нет свободных мест для размещения нового партнера.")
    
    # Определяем уровень
    if parent_user is None:
        # Это корневой пользователь (структура пуста)
        level = 0
        position = 1  # Корень всегда имеет позицию 1
    else:
        try:
            parent_node = StructureNode.objects.get(user=parent_user)
            level = parent_node.level + 1
        except StructureNode.DoesNotExist:
            raise ValidationError(f"Родительский узел для пользователя {parent_user.username} не найден")
    
    # Создаем узел структуры
    structure_node = StructureNode.objects.create(
        user=user,
        parent=parent_user,
        position=position or 1,  # Если корень, позиция 1
        level=level,
        tariff=tariff
    )
    
    return structure_node


def get_structure_tree(root_user=None, max_depth=None):
    """
    Получить дерево структуры для визуализации.
    
    Args:
        root_user: Корневой пользователь (если None - первый корневой)
        max_depth: Максимальная глубина (если None - без ограничений)
    
    Returns:
        dict: Дерево структуры
    """
    if root_user is None:
        # Находим корневой узел
        root_node = StructureNode.objects.filter(level=0).first()
        if not root_node:
            return None
        root_user = root_node.user
    
    def build_tree(node_user, current_depth=0):
        """Рекурсивно строим дерево."""
        if max_depth is not None and current_depth >= max_depth:
            return None
        
        try:
            node = StructureNode.objects.get(user=node_user)
        except StructureNode.DoesNotExist:
            return None
        
        # Получаем детей
        children_nodes = StructureNode.objects.filter(
            parent=node_user
        ).select_related('user', 'tariff').order_by('position')
        
        children = []
        for child_node in children_nodes:
            child_tree = build_tree(child_node.user, current_depth + 1)
            children.append({
                'user': {
                    'id': child_node.user.id,
                    'username': child_node.user.username,
                    'referral_code': child_node.user.referral_code,
                },
                'level': child_node.level,
                'position': child_node.position,
                'tariff': {
                    'code': child_node.tariff.code if child_node.tariff else None,
                    'name': child_node.tariff.name if child_node.tariff else None,
                } if child_node.tariff else None,
                'children': child_tree['children'] if child_tree else [],
            })
        
        return {
            'user': {
                'id': node.user.id,
                'username': node.user.username,
                'referral_code': node.user.referral_code,
            },
            'level': node.level,
            'position': node.position,
            'tariff': {
                'code': node.tariff.code if node.tariff else None,
                'name': node.tariff.name if node.tariff else None,
            } if node.tariff else None,
            'children': children,
        }
    
    return build_tree(root_user)

