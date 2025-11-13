"""
API Views для REST API.
Все расчеты и размещение происходят на сервере.
"""
import secrets
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
@permission_classes([IsAuthenticated])
def complete(request):
    """
    Завершить регистрацию партнера.
    Все расчеты и размещение на сервере.
    """
    serializer = CompleteRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_id = serializer.validated_data['user_id']
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "Пользователь не найден"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Получаем pending платеж
    try:
        payment = Payment.objects.get(
            user=user,
            status=Payment.PaymentStatus.PENDING
        )
    except Payment.DoesNotExist:
        return Response(
            {"error": "Ожидающий платеж не найден"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        with transaction.atomic():
            # 1. Завершаем платеж
            payment.mark_completed()
            
            # 2. Меняем статус пользователя на PARTNER
            user.status = User.UserStatus.PARTNER
            user.save()
            
            # 3. Размещаем пользователя в структуре (на сервере)
            structure_node = place_user(user, payment)
            
            # 4. Начисляем бонусы (на сервере, согласно БД)
            bonuses = apply_signup_bonuses(user, payment)
            
            return Response({
                "detail": "Регистрация завершена",
                "placement_parent": structure_node.parent.username if structure_node.parent else None,
                "level": structure_node.level,
                "position": structure_node.position,
                "bonuses_created": len(bonuses),
            }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": str(e)},
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


@api_view(['GET'])
@permission_classes([AllowAny])
def tariffs(request):
    """
    Получить все активные тарифы.
    """
    tariffs_list = Tariff.objects.filter(is_active=True)
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
