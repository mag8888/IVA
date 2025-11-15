"""
Telegram Bot integration для Equilibrium MLM.
"""
import logging
import json
import asyncio
import secrets
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.request import HTTPXRequest
from django.db import models
from asgiref.sync import sync_to_async
from core.models import User
from mlm.models import StructureNode, Tariff
from billing.models import Bonus, Payment

logger = logging.getLogger(__name__)

# Глобальная переменная для бота
bot_application = None
bot_event_loop = None


@sync_to_async
def get_user_by_telegram_id(telegram_id):
    return User.objects.get(telegram_id=telegram_id)


@sync_to_async
def create_user_from_telegram(telegram_id, telegram_user, inviter=None):
    username = f"tg_{telegram_id}"
    if User.objects.filter(username=username).exists():
        username = f"tg_{telegram_id}_{secrets.token_hex(4)}"
    return User.objects.create_user(
        username=username,
        email=f"tg_{telegram_id}@telegram.local",
        telegram_id=telegram_id,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name or '',
        invited_by=inviter,
    )


@sync_to_async
def get_node_for_user(db_user):
    try:
        return StructureNode.objects.get(user=db_user)
    except StructureNode.DoesNotExist:
        return None


@sync_to_async
def get_bonus_summary(db_user):
    total = Bonus.objects.filter(user=db_user).aggregate(total=models.Sum('amount'))['total'] or 0
    green = Bonus.objects.filter(user=db_user, bonus_type=Bonus.BonusType.GREEN).aggregate(total=models.Sum('amount'))['total'] or 0
    yellow = Bonus.objects.filter(user=db_user, bonus_type=Bonus.BonusType.YELLOW).aggregate(total=models.Sum('amount'))['total'] or 0
    return total, green, yellow


@sync_to_async
def get_active_tariffs():
    """Получить список активных тарифов."""
    return list(Tariff.objects.filter(is_active=True).order_by('entry_amount'))


@sync_to_async
def create_payment_for_user(user, tariff, amount):
    """Создать платеж для пользователя."""
    from django.utils import timezone
    payment = Payment.objects.create(
        user=user,
        tariff=tariff,
        amount=amount,
        status=Payment.PaymentStatus.PENDING,
    )
    return payment


@sync_to_async
def get_invited_stats(db_user):
    """Получить статистику приглашенных пользователей."""
    # Все приглашенные пользователи
    total_invited = User.objects.filter(invited_by=db_user).count()
    
    # Приглашенные, которые оплатили (имеют хотя бы один завершенный платеж)
    invited_with_payment = User.objects.filter(
        invited_by=db_user,
        payments__status=Payment.PaymentStatus.COMPLETED
    ).distinct().count()
    
    return total_invited, invited_with_payment


async def get_referral_link(db_user, bot=None):
    """Получить реферальную ссылку для пользователя."""
    bot_username = None
    
    # Сначала проверяем настройки (быстрее)
    bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', None)
    
    # Если нет в настройках и есть бот, пытаемся получить из API
    if not bot_username and bot:
        try:
            bot_info = await bot.get_me()
            bot_username = bot_info.username if bot_info else None
            if bot_username:
                logger.info(f"✅ Получен username бота из API: {bot_username}")
        except Exception as e:
            logger.warning(f"⚠️  Не удалось получить username бота из API: {e}")
    
    # Если есть username бота, используем его для реферальной ссылки
    if bot_username:
        referral_link = f"https://t.me/{bot_username}?start={db_user.referral_code}"
        logger.debug(f"📝 Реферальная ссылка (Telegram): {referral_link}")
    else:
        # Иначе используем веб-ссылку
        base_url = settings.RAILWAY_PUBLIC_DOMAIN or settings.TELEGRAM_WEBAPP_URL or 'https://iva.up.railway.app'
        if not base_url.startswith('http'):
            base_url = f"https://{base_url}"
        referral_link = f"{base_url}/?ref={db_user.referral_code}"
        logger.debug(f"📝 Реферальная ссылка (Web): {referral_link}")
    
    return referral_link


