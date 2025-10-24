import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Helper para obter o token dos cookies
export const getToken = () => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; token=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return null
}

// Helper para remover o token
export const removeToken = () => {
  document.cookie = 'token=; path=/; max-age=0'
}

// Interceptor para adicionar token em todas as requisições
api.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Interceptor para logging de erros e tratamento de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    
    // Se retornar 401, redireciona para login
    if (error.response?.status === 401) {
      removeToken()
      window.location.href = '/auth'
    }
    
    return Promise.reject(error)
  }
)

export default api

// Funções da API

export const getTables = async () => {
  const { data } = await api.get('/tables')
  return data
}

export const getTableData = async ({ table_name, page = 1, page_size = 50, search = '', sort_by = '', sort_order = 'asc' }) => {
  const params = {
    page,
    page_size,
    ...(search && { search }),
    ...(sort_by && { sort_by, sort_order }),
  }
  
  const { data } = await api.get(`/tables/${table_name}/data`, { params })
  return data
}

export const uploadExcel = async (file, table_name = null) => {
  const formData = new FormData()
  formData.append('file', file)
  if (table_name) {
    formData.append('table_name', table_name)
  }
  
  const { data } = await api.post('/upload/excel', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}

export const queryData = async (question) => {
  const { data } = await api.post('/query', null, {
    params: { question },
  })
  return data
}

// Funções de Autenticação

export const register = async (username, password) => {
  const { data } = await api.post('/auth/register', { username, password })
  return data
}

export const login = async (username, password) => {
  const { data } = await api.post('/auth/login', { username, password })
  return data
}

export const getMe = async () => {
  const { data } = await api.get('/auth/me')
  return data
}

export const logout = () => {
  removeToken()
  window.location.href = '/auth'
}
