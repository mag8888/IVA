FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем директорию для статических файлов
RUN mkdir -p staticfiles

# Собираем статические файлы (с таймаутом)
RUN timeout 300 python manage.py collectstatic --noinput || true

# Применяем миграции (с таймаутом)
RUN timeout 300 python manage.py migrate --noinput || true

# Запуск через start.sh
CMD ["bash", "/app/start.sh"]

