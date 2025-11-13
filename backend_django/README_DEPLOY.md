# Развертывание Equilibrium MLM на Railway

## Структура проекта

```
Equilibrium/
├── backend_django/      # Django Backend
│   ├── Dockerfile
│   ├── start.sh
│   ├── railway.json
│   └── ...
├── frontend_react/      # React Frontend
│   ├── Dockerfile
│   ├── railway.json
│   └── ...
└── ...
```

## Переменные окружения для Backend

### Обязательные:
- `DJANGO_SECRET_KEY` - секретный ключ Django
- `DATABASE_URL` - URL PostgreSQL базы данных
- `DJANGO_DEBUG=False` - режим production

### Опциональные:
- `TELEGRAM_BOT_TOKEN` - токен Telegram бота
- `TELEGRAM_WEBAPP_URL` - URL веб-приложения для Telegram
- `MAX_PARTNERS_PER_LEVEL=3` - максимум партнеров на уровень
- `DEFAULT_GREEN_BONUS_PERCENT=50` - процент зеленого бонуса
- `DEFAULT_YELLOW_BONUS_PERCENT=50` - процент желтого бонуса
- `RAILWAY_PUBLIC_DOMAIN` - публичный домен (автоматически)

## Переменные окружения для Frontend

- `VITE_API_URL` - URL Backend API (например: `https://backend.up.railway.app`)

## Развертывание на Railway

### 1. Backend сервис

1. Создайте новый сервис на Railway
2. Подключите репозиторий
3. Укажите Root Directory: `backend_django`
4. Добавьте переменные окружения (см. выше)
5. Railway автоматически соберет и запустит через Docker

### 2. Frontend сервис

1. Создайте новый сервис на Railway
2. Подключите тот же репозиторий
3. Укажите Root Directory: `frontend_react`
4. Добавьте переменную `VITE_API_URL` с URL Backend сервиса
5. Railway автоматически соберет и запустит через Docker

### 3. PostgreSQL сервис

1. Создайте PostgreSQL сервис на Railway
2. Подключите `DATABASE_URL` к Backend сервису через Reference Variable

## Проверка

После развертывания проверьте:

- Backend: `https://your-backend.railway.app/health/`
- Frontend: `https://your-frontend.railway.app/`
- API: `https://your-backend.railway.app/api/status/`

## Инициализация

После первого запуска:

```bash
# Создать тарифы
python manage.py auto_init

# Создать суперпользователя
python manage.py create_superuser
```

Или через Railway CLI:

```bash
railway run python manage.py auto_init
railway run python manage.py create_superuser
```

