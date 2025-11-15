#!/bin/bash
set -e

echo "🚀 Starting Equilibrium MLM Backend..."

# Проверка переменных окружения
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  WARNING: DATABASE_URL is not set"
fi

# Очистка Python кэша
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Создание директории staticfiles
mkdir -p staticfiles

# Определение структуры проекта
if [ -d "equilibrium_backend" ]; then
    echo "📁 Project structure detected: equilibrium_backend/"
    PROJECT_DIR="equilibrium_backend"
else
    echo "📁 Project structure: root level"
    PROJECT_DIR="."
fi

# Сбор статических файлов (с таймаутом)
echo "📦 Collecting static files..."
timeout 300 python manage.py collectstatic --noinput || echo "⚠️  Static files collection timeout or failed"

# Применение миграций (с таймаутом)
echo "🔄 Applying migrations..."
timeout 300 python manage.py migrate --noinput || echo "⚠️  Migrations timeout or failed"

# Создание администратора (если указаны переменные окружения)
if [ -n "$ADMIN_PASSWORD" ]; then
    echo "👤 Creating/updating admin user..."
    ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
    ADMIN_EMAIL=${ADMIN_EMAIL:-admin@equilibrium.com}
    timeout 60 python manage.py init_admin \
        --username "$ADMIN_USERNAME" \
        --email "$ADMIN_EMAIL" \
        --password "$ADMIN_PASSWORD" || echo "⚠️  Admin creation timeout or failed"
else
    echo "ℹ️  ADMIN_PASSWORD not set, skipping admin creation"
fi

# Запуск Gunicorn
echo "🌐 Starting Gunicorn..."
# Устанавливаем переменную для главного процесса
export RUN_MAIN=true
exec gunicorn \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance \
    --preload \
    equilibrium_backend.wsgi:application

