"""
Django команда для создания суперпользователя.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Создание root администратора'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Имя пользователя (по умолчанию: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@equilibrium.com',
            help='Email (по умолчанию: admin@equilibrium.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Пароль (если не указан, будет запрошен)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options.get('password')
        
        # Проверяем, существует ли уже пользователь
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'⚠️  Пользователь {username} уже существует')
            )
            return
        
        # Запрашиваем пароль, если не указан
        if not password:
            password = self.get_pass('Введите пароль: ')
            password_confirm = self.get_pass('Подтвердите пароль: ')
            
            if password != password_confirm:
                self.stdout.write(self.style.ERROR('❌ Пароли не совпадают!'))
                return
        
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                status=User.UserStatus.ADMIN,
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Создан суперпользователь: {username}')
            )
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))
    
    def get_pass(self, prompt='Password: '):
        """Безопасный ввод пароля."""
        import getpass
        return getpass.getpass(prompt)

