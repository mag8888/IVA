# Быстрый старт для тестового запуска

## Локальный тестовый запуск

### 1. Установка зависимостей

```bash
npm run install:all
```

### 2. Настройка базы данных

Убедитесь, что PostgreSQL запущен, затем создайте базу данных:

```bash
createdb equilibrium
# или через psql:
psql -U postgres -c "CREATE DATABASE equilibrium;"
```

### 3. Создание файлов окружения

**Backend** (`backend/.env`):
```env
PORT=3001
NODE_ENV=development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/equilibrium
TELEGRAM_BOT_TOKEN=ваш_токен_бота
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:3001
```

> **Примечание**: Получите токен бота у [@BotFather](https://t.me/BotFather) в Telegram

### 4. Запуск серверов

Откройте два терминала:

**Терминал 1 - Backend:**
```bash
npm run dev:backend
```

**Терминал 2 - Frontend:**
```bash
npm run dev:frontend
```

### 5. Проверка работы

- Backend API: http://localhost:3001/health
- Frontend: http://localhost:3000
- Telegram бот: отправьте `/start` вашему боту

## Развертывание на Railway (тестовое)

### Шаг 1: Создание проекта на Railway

1. Зайдите на [railway.app](https://railway.app)
2. Создайте новый проект
3. Добавьте PostgreSQL сервис (автоматически создастся база)

### Шаг 2: Backend сервис

1. В проекте Railway нажмите "New" → "GitHub Repo" (или "Empty Service")
2. Если через GitHub - подключите репозиторий
3. В настройках сервиса:
   - **Root Directory**: `backend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run start`

4. Добавьте переменные окружения:
   - `DATABASE_URL` - скопируйте из PostgreSQL сервиса (Connect → Connection String)
   - `TELEGRAM_BOT_TOKEN` - ваш токен бота
   - `NODE_ENV=production`
   - `PORT` - Railway установит автоматически

### Шаг 3: Frontend сервис

1. Создайте еще один сервис в том же проекте
2. В настройках:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run start`

3. Добавьте переменные окружения:
   - `NEXT_PUBLIC_API_URL` - URL вашего backend сервиса (например: `https://your-backend.railway.app`)

### Шаг 4: Проверка

После деплоя:
- Backend будет доступен по URL из Railway
- Frontend будет доступен по своему URL
- Проверьте `/health` endpoint на backend
- Откройте frontend в браузере

## Тестирование

### Проверка Backend API

```bash
# Health check
curl http://localhost:3001/health

# Статистика
curl http://localhost:3001/api/stats

# Пользователи
curl http://localhost:3001/api/users
```

### Проверка Telegram бота

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Отправьте любое сообщение
4. Проверьте в веб-интерфейсе, что данные появились

## Возможные проблемы

### База данных не подключается
- Проверьте, что PostgreSQL запущен
- Проверьте правильность `DATABASE_URL`
- Убедитесь, что база данных `equilibrium` создана

### Telegram бот не отвечает
- Проверьте правильность `TELEGRAM_BOT_TOKEN`
- Убедитесь, что бот запущен (нет ошибок в логах backend)

### Frontend не подключается к Backend
- Проверьте `NEXT_PUBLIC_API_URL` в `.env.local`
- Убедитесь, что backend запущен
- Проверьте CORS настройки (должны быть настроены)

## Следующие шаги

После успешного тестового запуска можно:
1. Улучшить UI/UX
2. Добавить аутентификацию
3. Расширить функционал бота
4. Добавить аналитику
5. Настроить мониторинг

