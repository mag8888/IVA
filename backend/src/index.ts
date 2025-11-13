import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { initDatabase } from './db';
import { initTelegramBot } from './telegram';
import { router as apiRouter } from './routes/api';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api', apiRouter);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Initialize database and Telegram bot
async function startServer() {
  try {
    await initDatabase();
    console.log('✅ Database connected');

    if (process.env.TELEGRAM_BOT_TOKEN) {
      initTelegramBot();
      console.log('✅ Telegram bot initialized');
    } else {
      console.log('⚠️  Telegram bot token not provided');
    }

    app.listen(PORT, () => {
      console.log(`🚀 Backend server running on port ${PORT}`);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

startServer();

