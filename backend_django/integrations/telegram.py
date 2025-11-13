"""
Telegram Bot integration для Equilibrium MLM.
"""
import logging
from django.conf import settings
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


def start_telegram_bot_async(application):
    """Запуск Telegram бота в асинхронном режиме (для использования в потоке)."""
    try:
        logger.info("🚀 Запуск Telegram бота (polling)...")
        # Останавливаем предыдущий polling, если был
        try:
            if application.running:
                logger.info("⚠️  Останавливаем предыдущий polling...")
                application.stop()
        except:
            pass
        
        # Запускаем polling с обработкой ошибок
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False  # Не закрываем event loop при ошибке
        )
    except Exception as e:
        error_msg = str(e)
        if "409" in error_msg or "Conflict" in error_msg:
            logger.error(f"❌ Конфликт: Другой экземпляр бота уже запущен. Остановите другие процессы бота.")
        else:
            logger.error(f"❌ Ошибка при запуске Telegram бота: {e}", exc_info=True)


def start_telegram_bot():
    """Запуск Telegram бота (для использования в отдельном процессе)."""
    application = init_telegram_bot()
    if application:
        start_telegram_bot_async(application)
