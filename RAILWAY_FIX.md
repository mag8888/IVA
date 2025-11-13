# Исправление ошибки "Missing script: start" на Railway

## Проблема

Railway не может найти скрипт `start` в package.json. Это происходит, если:
1. Root Directory не установлен правильно
2. Railway не видит railway.json в нужной папке
3. Команда запуска указана неправильно

## Решение

### Важно: Настройка Root Directory на Railway

**Для Backend сервиса:**
- Service Settings → Root Directory: `backend` ⭐
- Railway будет искать файлы в `backend/`

**Для Frontend сервиса:**
- Service Settings → Root Directory: `frontend` ⭐
- Railway будет искать файлы в `frontend/`

### Команды запуска

#### Backend:
- **Procfile**: `web: node dist/index.js`
- **railway.json**: `"startCommand": "node dist/index.js"`
- **nixpacks.toml**: `cmd = "node dist/index.js"`

#### Frontend:
- **Procfile**: `web: npm run start`
- **railway.json**: `"startCommand": "npm run start"`
- **nixpacks.toml**: `cmd = "npm run start"`

## Проверка на Railway

### 1. Проверьте Root Directory

В настройках каждого сервиса:
- Backend: Root Directory = `backend`
- Frontend: Root Directory = `frontend`

### 2. Проверьте Build Command

Можно оставить пустым - Railway использует `railway.json` или `nixpacks.toml`

Или укажите явно:
- Backend: `npm install && npm run build`
- Frontend: `npm install && npm run build`

### 3. Проверьте Start Command

Можно оставить пустым - Railway использует `railway.json` или `Procfile`

Или укажите явно:
- Backend: `node dist/index.js`
- Frontend: `npm run start`

## Альтернативное решение

Если проблема сохраняется, можно указать команды напрямую в настройках Railway:

### Backend Service Settings:
```
Root Directory: backend
Build Command: npm install && npm run build
Start Command: node dist/index.js
```

### Frontend Service Settings:
```
Root Directory: frontend
Build Command: npm install && npm run build
Start Command: npm run start
```

## Проверка логов

После деплоя проверьте логи:
- Должно быть: `npm install` → `npm run build` → `node dist/index.js` (для backend)
- Должно быть: `npm install` → `npm run build` → `npm run start` (для frontend)

## Если проблема не решается

1. Убедитесь, что Root Directory установлен правильно
2. Проверьте, что все файлы закоммичены и запушены
3. Попробуйте пересоздать сервис на Railway
4. Проверьте логи сборки - возможно, ошибка на этапе build

