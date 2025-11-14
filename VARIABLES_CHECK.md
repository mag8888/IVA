# Проверка переменных окружения - Найденные проблемы

## ❌ Проблема 1: Несоответствие доменов

В переменных окружения видно несоответствие:

- `RAILWAY_PUBLIC_DOMAIN` = `iva-production.up.railway.app`
- `TELEGRAM_WEBAPP_URL` = `https://django-backend.up.railway.app` ❌
- `TELEGRAM_WEBHOOK_URL` = `https://django-backend.up.railway.app/telegram/webhook/` ❌
- `CORS_ALLOWED_ORIGINS` = `https://iva-production.up.railway.app/`

**Проблема:** Домены не совпадают! `RAILWAY_PUBLIC_DOMAIN` указывает на `iva-production`, а webhook/webapp указывают на `django-backend`.

## ✅ Исправление

### Вариант 1: Использовать домен `iva-production` (рекомендуется)

Измените переменные в Railway → сервис "IVA" → Variables:

1. **TELEGRAM_WEBAPP_URL:**
   - Было: `https://django-backend.up.railway.app`
   - Должно быть: `https://iva-production.up.railway.app`

2. **TELEGRAM_WEBHOOK_URL:**
   - Было: `https://django-backend.up.railway.app/telegram/webhook/`
   - Должно быть: `https://iva-production.up.railway.app/telegram/webhook/`

3. **DJANGO_ALLOWED_HOSTS:**
   - Должно быть: `iva-production.up.railway.app,iva.up.railway.app`
   - (Убедитесь, что оба домена указаны)

### Вариант 2: Использовать домен `django-backend`

Если ваш сервис действительно называется `django-backend`:

1. **RAILWAY_PUBLIC_DOMAIN:**
   - Измените на: `django-backend.up.railway.app`

2. **CORS_ALLOWED_ORIGINS:**
   - Измените на: `https://iva.up.railway.app` (без слэша в конце!)

## ❌ Проблема 2: Слэш в конце CORS_ALLOWED_ORIGINS

- Текущее значение: `https://iva-production.up.railway.app/` (слэш в конце)
- Должно быть: `https://iva-production.up.railway.app` (без слэша)

Или, если фронтенд на другом домене:
- `https://iva.up.railway.app` (без слэша)

## ❌ Проблема 3: DISABLE_TELEGRAM_BOT

Проверьте, есть ли переменная `DISABLE_TELEGRAM_BOT`:
- Если есть и значение не `false` - **УДАЛИТЕ** эту переменную
- Или установите значение: `false`

## ✅ Правильная конфигурация (если домен `iva-production`)

```bash
# Домены
RAILWAY_PUBLIC_DOMAIN = iva-production.up.railway.app
DJANGO_ALLOWED_HOSTS = iva-production.up.railway.app,iva.up.railway.app

# Telegram
TELEGRAM_BOT_TOKEN = <ваш_токен>
TELEGRAM_WEBAPP_URL = https://iva-production.up.railway.app
TELEGRAM_WEBHOOK_URL = https://iva-production.up.railway.app/telegram/webhook/

# CORS
CORS_ALLOWED_ORIGINS = https://iva.up.railway.app
# (без слэша в конце!)

# Django
DJANGO_SECRET_KEY = md*3-haow%@+i(c=mrsk!%jywy9%x_*1yv^+t5yw3&y+qw01ne
DJANGO_DEBUG = False
DATABASE_URL = <из_Postgres>
```

## 🔍 Как узнать правильный домен

1. Railway Dashboard → сервис "IVA" → **Settings**
2. Найдите раздел **"Networking"** или **"Domains"**
3. Скопируйте домен, который Railway назначил вашему сервису
4. Используйте этот домен во всех переменных

## ✅ После исправления

1. **Сохраните все переменные**
2. Railway автоматически перезапустит деплой
3. Проверьте логи - должно быть:
   ```
   ✅ Telegram бот инициализирован
   ✅ Webhook установлен: https://правильный-домен/telegram/webhook/
   ```

4. **Проверьте webhook:**
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
   ```
   Должен показать правильный URL

