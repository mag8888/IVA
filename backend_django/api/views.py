"""
API Views для REST API.
Все расчеты и размещение происходят на сервере.
"""
import secrets
import random
import string
import logging
from decimal import Decimal
from django.db import transaction, models
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.models import User
from mlm.models import StructureNode, Tariff
from mlm.services import place_user, get_structure_tree, get_active_tariff
from billing.models import Payment, Bonus
from billing.services import apply_signup_bonuses
from .serializers import (
    RegisterSerializer, CompleteRegistrationSerializer, QueueItemSerializer,
    StructureNodeSerializer, BonusSerializer, TariffSerializer
)

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_status(request):
    """Статус API."""
    return Response({
        "name": "Equilibrium API",
        "version": "0.1.0",
        "status": "ok"
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Регистрация нового партнера.
    Все расчеты на сервере.
    """
    serializer = RegisterSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Находим пригласившего по referral_code
    inviter = None
    if data.get('referral_code'):
        try:
            inviter = User.objects.get(referral_code=data['referral_code'])
        except User.DoesNotExist:
            return Response(
                {"error": "Реферальный код не найден"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Получаем тариф
    tariff_code = data.get('tariff_code')
    tariff = get_active_tariff(tariff_code)
    
    if not tariff:
        return Response(
            {"error": "Тариф не найден или неактивен"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        with transaction.atomic():
            # Генерируем временный пароль
            temporary_password = secrets.token_urlsafe(12)
            
            # Создаем пользователя
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=temporary_password,
                status=User.UserStatus.PARTICIPANT,
                invited_by=inviter,
            )
            
            # Создаем платеж
            payment = Payment.objects.create(
                user=user,
                tariff=tariff,
                amount=tariff.entry_amount,
                status=Payment.PaymentStatus.PENDING,
            )
            
            return Response({
                "id": user.id,
                "username": user.username,
                "temporary_password": temporary_password,
                "payment_id": payment.id,
            }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def queue(request):
    """
    Получить очередь регистраций.
    Только аутентифицированные пользователи.
    """
    # Получаем все pending платежи
    pending_payments = Payment.objects.filter(
        status=Payment.PaymentStatus.PENDING
    ).select_related('user', 'tariff', 'user__invited_by')
    
    queue_items = []
    for payment in pending_payments:
        user = payment.user
        inviter = user.invited_by
        
        queue_items.append({
            'id': payment.id,
            'user': user.id,
            'username': user.username,
            'email': user.email,
            'inviter': inviter.referral_code if inviter else None,
            'inviter_username': inviter.username if inviter else None,
            'tariff': {
                'code': payment.tariff.code,
                'name': payment.tariff.name,
                'entry_amount': str(payment.tariff.entry_amount),
            },
            'amount': payment.amount,
            'created_at': payment.created_at,
        })
    
    serializer = QueueItemSerializer(queue_items, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def queue_public(request):
    """
    Очередь для админ-панели (без аутентификации).
    """
    # Получаем все pending платежи
    pending_payments = Payment.objects.filter(
        status=Payment.PaymentStatus.PENDING
    ).select_related('user', 'tariff', 'user__invited_by')
    
    queue_items = []
    for payment in pending_payments:
        user = payment.user
        inviter = user.invited_by
        
        queue_items.append({
            'id': payment.id,
            'user': user.id,
            'username': user.username,
            'email': user.email,
            'inviter': inviter.referral_code if inviter else None,
            'inviter_username': inviter.username if inviter else None,
            'tariff': {
                'code': payment.tariff.code,
                'name': payment.tariff.name,
                'entry_amount': str(payment.tariff.entry_amount),
            },
            'amount': payment.amount,
            'created_at': payment.created_at,
        })
    
    serializer = QueueItemSerializer(queue_items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])  # Изменено на AllowAny для публичного доступа
def complete(request):
    """
    Завершить регистрацию партнера.
    Все расчеты и размещение на сервере.
    """
    serializer = CompleteRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.error(f"❌ Ошибка валидации: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_id = serializer.validated_data['user_id']
    logger.info(f"🔄 Завершение регистрации для пользователя {user_id}")
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"❌ Пользователь {user_id} не найден")
        return Response(
            {"error": f"Пользователь с ID {user_id} не найден"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Проверяем, размещен ли пользователь уже в структуре
    from mlm.models import StructureNode
    if StructureNode.objects.filter(user=user).exists():
        logger.warning(f"⚠️ Пользователь {user.username} уже размещен в структуре")
        return Response(
            {"error": f"Пользователь {user.username} уже размещен в структуре. Регистрация уже завершена."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Получаем pending платеж
    try:
        payment = Payment.objects.get(
            user=user,
            status=Payment.PaymentStatus.PENDING
        )
        logger.info(f"✅ Найден pending платеж {payment.id} для пользователя {user.username}")
    except Payment.DoesNotExist:
        # Проверяем, есть ли завершенный платеж
        completed_payment = Payment.objects.filter(
            user=user,
            status=Payment.PaymentStatus.COMPLETED
        ).first()
        
        if completed_payment:
            logger.warning(f"⚠️ Платеж уже завершен для пользователя {user.username}")
            return Response(
                {"error": f"Платеж уже завершен. Пользователь должен быть размещен в структуре."},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            logger.error(f"❌ Ожидающий платеж не найден для пользователя {user.username}")
            return Response(
                {"error": f"Ожидающий платеж не найден для пользователя {user.username}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        with transaction.atomic():
            # 1. Завершаем платеж
            logger.info(f"🔄 Завершаем платеж {payment.id}")
            payment.mark_completed()
            
            # 2. Меняем статус пользователя на PARTNER
            if user.status == User.UserStatus.PARTICIPANT:
                logger.info(f"🔄 Меняем статус пользователя {user.username} на PARTNER")
                user.status = User.UserStatus.PARTNER
                user.save()
            else:
                logger.info(f"ℹ️ Статус пользователя {user.username} уже {user.get_status_display()}")
            
            # 3. Размещаем пользователя в структуре (на сервере)
            try:
                logger.info(f"🔄 Размещаем пользователя {user.username} в структуре")
                structure_node = place_user(user, payment)
                logger.info(f"✅ Пользователь {user.username} размещен: Level {structure_node.level}, Position {structure_node.position}")
            except Exception as place_error:
                logger.error(f"❌ Ошибка при размещении пользователя {user.username} в структуре: {place_error}")
                # Если размещение не удалось, продолжаем и начисляем бонусы
                structure_node = None
            
            # 4. Начисляем бонусы (на сервере, согласно БД)
            try:
                logger.info(f"🔄 Начисляем бонусы для пользователя {user.username}")
                bonuses = apply_signup_bonuses(user, payment)
                logger.info(f"✅ Начислено бонусов: {len(bonuses)}")
            except Exception as bonus_error:
                logger.error(f"❌ Ошибка при начислении бонусов: {bonus_error}")
                bonuses = []
            
            response_data = {
                "detail": "Регистрация завершена",
                "bonuses_created": len(bonuses),
            }
            
            if structure_node:
                response_data.update({
                    "placement_parent": structure_node.parent.username if structure_node.parent else None,
                    "level": structure_node.level,
                    "position": structure_node.position,
                })
            else:
                response_data["warning"] = "Пользователь не был размещен в структуре (возможно, структура заполнена или произошла ошибка)"
            
            logger.info(f"✅ Регистрация завершена для пользователя {user.username}")
            return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при завершении регистрации: {e}", exc_info=True)
        return Response(
            {"error": f"Ошибка завершения регистрации: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def structure(request):
    """
    Получить структуру MLM.
    Данные из базы данных.
    """
    # Получаем все узлы структуры
    nodes = StructureNode.objects.select_related('user', 'parent', 'tariff').all()
    
    serializer = StructureNodeSerializer(nodes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def structure_tree(request):
    """
    Получить дерево структуры для визуализации.
    Данные из базы данных.
    """
    root_user_id = request.query_params.get('root_user_id', None)
    max_depth = request.query_params.get('max_depth', None)
    
    root_user = None
    if root_user_id:
        try:
            root_user = User.objects.get(id=root_user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    max_depth_int = int(max_depth) if max_depth else None
    
    tree = get_structure_tree(root_user, max_depth_int)
    
    if tree is None:
        return Response({"error": "Структура пуста"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(tree)


@api_view(['GET'])
@permission_classes([AllowAny])
def bonuses(request):
    """
    Получить все бонусы из базы данных.
    """
    user_id = request.query_params.get('user_id', None)
    
    if user_id:
        bonuses_list = Bonus.objects.filter(user_id=user_id).select_related(
            'user', 'source_user', 'payment'
        )
    else:
        bonuses_list = Bonus.objects.all().select_related(
            'user', 'source_user', 'payment'
        )
    
    serializer = BonusSerializer(bonuses_list, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def tariffs(request):
    """
    Получить все активные тарифы или создать новые.
    """
    if request.method == 'POST':
        # Создание тарифов через API
        try:
            from django.conf import settings
            
            # Получаем проценты бонусов из настроек
            green_bonus_percent = settings.MLM_SETTINGS.get('DEFAULT_GREEN_BONUS_PERCENT', 50)
            yellow_bonus_percent = settings.MLM_SETTINGS.get('DEFAULT_YELLOW_BONUS_PERCENT', 50)
            
            # Стандартные тарифы
            tariffs_data = [
                {'code': 'tariff_20', 'name': 'Тариф $20', 'entry_amount': Decimal('20.00')},
                {'code': 'tariff_50', 'name': 'Тариф $50', 'entry_amount': Decimal('50.00')},
                {'code': 'tariff_100', 'name': 'Тариф $100', 'entry_amount': Decimal('100.00')},
                {'code': 'tariff_500', 'name': 'Тариф $500', 'entry_amount': Decimal('500.00')},
                {'code': 'tariff_1000', 'name': 'Тариф $1000', 'entry_amount': Decimal('1000.00')},
            ]
            
            created_tariffs = []
            updated_tariffs = []
            
            with transaction.atomic():
                for tariff_data in tariffs_data:
                    tariff, created = Tariff.objects.get_or_create(
                        code=tariff_data['code'],
                        defaults={
                            'name': tariff_data['name'],
                            'entry_amount': tariff_data['entry_amount'],
                            'green_bonus_percent': green_bonus_percent,
                            'yellow_bonus_percent': yellow_bonus_percent,
                            'is_active': True,
                        }
                    )
                    
                    if created:
                        created_tariffs.append(tariff)
                    else:
                        # Обновляем существующий тариф
                        tariff.name = tariff_data['name']
                        tariff.entry_amount = tariff_data['entry_amount']
                        tariff.green_bonus_percent = green_bonus_percent
                        tariff.yellow_bonus_percent = yellow_bonus_percent
                        tariff.is_active = True
                        tariff.save()
                        updated_tariffs.append(tariff)
            
            serializer = TariffSerializer(created_tariffs + updated_tariffs, many=True)
            
            return Response({
                "success": True,
                "message": f"Создано тарифов: {len(created_tariffs)}, Обновлено: {len(updated_tariffs)}",
                "created": len(created_tariffs),
                "updated": len(updated_tariffs),
                "tariffs": serializer.data,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # GET запрос - получить все активные тарифы
    tariffs_list = Tariff.objects.filter(is_active=True).order_by('entry_amount')
    serializer = TariffSerializer(tariffs_list, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def stats(request):
    """
    Получить статистику системы.
    Все данные из базы данных.
    """
    total_users = User.objects.count()
    participants = User.objects.filter(status=User.UserStatus.PARTICIPANT).count()
    partners = User.objects.filter(status=User.UserStatus.PARTNER).count()
    admins = User.objects.filter(status=User.UserStatus.ADMIN).count()
    
    total_nodes = StructureNode.objects.count()
    pending_payments = Payment.objects.filter(status=Payment.PaymentStatus.PENDING).count()
    
    total_bonuses = Bonus.objects.aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    green_bonuses = Bonus.objects.filter(bonus_type=Bonus.BonusType.GREEN).aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    yellow_bonuses = Bonus.objects.filter(bonus_type=Bonus.BonusType.YELLOW).aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    return Response({
        "users": {
            "total": total_users,
            "participants": participants,
            "partners": partners,
            "admins": admins,
        },
        "structure": {
            "total_nodes": total_nodes,
        },
        "payments": {
            "pending": pending_payments,
        },
        "bonuses": {
            "total": float(total_bonuses),
            "green": float(green_bonuses),
            "yellow": float(yellow_bonuses),
        },
    })


def _get_or_create_root_user(preferred_username=None):
    """Возвращает пользователя, который будет корнем структуры."""
    if preferred_username:
        user, _ = User.objects.get_or_create(
            username=preferred_username,
            defaults={
                "email": f"{preferred_username}@example.com",
                "status": User.UserStatus.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        return user

    user = User.objects.filter(is_superuser=True).first()
    if user:
        return user

    # Создаем нового суперпользователя
    return User.objects.create_superuser(
        username="root_admin",
        email="root@example.com",
        password="root_admin_pass",
    )


def _get_or_create_tariff():
    """Создает или получает тариф."""
    tariff, _ = Tariff.objects.get_or_create(
        code="basic",
        defaults={
            "name": "Basic",
            "entry_amount": Decimal("100.00"),
            "green_bonus_percent": 50,
            "yellow_bonus_percent": 50,
            "is_active": True,
        },
    )
    return tariff


def _ensure_root_structure(root_user, tariff):
    """Создает корневой узел, если его еще нет."""
    StructureNode.objects.get_or_create(
        user=root_user,
        defaults={
            "parent": None,
            "position": 1,
            "level": 0,
            "tariff": tariff,
        },
    )
    if root_user.status != User.UserStatus.PARTNER:
        root_user.status = User.UserStatus.PARTNER
        root_user.save(update_fields=["status"])


def _generate_username(seed):
    """Генерирует уникальное имя пользователя."""
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"demo_partner_{seed+1}_{suffix}"


def _create_demo_partners(root_user, tariff, count):
    """Создает тестовых партнеров."""
    created_usernames = []
    for index in range(count):
        username = _generate_username(index)
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": f"{username}@example.com",
                "status": User.UserStatus.PARTNER,
                "invited_by": root_user,
            },
        )
        if not created:
            continue

        payment = Payment.objects.create(
            user=user,
            tariff=tariff,
            amount=tariff.entry_amount,
            status=Payment.PaymentStatus.COMPLETED,
            completed_at=timezone.now(),
        )
        place_user(user, payment)
        # Начисляем бонусы
        apply_signup_bonuses(user, payment)
        created_usernames.append(username)
    return created_usernames


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def generate_structure(request):
    """
    Генерирует тестовое MLM-дерево для визуализации.
    Можно вызвать через GET или POST запрос.
    """
    try:
        # Получаем параметры
        root_username = None
        children_count = 6
        
        if request.method == 'POST':
            root_username = request.data.get('root_username', None)
            children_count = request.data.get('children', 6)
        else:
            root_username = request.query_params.get('root_username', None)
            children_count = int(request.query_params.get('children', 6))
        
        with transaction.atomic():
            # 1. Получаем или создаем корневого пользователя
            root_user = _get_or_create_root_user(root_username)
            
            # 2. Получаем или создаем тариф
            tariff = _get_or_create_tariff()
            
            # 3. Создаем корневой узел, если его нет
            _ensure_root_structure(root_user, tariff)
            
            # 4. Создаем тестовых партнеров
            created_users = _create_demo_partners(root_user, tariff, children_count)
        
        # 5. Получаем статистику структуры
        total_nodes = StructureNode.objects.count()
        tree = get_structure_tree(root_user, max_depth=None)
        
        return Response({
            "success": True,
            "message": "Тестовое дерево структуры успешно создано",
            "root_user": {
                "id": root_user.id,
                "username": root_user.username,
                "referral_code": root_user.referral_code,
            },
            "created_partners": created_users,
            "total_nodes": total_nodes,
            "structure": tree,
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
