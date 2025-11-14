# Проверка переменных окружения для Django Backend

## ❌ Проблема: DISABLE_TELEGRAM_BOT

В переменных окружения видно:
- `DISABLE_TELEGRAM_BOT` = токен бота (это неправильно!)

**Это блокирует запуск Telegram бота!**

## ✅ Исправление

### 1. Исправьте DISABLE_TELEGRAM_BOT

В Railway Dashboard → сервис "IVA" → "Variables":

**Вариант А (рекомендуется): Удалите переменную**
- Нажмите на три точки справа от `DISABLE_TELEGRAM_BOT`
- Выберите "Delete"
- Бот будет работать автоматически

**Вариант Б: Установите правильное значение**
- Измените значение `DISABLE_TELEGRAM_BOT` на: `false`
- Или удалите переменную полностью

### 2. Добавьте недостающую переменную

Проверьте, есть ли переменная `RAILWAY_PUBLIC_DOMAIN`:

1. Откройте "Variables" → "+ New Variable"
2. Добавьте:
   ```
   RAILWAY_PUBLIC_DOMAIN = iva-production.up.railway.app
   ```
   (или домен, который Railway назначил вашему сервису)

### 3. Проверьте TELEGRAM_WEBHOOK_URL

Убедитесь, что `TELEGRAM_WEBHOOK_URL` указывает на правильный домен:
- Если домен сервиса: `iva-production.up.railway.app`
- То webhook должен быть: `https://iva-production.up.railway.app/telegram/webhook/`

## Полный список необходимых переменных

### Обязательные:

```bash
# 1. База данных
DATABASE_URL = <скопировано из Postgres>

# 2. Django
DJANGO_SECRET_KEY = md*3-haow%@+i(c=mrsk!%jywy9%x_*1yv^+t5yw3&y+qw01ne
DJANGO_DEBUG = False
RAILWAY_PUBLIC_DOMAIN = iva-production.up.railway.app  ⭐ ДОБАВЬТЕ ЭТО

# 3. Telegram Bot
TELEGRAM_BOT_TOKEN = <ваш_токен>
TELEGRAM_WEBHOOK_URL = https://iva-production.up.railway.app/telegram/webhook/
TELEGRAM_WEBAPP_URL = https://iva-production.up.railway.app

# 4. CORS и Hosts
CORS_ALLOWED_ORIGINS = https://iva.up.railway.app
DJANGO_ALLOWED_HOSTS = iva-production.up.railway.app,iva.up.railway.app

# 5. DISABLE_TELEGRAM_BOT - УДАЛИТЕ или установите = false
```

## Проверка после исправления

1. **Удалите или исправьте `DISABLE_TELEGRAM_BOT`**
2. **Добавьте `RAILWAY_PUBLIC_DOMAIN`**
3. **Перезапустите деплой** (Railway сделает это автоматически)
4. **Проверьте логи** - должно быть:
   ```
   ✅ Telegram бот инициализирован
   ✅ Webhook установлен
   ```

## Как узнать правильный домен

1. Откройте сервис "IVA" → "Settings"
2. Найдите раздел "Networking" или "Domains"
3. Скопируйте домен (например: `iva-production.up.railway.app`)
4. Используйте его в:
   - `RAILWAY_PUBLIC_DOMAIN`
   - `TELEGRAM_WEBHOOK_URL`
   - `DJANGO_ALLOWED_HOSTS`

