#!/usr/bin/env python3
"""
Скрипт для удаления webhook и polling из Telegram бота.
Используйте этот скрипт, если получаете ошибку 409 Conflict.
"""
import os
import sys
import django

# Настройка Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equilibrium_backend.settings')
django.setup()

from django.conf import settings
from telegram import Bot

def remove_webhook_and_polling():
    """Удаляет webhook и останавливает polling."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN не установлен")
        return
    
    bot = Bot(token=token)
    
    try:
        # Удаляем webhook
        result = bot.delete_webhook(drop_pending_updates=True)
        print(f"✅ Webhook удален: {result}")
        
        # Проверяем информацию о webhook
        webhook_info = bot.get_webhook_info()
        print(f"📡 Webhook info:")
        print(f"   URL: {webhook_info.url or 'None (polling mode)'}")
        print(f"   Pending updates: {webhook_info.pending_update_count}")
        
        if webhook_info.url:
            print("⚠️  Webhook все еще установлен, попробуйте еще раз")
        else:
            print("✅ Webhook полностью удален, бот готов к работе через webhook")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    remove_webhook_and_polling()

