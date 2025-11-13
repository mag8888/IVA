import { useEffect, useState } from 'react'
import { apiService, QueueItem } from '../services/api'

export default function Queue() {
  const [queue, setQueue] = useState<QueueItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadQueue()
    const interval = setInterval(loadQueue, 30000) // Обновление каждые 30 секунд
    return () => clearInterval(interval)
  }, [])

  const loadQueue = async () => {
    try {
      setError(null)
      const data = await apiService.getQueue()
      setQueue(data)
      setLoading(false)
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки очереди')
      setLoading(false)
    }
  }

  const handleComplete = async (userId: number) => {
    if (!confirm('Завершить регистрацию? Все расчеты будут выполнены на сервере.')) {
      return
    }

    try {
      // В production здесь нужен токен аутентификации
      await apiService.completeRegistration(userId)
      alert('Регистрация завершена! Все расчеты выполнены на сервере.')
      loadQueue()
    } catch (err: any) {
      alert(`Ошибка: ${err.message}`)
    }
  }

  if (loading) {
    return (
      <div className="text-center">
        <i className="fas fa-spinner fa-spin fa-3x"></i>
        <p>Загрузка очереди...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="alert alert-danger">
        Ошибка: {error}
      </div>
    )
  }

  return (
    <div>
      <h1 className="mb-4">Очередь регистраций</h1>
      <button className="btn btn-primary mb-3" onClick={loadQueue}>
        <i className="fas fa-sync"></i> Обновить
      </button>

      {queue.length === 0 ? (
        <div className="alert alert-info">Очередь пуста</div>
      ) : (
        <table className="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Email</th>
              <th>Пригласивший</th>
              <th>Тариф</th>
              <th>Сумма</th>
              <th>Дата</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {queue.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.username}</td>
                <td>{item.email}</td>
                <td>{item.inviter_username || 'Нет'}</td>
                <td>{item.tariff.name} ({item.tariff.code})</td>
                <td>${item.amount}</td>
                <td>{new Date(item.created_at).toLocaleString('ru-RU')}</td>
                <td>
                  <button
                    className="btn btn-sm btn-success"
                    onClick={() => handleComplete(item.user)}
                  >
                    <i className="fas fa-check"></i> Завершить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

