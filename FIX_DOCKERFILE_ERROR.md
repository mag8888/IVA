# Исправление ошибки: Dockerfile не найден

## Проблема

Ошибка: `Dockerfile 'Dockerfile' does not exist`

Это происходит, потому что сервис "IVA" ищет Dockerfile не в той директории.

## Решение

### Вариант 1: Изменить Root Directory сервиса "IVA" (если это Django бэкенд)

1. В Railway Dashboard откройте сервис **"IVA"**
2. Перейдите в **"Settings"** (вкладка справа)
3. Найдите раздел **"Source"** или **"Root Directory"**
4. Измените **Root Directory** на: `backend_django`
5. Сохраните изменения
6. Railway автоматически перезапустит деплой

### Вариант 2: Создать новый сервис (рекомендуется)

Если "IVA" - это старый Node.js бэкенд, создайте новый сервис:

1. Нажмите **"+ New"** → **"GitHub Repo"**
2. Выберите репозиторий: `mag8888/IVA`
3. В настройках:
   - **Service Name**: `django-backend`
   - **Root Directory**: `backend_django` ⭐
4. Добавьте переменные окружения (см. RAILWAY_QUICK_SETUP.md)

## Проверка

После изменения Root Directory:

1. Railway начнет новый деплой
2. В логах должно быть:
   ```
   Building Docker image...
   ✅ Dockerfile found
   ```

3. Если ошибка сохраняется, проверьте:
   - Root Directory точно установлен в `backend_django`
   - В репозитории есть файл `backend_django/Dockerfile`
   - Сервис подключен к правильному репозиторию

## Структура файлов

```
Equilibrium/
├── backend/              ← Старый Node.js (может не иметь Dockerfile)
├── backend_django/       ← Django Backend ⭐
│   ├── Dockerfile       ✅ Здесь должен быть Dockerfile
│   ├── railway.json
│   └── ...
└── frontend_react/
```

## Если Root Directory уже правильный

Если Root Directory = `backend_django`, но ошибка сохраняется:

1. Проверьте, что файл `backend_django/Dockerfile` существует в репозитории
2. Убедитесь, что изменения запушены в GitHub:
   ```bash
   git status
   git push origin main
   ```
3. Перезапустите деплой в Railway (кнопка "Redeploy")

