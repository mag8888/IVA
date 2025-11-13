import { Router } from 'express';
import { query } from '../db';

export const router = Router();

// Get all users
router.get('/users', async (req, res) => {
  try {
    const result = await query('SELECT * FROM users ORDER BY created_at DESC');
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching users:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get user by Telegram ID
router.get('/users/telegram/:telegramId', async (req, res) => {
  try {
    const { telegramId } = req.params;
    const result = await query('SELECT * FROM users WHERE telegram_id = $1', [telegramId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error fetching user:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get messages
router.get('/messages', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit as string) || 50;
    const result = await query(
      `SELECT m.*, u.telegram_id, u.username, u.first_name 
       FROM messages m 
       JOIN users u ON m.user_id = u.id 
       ORDER BY m.created_at DESC 
       LIMIT $1`,
      [limit]
    );
    res.json(result.rows);
  } catch (error) {
    console.error('Error fetching messages:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get stats
router.get('/stats', async (req, res) => {
  try {
    const usersResult = await query('SELECT COUNT(*) as count FROM users');
    const messagesResult = await query('SELECT COUNT(*) as count FROM messages');
    
    res.json({
      users: parseInt(usersResult.rows[0].count),
      messages: parseInt(messagesResult.rows[0].count),
    });
  } catch (error) {
    console.error('Error fetching stats:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

