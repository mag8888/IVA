#!/bin/bash

# Скрипт для проверки деплоя после обновления Railway
# Использование: ./check_deployment.sh [BASE_URL]
# Пример: ./check_deployment.sh https://iva-production-4400.up.railway.app

set -e  # Останавливаем выполнение при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Базовый URL (по умолчанию)
BASE_URL="${1:-https://iva-production-4400.up.railway.app}"

echo "🔍 Проверка деплоя на ${BASE_URL}"
echo ""

# Функция для проверки статуса HTTP
check_status() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    echo -n "Проверка: ${description}... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "${url}" || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK (${response})${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED (${response}, ожидалось ${expected_status})${NC}"
        return 1
    fi
}

# Функция для проверки JSON ответа
check_json() {
    local url=$1
    local description=$2
    local json_key=$3
    
    echo -n "Проверка: ${description}... "
    
    response=$(curl -s "${url}" || echo "{}")
    
    if echo "${response}" | grep -q "${json_key}"; then
        echo -e "${GREEN}✅ OK${NC}"
        echo "   Ответ: $(echo "${response}" | head -c 200)..."
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "   Ответ: ${response}"
        return 1
    fi
}

# Счетчик ошибок
ERRORS=0

# 1. Проверка Healthcheck
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Проверка Healthcheck"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ! check_status "${BASE_URL}/health/" "200" "Healthcheck endpoint"; then
    ((ERRORS++))
fi
echo ""

# 2. Проверка API Status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Проверка API Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ! check_json "${BASE_URL}/api/status/" "API Status" "status"; then
    ((ERRORS++))
fi
echo ""

# 3. Проверка структуры (до генерации)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Проверка структуры (до генерации)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ! check_status "${BASE_URL}/api/structure/" "200" "Structure endpoint"; then
    ((ERRORS++))
fi
echo ""

# 4. Генерация структуры
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Генерация тестовой структуры"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -n "Генерация структуры... "
GENERATE_URL="${BASE_URL}/api/structure/generate/?children=6"
generate_response=$(curl -s "${GENERATE_URL}" || echo "{}")

if echo "${generate_response}" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ OK${NC}"
    echo "   Ответ: $(echo "${generate_response}" | head -c 300)..."
else
    echo -e "${RED}❌ FAILED${NC}"
    echo "   Ответ: ${generate_response}"
    ((ERRORS++))
fi
echo ""

# 5. Проверка структуры (после генерации)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. Проверка структуры (после генерации)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ! check_status "${BASE_URL}/api/structure/" "200" "Structure endpoint"; then
    ((ERRORS++))
fi

# Проверка, что структура содержит данные
echo -n "Проверка: Структура содержит данные... "
structure_response=$(curl -s "${BASE_URL}/api/structure/" || echo "[]")
if echo "${structure_response}" | grep -q '"id"'; then
    node_count=$(echo "${structure_response}" | grep -o '"id"' | wc -l | tr -d ' ')
    echo -e "${GREEN}✅ OK (${node_count} узлов)${NC}"
else
    echo -e "${YELLOW}⚠️  Структура пуста${NC}"
    ((ERRORS++))
fi
echo ""

# 6. Проверка дерева структуры
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. Проверка дерева структуры"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ! check_status "${BASE_URL}/api/structure/tree/" "200" "Structure tree endpoint"; then
    ((ERRORS++))
fi

# Проверка, что дерево содержит данные
echo -n "Проверка: Дерево содержит данные... "
tree_response=$(curl -s "${BASE_URL}/api/structure/tree/" || echo "{}")
if echo "${tree_response}" | grep -q '"user"'; then
    echo -e "${GREEN}✅ OK${NC}"
    echo "   Ответ: $(echo "${tree_response}" | head -c 200)..."
else
    echo -e "${RED}❌ FAILED${NC}"
    echo "   Ответ: ${tree_response}"
    ((ERRORS++))
fi
echo ""

# 7. Проверка статистики
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. Проверка статистики"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ! check_json "${BASE_URL}/api/stats/" "Statistics" "total_nodes"; then
    ((ERRORS++))
fi
echo ""

# 8. Проверка тарифов
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8. Проверка тарифов"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ! check_status "${BASE_URL}/api/tariffs/" "200" "Tariffs endpoint"; then
    ((ERRORS++))
fi
echo ""

# 9. Проверка Telegram мини-приложения
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9. Проверка Telegram мини-приложения"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ! check_status "${BASE_URL}/telegram-app/" "200" "Telegram app page"; then
    ((ERRORS++))
fi
echo ""

# Итоговый результат
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Итоговый результат"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Все проверки пройдены успешно!${NC}"
    echo ""
    echo "🎉 Деплой завершен успешно!"
    echo "🔗 Мини-приложение: ${BASE_URL}/telegram-app/"
    echo "🔗 API структуры: ${BASE_URL}/api/structure/tree/"
    echo "🔗 Статистика: ${BASE_URL}/api/stats/"
    exit 0
else
    echo -e "${RED}❌ Обнаружено ${ERRORS} ошибок${NC}"
    echo ""
    echo "⚠️  Пожалуйста, проверьте логи Railway:"
    echo "   1. Откройте Railway Dashboard"
    echo "   2. Перейдите в проект backend-django"
    echo "   3. Откройте сервис IVA"
    echo "   4. Проверьте вкладку Logs"
    exit 1
fi

