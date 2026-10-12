import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000,
})

// 拦截器：自动添加 Token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 拦截器：处理 401 错误
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 认证相关
export const authApi = {
  register: (data: any) => api.post('/api/auth/register', data).then(r => r.data),
  login: (username: string, password: string) => {
    const form = new URLSearchParams()
    form.append('username', username)
    form.append('password', password)
    return api.post('/api/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }).then(r => r.data)
  },
  me: () => api.get('/api/auth/me').then(r => r.data),
}

// 菜单相关
export const menuApi = {
  list: (mealType?: string) => {
    const params = mealType ? `?meal_type=${mealType}` : ''
    return api.get(`/api/menus/${params}`).then(r => r.data)
  },
  get: (id: number) => api.get(`/api/menus/${id}`).then(r => r.data),
  create: (data: any) => api.post('/api/menus/', data).then(r => r.data),
  update: (id: number, data: any) => api.put(`/api/menus/${id}`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/api/menus/${id}`).then(r => r.data),
}

// 订单相关
export const orderApi = {
  listByTable: (token: string) => api.get(`/api/orders/table/${token}`).then(r => r.data),
  listAll: () => api.get('/api/orders/all').then(r => r.data),
  get: (id: number) => api.get(`/api/orders/${id}`).then(r => r.data),
  create: (data: any) => api.post('/api/orders/', data).then(r => r.data),
  updateStatus: (id: number, status: string) =>
    api.put(`/api/orders/${id}/status`, { status }).then(r => r.data),
}

// 餐桌相关
export const tableApi = {
  list: () => api.get('/api/tables/').then(r => r.data),
  getByToken: (token: string) => api.get(`/api/tables/by-token/${token}`).then(r => r.data),
  create: (data: any) => api.post('/api/tables/', data).then(r => r.data),
  delete: (id: number) => api.delete(`/api/tables/${id}`).then(r => r.data),
}

// 用户管理相关（管理员专用）
export const usersApi = {
  list: () => api.get('/api/users/').then(r => r.data),
  update: (id: number, data: any) => api.put(`/api/users/${id}`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/api/users/${id}`).then(r => r.data),
}

// WebSocket 连接
export function createWebSocket(): WebSocket {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const ws = new WebSocket(`${protocol}//${window.location.host}/ws`)
  return ws
}

export default api