@sync_to_async
def get_user_by_referral_code(referral_code):
    """Получить пользователя по реферальному коду."""
    try:
        return User.objects.get(referral_code=referral_code)
    except User.DoesNotExist:
        return None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    logger.info(f"📥 Получена команда /start от пользователя {update.effective_user.id if update.effective_user else 'unknown'}")
    telegram_user = update.effective_user
    if not telegram_user:
        logger.error("❌ update.effective_user is None")
        return
    
    telegram_id = telegram_user.id
    
    # Получаем реферальный код из параметра команды (если есть)
    referral_code = None
    if update.message and update.message.text:
        parts = update.message.text.split()
        if len(parts) > 1:
            referral_code = parts[1]
            logger.info(f"🔗 Найден реферальный код: {referral_code}")
    
    try:
        db_user = await get_user_by_telegram_id(telegram_id)
        logger.info(f"✅ Пользователь {telegram_id} найден в БД: {db_user.username}")
    except User.DoesNotExist:
        logger.info(f"ℹ️  Пользователь {telegram_id} не найден в БД, создаем нового")
        try:
            # Если есть реферальный код, находим пригласившего пользователя
            inviter = None
            if referral_code:
                inviter = await get_user_by_referral_code(referral_code)
                if inviter:
                    logger.info(f"✅ Найден пригласивший пользователь: {inviter.username}")
                else:
                    logger.warning(f"⚠️  Реферальный код {referral_code} не найден")
            
            # Создаем пользователя с указанием пригласившего
            db_user = await create_user_from_telegram(telegram_id, telegram_user, inviter)
            logger.info(f"✅ Создан новый пользователь для Telegram ID {telegram_id}: {db_user.username}")
            
            # Получаем имя пользователя (предпочтительно first_name из Telegram)
            if telegram_user.first_name:
                user_name = telegram_user.first_name
                if telegram_user.last_name:
                    user_name = f"{telegram_user.first_name} {telegram_user.last_name}"
            else:
                # Если нет имени, используем username из Telegram или базы
                user_name = telegram_user.username or db_user.username
            
            # Получаем активные тарифы для кнопки оплаты
            tariffs = await get_active_tariffs()
            
            # Создаем клавиатуру с кнопками
            keyboard = []
            if tariffs:
                keyboard.append([InlineKeyboardButton(
                    "💳 Оплатить",
                    callback_data="pay_select_tariff"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            # Получаем статистику приглашенных
            total_invited, invited_with_payment = await get_invited_stats(db_user)
            
            # Получаем реферальную ссылку
            referral_link = await get_referral_link(db_user, context.bot)
            
            # Формируем сообщение в новом формате
            message_text = (
                f"Привет, {user_name}! 👋\n\n"
                f"📊 Твоя информация:\n"
                f"📈 Статус: {db_user.get_status_display()}\n"
                f"🌳 Еще не размещен в структуре\n"
                f"💚 Бонус вывод (зеленый): $0.00\n"
                f"💛 Бонус накопительный (желтый): $0.00\n"
                f"💰 Всего бонусов: $0.00\n\n"
                f"Приглашенных {total_invited}/{invited_with_payment}\n\n"
                f"🔗 Реферальная ссылка: {referral_link}"
            )
            
            try:
                await update.message.reply_text(
                    message_text,
                    reply_markup=reply_markup
                )
                logger.info(f"✅ Сообщение успешно отправлено новому пользователю {telegram_id}")
            except Exception as send_error:
                logger.error(f"❌ Ошибка при отправке сообщения новому пользователю: {send_error}", exc_info=True)
            return
        except Exception as e:
            logger.error(f"❌ Ошибка создания пользователя: {e}", exc_info=True)
            await update.message.reply_text(
                f"Привет, {telegram_user.first_name}! 👋\n\n"
                f"Добро пожаловать в Equilibrium MLM System!\n\n"
                f"Для полной регистрации перейди на веб-сайт:\n"
                f"https://iva.up.railway.app\n\n"
                f"Или используй /app для просмотра структуры."
            )
            return
    
    try:
        node = await get_node_for_user(db_user)
        level_info = "Еще не размещен в структуре"
        if node:
            level_info = f"Уровень: {node.level}, Позиция: {node.position}"
        
        # Получаем бонусы: всего, зеленые (вывод), желтые (накопительный)
        total_bonuses, green_bonuses, yellow_bonuses = await get_bonus_summary(db_user)
        
        # Получаем статистику приглашенных
        total_invited, invited_with_payment = await get_invited_stats(db_user)
        
        # Получаем реферальную ссылку
        referral_link = await get_referral_link(db_user, context.bot)
        
        # Получаем имя пользователя (предпочтительно first_name из Telegram)
        if telegram_user.first_name:
            user_name = telegram_user.first_name
            if telegram_user.last_name:
                user_name = f"{telegram_user.first_name} {telegram_user.last_name}"
        else:
            # Если нет имени, используем username из Telegram или базы
            user_name = telegram_user.username or db_user.username
        
        # Получаем активные тарифы для кнопки оплаты
        tariffs = await get_active_tariffs()
        
        # Создаем клавиатуру с кнопками
        keyboard = []
        
        # Если есть тарифы, добавляем кнопку оплаты
        if tariffs:
            keyboard.append([InlineKeyboardButton(
                "💳 Оплатить",
                callback_data="pay_select_tariff"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        # Формируем сообщение в новом формате
        message_text = (
            f"Привет, {user_name}! 👋\n\n"
            f"📊 Твоя информация:\n"
            f"📈 Статус: {db_user.get_status_display()}\n"
            f"🌳 {level_info}\n"
            f"💚 Бонус вывод (зеленый): ${green_bonuses:.2f}\n"
            f"💛 Бонус накопительный (желтый): ${yellow_bonuses:.2f}\n"
            f"💰 Всего бонусов: ${total_bonuses:.2f}\n\n"
            f"Приглашенных {total_invited}/{invited_with_payment}\n\n"
            f"🔗 Реферальная ссылка: {referral_link}"
        )
        
        try:
            await update.message.reply_text(
                message_text,
                reply_markup=reply_markup
            )
            logger.info(f"✅ Сообщение успешно отправлено пользователю {telegram_id}")
        except Exception as send_error:
            logger.error(f"❌ Ошибка при отправке сообщения: {send_error}", exc_info=True)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка в start_command: {e}", exc_info=True)
        try:
            if update.message and update.effective_user:
                await update.message.reply_text(
                    "❌ Произошла ошибка при обработке команды. Попробуйте позже или обратитесь к администратору."
                )
        except Exception as send_error:
            logger.error(f"❌ Не удалось отправить сообщение об ошибке: {send_error}")


async def app_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /app - открытие мини-приложения с MLM структурой."""
    logger.info(f"📥 Получена команда /app от пользователя {update.effective_user.id}")
    webapp_url = settings.TELEGRAM_WEBAPP_URL or settings.RAILWAY_PUBLIC_DOMAIN
    
    logger.info(f"🔗 Webapp URL: {webapp_url}")
    
    if not webapp_url:
        # Если URL не настроен, используем текущий домен из запроса
        # В production это должно быть настроено через переменные окружения
        logger.warning("⚠️  TELEGRAM_WEBAPP_URL и RAILWAY_PUBLIC_DOMAIN не установлены")
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
    logger.info(f"🌐 Webapp path: {webapp_path}")
    
    # Создаем кнопку для открытия веб-приложения
    keyboard = [
        [InlineKeyboardButton(
            "🌳 Открыть мою структуру",
            web_app={"url": webapp_path}
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    logger.info(f"✅ Отправляю кнопку с Web App для пользователя {update.effective_user.id}")
    await update.message.reply_text(
        "👋 Добро пожаловать в Equilibrium MLM!\n\n"
        "Нажмите кнопку ниже, чтобы открыть вашу MLM структуру:",
        reply_markup=reply_markup
    )


async def payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик callback для кнопки оплаты."""
    query = update.callback_query
    await query.answer()
    
    telegram_user = update.effective_user
    if not telegram_user:
        return
    
    telegram_id = telegram_user.id
    
    try:
        db_user = await get_user_by_telegram_id(telegram_id)
    except User.DoesNotExist:
        await query.edit_message_text("❌ Вы не зарегистрированы в системе. Используйте /start")
        return
    
    if query.data == "pay_select_tariff":
        # Получаем активные тарифы
        tariffs = await get_active_tariffs()
        
        if not tariffs:
            await query.edit_message_text("❌ Нет доступных тарифов для оплаты.")
            return
        
        # Создаем кнопки для выбора тарифа
        keyboard = []
        for tariff in tariffs:
            keyboard.append([InlineKeyboardButton(
                f"{tariff.name} - ${tariff.entry_amount}",
                callback_data=f"pay_tariff_{tariff.id}"
            )])
        
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="pay_cancel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        tariffs_text = "\n".join([
            f"• {tariff.name} - ${tariff.entry_amount}"
            for tariff in tariffs
        ])
        
        await query.edit_message_text(
            f"💳 Выберите тариф для оплаты:\n\n{tariffs_text}",
            reply_markup=reply_markup
        )
    
    elif query.data.startswith("pay_tariff_"):
        tariff_id = int(query.data.split("_")[-1])
        tariffs = await get_active_tariffs()
        selected_tariff = next((t for t in tariffs if t.id == tariff_id), None)
        
        if not selected_tariff:
            await query.edit_message_text("❌ Тариф не найден.")
            return
        
        # Создаем платеж
        payment = await create_payment_for_user(
            db_user,
            selected_tariff,
            selected_tariff.entry_amount
        )
        
        # Здесь можно интегрировать платежную систему
        # Пока просто информируем пользователя
        payment_url = f"{settings.RAILWAY_PUBLIC_DOMAIN or 'https://iva.up.railway.app'}/pay/{payment.id}/"
        
        keyboard = [[InlineKeyboardButton(
            "🔗 Перейти к оплате",
            url=payment_url
        )]]
        keyboard.append([InlineKeyboardButton("↩️ Назад", callback_data="pay_select_tariff")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"💳 Создан платеж:\n\n"
            f"Тариф: {selected_tariff.name}\n"
            f"Сумма: ${selected_tariff.entry_amount}\n"
            f"ID платежа: {payment.id}\n\n"
            f"Нажмите кнопку ниже для оплаты:",
            reply_markup=reply_markup
        )
    
    elif query.data == "pay_cancel":
        await query.edit_message_text("❌ Оплата отменена. Используйте /start для возврата в главное меню.")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /stats - статистика пользователя."""
    telegram_user = update.effective_user
    telegram_id = telegram_user.id
    
    try:
        db_user = User.objects.get(telegram_id=telegram_id)
        
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
    
    # Создаем приложение с увеличенными таймаутами
    # Увеличиваем таймауты для Railway (может быть медленное соединение с Telegram API)
    request = HTTPXRequest(
        connect_timeout=30.0,  # Увеличен до 30 секунд
        read_timeout=30.0,     # Увеличен до 30 секунд
        write_timeout=30.0,    # Увеличен до 30 секунд
        pool_timeout=30.0,     # Увеличен до 30 секунд
    )
    application = Application.builder().token(token).request(request).build()
    
    # Инициализируем приложение (обязательно для обработки событий)
    global bot_event_loop
    bot_event_loop = asyncio.new_event_loop()
    bot_event_loop.run_until_complete(application.initialize())
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("app", app_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Регистрируем обработчик callback для кнопок оплаты
    application.add_handler(CallbackQueryHandler(payment_callback, pattern="^pay_"))
    
    # Сохраняем глобально
    bot_application = application
    
    logger.info("✅ Telegram бот инициализирован")
    return application


async def setup_webhook(application, webhook_url):
    """Установка webhook для Telegram бота."""
    try:
        # Удаляем предыдущий webhook, если был
        await application.bot.delete_webhook(drop_pending_updates=True)
        logger.info("🗑️  Удален предыдущий webhook")
        
        # Устанавливаем новый webhook
        result = await application.bot.set_webhook(
            url=webhook_url,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
        if result:
            logger.info(f"✅ Webhook установлен: {webhook_url}")
            
            # Проверяем информацию о webhook
            webhook_info = await application.bot.get_webhook_info()
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
            asyncio.run(application.bot.delete_webhook())
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
        global bot_event_loop
        if bot_event_loop is None:
            bot_event_loop = asyncio.new_event_loop()
        result = bot_event_loop.run_until_complete(setup_webhook(application, webhook_url))
        if result:
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
        
        # Логируем входящее обновление
        if update.message and update.message.text:
            logger.info(f"📨 Получено сообщение: {update.message.text} от {update.effective_user.id if update.effective_user else 'unknown'}")
        elif update.callback_query:
            logger.info(f"📨 Получен callback: {update.callback_query.data} от {update.effective_user.id if update.effective_user else 'unknown'}")
        elif update.message:
            logger.info(f"📨 Получено обновление от {update.effective_user.id if update.effective_user else 'unknown'}")
        
        # Обрабатываем обновление синхронно, но в отдельном потоке с новым event loop
        global bot_event_loop
        if bot_event_loop is None:
            bot_event_loop = asyncio.new_event_loop()
        try:
            logger.info(f"🔄 Начинаю обработку обновления для пользователя {update.effective_user.id if update.effective_user else 'unknown'}")
            bot_event_loop.run_until_complete(bot_application.process_update(update))
            logger.info(f"✅ Обновление успешно обработано для пользователя {update.effective_user.id if update.effective_user else 'unknown'}")
        except Exception as process_error:
            logger.error(f"❌ Ошибка при process_update: {process_error}", exc_info=True)
            try:
                if update.effective_user:
                    if update.message:
                        bot_event_loop.run_until_complete(
                            bot_application.bot.send_message(
                                chat_id=update.effective_user.id,
                                text="❌ Произошла ошибка при обработке команды. Попробуйте позже."
                            )
                        )
                    elif update.callback_query:
                        bot_event_loop.run_until_complete(
                            bot_application.bot.answer_callback_query(
                                callback_query_id=update.callback_query.id,
                                text="❌ Произошла ошибка при обработке. Попробуйте позже.",
                                show_alert=True
                            )
                        )
            except Exception as send_error:
                logger.error(f"❌ Не удалось отправить сообщение об ошибке: {send_error}")
        
        logger.info(f"✅ Webhook запрос обработан")
        return JsonResponse({"ok": True})
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Ошибка парсинга JSON: {e}")
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook: {e}", exc_info=True)
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


def start_telegram_bot():
    """Запуск Telegram бота (для использования в отдельном процессе)."""
    # Эта функция больше не используется - бот работает через webhook
    # Оставлена для обратной совместимости
    logger.warning("⚠️  start_telegram_bot() больше не используется - бот работает через webhook")
    application = init_telegram_bot()
    if application:
        logger.info("✅ Бот инициализирован, но не запущен через polling (используется webhook)")
