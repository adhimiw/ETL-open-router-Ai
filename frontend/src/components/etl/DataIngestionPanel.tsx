/**
 * Data Ingestion Panel Component
 * Handles file uploads, database connections, and API integrations
 */

import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import {
  CloudArrowUpIcon,
  DocumentIcon,
  CircleStackIcon as DatabaseIcon,
  GlobeAltIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline'
import { browserMCP } from '@/services/browserMcp'
import toast from 'react-hot-toast'

interface DataIngestionPanelProps {
  onDataSourceAdded: (dataSource: any) => void
}

const DataIngestionPanel: React.FC<DataIngestionPanelProps> = ({ onDataSourceAdded }) => {
  const [activeTab, setActiveTab] = useState<'file' | 'database' | 'api'>('file')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  // File upload handling
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setIsUploading(true)
    setUploadProgress(0)

    try {
      // Listen for progress events
      const handleProgress = (event: CustomEvent) => {
        if (event.detail.operation === 'upload') {
          setUploadProgress(event.detail.progress)
        }
      }

      window.addEventListener('etl-progress', handleProgress as EventListener)

      const dataSource = await browserMCP.uploadDataSource(file, {
        name: file.name,
        description: `Uploaded file: ${file.name}`,
      })

      toast.success('File uploaded successfully!')
      onDataSourceAdded(dataSource)
      setUploadProgress(100)

      window.removeEventListener('etl-progress', handleProgress as EventListener)
    } catch (error) {
      toast.error('Failed to upload file')
      console.error('Upload error:', error)
    } finally {
      setIsUploading(false)
      setTimeout(() => setUploadProgress(0), 2000)
    }
  }, [onDataSourceAdded])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/json': ['.json'],
    },
    multiple: false,
  })

  const tabs = [
    { id: 'file', name: 'File Upload', icon: DocumentIcon },
    { id: 'database', name: 'Database', icon: DatabaseIcon },
    { id: 'api', name: 'API', icon: GlobeAltIcon },
  ]

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8 px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`
                flex items-center py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              <tab.icon className="mr-2 h-5 w-5" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      <div className="p-6">
        {activeTab === 'file' && (
          <FileUploadTab
            getRootProps={getRootProps}
            getInputProps={getInputProps}
            isDragActive={isDragActive}
            isUploading={isUploading}
            uploadProgress={uploadProgress}
          />
        )}

        {activeTab === 'database' && (
          <DatabaseConnectionTab onDataSourceAdded={onDataSourceAdded} />
        )}

        {activeTab === 'api' && (
          <APIConnectionTab onDataSourceAdded={onDataSourceAdded} />
        )}
      </div>
    </div>
  )
}

const FileUploadTab: React.FC<{
  getRootProps: any
  getInputProps: any
  isDragActive: boolean
  isUploading: boolean
  uploadProgress: number
}> = ({ getRootProps, getInputProps, isDragActive, isUploading, uploadProgress }) => (
  <div className="space-y-6">
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
        ${isDragActive
          ? 'border-primary-400 bg-primary-50'
          : 'border-gray-300 hover:border-gray-400'
        }
        ${isUploading ? 'pointer-events-none opacity-50' : ''}
      `}
    >
      <input {...getInputProps()} />
      <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
      <div className="mt-4">
        <p className="text-lg font-medium text-gray-900">
          {isDragActive ? 'Drop the file here' : 'Upload your data file'}
        </p>
        <p className="mt-2 text-sm text-gray-500">
          Drag and drop a file here, or click to select
        </p>
        <p className="mt-1 text-xs text-gray-400">
          Supports CSV, Excel (.xlsx, .xls), and JSON files
        </p>
      </div>
    </div>

    {isUploading && (
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Uploading...</span>
          <span className="text-gray-600">{uploadProgress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${uploadProgress}%` }}
          />
        </div>
      </div>
    )}

    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
      <div className="flex items-center space-x-2">
        <CheckCircleIcon className="h-5 w-5 text-green-500" />
        <span>Automatic data type detection</span>
      </div>
      <div className="flex items-center space-x-2">
        <CheckCircleIcon className="h-5 w-5 text-green-500" />
        <span>Quality assessment</span>
      </div>
      <div className="flex items-center space-x-2">
        <CheckCircleIcon className="h-5 w-5 text-green-500" />
        <span>AI-powered insights</span>
      </div>
    </div>
  </div>
)

const DatabaseConnectionTab: React.FC<{
  onDataSourceAdded: (dataSource: any) => void
}> = ({ onDataSourceAdded }) => {
  const [connectionData, setConnectionData] = useState({
    db_type: 'postgresql',
    db_host: '',
    db_port: '5432',
    db_name: '',
    db_username: '',
    db_password: '',
    db_table: '',
  })
  const [isConnecting, setIsConnecting] = useState(false)

  const handleConnect = async () => {
    setIsConnecting(true)
    try {
      // Test connection first
      await browserMCP.testConnection()
      
      // Create data source
      const dataSource = await browserMCP.uploadDataSource(new File([], 'database'), {
        ...connectionData,
        source_type: 'database',
        name: `${connectionData.db_name}.${connectionData.db_table}`,
      })

      toast.success('Database connected successfully!')
      onDataSourceAdded(dataSource)
    } catch (error) {
      toast.error('Failed to connect to database')
    } finally {
      setIsConnecting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Database Type
          </label>
          <select
            value={connectionData.db_type}
            onChange={(e) => setConnectionData({ ...connectionData, db_type: e.target.value })}
            className="input"
          >
            <option value="postgresql">PostgreSQL</option>
            <option value="mysql">MySQL</option>
            <option value="sqlite">SQLite</option>
            <option value="oracle">Oracle</option>
            <option value="mssql">SQL Server</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Host
          </label>
          <input
            type="text"
            value={connectionData.db_host}
            onChange={(e) => setConnectionData({ ...connectionData, db_host: e.target.value })}
            className="input"
            placeholder="localhost"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Port
          </label>
          <input
            type="text"
            value={connectionData.db_port}
            onChange={(e) => setConnectionData({ ...connectionData, db_port: e.target.value })}
            className="input"
            placeholder="5432"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Database Name
          </label>
          <input
            type="text"
            value={connectionData.db_name}
            onChange={(e) => setConnectionData({ ...connectionData, db_name: e.target.value })}
            className="input"
            placeholder="my_database"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Username
          </label>
          <input
            type="text"
            value={connectionData.db_username}
            onChange={(e) => setConnectionData({ ...connectionData, db_username: e.target.value })}
            className="input"
            placeholder="username"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Password
          </label>
          <input
            type="password"
            value={connectionData.db_password}
            onChange={(e) => setConnectionData({ ...connectionData, db_password: e.target.value })}
            className="input"
            placeholder="password"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Table Name
          </label>
          <input
            type="text"
            value={connectionData.db_table}
            onChange={(e) => setConnectionData({ ...connectionData, db_table: e.target.value })}
            className="input"
            placeholder="table_name"
          />
        </div>
      </div>

      <button
        onClick={handleConnect}
        disabled={isConnecting}
        className="btn-primary"
      >
        {isConnecting ? 'Connecting...' : 'Connect Database'}
      </button>
    </div>
  )
}

const APIConnectionTab: React.FC<{
  onDataSourceAdded: (dataSource: any) => void
}> = ({ onDataSourceAdded }) => {
  const [apiData, setApiData] = useState({
    api_url: '',
    api_method: 'GET',
    api_headers: '{}',
    api_params: '{}',
    api_auth_type: 'none',
    api_auth_token: '',
  })
  const [isConnecting, setIsConnecting] = useState(false)

  const handleConnect = async () => {
    setIsConnecting(true)
    try {
      const dataSource = await browserMCP.uploadDataSource(new File([], 'api'), {
        ...apiData,
        source_type: 'api',
        name: `API: ${new URL(apiData.api_url).hostname}`,
      })

      toast.success('API connected successfully!')
      onDataSourceAdded(dataSource)
    } catch (error) {
      toast.error('Failed to connect to API')
    } finally {
      setIsConnecting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            API URL
          </label>
          <input
            type="url"
            value={apiData.api_url}
            onChange={(e) => setApiData({ ...apiData, api_url: e.target.value })}
            className="input"
            placeholder="https://api.example.com/data"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Method
            </label>
            <select
              value={apiData.api_method}
              onChange={(e) => setApiData({ ...apiData, api_method: e.target.value })}
              className="input"
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="PATCH">PATCH</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Authentication
            </label>
            <select
              value={apiData.api_auth_type}
              onChange={(e) => setApiData({ ...apiData, api_auth_type: e.target.value })}
              className="input"
            >
              <option value="none">None</option>
              <option value="bearer">Bearer Token</option>
              <option value="api_key">API Key</option>
              <option value="basic">Basic Auth</option>
            </select>
          </div>
        </div>

        {apiData.api_auth_type !== 'none' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Auth Token
            </label>
            <input
              type="password"
              value={apiData.api_auth_token}
              onChange={(e) => setApiData({ ...apiData, api_auth_token: e.target.value })}
              className="input"
              placeholder="Your API token"
            />
          </div>
        )}
      </div>

      <button
        onClick={handleConnect}
        disabled={isConnecting}
        className="btn-primary"
      >
        {isConnecting ? 'Connecting...' : 'Connect API'}
      </button>
    </div>
  )
}

export default DataIngestionPanel
