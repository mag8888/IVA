"""
Views для админ-панели.
"""
from django.shortcuts import render
from django.db.models import Sum, Count
from core.models import User
from mlm.models import StructureNode
from billing.models import Payment, Bonus


def dashboard(request):
    """
    Главная страница админ-панели с дашбордом.
    Все данные из базы данных.
    """
    # Статистика пользователей
    total_users = User.objects.count()
    participants = User.objects.filter(status=User.UserStatus.PARTICIPANT).count()
    partners = User.objects.filter(status=User.UserStatus.PARTNER).count()
    admins = User.objects.filter(status=User.UserStatus.ADMIN).count()
    
    # Статистика структуры
    total_nodes = StructureNode.objects.count()
    
    # Статистика платежей
    pending_payments = Payment.objects.filter(status=Payment.PaymentStatus.PENDING).count()
    completed_payments = Payment.objects.filter(status=Payment.PaymentStatus.COMPLETED).count()
    
    # Статистика бонусов (из БД)
    total_bonuses = Bonus.objects.aggregate(total=Sum('amount'))['total'] or 0
    green_bonuses = Bonus.objects.filter(
        bonus_type=Bonus.BonusType.GREEN
    ).aggregate(total=Sum('amount'))['total'] or 0
    yellow_bonuses = Bonus.objects.filter(
        bonus_type=Bonus.BonusType.YELLOW
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Последние регистрации
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Последние бонусы (из БД)
    recent_bonuses = Bonus.objects.select_related('user', 'source_user').order_by('-created_at')[:10]
    
    context = {
        'stats': {
            'users': {
                'total': total_users,
                'participants': participants,
                'partners': partners,
                'admins': admins,
            },
            'structure': {
                'total_nodes': total_nodes,
            },
            'payments': {
                'pending': pending_payments,
                'completed': completed_payments,
            },
            'bonuses': {
                'total': float(total_bonuses),
                'green': float(green_bonuses),
                'yellow': float(yellow_bonuses),
            },
        },
        'recent_users': recent_users,
        'recent_bonuses': recent_bonuses,
    }
    
    return render(request, 'admin/dashboard.html', context)


def structure_view(request):
    """
    Визуализация MLM структуры.
    Данные из базы данных.
    """
    return render(request, 'admin/structure.html')


def queue_view(request):
    """
    Очередь регистраций.
    Данные из базы данных.
    """
    return render(request, 'admin/queue.html')

