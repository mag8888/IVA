import { useEffect, useState } from 'react'
import { apiService, Stats } from '../services/api'

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStats()
    const interval = setInterval(loadStats, 30000) // Обновление каждые 30 секунд
    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    try {
      setError(null)
      const data = await apiService.getStats()
      setStats(data)
      setLoading(false)
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки данных')
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="text-center">
        <i className="fas fa-spinner fa-spin fa-3x"></i>
        <p>Загрузка данных...</p>
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

  if (!stats) return null

  return (
    <div>
      <h1 className="mb-4">Дашборд</h1>

      {/* Статистика пользователей */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body">
              <h3>{stats.users.total}</h3>
              <p>Всего пользователей</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body">
              <h3>{stats.users.participants}</h3>
              <p>Участников</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body">
              <h3>{stats.users.partners}</h3>
              <p>Партнеров</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body">
              <h3>{stats.users.admins}</h3>
              <p>Администраторов</p>
            </div>
          </div>
        </div>
      </div>

      {/* Статистика структуры и платежей */}
      <div className="row mb-4">
        <div className="col-md-4">
          <div className="card bg-secondary text-white">
            <div className="card-body">
              <h3>{stats.structure.total_nodes}</h3>
              <p>Узлов в структуре</p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card bg-danger text-white">
            <div className="card-body">
              <h3>{stats.payments.pending}</h3>
              <p>Ожидающих платежей</p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card bg-success text-white">
            <div className="card-body">
              <h3>{stats.payments.completed}</h3>
              <p>Завершенных платежей</p>
            </div>
          </div>
        </div>
      </div>

      {/* Статистика бонусов (из БД) */}
      <div className="row">
        <div className="col-md-4">
          <div className="card bg-success text-white">
            <div className="card-body">
              <h3>${stats.bonuses.total.toFixed(2)}</h3>
              <p>Всего бонусов</p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card text-white" style={{ backgroundColor: '#28a745' }}>
            <div className="card-body">
              <h3>${stats.bonuses.green.toFixed(2)}</h3>
              <p>Зеленых бонусов</p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card bg-warning text-white">
            <div className="card-body">
              <h3>${stats.bonuses.yellow.toFixed(2)}</h3>
              <p>Желтых бонусов</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

