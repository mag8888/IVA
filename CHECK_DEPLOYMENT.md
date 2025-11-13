# Проверка работы приложения на Railway

## Текущая ситуация

✅ Frontend работает: https://iva.up.railway.app  
❓ Backend нужно проверить отдельно (у него свой URL)

## Проблема

По адресу `https://iva.up.railway.app` работает **Frontend** (Next.js), который показывает "Загрузка данных...". Это означает, что Frontend не может подключиться к Backend API.

## Что нужно проверить

### 1. Найти URL Backend сервиса

На Railway у каждого сервиса свой URL:

1. Откройте Railway dashboard
2. Найдите сервис **"IVA"** (Backend) - не Frontend!
3. Перейдите на вкладку **"Settings"**
4. Найдите секцию **"Networking"** или **"Domains"**
5. Скопируйте **Public URL** Backend сервиса
   - Обычно выглядит как: `https://iva-backend-xxxx.up.railway.app`
   - Или: `https://iva-production-xxxx.up.railway.app`

### 2. Проверить Backend напрямую

Откройте в браузере:
```
https://[URL_BACKEND]/health
```

Должно вернуть:
```json
{"status":"ok","timestamp":"2025-01-13T..."}
```

### 3. Проверить API Backend

Проверьте endpoints:
- `https://[URL_BACKEND]/api/stats` - статистика
- `https://[URL_BACKEND]/api/users` - пользователи
- `https://[URL_BACKEND]/api/messages` - сообщения

### 4. Настроить Frontend для подключения к Backend

1. Откройте **Frontend сервис** на Railway
2. Перейдите на вкладку **"Variables"**
3. Проверьте переменную `NEXT_PUBLIC_API_URL`
4. Убедитесь, что значение = URL вашего Backend сервиса
   - Например: `https://iva-backend-xxxx.up.railway.app`
5. Если переменной нет или она неправильная:
   - Нажмите **"+ New"**
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: URL вашего Backend сервиса
   - Нажмите **"Add"**

### 5. Перезапустить Frontend

После изменения `NEXT_PUBLIC_API_URL`:
- Railway автоматически перезапустит Frontend
- Или нажмите **"Redeploy"** вручную

## Проверка работы с базой данных

### Через Backend API:

1. Откройте Backend URL в браузере:
   ```
   https://[URL_BACKEND]/api/stats
   ```

2. Должно вернуть:
   ```json
   {
     "users": 0,
     "messages": 0
   }
   ```

3. Если возвращает данные - БД работает! ✅

### Через Telegram бота:

1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Проверьте Backend API:
   ```
   https://[URL_BACKEND]/api/users
   ```
4. Должен появиться новый пользователь ✅

### Через Frontend:

1. Откройте https://iva.up.railway.app
2. После настройки `NEXT_PUBLIC_API_URL` должны отображаться:
   - Статистика (пользователи, сообщения)
   - Список пользователей
   - Список сообщений

## Типичные проблемы

### Проблема 1: Frontend показывает "Загрузка данных..."

**Причина**: Frontend не может подключиться к Backend

**Решение**:
- Проверьте `NEXT_PUBLIC_API_URL` в Frontend сервисе
- Убедитесь, что URL правильный и Backend доступен

### Проблема 2: Backend возвращает ошибки

**Причина**: Не подключена база данных

**Решение**:
- Проверьте `DATABASE_URL` в Backend сервисе
- Убедитесь, что PostgreSQL сервис запущен

### Проблема 3: 404 ошибки

**Причина**: Неправильный URL или сервис не запущен

**Решение**:
- Проверьте, что Backend сервис запущен (зеленая галочка)
- Проверьте правильность URL

## Чеклист проверки

- [ ] Backend сервис запущен на Railway
- [ ] Backend URL доступен (проверка `/health`)
- [ ] `DATABASE_URL` установлен в Backend сервисе
- [ ] Backend API работает (`/api/stats` возвращает данные)
- [ ] Frontend сервис запущен
- [ ] `NEXT_PUBLIC_API_URL` установлен в Frontend сервисе
- [ ] Frontend может подключиться к Backend
- [ ] Данные отображаются на Frontend

## Команды для проверки

### Проверка Backend:
```bash
# Health check
curl https://[URL_BACKEND]/health

# Статистика
curl https://[URL_BACKEND]/api/stats

# Пользователи
curl https://[URL_BACKEND]/api/users

# Сообщения
curl https://[URL_BACKEND]/api/messages
```

### Проверка Frontend:
```bash
# Главная страница
curl https://iva.up.railway.app
```

## Итого

1. **Найдите URL Backend сервиса** на Railway
2. **Проверьте Backend** напрямую через `/health` и `/api/stats`
3. **Настройте `NEXT_PUBLIC_API_URL`** в Frontend сервисе
4. **Перезапустите Frontend**
5. **Проверьте работу** через Frontend интерфейс

