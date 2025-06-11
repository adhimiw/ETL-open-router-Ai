/**
 * Custom HTTP client service for EETL AI Platform
 * Provides seamless communication between React frontend and Django backend
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import axiosRetry from 'axios-retry'

interface HTTPConfig {
  baseURL: string
  timeout: number
  retries: number
  retryDelay: number
}

interface ETLOperation {
  id: string
  type: 'ingestion' | 'transformation' | 'analysis' | 'visualization'
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  data?: any
  error?: string
}

interface DataSource {
  id: string
  name: string
  type: 'file' | 'database' | 'api'
  status: string
  rowCount?: number
  columnCount?: number
  lastUpdated: string
}

interface QueryResult {
  id: string
  query: string
  sql?: string
  results: any[]
  executionTime: number
  rowCount: number
  aiResponse?: string
  model?: string
  tokensUsed?: number
  visualizationSuggestions?: any[]
}

class ETLHttpService {
  private axios: AxiosInstance
  private config: HTTPConfig
  private isConnected: boolean = false

  constructor(config: Partial<HTTPConfig> = {}) {
    this.config = {
      baseURL: config.baseURL || import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
      timeout: config.timeout || 30000,
      retries: config.retries || 3,
      retryDelay: config.retryDelay || 1000,
      ...config
    }

    // Initialize axios with retry logic
    this.axios = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Configure retry logic
    axiosRetry(this.axios, {
      retries: this.config.retries,
      retryDelay: (retryCount) => {
        return retryCount * this.config.retryDelay
      },
      retryCondition: (error) => {
        return axiosRetry.isNetworkOrIdempotentRequestError(error) ||
               error.response?.status === 429 ||
               error.response?.status === 503
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.axios.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor
    this.axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Handle token refresh or logout
          await this.handleAuthError()
        }
        return Promise.reject(error)
      }
    )
  }

  private async handleAuthError(): Promise<void> {
    // Clear auth data and redirect to login
    localStorage.removeItem('auth_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/auth/login'
  }

  async connect(): Promise<boolean> {
    try {
      // Test connection to backend
      const response = await this.axios.get('/health/')
      this.isConnected = response.status === 200
      
      if (this.isConnected) {
        console.log('✅ HTTP client connected to Django backend')
      }

      return this.isConnected
    } catch (error) {
      console.error('❌ Failed to connect to Django backend:', error)
      this.isConnected = false
      return false
    }
  }

  async disconnect(): Promise<void> {
    this.isConnected = false
    console.log('🔌 HTTP client disconnected')
  }

  // Authentication Methods
  async adminLogin(username: string, password: string): Promise<any> {
    try {
      const response = await this.axios.post('/auth/login/', {
        email: username === 'admin' ? 'admin@eetl.ai' : username,
        password
      })

      if (response.data.tokens) {
        localStorage.setItem('auth_token', response.data.tokens.access)
        localStorage.setItem('refresh_token', response.data.tokens.refresh)
      }

      return response.data
    } catch (error) {
      throw new Error('Admin login failed')
    }
  }

  async logout(): Promise<void> {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        await this.axios.post('/auth/logout/', {
          refresh_token: refreshToken
        })
      }
    } catch (error) {
      console.warn('Logout request failed:', error)
    } finally {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('refresh_token')
    }
  }

  // Data Source Management
  async getDataSources(): Promise<DataSource[]> {
    try {
      const response = await this.axios.get('/data/sources/')
      return response.data.results || response.data
    } catch (error) {
      console.error('Failed to fetch data sources:', error)
      throw error
    }
  }

  async uploadDataSource(file: File, metadata: any = {}): Promise<DataSource> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('name', metadata.name || file.name)
      formData.append('description', metadata.description || '')

      const response = await this.axios.post('/data/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || 1)
          )
          // Emit progress event
          this.emitProgress('upload', progress)
        },
      })

      return response.data.data_source
    } catch (error) {
      console.error('Failed to upload data source:', error)
      throw error
    }
  }

  async analyzeDataSource(dataSourceId: string): Promise<any> {
    try {
      const response = await this.axios.post(`/data/sources/${dataSourceId}/analyze/`)
      return response.data
    } catch (error) {
      console.error('Failed to analyze data source:', error)
      throw error
    }
  }

  async getDataPreview(dataSourceId: string, options: any = {}): Promise<any> {
    try {
      const response = await this.axios.get(`/data/sources/${dataSourceId}/preview/`, {
        params: options
      })
      return response.data
    } catch (error) {
      console.error('Failed to get data preview:', error)
      throw error
    }
  }

  // Natural Language Query Processing
  async processNaturalLanguageQuery(query: string, dataSourceId?: string): Promise<QueryResult> {
    try {
      const response = await this.axios.post('/query/process/', {
        query,
        data_source_id: dataSourceId,
        include_sql: true,
        include_visualization: true
      })

      return {
        id: response.data.id || Date.now().toString(),
        query,
        sql: response.data.sql_query,
        results: response.data.results || [],
        executionTime: response.data.execution_time || 0,
        rowCount: response.data.row_count || 0,
        aiResponse: response.data.ai_response,
        model: response.data.model,
        tokensUsed: response.data.tokens_used,
        visualizationSuggestions: response.data.visualization_suggestions
      }
    } catch (error) {
      console.error('Failed to process natural language query:', error)
      throw error
    }
  }

  // Generate SQL from natural language
  async generateSQL(query: string, dataSourceId?: string): Promise<any> {
    try {
      const response = await this.axios.post('/query/generate-sql/', {
        query,
        data_source_id: dataSourceId
      })
      return response.data
    } catch (error) {
      console.error('Failed to generate SQL:', error)
      throw error
    }
  }

  // Generate Python code from natural language
  async generatePython(query: string, dataSourceId?: string): Promise<any> {
    try {
      const response = await this.axios.post('/query/generate-python/', {
        query,
        data_source_id: dataSourceId
      })
      return response.data
    } catch (error) {
      console.error('Failed to generate Python code:', error)
      throw error
    }
  }

  // Get query history
  async getQueryHistory(): Promise<any> {
    try {
      const response = await this.axios.get('/query/history/')
      return response.data
    } catch (error) {
      console.error('Failed to get query history:', error)
      throw error
    }
  }

  // Visualization Methods
  async generateChartConfig(data: any[], chartType: string, xColumn?: string, yColumn?: string): Promise<any> {
    try {
      const response = await this.axios.post('/viz/chart-config/', {
        data,
        chart_type: chartType,
        x_column: xColumn,
        y_column: yColumn
      })
      return response.data
    } catch (error) {
      console.error('Failed to generate chart config:', error)
      throw error
    }
  }

  async suggestVisualizations(data: any[]): Promise<any> {
    try {
      const response = await this.axios.post('/viz/suggestions/', {
        data
      })
      return response.data
    } catch (error) {
      console.error('Failed to suggest visualizations:', error)
      throw error
    }
  }



  async executeQuery(sql: string, dataSourceId: string): Promise<QueryResult> {
    try {
      const response = await this.axios.post('/query/execute/', {
        sql,
        data_source_id: dataSourceId
      })

      return {
        id: response.data.id || Date.now().toString(),
        query: sql,
        sql,
        results: response.data.results || [],
        executionTime: response.data.execution_time || 0,
        rowCount: response.data.row_count || 0
      }
    } catch (error) {
      console.error('Failed to execute query:', error)
      throw error
    }
  }

  // Data Transformation and Cleaning
  async getDataQualityReport(dataSourceId: string): Promise<any> {
    try {
      const response = await this.axios.get(`/data/sources/${dataSourceId}/quality-report/`)
      return response.data
    } catch (error) {
      console.error('Failed to get data quality report:', error)
      throw error
    }
  }

  async applyDataTransformation(dataSourceId: string, transformations: any[]): Promise<any> {
    try {
      const response = await this.axios.post('/data/transformations/', {
        data_source: dataSourceId,
        operations: transformations,
        name: `Transformation_${Date.now()}`,
        transformation_type: 'clean'
      })
      return response.data
    } catch (error) {
      console.error('Failed to apply data transformation:', error)
      throw error
    }
  }

  // Visualization
  async createVisualization(config: any): Promise<any> {
    try {
      const response = await this.axios.post('/viz/charts/', config)
      return response.data
    } catch (error) {
      console.error('Failed to create visualization:', error)
      throw error
    }
  }

  async getVisualizations(): Promise<any[]> {
    try {
      const response = await this.axios.get('/viz/charts/')
      return response.data.results || response.data
    } catch (error) {
      console.error('Failed to get visualizations:', error)
      throw error
    }
  }

  // Real-time Operations Monitoring
  async getETLOperations(): Promise<ETLOperation[]> {
    try {
      const response = await this.axios.get('/data/operations/')
      return response.data.results || response.data
    } catch (error) {
      console.error('Failed to get ETL operations:', error)
      return []
    }
  }

  async monitorOperation(operationId: string): Promise<ETLOperation> {
    try {
      const response = await this.axios.get(`/data/operations/${operationId}/`)
      return response.data
    } catch (error) {
      console.error('Failed to monitor operation:', error)
      throw error
    }
  }

  // AI-Assisted Analysis
  async getAIInsights(dataSourceId: string): Promise<any> {
    try {
      const response = await this.axios.post('/ai/insights/', {
        data_source_id: dataSourceId,
        analysis_type: 'comprehensive'
      })
      return response.data
    } catch (error) {
      console.error('Failed to get AI insights:', error)
      throw error
    }
  }

  async startConversation(dataSourceId?: string): Promise<string> {
    try {
      const response = await this.axios.post('/ai/conversations/', {
        data_source_id: dataSourceId,
        title: `Analysis Session ${new Date().toLocaleString()}`
      })
      return response.data.id
    } catch (error) {
      console.error('Failed to start conversation:', error)
      throw error
    }
  }

  async sendMessage(conversationId: string, message: string): Promise<any> {
    try {
      const response = await this.axios.post(`/ai/conversations/${conversationId}/messages/`, {
        content: message,
        role: 'user'
      })
      return response.data
    } catch (error) {
      console.error('Failed to send message:', error)
      throw error
    }
  }

  // Utility Methods
  private emitProgress(operation: string, progress: number): void {
    window.dispatchEvent(new CustomEvent('etl-progress', {
      detail: { operation, progress }
    }))
  }

  async testConnection(): Promise<boolean> {
    try {
      const response = await this.axios.get('/health/')
      return response.status === 200
    } catch (error) {
      return false
    }
  }

  getConnectionStatus(): boolean {
    return this.isConnected
  }

  // Export data
  async exportData(dataSourceId: string, format: 'csv' | 'excel' | 'json'): Promise<Blob> {
    try {
      const response = await this.axios.post(`/viz/export/`, {
        data_source_id: dataSourceId,
        format
      }, {
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.error('Failed to export data:', error)
      throw error
    }
  }
}

// Create singleton instance
export const browserMCP = new ETLHttpService()

// Export types
export type {
  ETLOperation,
  DataSource,
  QueryResult,
  HTTPConfig
}

export default ETLHttpService
