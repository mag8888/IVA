import random
import string
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import User
from mlm.models import Tariff, StructureNode
from billing.models import Payment
from mlm.services import place_user


class Command(BaseCommand):
    help = "Создает тестовое MLM-дерево для визуализации и интеграций."

    def add_arguments(self, parser):
        parser.add_argument(
            "--root-username",
            dest="root_username",
            default=None,
            help="Имя пользователя, который станет корнем дерева. "
                 "Если не указано — используется первый суперпользователь или создается новый.",
        )
        parser.add_argument(
            "--children",
            dest="children",
            type=int,
            default=6,
            help="Количество тестовых партнеров, которых нужно сгенерировать.",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            root_user = self._get_or_create_root_user(options["root_username"])
            tariff = self._get_or_create_tariff()
            self._ensure_root_structure(root_user, tariff)
            created_users = self._create_demo_partners(root_user, tariff, options["children"])

        self.stdout.write(self.style.SUCCESS("Тестовое дерево структуры успешно создано"))
        self.stdout.write(self.style.SUCCESS(f"Корневой пользователь: {root_user.username}"))
        if created_users:
            self.stdout.write(self.style.SUCCESS(f"Добавлены партнеры: {', '.join(created_users)}"))
        else:
            self.stdout.write(self.style.WARNING("Новые партнеры не были созданы (children=0)."))

    def _get_or_create_root_user(self, preferred_username: str | None) -> User:
        """
        Возвращает пользователя, который будет корнем структуры.
        """
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

    def _get_or_create_tariff(self) -> Tariff:
        tariff, _ = Tariff.objects.get_or_create(
            code="basic",
            defaults={
                "name": "Basic",
                "entry_amount": Decimal("100.00"),
                "green_bonus_percent": 50,
                "yellow_bonus_percent": 50,
            },
        )
        return tariff

    def _ensure_root_structure(self, root_user: User, tariff: Tariff) -> None:
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

    def _create_demo_partners(self, root_user: User, tariff: Tariff, count: int):
        created_usernames = []
        for index in range(count):
            username = self._generate_username(index)
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
            created_usernames.append(username)
        return created_usernames

    def _generate_username(self, seed: int) -> str:
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"demo_partner_{seed+1}_{suffix}"

