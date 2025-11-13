import { Pool, PoolClient } from 'pg';
import dotenv from 'dotenv';

dotenv.config();

// Проверка наличия DATABASE_URL
if (!process.env.DATABASE_URL) {
  console.error('❌ DATABASE_URL is not set in environment variables');
  console.error('Please set DATABASE_URL in Railway service settings');
  throw new Error('DATABASE_URL environment variable is required');
}

console.log('📝 DATABASE_URL:', process.env.DATABASE_URL ? 'Set (hidden)' : 'NOT SET');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
  // Добавляем настройки для лучшего подключения
  connectionTimeoutMillis: 10000,
  idleTimeoutMillis: 30000,
  max: 20,
});

// Обработка ошибок подключения
pool.on('error', (err) => {
  console.error('❌ Unexpected error on idle client', err);
});

export async function initDatabase() {
  let retries = 5;
  let delay = 2000; // 2 секунды

  while (retries > 0) {
    try {
      console.log(`🔄 Attempting to connect to database... (${6 - retries}/5)`);
      
      const client = await pool.connect();
      console.log('✅ Connected to PostgreSQL database');
      
      // Проверяем подключение
      await client.query('SELECT NOW()');
      console.log('✅ Database connection verified');
      
      // Create tables if they don't exist
      await client.query(`
        CREATE TABLE IF NOT EXISTS users (
          id SERIAL PRIMARY KEY,
          telegram_id BIGINT UNIQUE NOT NULL,
          username VARCHAR(255),
          first_name VARCHAR(255),
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      `);

      await client.query(`
        CREATE TABLE IF NOT EXISTS messages (
          id SERIAL PRIMARY KEY,
          user_id INTEGER REFERENCES users(id),
          telegram_message_id BIGINT,
          text TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      `);

      client.release();
      console.log('✅ Database tables initialized');
      return; // Успешное подключение
    } catch (error: any) {
      retries--;
      
      if (error.code === 'ECONNREFUSED') {
        console.error(`❌ Database connection refused. Retries left: ${retries}`);
        console.error('💡 Check that:');
        console.error('   1. PostgreSQL service is running on Railway');
        console.error('   2. DATABASE_URL is correctly set in service variables');
        console.error('   3. PostgreSQL service is connected to this service');
      } else {
        console.error('❌ Database error:', error.message);
      }
      
      if (retries === 0) {
        console.error('❌ Failed to connect to database after 5 attempts');
        console.error('Full error:', error);
        throw error;
      }
      
      console.log(`⏳ Retrying in ${delay / 1000} seconds...`);
      await new Promise(resolve => setTimeout(resolve, delay));
      delay *= 1.5; // Увеличиваем задержку с каждой попыткой
    }
  }
}

export async function query(text: string, params?: any[]) {
  return pool.query(text, params);
}

export async function getClient(): Promise<PoolClient> {
  return pool.connect();
}

export { pool };

