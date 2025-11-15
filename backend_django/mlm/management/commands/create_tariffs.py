"""
Django команда для создания тарифов.
Создает стандартные тарифы: $20, $50, $100, $500, $1000
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from mlm.models import Tariff
from decimal import Decimal


class Command(BaseCommand):
    help = 'Создание стандартных тарифов для MLM системы'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Обновить существующие тарифы',
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Создание тарифов для Equilibrium MLM System...')
        
        # Определяем тарифы
        tariffs_data = [
            {
                'code': 'tariff_20',
                'name': 'Тариф $20',
                'entry_amount': Decimal('20.00'),
            },
            {
                'code': 'tariff_50',
                'name': 'Тариф $50',
                'entry_amount': Decimal('50.00'),
            },
            {
                'code': 'tariff_100',
                'name': 'Тариф $100',
                'entry_amount': Decimal('100.00'),
            },
            {
                'code': 'tariff_500',
                'name': 'Тариф $500',
                'entry_amount': Decimal('500.00'),
            },
            {
                'code': 'tariff_1000',
                'name': 'Тариф $1000',
                'entry_amount': Decimal('1000.00'),
            },
        ]
        
        # Получаем проценты бонусов из настроек
        green_bonus_percent = settings.MLM_SETTINGS.get('DEFAULT_GREEN_BONUS_PERCENT', 50)
        yellow_bonus_percent = settings.MLM_SETTINGS.get('DEFAULT_YELLOW_BONUS_PERCENT', 50)
        
        created_count = 0
        updated_count = 0
        
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
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Создан тариф: {tariff.name} (${tariff.entry_amount})'
                    )
                )
            else:
                if options['update']:
                    # Обновляем существующий тариф
                    tariff.name = tariff_data['name']
                    tariff.entry_amount = tariff_data['entry_amount']
                    tariff.green_bonus_percent = green_bonus_percent
                    tariff.yellow_bonus_percent = yellow_bonus_percent
                    tariff.is_active = True
                    tariff.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'🔄 Обновлен тариф: {tariff.name} (${tariff.entry_amount})'
                        )
                    )
                else:
                    self.stdout.write(
                        f'ℹ️  Тариф уже существует: {tariff.name} (${tariff.entry_amount})'
                    )
        
        # Итоговая статистика
        total_tariffs = Tariff.objects.filter(is_active=True).count()
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Тарифы созданы/обновлены!'))
        self.stdout.write(f'📊 Статистика:')
        self.stdout.write(f'   - Создано новых: {created_count}')
        if options['update']:
            self.stdout.write(f'   - Обновлено: {updated_count}')
        self.stdout.write(f'   - Всего активных тарифов: {total_tariffs}')
        
        # Выводим список всех активных тарифов
        self.stdout.write('')
        self.stdout.write('📋 Активные тарифы:')
        active_tariffs = Tariff.objects.filter(is_active=True).order_by('entry_amount')
        for tariff in active_tariffs:
            self.stdout.write(
                f'   • {tariff.name} - ${tariff.entry_amount} '
                f'(Зеленый: {tariff.green_bonus_percent}%, Желтый: {tariff.yellow_bonus_percent}%)'
            )

