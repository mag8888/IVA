import TelegramBot, { Message } from 'node-telegram-bot-api';
import dotenv from 'dotenv';
import { query } from './db';

dotenv.config();

let bot: TelegramBot | null = null;

export function initTelegramBot() {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  if (!token) {
    throw new Error('TELEGRAM_BOT_TOKEN is not set');
  }

  bot = new TelegramBot(token, { polling: true });

  // Handle /start command
  bot.onText(/\/start/, async (msg: Message) => {
    const chatId = msg.chat.id;
    const userId = msg.from?.id;
    const username = msg.from?.username;
    const firstName = msg.from?.first_name;

    try {
      // Save or update user in database
      await query(
        `INSERT INTO users (telegram_id, username, first_name)
         VALUES ($1, $2, $3)
         ON CONFLICT (telegram_id) 
         DO UPDATE SET username = $2, first_name = $3`,
        [userId, username || null, firstName || null]
      );

      // Save message
      const userResult = await query('SELECT id FROM users WHERE telegram_id = $1', [userId]);
      const dbUserId = userResult.rows[0]?.id;

      if (dbUserId) {
        await query(
          `INSERT INTO messages (user_id, telegram_message_id, text)
           VALUES ($1, $2, $3)`,
          [dbUserId, msg.message_id, msg.text]
        );
      }

      bot?.sendMessage(chatId, `Привет, ${firstName || 'пользователь'}! 👋\n\nБот успешно подключен к базе данных.`);
    } catch (error) {
      console.error('Error handling /start command:', error);
      bot?.sendMessage(chatId, 'Произошла ошибка при обработке команды.');
    }
  });

  // Handle all messages
  bot.on('message', async (msg: Message) => {
    if (msg.text?.startsWith('/')) {
      return; // Skip commands (already handled)
    }

    const chatId = msg.chat.id;
    const userId = msg.from?.id;

    try {
      const userResult = await query('SELECT id FROM users WHERE telegram_id = $1', [userId]);
      const dbUserId = userResult.rows[0]?.id;

      if (dbUserId && msg.text) {
        await query(
          `INSERT INTO messages (user_id, telegram_message_id, text)
           VALUES ($1, $2, $3)`,
          [dbUserId, msg.message_id, msg.text]
        );
      }

      bot?.sendMessage(chatId, `Вы написали: ${msg.text}`);
    } catch (error) {
      console.error('Error handling message:', error);
    }
  });

  console.log('Telegram bot is running...');
  return bot;
}

export function getBot(): TelegramBot | null {
  return bot;
}

