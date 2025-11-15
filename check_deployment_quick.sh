#!/bin/bash

# Быстрая проверка деплоя
# Использование: ./check_deployment_quick.sh [BASE_URL]

set -e

BASE_URL="${1:-https://iva-production-4400.up.railway.app}"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 Быстрая проверка деплоя: ${BASE_URL}"
echo ""

# 1. Healthcheck
echo -n "1. Healthcheck... "
if curl -s -f "${BASE_URL}/health/" > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    exit 1
fi

# 2. Генерация структуры
echo -n "2. Генерация структуры... "
if curl -s -f "${BASE_URL}/api/structure/generate/?children=6" | grep -q '"success":true'; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    exit 1
fi

# 3. Проверка дерева
echo -n "3. Проверка дерева... "
if curl -s -f "${BASE_URL}/api/structure/tree/" | grep -q '"user"'; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Все проверки пройдены!${NC}"

