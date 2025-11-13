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
        
        # 1. Создаем базовые тарифы
        self.stdout.write('📋 Создание тарифов...')
        
        basic_tariff, created = Tariff.objects.get_or_create(
            code='basic',
            defaults={
                'name': 'Basic',
                'entry_amount': 100.00,
                'green_bonus_percent': 50,
                'yellow_bonus_percent': 50,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Создан тариф: {basic_tariff.name}'))
        else:
            self.stdout.write(f'ℹ️  Тариф уже существует: {basic_tariff.name}')
        
        premium_tariff, created = Tariff.objects.get_or_create(
            code='premium',
            defaults={
                'name': 'Premium',
                'entry_amount': 500.00,
                'green_bonus_percent': 50,
                'yellow_bonus_percent': 50,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Создан тариф: {premium_tariff.name}'))
        else:
            self.stdout.write(f'ℹ️  Тариф уже существует: {premium_tariff.name}')
        
        self.stdout.write(self.style.SUCCESS('✅ Инициализация завершена!'))

