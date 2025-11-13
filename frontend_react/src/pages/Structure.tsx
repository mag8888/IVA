import { useEffect, useState } from 'react'
import { apiService } from '../services/api'

export default function Structure() {
  const [tree, setTree] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStructure()
  }, [])

  const loadStructure = async () => {
    try {
      setError(null)
      const data = await apiService.getStructureTree()
      setTree(data)
      setLoading(false)
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки структуры')
      setLoading(false)
    }
  }

  const renderNode = (node: any, level: number = 0): JSX.Element => {
    return (
      <div key={node.user.id} style={{ marginLeft: `${level * 20}px`, marginTop: '10px' }}>
        <div className={`card ${level === 0 ? 'bg-primary text-white' : ''}`} style={{ display: 'inline-block', minWidth: '200px' }}>
          <div className="card-body">
            <h6>{node.user.username}</h6>
            <small>Level {node.level}, Pos {node.position}</small>
            {node.tariff && <div><small>{node.tariff.name}</small></div>}
          </div>
        </div>
        {node.children && node.children.length > 0 && (
          <div>
            {node.children.map((child: any) => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="text-center">
        <i className="fas fa-spinner fa-spin fa-3x"></i>
        <p>Загрузка структуры...</p>
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

  if (!tree) {
    return <div className="alert alert-info">Структура пуста</div>
  }

  return (
    <div>
      <h1 className="mb-4">MLM Структура</h1>
      <button className="btn btn-primary mb-3" onClick={loadStructure}>
        <i className="fas fa-sync"></i> Обновить
      </button>
      <div>
        {renderNode(tree)}
      </div>
    </div>
  )
}

