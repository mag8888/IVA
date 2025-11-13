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
    // Проверяем переменные окружения
    console.log('🔍 Checking environment variables...');
    console.log('   PORT:', process.env.PORT || '3001 (default)');
    console.log('   NODE_ENV:', process.env.NODE_ENV || 'not set');
    console.log('   DATABASE_URL:', process.env.DATABASE_URL ? '✅ Set' : '❌ NOT SET');
    console.log('   TELEGRAM_BOT_TOKEN:', process.env.TELEGRAM_BOT_TOKEN ? '✅ Set' : '⚠️  Not set');
    
    await initDatabase();
    console.log('✅ Database connected and initialized');

    if (process.env.TELEGRAM_BOT_TOKEN) {
      initTelegramBot();
      console.log('✅ Telegram bot initialized');
    } else {
      console.log('⚠️  Telegram bot token not provided - bot will not work');
    }

    app.listen(PORT, () => {
      console.log(`🚀 Backend server running on port ${PORT}`);
      console.log(`🌐 Health check: http://localhost:${PORT}/health`);
    });
  } catch (error: any) {
    console.error('❌ Failed to start server:', error);
    
    if (error.message?.includes('DATABASE_URL')) {
      console.error('\n📋 SOLUTION:');
      console.error('   1. Go to Railway dashboard');
      console.error('   2. Select your PostgreSQL service');
      console.error('   3. Go to "Variables" tab');
      console.error('   4. Copy the "DATABASE_URL" value');
      console.error('   5. Go to your Backend service');
      console.error('   6. Add variable: DATABASE_URL = <copied value>');
      console.error('   7. Or connect PostgreSQL service to Backend service');
    }
    
    process.exit(1);
  }
}

startServer();

