# Принудительный перезапуск деплоя на Railway

## Проблема

Ошибка `Dockerfile 'Dockerfile' does not exist` все еще появляется, даже после исправлений.

## Решение: Принудительный перезапуск

### Вариант 1: Переподключить репозиторий (рекомендуется)

1. **Railway Dashboard** → сервис "IVA" → **Settings** → **Source**
2. Нажмите **"Disconnect"** рядом с репозиторием
3. Подождите несколько секунд
4. Нажмите **"+ New"** → **"GitHub Repo"**
5. Выберите репозиторий: `mag8888/IVA`
6. **ВАЖНО**: Убедитесь, что **Root Directory** = `backend_django` (без слэша!)
7. Нажмите **"Connect"**
8. Railway автоматически начнет новый деплой

### Вариант 2: Принудительный редеплой

1. **Railway Dashboard** → сервис "IVA" → **Deployments**
2. Найдите последний деплой
3. Нажмите на три точки (⋮) справа от деплоя
4. Выберите **"Redeploy"**
5. Или нажмите кнопку **"Redeploy"** вверху

### Вариант 3: Проверка и исправление Root Directory

1. **Railway Dashboard** → сервис "IVA" → **Settings** → **Source**
2. Проверьте поле **"Root Directory"**:
   - ✅ Должно быть: `backend_django` (без слэша)
   - ❌ Не должно быть: `/backend_django` (с слэшем)
3. Если неправильно - исправьте и сохраните
4. Railway автоматически перезапустит деплой

## Проверка в GitHub

Убедитесь, что файлы точно в репозитории:

1. Откройте в браузере:
   ```
   https://github.com/mag8888/IVA/tree/main/backend_django
   ```

2. Должны быть видны:
   - ✅ `Dockerfile`
   - ✅ `railway.json`
   - ✅ `requirements.txt`
   - ✅ `start.sh`
   - ✅ `manage.py`

3. Если файлов нет - проверьте, что они закоммичены:
   ```bash
   git status
   git push origin main
   ```

## После переподключения

В логах должно появиться:

```
Building Docker image...
Step 1/10 : FROM python:3.12-slim
...
Step 10/10 : CMD ["bash", "/app/start.sh"]
✅ Build successful
```

## Если ошибка сохраняется

1. **Проверьте коммит в Railway:**
   - Railway Dashboard → Deployments
   - Убедитесь, что виден последний коммит (например: `ac0537a`)

2. **Проверьте Root Directory еще раз:**
   - Должно быть точно: `backend_django` (без пробелов, без слэшей)

3. **Попробуйте создать новый сервис:**
   - Создайте новый сервис с нуля
   - Root Directory: `backend_django`
   - Подключите тот же репозиторий

