'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

interface Stats {
  users: number;
  messages: number;
}

interface User {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  created_at: string;
}

interface Message {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  text: string;
  created_at: string;
}

export default function Home() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Обновление каждые 5 секунд
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setError(null);
      const [statsRes, usersRes, messagesRes] = await Promise.all([
        axios.get(`${API_URL}/api/stats`),
        axios.get(`${API_URL}/api/users`),
        axios.get(`${API_URL}/api/messages?limit=10`),
      ]);

      setStats(statsRes.data);
      setUsers(usersRes.data);
      setMessages(messagesRes.data);
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки данных');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Загрузка данных...</div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1 style={{ marginBottom: '2rem', fontSize: '2.5rem' }}>Equilibrium Dashboard</h1>

      {error && (
        <div className="error">
          Ошибка: {error}
        </div>
      )}

      {stats && (
        <div className="stats">
          <div className="stat-card">
            <h3>{stats.users}</h3>
            <p>Пользователей</p>
          </div>
          <div className="stat-card">
            <h3>{stats.messages}</h3>
            <p>Сообщений</p>
          </div>
        </div>
      )}

      <div className="card">
        <h2>Последние пользователи</h2>
        {users.length === 0 ? (
          <p>Пользователей пока нет</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Telegram ID</th>
                <th>Username</th>
                <th>Имя</th>
                <th>Дата регистрации</th>
              </tr>
            </thead>
            <tbody>
              {users.slice(0, 10).map((user) => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>{user.telegram_id}</td>
                  <td>@{user.username || '—'}</td>
                  <td>{user.first_name || '—'}</td>
                  <td>{new Date(user.created_at).toLocaleString('ru-RU')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h2>Последние сообщения</h2>
        {messages.length === 0 ? (
          <p>Сообщений пока нет</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Пользователь</th>
                <th>Сообщение</th>
                <th>Дата</th>
              </tr>
            </thead>
            <tbody>
              {messages.map((msg) => (
                <tr key={msg.id}>
                  <td>
                    {msg.first_name || msg.username || 'Неизвестно'}
                    {msg.username && ` (@${msg.username})`}
                  </td>
                  <td>{msg.text}</td>
                  <td>{new Date(msg.created_at).toLocaleString('ru-RU')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
