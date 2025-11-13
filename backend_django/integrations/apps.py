from django.apps import AppConfig
import threading
import logging

logger = logging.getLogger(__name__)


class IntegrationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'integrations'
    
    def ready(self):
        """Инициализация при запуске приложения."""
        # Запускаем бота только в основном процессе (не в миграциях)
        import sys
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
        
        from django.conf import settings
        if settings.TELEGRAM_BOT_TOKEN:
            try:
                from .telegram import init_telegram_bot, start_telegram_bot_async
                
                # Инициализируем бота
                application = init_telegram_bot()
                
                if application:
                    # Запускаем бота в отдельном потоке
                    bot_thread = threading.Thread(
                        target=start_telegram_bot_async,
                        args=(application,),
                        daemon=True,
                        name="TelegramBotThread"
                    )
                    bot_thread.start()
                    logger.info("✅ Telegram бот запущен в отдельном потоке")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации Telegram бота: {e}", exc_info=True)
