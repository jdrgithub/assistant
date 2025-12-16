/**
 * Backend API client.
 */
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export interface ChatRequest {
  message: string
  conversation_id?: number
  role?: string
  use_rag?: boolean
}

export interface ChatResponse {
  message: string
  conversation_id: number
  sources?: Array<{
    id: string
    source: string
    content_preview: string
  }>
}

export interface DocumentIngest {
  content: string
  source: string
  metadata?: Record<string, any>
  tags?: string[]
}

export const authApi = {
  login: async (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    const response = await api.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
  register: async (username: string, password: string) => {
    const response = await api.post('/api/auth/register', {
      username,
      password,
    })
    return response.data
  },
}

export const chatApi = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/api/chat/', request)
    return response.data
  },
}

export const ingestApi = {
  ingestDocument: async (document: DocumentIngest) => {
    const response = await api.post('/api/ingest/', document)
    return response.data
  },
}

export default api

