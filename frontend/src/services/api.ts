/**
 * API service for EETL AI Platform
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/authStore'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const { tokens } = useAuthStore.getState()
    
    if (tokens?.access) {
      config.headers.Authorization = `Bearer ${tokens.access}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        await useAuthStore.getState().refreshToken()
        
        // Retry original request with new token
        const { tokens } = useAuthStore.getState()
        if (tokens?.access) {
          originalRequest.headers.Authorization = `Bearer ${tokens.access}`
        }
        
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh failed, logout user
        useAuthStore.getState().logout()
        window.location.href = '/auth/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

// API response types
export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: number
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// Generic API methods
export const apiService = {
  // GET request
  get: async <T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response: AxiosResponse<T> = await api.get(url, config)
    return response.data
  },

  // POST request
  post: async <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response: AxiosResponse<T> = await api.post(url, data, config)
    return response.data
  },

  // PUT request
  put: async <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response: AxiosResponse<T> = await api.put(url, data, config)
    return response.data
  },

  // PATCH request
  patch: async <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response: AxiosResponse<T> = await api.patch(url, data, config)
    return response.data
  },

  // DELETE request
  delete: async <T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response: AxiosResponse<T> = await api.delete(url, config)
    return response.data
  },

  // File upload
  upload: async <T = any>(
    url: string,
    file: File,
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<T> => {
    const formData = new FormData()
    formData.append('file', file)

    const response: AxiosResponse<T> = await api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    })
    
    return response.data
  },
}

// Authentication API
export const authApi = {
  login: (email: string, password: string) =>
    apiService.post('/auth/login/', { email, password }),
  
  register: (userData: any) =>
    apiService.post('/auth/register/', userData),
  
  logout: (refreshToken: string) =>
    apiService.post('/auth/logout/', { refresh_token: refreshToken }),
  
  refreshToken: (refresh: string) =>
    apiService.post('/auth/token/refresh/', { refresh }),
  
  getProfile: () =>
    apiService.get('/auth/profile/'),
  
  updateProfile: (userData: any) =>
    apiService.patch('/auth/profile/', userData),
  
  changePassword: (passwordData: any) =>
    apiService.post('/auth/change-password/', passwordData),
  
  getUserStats: () =>
    apiService.get('/auth/stats/'),
  
  getApiKeys: () =>
    apiService.get('/auth/api-keys/'),
  
  createApiKey: (keyData: any) =>
    apiService.post('/auth/api-keys/', keyData),
  
  deleteApiKey: (keyId: string) =>
    apiService.delete(`/auth/api-keys/${keyId}/`),
}

// Data Sources API
export const dataSourcesApi = {
  list: (params?: any) =>
    apiService.get<PaginatedResponse<any>>('/data/', { params }),
  
  get: (id: string) =>
    apiService.get(`/data/${id}/`),
  
  create: (data: any) =>
    apiService.post('/data/', data),
  
  update: (id: string, data: any) =>
    apiService.patch(`/data/${id}/`, data),
  
  delete: (id: string) =>
    apiService.delete(`/data/${id}/`),
  
  upload: (file: File, onProgress?: (progress: number) => void) =>
    apiService.upload('/data/upload/', file, onProgress),
  
  analyze: (id: string) =>
    apiService.post(`/data/${id}/analyze/`),
  
  getQualityReport: (id: string) =>
    apiService.get(`/data/${id}/quality-report/`),
  
  getColumns: (id: string) =>
    apiService.get(`/data/${id}/columns/`),
  
  preview: (id: string, params?: any) =>
    apiService.get(`/data/${id}/preview/`, { params }),
}

// AI Engine API
export const aiApi = {
  // Conversations
  getConversations: (params?: any) =>
    apiService.get<PaginatedResponse<any>>('/ai/conversations/', { params }),
  
  getConversation: (id: string) =>
    apiService.get(`/ai/conversations/${id}/`),
  
  createConversation: (data: any) =>
    apiService.post('/ai/conversations/', data),
  
  updateConversation: (id: string, data: any) =>
    apiService.patch(`/ai/conversations/${id}/`, data),
  
  deleteConversation: (id: string) =>
    apiService.delete(`/ai/conversations/${id}/`),
  
  // Messages
  getMessages: (conversationId: string, params?: any) =>
    apiService.get(`/ai/conversations/${conversationId}/messages/`, { params }),
  
  sendMessage: (conversationId: string, message: any) =>
    apiService.post(`/ai/conversations/${conversationId}/messages/`, message),
  
  // AI Models
  getModels: () =>
    apiService.get('/ai/models/'),
  
  getModelUsage: (modelId: string) =>
    apiService.get(`/ai/models/${modelId}/usage/`),
}

// Query Processor API
export const queryApi = {
  // Natural language queries
  processQuery: (data: any) =>
    apiService.post('/query/process/', data),
  
  generateSQL: (data: any) =>
    apiService.post('/query/generate-sql/', data),
  
  generatePython: (data: any) =>
    apiService.post('/query/generate-python/', data),
  
  executeQuery: (data: any) =>
    apiService.post('/query/execute/', data),
  
  // Query history
  getQueryHistory: (params?: any) =>
    apiService.get<PaginatedResponse<any>>('/query/history/', { params }),
  
  getQueryExecution: (id: string) =>
    apiService.get(`/query/executions/${id}/`),
  
  saveQuery: (data: any) =>
    apiService.post('/query/save/', data),
}

// Visualization API
export const visualizationApi = {
  // Charts and reports
  createChart: (data: any) =>
    apiService.post('/viz/charts/', data),
  
  getCharts: (params?: any) =>
    apiService.get<PaginatedResponse<any>>('/viz/charts/', { params }),
  
  getChart: (id: string) =>
    apiService.get(`/viz/charts/${id}/`),
  
  updateChart: (id: string, data: any) =>
    apiService.patch(`/viz/charts/${id}/`, data),
  
  deleteChart: (id: string) =>
    apiService.delete(`/viz/charts/${id}/`),
  
  // Reports
  createReport: (data: any) =>
    apiService.post('/viz/reports/', data),
  
  getReports: (params?: any) =>
    apiService.get<PaginatedResponse<any>>('/viz/reports/', { params }),
  
  getReport: (id: string) =>
    apiService.get(`/viz/reports/${id}/`),
  
  generateReport: (id: string, format: string) =>
    apiService.post(`/viz/reports/${id}/generate/`, { format }),
  
  // Chart configuration and suggestions
  generateChartConfig: (data: any) =>
    apiService.post('/viz/chart-config/', data),

  suggestVisualizations: (data: any) =>
    apiService.post('/viz/suggestions/', data),

  // Export
  exportData: (data: any) =>
    apiService.post('/viz/export/', data, {
      responseType: 'blob',
    }),
}

export default api
