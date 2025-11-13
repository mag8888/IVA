# Equilibrium MLM Backend (Django)

## Структура проекта

```
backend_django/
├── equilibrium_backend/    # Настройки проекта
│   ├── settings.py        # Конфигурация (все переменные изменяемые)
│   ├── urls.py            # Главный URL router
│   └── wsgi.py            # WSGI приложение
├── core/                  # Основные модели
│   ├── models.py          # User модель
│   └── admin.py           # Админ-панель
├── mlm/                   # MLM логика
│   ├── models.py          # StructureNode, Tariff
│   └── admin.py
├── billing/               # Платежи и бонусы
│   ├── models.py          # Payment, Bonus
│   └── admin.py
├── api/                   # REST API
│   ├── views.py           # API endpoints
│   └── urls.py
├── integrations/          # Внешние интеграции
│   └── telegram.py        # Telegram bot
├── requirements.txt       # Зависимости
└── manage.py              # Django management
```

## Установка и запуск

### Локальная разработка

```bash
# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver
```

## Переменные окружения

Все переменные изменяемые через `.env` или переменные окружения:

- `DJANGO_SECRET_KEY` - секретный ключ Django
- `DJANGO_DEBUG` - режим отладки (False для production)
- `DATABASE_URL` - URL базы данных
- `TELEGRAM_BOT_TOKEN` - токен Telegram бота
- `TELEGRAM_WEBAPP_URL` - URL веб-приложения
- `MAX_PARTNERS_PER_LEVEL` - максимум партнеров на уровень (по умолчанию 3)
- `DEFAULT_GREEN_BONUS_PERCENT` - процент зеленого бонуса (по умолчанию 50)
- `DEFAULT_YELLOW_BONUS_PERCENT` - процент желтого бонуса (по умолчанию 50)

## Текущий статус

✅ Базовая структура проекта
✅ Модели данных (User, Tariff, StructureNode, Payment, Bonus)
✅ Настройки Django
✅ Healthcheck endpoint

⏳ В разработке:
- MLM логика размещения
- Система бонусов
- REST API endpoints
- Telegram Bot
- Frontend

## Следующие шаги

1. Реализовать MLM логику размещения пользователей
2. Реализовать систему бонусов
3. Создать REST API endpoints
4. Интегрировать Telegram Bot
5. Создать Frontend

