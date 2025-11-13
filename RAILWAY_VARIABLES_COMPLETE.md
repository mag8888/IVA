# Полный список переменных окружения для Railway

## 🔴 BACKEND сервис (iva-production.up.railway.app)

### Скопируйте и вставьте эти переменные:

```
DATABASE_URL=******* (уже есть - не трогайте)
TELEGRAM_BOT_TOKEN=******* (уже есть - не трогайте)
TELEGRAM_WEBAPP_URL=https://iva-production.up.railway.app
RAILWAY_PUBLIC_DOMAIN=iva-production.up.railway.app
TELEGRAM_WEBHOOK_URL=https://iva-production.up.railway.app/telegram/webhook/
DJANGO_SECRET_KEY=md*3-haow%@+i(c=mrsk!%jywy9%x_*1yv^+t5yw3&y+qw01ne
DJANGO_DEBUG=False
CORS_ALLOWED_ORIGINS=https://iva.up.railway.app
DJANGO_ALLOWED_HOSTS=iva-production.up.railway.app,iva.up.railway.app
```

### Пошаговая инструкция для Backend:

1. Откройте **Backend сервис** на Railway (iva-production.up.railway.app)
2. Перейдите в **Variables**
3. Добавьте каждую переменную по очереди:

#### Переменная 1: RAILWAY_PUBLIC_DOMAIN
- **Имя**: `RAILWAY_PUBLIC_DOMAIN`
- **Значение**: `iva-production.up.railway.app`
- Нажмите **Add**

#### Переменная 2: TELEGRAM_WEBHOOK_URL
- **Имя**: `TELEGRAM_WEBHOOK_URL`
- **Значение**: `https://iva-production.up.railway.app/telegram/webhook/`
- Нажмите **Add**

#### Переменная 3: DJANGO_SECRET_KEY
- **Имя**: `DJANGO_SECRET_KEY`
- **Значение**: `md*3-haow%@+i(c=mrsk!%jywy9%x_*1yv^+t5yw3&y+qw01ne`
- Нажмите **Add**
- ⚠️ **ВАЖНО**: Это секретный ключ, не делитесь им!

#### Переменная 4: DJANGO_DEBUG
- **Имя**: `DJANGO_DEBUG`
- **Значение**: `False`
- Нажмите **Add**

#### Переменная 5: CORS_ALLOWED_ORIGINS
- **Имя**: `CORS_ALLOWED_ORIGINS`
- **Значение**: `https://iva.up.railway.app`
- Нажмите **Add**

#### Переменная 6: DJANGO_ALLOWED_HOSTS
- **Имя**: `DJANGO_ALLOWED_HOSTS`
- **Значение**: `iva-production.up.railway.app,iva.up.railway.app`
- Нажмите **Add**

#### Переменная 7: TELEGRAM_WEBAPP_URL (обновить)
- Найдите существующую переменную `TELEGRAM_WEBAPP_URL`
- Нажмите на неё для редактирования
- Измените значение на: `https://iva-production.up.railway.app`
- Нажмите **Save**

---

## 🟢 FRONTEND сервис (iva.up.railway.app)

### Скопируйте и вставьте эту переменную:

```
VITE_API_URL=https://iva-production.up.railway.app
```

### Пошаговая инструкция для Frontend:

1. Откройте **Frontend сервис** на Railway (iva.up.railway.app)
2. Перейдите в **Variables**
3. Добавьте переменную:

#### Переменная: VITE_API_URL
- **Имя**: `VITE_API_URL`
- **Значение**: `https://iva-production.up.railway.app`
- Нажмите **Add**

---

## ✅ После добавления всех переменных:

### 1. Перезапустите Backend сервис:
- Откройте Backend сервис
- Нажмите **Deployments**
- Нажмите **Redeploy** или **Restart**

### 2. Перезапустите Frontend сервис:
- Откройте Frontend сервис
- Нажмите **Deployments**
- Нажмите **Redeploy** или **Restart**

### 3. Проверьте работу:

#### Backend:
- ✅ Health check: https://iva-production.up.railway.app/health/
- ✅ API Status: https://iva-production.up.railway.app/api/status/

#### Frontend:
- ✅ Откройте: https://iva.up.railway.app
- ✅ Должен загрузиться интерфейс
- ✅ Должен подключаться к Backend API

#### Telegram бот:
- ✅ Отправьте `/start` боту
- ✅ Отправьте `/app` боту → должна появиться кнопка
- ✅ Отправьте `/stats` боту → должна показаться статистика

---

## 📋 Итоговый список переменных

### Backend (iva-production.up.railway.app):
```
✅ DATABASE_URL (уже есть)
✅ TELEGRAM_BOT_TOKEN (уже есть)
✅ TELEGRAM_WEBAPP_URL=https://iva-production.up.railway.app
✅ RAILWAY_PUBLIC_DOMAIN=iva-production.up.railway.app
✅ TELEGRAM_WEBHOOK_URL=https://iva-production.up.railway.app/telegram/webhook/
✅ DJANGO_SECRET_KEY=md*3-haow%@+i(c=mrsk!%jywy9%x_*1yv^+t5yw3&y+qw01ne
✅ DJANGO_DEBUG=False
✅ CORS_ALLOWED_ORIGINS=https://iva.up.railway.app
✅ DJANGO_ALLOWED_HOSTS=iva-production.up.railway.app,iva.up.railway.app
```

### Frontend (iva.up.railway.app):
```
✅ VITE_API_URL=https://iva-production.up.railway.app
```

---

## 🔒 Безопасность

⚠️ **ВАЖНО**: 
- `DJANGO_SECRET_KEY` - это секретный ключ, не делитесь им публично
- `TELEGRAM_BOT_TOKEN` - тоже секретный, не публикуйте
- `DATABASE_URL` - содержит пароль к базе данных

Все эти переменные уже скрыты в Railway (показываются как `*******`), это правильно.

---

## 🆘 Если что-то не работает:

1. **Проверьте логи** в Railway:
   - Backend → Metrics → Logs
   - Frontend → Metrics → Logs

2. **Убедитесь, что все переменные добавлены**:
   - Проверьте список переменных в каждом сервисе

3. **Перезапустите сервисы**:
   - Иногда нужно перезапустить после добавления переменных

4. **Проверьте домены**:
   - Backend должен быть доступен по `iva-production.up.railway.app`
   - Frontend должен быть доступен по `iva.up.railway.app`

