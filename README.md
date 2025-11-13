# Equilibrium Project

Проект с двумя серверами (backend и frontend), PostgreSQL базой данных и интеграцией Telegram Bot API.

## Структура проекта

```
Equilibrium/
├── backend/          # Backend сервер (Node.js/Express)
├── frontend/         # Frontend сервер (Next.js)
└── README.md
```

## Технологии

- **Backend**: Node.js, Express, TypeScript, PostgreSQL
- **Frontend**: Next.js 14, React, TypeScript
- **Database**: PostgreSQL
- **Telegram**: node-telegram-bot-api
- **Deployment**: Railway

## Локальная установка

### Требования

- Node.js 18+
- PostgreSQL 14+
- Telegram Bot Token (получить у @BotFather)

### Шаги установки

1. **Клонируйте репозиторий и установите зависимости:**

```bash
npm run install:all
```

2. **Настройте базу данных PostgreSQL:**

Создайте базу данных:
```sql
CREATE DATABASE equilibrium;
```

3. **Настройте переменные окружения:**

Backend (создайте `backend/.env`):
```env
PORT=3001
NODE_ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/equilibrium
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

Frontend (создайте `frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:3001
```

4. **Запустите серверы:**

В отдельных терминалах:

```bash
# Backend
npm run dev:backend

# Frontend
npm run dev:frontend
```

Backend будет доступен на `http://localhost:3001`
Frontend будет доступен на `http://localhost:3000`

## Развертывание на Railway

### Подготовка

1. Создайте аккаунт на [Railway](https://railway.app)
2. Создайте новый проект
3. Добавьте PostgreSQL сервис
4. Добавьте два сервиса для backend и frontend

### Backend на Railway

1. Подключите репозиторий или загрузите код
2. Укажите корневую директорию: `backend`
3. Добавьте переменные окружения:
   - `DATABASE_URL` (автоматически из PostgreSQL сервиса)
   - `TELEGRAM_BOT_TOKEN` (ваш токен бота)
   - `PORT` (Railway установит автоматически)
   - `NODE_ENV=production`

### Frontend на Railway

1. Подключите репозиторий или загрузите код
2. Укажите корневую директорию: `frontend`
3. Добавьте переменные окружения:
   - `NEXT_PUBLIC_API_URL` (URL вашего backend сервера на Railway)

### Настройка базы данных

Railway автоматически создаст PostgreSQL базу данных. Используйте `DATABASE_URL` из настроек PostgreSQL сервиса.

## API Endpoints

### Backend API

- `GET /health` - Проверка здоровья сервера
- `GET /api/users` - Получить всех пользователей
- `GET /api/users/telegram/:telegramId` - Получить пользователя по Telegram ID
- `GET /api/messages` - Получить сообщения (параметр `?limit=50`)
- `GET /api/stats` - Получить статистику

## Telegram Bot

Бот автоматически:
- Сохраняет пользователей в базу данных при команде `/start`
- Сохраняет все сообщения
- Отвечает на сообщения

## Разработка

### Структура Backend

```
backend/
├── src/
│   ├── index.ts          # Точка входа
│   ├── db.ts             # Подключение к БД
│   ├── telegram.ts       # Telegram Bot логика
│   └── routes/
│       └── api.ts        # API маршруты
├── package.json
└── tsconfig.json
```

### Структура Frontend

```
frontend/
├── src/
│   └── app/
│       ├── page.tsx      # Главная страница
│       ├── layout.tsx    # Layout
│       └── globals.css   # Стили
├── package.json
└── next.config.js
```

## Следующие шаги

После тестового запуска можно улучшить:

- [ ] Аутентификация и авторизация
- [ ] WebSocket для real-time обновлений
- [ ] Расширенная аналитика
- [ ] Админ панель
- [ ] Уведомления
- [ ] Логирование и мониторинг
- [ ] Тесты

## Лицензия

ISC

