# Проверка Dockerfile в репозитории

## Проблема

Ошибка: `Dockerfile 'Dockerfile' does not exist`

Это означает, что Railway не может найти Dockerfile в указанной директории.

## Проверка

### 1. Убедитесь, что Dockerfile в репозитории

Выполните локально:
```bash
cd /Users/ADMIN/Equilibrium
git ls-files backend_django/Dockerfile
```

Должно вернуть: `backend_django/Dockerfile`

### 2. Проверьте Root Directory в Railway

В Railway Dashboard → сервис "IVA" → Settings → Source:

- **Root Directory** должен быть: `backend_django` (без слэша в начале!)
- ❌ Неправильно: `/backend_django`
- ✅ Правильно: `backend_django`

### 3. Убедитесь, что файлы запушены в GitHub

```bash
git status
git add backend_django/Dockerfile
git commit -m "Ensure Dockerfile is tracked"
git push origin main
```

### 4. Проверьте структуру в GitHub

Откройте в браузере:
`https://github.com/mag8888/IVA/tree/main/backend_django`

Должны быть видны:
- ✅ `Dockerfile`
- ✅ `railway.json`
- ✅ `requirements.txt`
- ✅ `manage.py`

## Решение

### Если Dockerfile не в репозитории:

1. Добавьте файл:
   ```bash
   git add backend_django/Dockerfile
   git commit -m "Add Dockerfile for Django backend"
   git push origin main
   ```

2. Перезапустите деплой в Railway

### Если Root Directory неправильный:

1. Railway Dashboard → сервис "IVA" → Settings
2. Найдите "Root Directory"
3. Измените на: `backend_django` (без слэша)
4. Сохраните

### Если все правильно, но ошибка сохраняется:

1. В Railway Dashboard → сервис "IVA" → Settings
2. Найдите "Source Repo"
3. Нажмите "Disconnect"
4. Подключите заново:
   - "+ New" → "GitHub Repo"
   - Выберите `mag8888/IVA`
   - Root Directory: `backend_django`
   - Сохраните

## Проверка после исправления

После исправления в логах должно быть:

```
Building Docker image...
Step 1/10 : FROM python:3.12-slim
...
✅ Build successful
```

