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
        
        # Запускаем бота только в главном процессе Gunicorn (не в воркерах)
        # Gunicorn устанавливает RUN_MAIN='true' только в главном процессе
        if hasattr(sys, '_getframe'):
            # Проверяем, не воркер ли это
            frame = sys._getframe(1)
            if frame and 'gunicorn' in str(frame.f_globals.get('__file__', '')):
                # Это может быть воркер, проверяем RUN_MAIN
                if os.environ.get('RUN_MAIN') != 'true':
                    logger.info("⚠️  Пропускаем запуск бота в воркере Gunicorn")
                    return
        
        # Запускаем бота только один раз (даже если ready() вызывается несколько раз)
        with _bot_lock:
            if _bot_started:
                logger.info("⚠️  Telegram бот уже запущен, пропускаем повторную инициализацию")
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
                        _bot_started = True
                        logger.info("✅ Telegram бот запущен в отдельном потоке")
                except Exception as e:
                    logger.error(f"❌ Ошибка инициализации Telegram бота: {e}", exc_info=True)
