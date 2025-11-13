"""
Telegram Bot integration для Equilibrium MLM.
"""
import logging
import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from django.db import models
from core.models import User
from mlm.models import StructureNode
from billing.models import Bonus

logger = logging.getLogger(__name__)

# Глобальная переменная для бота
bot_application = None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    
    # Проверяем, зарегистрирован ли пользователь
    try:
        db_user = User.objects.get(username=str(user.id))
        await update.message.reply_text(
            f"Привет, {db_user.username}! 👋\n\n"
            f"Твой реферальный код: {db_user.referral_code}\n\n"
            f"Используй /app для просмотра структуры."
        )
    except User.DoesNotExist:
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋\n\n"
            f"Добро пожаловать в Equilibrium MLM System!\n\n"
            f"Для регистрации перейди на веб-сайт или используй /app"
        )


async def app_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /app - открытие мини-приложения с MLM структурой."""
    webapp_url = settings.TELEGRAM_WEBAPP_URL or settings.RAILWAY_PUBLIC_DOMAIN
    
    if not webapp_url:
        # Если URL не настроен, используем текущий домен из запроса
        # В production это должно быть настроено через переменные окружения
        await update.message.reply_text(
            "Мини-приложение не настроено. Обратитесь к администратору.\n\n"
            "Для настройки добавьте переменную TELEGRAM_WEBAPP_URL в Railway."
        )
        return
    
    # Убеждаемся, что URL начинается с https://
    if not webapp_url.startswith('http'):
        webapp_url = f"https://{webapp_url}"
    
    # URL мини-приложения
    webapp_path = f"{webapp_url}/telegram-app/"
    
    # Создаем кнопку для открытия веб-приложения
    keyboard = [
        [InlineKeyboardButton(
            "🌳 Открыть мою структуру",
            web_app={"url": webapp_path}
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Добро пожаловать в Equilibrium MLM!\n\n"
        "Нажмите кнопку ниже, чтобы открыть вашу MLM структуру:",
        reply_markup=reply_markup
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /stats - статистика пользователя."""
    user = update.effective_user
    
    try:
        db_user = User.objects.get(username=str(user.id))
        
        # Получаем узел структуры
        try:
            node = StructureNode.objects.get(user=db_user)
            level = node.level
            position = node.position
            tariff = node.tariff.name if node.tariff else "Нет"
        except StructureNode.DoesNotExist:
            level = "Не размещен"
            position = "-"
            tariff = "Нет"
        
        # Получаем бонусы из БД
        total_bonuses = Bonus.objects.filter(user=db_user).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        green_bonuses = Bonus.objects.filter(
            user=db_user,
            bonus_type=Bonus.BonusType.GREEN
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        yellow_bonuses = Bonus.objects.filter(
            user=db_user,
            bonus_type=Bonus.BonusType.YELLOW
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        stats_text = f"""
📊 Твоя статистика:

👤 Пользователь: {db_user.username}
🔗 Реферальный код: {db_user.referral_code}
📈 Статус: {db_user.get_status_display()}

🌳 Структура:
   Уровень: {level}
   Позиция: {position}
   Тариф: {tariff}

💰 Бонусы (из БД):
   Всего: ${total_bonuses:.2f}
   Зеленые: ${green_bonuses:.2f}
   Желтые: ${yellow_bonuses:.2f}
        """
        
        await update.message.reply_text(stats_text)
        
    except User.DoesNotExist:
        await update.message.reply_text(
            "Вы не зарегистрированы в системе. Используйте /start для начала."
        )


def init_telegram_bot():
    """Инициализация Telegram бота."""
    global bot_application
    
    # Проверяем, не запущен ли уже бот
    if bot_application is not None:
        logger.warning("⚠️  Telegram бот уже инициализирован, возвращаем существующий экземпляр")
        return bot_application
    
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN не установлен. Telegram бот не будет запущен.")
        return None
    
    # Создаем приложение
    application = Application.builder().token(token).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("app", app_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Сохраняем глобально
    bot_application = application
    
    logger.info("✅ Telegram бот инициализирован")
    return application


def setup_webhook(application, webhook_url):
    """Установка webhook для Telegram бота."""
    try:
        # Удаляем предыдущий webhook, если был
        application.bot.delete_webhook(drop_pending_updates=True)
        logger.info("🗑️  Удален предыдущий webhook")
        
        # Устанавливаем новый webhook
        result = application.bot.set_webhook(
            url=webhook_url,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
        if result:
            logger.info(f"✅ Webhook установлен: {webhook_url}")
            
            # Проверяем информацию о webhook
            webhook_info = application.bot.get_webhook_info()
            logger.info(f"📡 Webhook info: {webhook_info.url}, pending updates: {webhook_info.pending_update_count}")
            return True
        else:
            logger.error("❌ Не удалось установить webhook")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка при установке webhook: {e}", exc_info=True)
        return False


def remove_webhook(application):
    """Удаление webhook для Telegram бота."""
    try:
        if application and application.bot:
            application.bot.delete_webhook()
            logger.info("✅ Webhook удален")
            return True
    except Exception as e:
        logger.error(f"❌ Ошибка при удалении webhook: {e}", exc_info=True)
    return False


def start_telegram_bot_webhook(application, webhook_url):
    """Настройка webhook для Telegram бота (вместо polling)."""
    try:
        logger.info(f"🚀 Настройка Telegram бота через Webhook...")
        logger.info(f"📡 Webhook URL: {webhook_url}")
        
        # Устанавливаем webhook
        if setup_webhook(application, webhook_url):
            logger.info("✅ Telegram бот настроен через Webhook")
            return True
        else:
            logger.error("❌ Не удалось настроить webhook")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка при настройке webhook: {e}", exc_info=True)
        return False


@csrf_exempt
@require_http_methods(["POST"])
def telegram_webhook(request):
    """Django view для обработки webhook запросов от Telegram."""
    import asyncio
    import threading
    global bot_application
    
    if bot_application is None:
        logger.error("❌ Telegram бот не инициализирован")
        return JsonResponse({"ok": False, "error": "Bot not initialized"}, status=500)
    
    try:
        # Получаем JSON данные из запроса
        body = request.body.decode('utf-8')
        data = json.loads(body)
        
        # Создаем Update объект
        update = Update.de_json(data, bot_application.bot)
        
        # Обрабатываем обновление в отдельном потоке с новым event loop
        def process_update_async():
            """Обработка обновления в отдельном потоке."""
            try:
                # Создаем новый event loop для этого потока
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Запускаем обработку обновления
                loop.run_until_complete(bot_application.process_update(update))
                loop.close()
            except Exception as e:
                logger.error(f"❌ Ошибка обработки обновления в потоке: {e}", exc_info=True)
        
        # Запускаем обработку в отдельном потоке (не блокируем ответ)
        thread = threading.Thread(target=process_update_async, daemon=True)
        thread.start()
        
        # Сразу возвращаем ответ Telegram (не ждем обработки)
        return JsonResponse({"ok": True})
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Ошибка парсинга JSON: {e}")
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook: {e}", exc_info=True)
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


def start_telegram_bot():
    """Запуск Telegram бота (для использования в отдельном процессе)."""
    application = init_telegram_bot()
    if application:
        start_telegram_bot_async(application)
