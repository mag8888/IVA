"""
Django команда для автоматической инициализации системы.
Создает корневого пользователя и базовые тарифы.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from mlm.models import Tariff

User = get_user_model()


class Command(BaseCommand):
    help = 'Автоматическая инициализация системы MLM'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Инициализация Equilibrium MLM System...')
        
        # 1. Создаем стандартные тарифы
        self.stdout.write('📋 Создание тарифов...')
        
        from decimal import Decimal
        from django.conf import settings
        
        # Получаем проценты бонусов из настроек
        green_bonus_percent = settings.MLM_SETTINGS.get('DEFAULT_GREEN_BONUS_PERCENT', 50)
        yellow_bonus_percent = settings.MLM_SETTINGS.get('DEFAULT_YELLOW_BONUS_PERCENT', 50)
        
        # Определяем стандартные тарифы
        tariffs_data = [
            {'code': 'tariff_20', 'name': 'Тариф $20', 'entry_amount': Decimal('20.00')},
            {'code': 'tariff_50', 'name': 'Тариф $50', 'entry_amount': Decimal('50.00')},
            {'code': 'tariff_100', 'name': 'Тариф $100', 'entry_amount': Decimal('100.00')},
            {'code': 'tariff_500', 'name': 'Тариф $500', 'entry_amount': Decimal('500.00')},
            {'code': 'tariff_1000', 'name': 'Тариф $1000', 'entry_amount': Decimal('1000.00')},
        ]
        
        created_count = 0
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
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Создан тариф: {tariff.name} (${tariff.entry_amount})'))
            else:
                self.stdout.write(f'ℹ️  Тариф уже существует: {tariff.name} (${tariff.entry_amount})')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Инициализация завершена! Создано тарифов: {created_count}'))
        
        # Выводим список всех активных тарифов
        active_tariffs = Tariff.objects.filter(is_active=True).order_by('entry_amount')
        self.stdout.write(f'📋 Всего активных тарифов: {active_tariffs.count()}')
        for tariff in active_tariffs:
            self.stdout.write(f'   • {tariff.name} - ${tariff.entry_amount}')

