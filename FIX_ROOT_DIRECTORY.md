# Исправление Root Directory

## Проблема

В настройках сервиса "IVA" указано:
- **Root Directory**: `/backend_django` ❌ (с ведущим слэшем)

## Решение

### Измените Root Directory

1. В Railway Dashboard → сервис "IVA" → вкладка **"Settings"**
2. Найдите раздел **"Source"** → **"Root Directory"**
3. Измените значение с `/backend_django` на: `backend_django` (без ведущего слэша)
4. Нажмите **"Save"** или изменения сохранятся автоматически
5. Railway автоматически перезапустит деплой

### Правильный формат

- ❌ Неправильно: `/backend_django`
- ✅ Правильно: `backend_django`

## После исправления

1. Railway начнет новый деплой
2. В логах должно появиться:
   ```
   Building Docker image...
   ✅ Found Dockerfile in backend_django/
   ```

3. Если деплой все еще падает, проверьте:
   - Root Directory = `backend_django` (без слэша)
   - Переменные окружения добавлены (см. ниже)
   - DATABASE_URL скопирован из Postgres сервиса

## Переменные окружения для сервиса "IVA"

Убедитесь, что в сервисе "IVA" добавлены все необходимые переменные:

1. Откройте сервис "IVA" → вкладка **"Variables"**
2. Добавьте переменные (если их нет):

```bash
# 1. База данных (скопируйте из Postgres сервиса)
DATABASE_URL = <скопируйте из Postgres>

# 2. Django настройки
DJANGO_SECRET_KEY = md*3-haow%@+i(c=mrsk!%jywy9%x_*1yv^+t5yw3&y+qw01ne
DJANGO_DEBUG = False
RAILWAY_PUBLIC_DOMAIN = iva-production.up.railway.app

# 3. Telegram Bot
TELEGRAM_BOT_TOKEN = <ваш_токен>
TELEGRAM_WEBHOOK_URL = https://iva-production.up.railway.app/telegram/webhook/
TELEGRAM_WEBAPP_URL = https://iva-production.up.railway.app

# 4. CORS
CORS_ALLOWED_ORIGINS = https://iva.up.railway.app
DJANGO_ALLOWED_HOSTS = iva-production.up.railway.app,iva.up.railway.app
```

## Проверка

После исправления Root Directory и добавления переменных:

1. Дождитесь завершения деплоя
2. Проверьте логи - не должно быть ошибок
3. Проверьте healthcheck:
   ```bash
   curl https://iva-production.up.railway.app/health/
   ```
4. Проверьте webhook:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
   ```

