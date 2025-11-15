"""
Django команда для автоматического создания администратора с паролем по умолчанию.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Автоматическое создание администратора с паролем по умолчанию'

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
            default='admin123',
            help='Пароль (по умолчанию: admin123)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        
        # Проверяем, существует ли уже пользователь
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'⚠️  Пользователь {username} уже существует')
            )
            # Обновляем пароль, если пользователь существует
            try:
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Пароль для пользователя {username} обновлен')
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Ошибка при обновлении пароля: {e}'))
            return
        
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                status=User.UserStatus.ADMIN,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Создан суперпользователь:\n'
                    f'   Username: {username}\n'
                    f'   Email: {email}\n'
                    f'   Password: {password}'
                )
            )
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))

