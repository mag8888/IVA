from django.apps import AppConfig
import threading
import logging
import os

logger = logging.getLogger(__name__)

# Флаг для предотвращения множественного запуска
_bot_started = False
_bot_lock = threading.Lock()


class IntegrationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'integrations'
    
    def ready(self):
        """Инициализация при запуске приложения."""
        global _bot_started
        
        # Запускаем бота только в основном процессе (не в миграциях)
        import sys
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
        
        # Проверяем, не запускаем ли бота через переменную окружения
        if os.environ.get('DISABLE_TELEGRAM_BOT') == 'true':
            logger.info("⚠️  Telegram бот отключен через DISABLE_TELEGRAM_BOT")
            return
        
        # Запускаем бота только в главном процессе (не в воркерах)
        # При использовании --preload Gunicorn загружает приложение до форка воркеров
        # Но ready() может вызываться несколько раз, поэтому используем флаг
        
        # Запускаем бота только один раз (даже если ready() вызывается несколько раз)
        with _bot_lock:
            if _bot_started:
                logger.info("⚠️  Telegram бот уже запущен, пропускаем повторную инициализацию")
                return
            
            from django.conf import settings
            if settings.TELEGRAM_BOT_TOKEN:
                try:
                    from .telegram import init_telegram_bot, start_telegram_bot_webhook
                    
                    # Инициализируем бота
                    application = init_telegram_bot()
                    
                    if application:
                        # Определяем URL для webhook
                        webhook_url = None
                        
                        # Пробуем получить из переменных окружения
                        if hasattr(settings, 'TELEGRAM_WEBHOOK_URL') and settings.TELEGRAM_WEBHOOK_URL:
                            webhook_url = settings.TELEGRAM_WEBHOOK_URL
                        elif hasattr(settings, 'RAILWAY_PUBLIC_DOMAIN') and settings.RAILWAY_PUBLIC_DOMAIN:
                            # Автоматически формируем URL из Railway домена
                            domain = settings.RAILWAY_PUBLIC_DOMAIN
                            if not domain.startswith('http'):
                                domain = f"https://{domain}"
                            webhook_url = f"{domain}/telegram/webhook/"
                        else:
                            logger.warning(
                                "⚠️  TELEGRAM_WEBHOOK_URL или RAILWAY_PUBLIC_DOMAIN не установлены.\n"
                                "   Webhook не будет настроен автоматически.\n"
                                "   Установите TELEGRAM_WEBHOOK_URL в переменных окружения Railway."
                            )
                        
                        if webhook_url:
                            # Настраиваем webhook (синхронно, не в потоке)
                            start_telegram_bot_webhook(application, webhook_url)
                            _bot_started = True
                            logger.info("✅ Telegram бот настроен через Webhook")
                        else:
                            logger.warning("⚠️  Webhook URL не определен, бот не будет работать")
                except Exception as e:
                    logger.error(f"❌ Ошибка инициализации Telegram бота: {e}", exc_info=True)
