# Настройка сервисов на Railway

## Как Railway различает Backend и Frontend

Railway определяет, какой сервис запускать, по **Root Directory** в настройках каждого сервиса. Это главный параметр разделения.

## Структура проекта

```
Equilibrium/
├── backend/          ← Backend сервис (Root Directory: backend)
│   ├── railway.json  ← Конфигурация для Railway
│   ├── package.json  ← Имя: "equilibrium-backend"
│   ├── Procfile      ← Маркер для Railway
│   └── src/
├── frontend/         ← Frontend сервис (Root Directory: frontend)
│   ├── railway.json  ← Конфигурация для Railway
│   ├── package.json  ← Имя: "equilibrium-frontend"
│   ├── Procfile      ← Маркер для Railway
│   └── src/
└── railway.json      ← Общая конфигурация (не используется для разделения)
```

## Маркеры для разделения сервисов

### 1. Root Directory (ГЛАВНЫЙ параметр)
- **Backend сервис**: `backend`
- **Frontend сервис**: `frontend`

### 2. package.json name
- **Backend**: `"name": "equilibrium-backend"`
- **Frontend**: `"name": "equilibrium-frontend"`

### 3. railway.json в каждой папке
- Каждый сервис имеет свой `railway.json` с настройками сборки и запуска

### 4. Procfile
- Содержит команду запуска для каждого сервиса

## Пошаговая настройка на Railway

### Шаг 1: Создание проекта

1. Зайдите на [railway.app](https://railway.app)
2. Создайте новый проект
3. Подключите репозиторий: `https://github.com/mag8888/IVA.git`

### Шаг 2: Добавление PostgreSQL

1. В проекте нажмите **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway автоматически создаст базу данных
3. Скопируйте `DATABASE_URL` из настроек PostgreSQL сервиса

### Шаг 3: Создание Backend сервиса

1. В проекте нажмите **"New"** → **"GitHub Repo"** (или **"Empty Service"**)
2. Выберите репозиторий `mag8888/IVA`
3. **ВАЖНО**: В настройках сервиса:
   - **Service Name**: `backend` (или `equilibrium-backend`)
   - **Root Directory**: `backend` ← **ЭТО ГЛАВНОЕ!**
   - **Build Command**: `npm install && npm run build` (или оставьте пустым, Railway использует railway.json)
   - **Start Command**: `npm run start` (или оставьте пустым)

4. Добавьте переменные окружения:
   ```
   DATABASE_URL=<скопируйте из PostgreSQL сервиса>
   TELEGRAM_BOT_TOKEN=<ваш_токен_бота>
   NODE_ENV=production
   PORT=<Railway установит автоматически>
   ```

5. Railway автоматически обнаружит:
   - `backend/railway.json` - конфигурацию
   - `backend/package.json` - зависимости и скрипты
   - `backend/Procfile` - команду запуска

### Шаг 4: Создание Frontend сервиса

1. В том же проекте нажмите **"New"** → **"GitHub Repo"** (или **"Empty Service"**)
2. Выберите тот же репозиторий `mag8888/IVA`
3. **ВАЖНО**: В настройках сервиса:
   - **Service Name**: `frontend` (или `equilibrium-frontend`)
   - **Root Directory**: `frontend` ← **ЭТО ГЛАВНОЕ!**
   - **Build Command**: `npm install && npm run build` (или оставьте пустым)
   - **Start Command**: `npm run start` (или оставьте пустым)

4. Добавьте переменные окружения:
   ```
   NEXT_PUBLIC_API_URL=<URL_вашего_backend_сервиса>
   NODE_ENV=production
   PORT=<Railway установит автоматически>
   ```

5. Railway автоматически обнаружит:
   - `frontend/railway.json` - конфигурацию
   - `frontend/package.json` - зависимости и скрипты
   - `frontend/Procfile` - команду запуска

## Как Railway понимает, какой сервис какой

### Автоматическое определение:

1. **По Root Directory**:
   - Если Root Directory = `backend` → Railway ищет файлы в `backend/`
   - Если Root Directory = `frontend` → Railway ищет файлы в `frontend/`

2. **По package.json**:
   - Railway читает `package.json` в указанной Root Directory
   - Видит скрипты `build` и `start`
   - По имени пакета понимает тип (`equilibrium-backend` vs `equilibrium-frontend`)

3. **По railway.json**:
   - Railway читает `railway.json` в Root Directory
   - Использует команды из конфигурации

4. **По Procfile**:
   - Если есть `Procfile`, Railway использует команду из него

## Проверка правильности настройки

### Backend сервис должен:
- ✅ Root Directory = `backend`
- ✅ Иметь переменную `DATABASE_URL`
- ✅ Иметь переменную `TELEGRAM_BOT_TOKEN`
- ✅ Собираться командой: `npm install && npm run build`
- ✅ Запускаться командой: `npm run start`
- ✅ Открывать порт (Railway назначит автоматически)

### Frontend сервис должен:
- ✅ Root Directory = `frontend`
- ✅ Иметь переменную `NEXT_PUBLIC_API_URL` (URL backend)
- ✅ Собираться командой: `npm install && npm run build`
- ✅ Запускаться командой: `npm run start`
- ✅ Открывать порт (Railway назначит автоматически)

## Пример настройки в Railway UI

### Backend Service Settings:
```
Service Name: backend
Root Directory: backend          ← КЛЮЧЕВОЙ ПАРАМЕТР
Build Command: (оставить пустым, используется railway.json)
Start Command: (оставить пустым, используется railway.json)
```

### Frontend Service Settings:
```
Service Name: frontend
Root Directory: frontend         ← КЛЮЧЕВОЙ ПАРАМЕТР
Build Command: (оставить пустым, используется railway.json)
Start Command: (оставить пустым, используется railway.json)
```

## Важные моменты

1. **Root Directory - это главное!** Без правильного Root Directory Railway не сможет найти нужные файлы.

2. **Один репозиторий, два сервиса**: Оба сервиса используют один репозиторий, но разные Root Directory.

3. **Переменные окружения**: Каждый сервис имеет свои переменные окружения.

4. **Порты**: Railway автоматически назначает порты и предоставляет URL для каждого сервиса.

5. **Автоматический деплой**: При пуше в `main` ветку оба сервиса автоматически пересобираются и перезапускаются.

## Troubleshooting

### Проблема: Railway не может найти package.json
**Решение**: Проверьте Root Directory - он должен быть `backend` или `frontend`, а не корень проекта.

### Проблема: Неправильная команда запуска
**Решение**: Проверьте `railway.json` в соответствующей папке или укажите команду явно в настройках сервиса.

### Проблема: Frontend не подключается к Backend
**Решение**: 
- Проверьте `NEXT_PUBLIC_API_URL` - должен быть полный URL backend сервиса
- Убедитесь, что backend запущен и доступен
- Проверьте CORS настройки на backend

