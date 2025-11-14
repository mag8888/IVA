# Настройка Django Backend на Railway

## Текущая ситуация

У вас есть **3 сервиса**, которые должны быть настроены на Railway:

1. **Старый Node.js Backend** (`backend/`) - можно оставить или остановить
2. **Новый Django Backend** (`backend_django/`) - **ОСНОВНОЙ**, здесь работает Telegram бот
3. **React Frontend** (`frontend_react/`) - фронтенд

## Настройка Django Backend сервиса

### Шаг 1: Создайте новый сервис на Railway

1. В Railway Dashboard → ваш проект
2. Нажмите **"+ New"** → **"GitHub Repo"**
3. Выберите репозиторий: `mag8888/IVA`
4. **ВАЖНО**: В настройках сервиса установите:
   - **Service Name**: `iva-production` (или `django-backend`)
   - **Root Directory**: `backend_django` ⭐ **ГЛАВНОЕ!**
   - **Build Command**: (оставьте пустым, Railway определит автоматически)
   - **Start Command**: (оставьте пустым, используется из `railway.json`)

### Шаг 2: Переменные окружения для Django Backend

Добавьте следующие переменные в сервис `iva-production`:

```bash
# Обязательные
DATABASE_URL=<ваш_DATABASE_URL_из_PostgreSQL>
DJANGO_SECRET_KEY=md*3-haow%@+i(c=mrsk!%jywy9%x_*1yv^+t5yw3&y+qw01ne
DJANGO_DEBUG=False
RAILWAY_PUBLIC_DOMAIN=iva-production.up.railway.app

# Telegram Bot
TELEGRAM_BOT_TOKEN=<ваш_токен_бота>
TELEGRAM_WEBHOOK_URL=https://iva-production.up.railway.app/telegram/webhook/
TELEGRAM_WEBAPP_URL=https://iva-production.up.railway.app

# CORS
CORS_ALLOWED_ORIGINS=https://iva.up.railway.app
DJANGO_ALLOWED_HOSTS=iva-production.up.railway.app,iva.up.railway.app

# Опциональные (MLM настройки)
MAX_PARTNERS_PER_LEVEL=3
DEFAULT_GREEN_BONUS_PERCENT=50
DEFAULT_YELLOW_BONUS_PERCENT=50
```

### Шаг 3: Проверьте настройки сервиса

В настройках сервиса `iva-production`:

- ✅ **Root Directory**: `backend_django`
- ✅ **Port**: Railway установит автоматически (обычно 8080)
- ✅ **Healthcheck Path**: `/health/` (уже настроено в `railway.json`)

## Проверка работы

### 1. Проверьте логи Django сервиса

После деплоя в логах должно быть:

```
🚀 Starting Equilibrium MLM Backend...
📦 Collecting static files...
🔄 Applying migrations...
🌐 Starting Gunicorn...
✅ Telegram бот инициализирован
🚀 Настройка Telegram бота через Webhook...
📡 Webhook URL: https://iva-production.up.railway.app/telegram/webhook/
✅ Webhook установлен: https://iva-production.up.railway.app/telegram/webhook/
✅ Telegram бот настроен через Webhook
```

### 2. Проверьте healthcheck

```bash
curl https://iva-production.up.railway.app/health/
```

Должно вернуть:
```json
{"status": "ok", "message": "Equilibrium MLM backend is running"}
```

### 3. Проверьте webhook

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

Должно показать:
```json
{
  "ok": true,
  "result": {
    "url": "https://iva-production.up.railway.app/telegram/webhook/",
    "pending_update_count": 0
  }
}
```

## Что делать со старым Node.js Backend

### Вариант 1: Остановить (рекомендуется)

1. В Railway Dashboard → сервис `backend` (старый Node.js)
2. Settings → **Pause Service** или удалите сервис

### Вариант 2: Оставить, но отключить Telegram бота

В переменных окружения старого сервиса:
- Удалите `TELEGRAM_BOT_TOKEN`
- Или установите `DISABLE_TELEGRAM_BOT=true`

## Структура сервисов на Railway

```
Railway Project
│
├── PostgreSQL Service
│   └── DATABASE_URL (используется Django)
│
├── iva-production (Django Backend) ⭐
│   ├── Root Directory: backend_django
│   ├── Domain: iva-production.up.railway.app
│   └── Telegram Bot работает здесь
│
├── iva (React Frontend)
│   ├── Root Directory: frontend_react
│   ├── Domain: iva.up.railway.app
│   └── VITE_API_URL=https://iva-production.up.railway.app
│
└── backend (Node.js - старый, можно остановить)
    └── Root Directory: backend
```

## Если Django сервис не запускается

1. **Проверьте Root Directory**: должно быть `backend_django`
2. **Проверьте переменные окружения**: особенно `DATABASE_URL` и `TELEGRAM_BOT_TOKEN`
3. **Проверьте логи**: ищите ошибки в логах Railway
4. **Проверьте миграции**: если есть ошибки миграций, исправьте их

## Если бот не отвечает

1. Проверьте логи Django сервиса на наличие:
   - `✅ Telegram бот инициализирован`
   - `✅ Webhook установлен`
2. Проверьте webhook через API (см. выше)
3. Проверьте, что endpoint доступен:
   ```bash
   curl -X POST https://iva-production.up.railway.app/telegram/webhook/ \
     -H "Content-Type: application/json" \
     -d '{"update_id": 1}'
   ```

## Важно!

- **Django Backend** должен иметь Root Directory = `backend_django`
- **Frontend** должен иметь Root Directory = `frontend_react`
- **Старый Node.js Backend** можно остановить или оставить без Telegram бота

