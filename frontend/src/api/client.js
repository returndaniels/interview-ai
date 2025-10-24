import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para logging de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
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
