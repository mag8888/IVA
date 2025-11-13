# API Endpoints - Equilibrium MLM

## Принцип работы

**Все расчеты и размещение происходят на сервере!**
Frontend только отображает данные из базы данных.

## Endpoints

### 1. Статус API
- **URL**: `/api/status/`
- **Метод**: `GET`
- **Аутентификация**: Не требуется
- **Описание**: Проверка работоспособности API

**Ответ**:
```json
{
  "name": "Equilibrium API",
  "version": "0.1.0",
  "status": "ok"
}
```

### 2. Регистрация партнера
- **URL**: `/api/register/`
- **Метод**: `POST`
- **Аутентификация**: Не требуется
- **Описание**: Регистрация нового участника. Все расчеты на сервере.

**Запрос**:
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "referral_code": "ABC12345",
  "tariff_code": "basic"
}
```

**Ответ** (201 Created):
```json
{
  "id": 123,
  "username": "newuser",
  "temporary_password": "random_password",
  "payment_id": 456
}
```

**Что происходит на сервере**:
1. Создается User со статусом PARTICIPANT
2. Создается Payment со статусом PENDING
3. Генерируется временный пароль
4. Все сохраняется в БД

### 3. Очередь регистраций
- **URL**: `/api/queue/`
- **Метод**: `GET`
- **Аутентификация**: Требуется (Token или Session)
- **Описание**: Список пользователей, ожидающих оплаты

**Ответ**:
```json
[
  {
    "id": 456,
    "user": 123,
    "username": "newuser",
    "email": "user@example.com",
    "inviter": "ABC12345",
    "inviter_username": "inviter_user",
    "tariff": {
      "code": "basic",
      "name": "Basic",
      "entry_amount": "100.00"
    },
    "amount": "100.00",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

**Для админ-панели** (без аутентификации):
- **URL**: `/api/queue/public/`

### 4. Завершение регистрации
- **URL**: `/api/complete/`
- **Метод**: `POST`
- **Аутентификация**: Требуется
- **Описание**: Завершение регистрации. Все расчеты и размещение на сервере.

**Запрос**:
```json
{
  "user_id": 123
}
```

**Ответ** (200 OK):
```json
{
  "detail": "Регистрация завершена",
  "placement_parent": "parent_username",
  "level": 2,
  "position": 1,
  "bonuses_created": 2
}
```

**Что происходит на сервере**:
1. Платеж переводится в статус COMPLETED
2. Статус пользователя меняется на PARTNER
3. **Размещение в структуре** (BFS алгоритм на сервере)
4. **Начисление бонусов** (расчет на сервере, сохранение в БД)
5. Все данные сохраняются в БД

### 5. Структура MLM
- **URL**: `/api/structure/`
- **Метод**: `GET`
- **Аутентификация**: Не требуется
- **Описание**: Список всех узлов структуры из БД

**Ответ**:
```json
[
  {
    "id": 1,
    "user": {
      "id": 1,
      "username": "user1",
      "referral_code": "ABC12345"
    },
    "parent_username": null,
    "level": 0,
    "position": 1,
    "tariff_name": "Basic",
    "tariff_code": "basic",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### 6. Дерево структуры
- **URL**: `/api/structure/tree/`
- **Метод**: `GET`
- **Аутентификация**: Не требуется
- **Описание**: Дерево структуры для визуализации (из БД)

**Параметры**:
- `root_user_id` (опционально) - ID корневого пользователя
- `max_depth` (опционально) - максимальная глубина

**Ответ**:
```json
{
  "user": {
    "id": 1,
    "username": "user1",
    "referral_code": "ABC12345"
  },
  "level": 0,
  "position": 1,
  "tariff": {
    "code": "basic",
    "name": "Basic"
  },
  "children": [
    {
      "user": {...},
      "level": 1,
      "position": 1,
      "children": [...]
    }
  ]
}
```

### 7. Бонусы
- **URL**: `/api/bonuses/`
- **Метод**: `GET`
- **Аутентификация**: Не требуется
- **Описание**: Все бонусы из базы данных

**Параметры**:
- `user_id` (опционально) - фильтр по пользователю

**Ответ**:
```json
[
  {
    "id": 1,
    "user": {
      "id": 2,
      "username": "user2"
    },
    "source_user": {
      "id": 3,
      "username": "user3"
    },
    "bonus_type": "GREEN",
    "bonus_type_display": "Зеленый бонус",
    "amount": "50.00",
    "description": "Зеленый бонус за приглашение user3",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

**Важно**: Отображаются только бонусы, которые есть в БД (рассчитаны на сервере).

### 8. Тарифы
- **URL**: `/api/tariffs/`
- **Метод**: `GET`
- **Аутентификация**: Не требуется
- **Описание**: Все активные тарифы

**Ответ**:
```json
[
  {
    "code": "basic",
    "name": "Basic",
    "entry_amount": "100.00",
    "green_bonus_percent": 50,
    "yellow_bonus_percent": 50
  }
]
```

### 9. Статистика
- **URL**: `/api/stats/`
- **Метод**: `GET`
- **Аутентификация**: Не требуется
- **Описание**: Статистика системы (все данные из БД)

**Ответ**:
```json
{
  "users": {
    "total": 100,
    "participants": 20,
    "partners": 75,
    "admins": 5
  },
  "structure": {
    "total_nodes": 75
  },
  "payments": {
    "pending": 5
  },
  "bonuses": {
    "total": 5000.00,
    "green": 2500.00,
    "yellow": 2500.00
  }
}
```

**Важно**: Все данные берутся из БД, никаких расчетов на клиенте.

## Принципы

1. **Все расчеты на сервере**: Размещение, бонусы, статистика - все считается на backend
2. **Данные из БД**: Frontend только отображает то, что есть в базе
3. **Транзакции**: Все операции атомарные (либо все успешно, либо откат)
4. **Валидация**: Все данные валидируются на сервере

## Примеры использования

### Регистрация и завершение

```bash
# 1. Регистрация
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "referral_code": "ABC12345",
    "tariff_code": "basic"
  }'

# 2. Проверка очереди
curl http://localhost:8000/api/queue/

# 3. Завершение регистрации
curl -X POST http://localhost:8000/api/complete/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123}'

# 4. Проверка структуры
curl http://localhost:8000/api/structure/

# 5. Проверка бонусов
curl http://localhost:8000/api/bonuses/
```

