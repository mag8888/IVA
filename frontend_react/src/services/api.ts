/**
 * API Service - все данные из базы данных через API
 */
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Stats {
  users: {
    total: number
    participants: number
    partners: number
    admins: number
  }
  structure: {
    total_nodes: number
  }
  payments: {
    pending: number
    completed: number
  }
  bonuses: {
    total: number
    green: number
    yellow: number
  }
}

export interface QueueItem {
  id: number
  user: number
  username: string
  email: string
  inviter: string | null
  inviter_username: string | null
  tariff: {
    code: string
    name: string
    entry_amount: string
  }
  amount: string
  created_at: string
}

export interface StructureNode {
  id: number
  user: {
    id: number
    username: string
    referral_code: string
  }
  parent_username: string | null
  level: number
  position: number
  tariff_name: string | null
  tariff_code: string | null
  created_at: string
}

export interface Bonus {
  id: number
  user: {
    id: number
    username: string
  }
  source_user: {
    id: number
    username: string
  }
  bonus_type: 'GREEN' | 'YELLOW'
  bonus_type_display: string
  amount: string
  description: string
  created_at: string
}

export const apiService = {
  // Статистика (из БД)
  async getStats(): Promise<Stats> {
    const response = await api.get<Stats>('/api/stats/')
    return response.data
  },

  // Очередь (из БД)
  async getQueue(): Promise<QueueItem[]> {
    const response = await api.get<QueueItem[]>('/api/queue/public/')
    return response.data
  },

  // Структура (из БД)
  async getStructure(): Promise<StructureNode[]> {
    const response = await api.get<StructureNode[]>('/api/structure/')
    return response.data
  },

  // Дерево структуры (из БД)
  async getStructureTree(rootUserId?: number, maxDepth?: number): Promise<any> {
    const params: any = {}
    if (rootUserId) params.root_user_id = rootUserId
    if (maxDepth) params.max_depth = maxDepth
    
    const response = await api.get('/api/structure/tree/', { params })
    return response.data
  },

  // Бонусы (из БД)
  async getBonuses(userId?: number): Promise<Bonus[]> {
    const params: any = {}
    if (userId) params.user_id = userId
    
    const response = await api.get<Bonus[]>('/api/bonuses/', { params })
    return response.data
  },

  // Завершение регистрации (все расчеты на сервере)
  async completeRegistration(userId: number, token?: string): Promise<any> {
    const headers: any = {}
    if (token) {
      headers.Authorization = `Token ${token}`
    }
    
    const response = await api.post(
      '/api/complete/',
      { user_id: userId },
      { headers }
    )
    return response.data
  },
}

export default api

