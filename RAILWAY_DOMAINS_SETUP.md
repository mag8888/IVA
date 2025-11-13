# Настройка доменов на Railway

## Текущая конфигурация

- **Backend**: `iva-production.up.railway.app`
- **Frontend**: `iva.up.railway.app` (основной домен)

## Шаг 1: Настройка основного домена для Frontend

### На Railway:

1. Откройте **Frontend сервис** на Railway
2. Перейдите в **Settings** → **Networking**
3. В разделе **Custom Domain**:
   - Если домен уже настроен, проверьте, что он указывает на `iva.up.railway.app`
   - Если нет, Railway автоматически создаст домен `iva.up.railway.app`

4. **Или используйте Railway Public Domain:**
   - Railway автоматически создает публичный домен для каждого сервиса
   - Проверьте, что Frontend сервис имеет домен `iva.up.railway.app`

## Шаг 2: Настройка переменных окружения

### Frontend сервис (`iva.up.railway.app`):

Добавьте переменную окружения:
```
VITE_API_URL=https://iva-production.up.railway.app
```

### Backend сервис (`iva-production.up.railway.app`):

Добавьте переменные окружения:
```
RAILWAY_PUBLIC_DOMAIN=iva-production.up.railway.app
DJANGO_ALLOWED_HOSTS=iva-production.up.railway.app,iva.up.railway.app
CORS_ALLOWED_ORIGINS=https://iva.up.railway.app
```

## Шаг 3: Настройка CORS в Django

CORS уже настроен в `backend_django/equilibrium_backend/settings.py`:
- Разрешены запросы с `iva.up.railway.app`
- Разрешены все домены (для разработки)

## Шаг 4: Проверка работы

1. **Frontend**: Откройте `https://iva.up.railway.app`
2. **Backend API**: Проверьте `https://iva-production.up.railway.app/api/status/`
3. **Health check**: `https://iva-production.up.railway.app/health/`

## Шаг 5: Настройка Telegram Webhook

В Backend сервисе добавьте:
```
TELEGRAM_WEBHOOK_URL=https://iva-production.up.railway.app/telegram/webhook/
TELEGRAM_WEBAPP_URL=https://iva-production.up.railway.app
```

## Проверка

После настройки проверьте:

1. ✅ Frontend открывается по `https://iva.up.railway.app`
2. ✅ Frontend может делать запросы к Backend API
3. ✅ Backend отвечает на запросы с Frontend (нет CORS ошибок)
4. ✅ Telegram webhook работает

## Если есть проблемы

### CORS ошибки:
- Проверьте `CORS_ALLOWED_ORIGINS` в Backend
- Убедитесь, что используется HTTPS
- Проверьте, что домены указаны без слэша в конце

### Frontend не подключается к API:
- Проверьте `VITE_API_URL` в Frontend
- Убедитесь, что Backend доступен по `iva-production.up.railway.app`
- Проверьте логи Backend на ошибки

