/**
 * ETL Dashboard page component
 * Main interface for the EETL AI Platform
 */

import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  ChartBarIcon,
  ChatBubbleLeftRightIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  CpuChipIcon,
  PlayIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline'
import { useAuthStore } from '@/stores/authStore'
import { browserMCP, DataSource, ETLOperation } from '@/services/browserMcp'
import DataIngestionPanel from '@/components/etl/DataIngestionPanel'
import NaturalLanguageQuery from '@/components/etl/NaturalLanguageQuery'
import DataVisualization from '@/components/etl/DataVisualization'
import toast from 'react-hot-toast'

const stats = [
  { name: 'Total Data Sources', stat: '12', icon: CloudArrowUpIcon, change: '+4.75%', changeType: 'positive' },
  { name: 'Active Conversations', stat: '8', icon: ChatBubbleLeftRightIcon, change: '+54.02%', changeType: 'positive' },
  { name: 'Queries This Month', stat: '2,847', icon: ChartBarIcon, change: '-1.39%', changeType: 'negative' },
  { name: 'Data Processed (GB)', stat: '45.2', icon: CpuChipIcon, change: '+10.18%', changeType: 'positive' },
]

const quickActions = [
  {
    name: 'Upload Data',
    description: 'Upload CSV, Excel, or JSON files',
    href: '/data-sources',
    icon: CloudArrowUpIcon,
    color: 'bg-blue-500',
  },
  {
    name: 'Start Chat',
    description: 'Ask questions about your data',
    href: '/chat',
    icon: ChatBubbleLeftRightIcon,
    color: 'bg-green-500',
  },
  {
    name: 'View Analytics',
    description: 'Explore your data insights',
    href: '/analytics',
    icon: ChartBarIcon,
    color: 'bg-purple-500',
  },
  {
    name: 'Create Report',
    description: 'Generate automated reports',
    href: '/reports',
    icon: DocumentTextIcon,
    color: 'bg-orange-500',
  },
]

const recentActivity = [
  {
    id: 1,
    type: 'upload',
    title: 'Sales Data Q4 2023',
    description: 'Uploaded sales_data_q4.csv (2.3 MB)',
    time: '2 hours ago',
    icon: CloudArrowUpIcon,
  },
  {
    id: 2,
    type: 'chat',
    title: 'Customer Analysis Chat',
    description: 'Asked about top customers by revenue',
    time: '4 hours ago',
    icon: ChatBubbleLeftRightIcon,
  },
  {
    id: 3,
    type: 'report',
    title: 'Monthly Revenue Report',
    description: 'Generated automated report for November',
    time: '1 day ago',
    icon: DocumentTextIcon,
  },
  {
    id: 4,
    type: 'analysis',
    title: 'Product Performance Analysis',
    description: 'Analyzed product sales trends',
    time: '2 days ago',
    icon: ChartBarIcon,
  },
]

const DashboardPage: React.FC = () => {
  const { user } = useAuthStore()
  const [dataSources, setDataSources] = useState<DataSource[]>([])
  const [etlOperations, setETLOperations] = useState<ETLOperation[]>([])
  const [selectedDataSource, setSelectedDataSource] = useState<string>()
  const [activeTab, setActiveTab] = useState<'overview' | 'ingestion' | 'query' | 'visualization' | 'monitoring'>('overview')
  const [isLoading, setIsLoading] = useState(true)
  const [connectionStatus, setConnectionStatus] = useState(false)

  useEffect(() => {
    initializeDashboard()

    // Set up real-time monitoring
    const interval = setInterval(() => {
      if (activeTab === 'monitoring') {
        loadETLOperations()
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [activeTab])

  const initializeDashboard = async () => {
    setIsLoading(true)
    try {
      // Connect to backend via BrowserMCP
      const connected = await browserMCP.connect()
      setConnectionStatus(connected)

      if (connected) {
        await Promise.all([
          loadDataSources(),
          loadETLOperations(),
        ])
        toast.success('Dashboard initialized successfully!')
      } else {
        toast.error('Failed to connect to backend')
      }
    } catch (error) {
      console.error('Dashboard initialization error:', error)
      toast.error('Failed to initialize dashboard')
    } finally {
      setIsLoading(false)
    }
  }

  const loadDataSources = async () => {
    try {
      const sources = await browserMCP.getDataSources()
      setDataSources(sources)
    } catch (error) {
      console.error('Failed to load data sources:', error)
    }
  }

  const loadETLOperations = async () => {
    try {
      const operations = await browserMCP.getETLOperations()
      setETLOperations(operations)
    } catch (error) {
      console.error('Failed to load ETL operations:', error)
    }
  }

  const handleDataSourceAdded = (dataSource: DataSource) => {
    setDataSources(prev => [dataSource, ...prev])
    setSelectedDataSource(dataSource.id)
    toast.success(`Data source "${dataSource.name}" added successfully!`)
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            ETL AI Platform Dashboard
          </h1>
          <p className="mt-2 text-gray-600">
            Welcome back, {user?.firstName}! Manage your data workflows with AI assistance.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            connectionStatus
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-2 h-2 rounded-full mr-1 ${
              connectionStatus ? 'bg-green-400' : 'bg-red-400'
            }`} />
            {connectionStatus ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview', icon: ChartBarIcon },
            { id: 'ingestion', name: 'Data Ingestion', icon: CloudArrowUpIcon },
            { id: 'query', name: 'AI Query', icon: ChatBubbleLeftRightIcon },
            { id: 'visualization', name: 'Visualization', icon: ChartBarIcon },
            { id: 'monitoring', name: 'Monitoring', icon: CpuChipIcon },
          ].map((tab) => (
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

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'overview' && (
          <OverviewTab
            dataSources={dataSources}
            etlOperations={etlOperations}
            isLoading={isLoading}
          />
        )}

        {activeTab === 'ingestion' && (
          <DataIngestionPanel onDataSourceAdded={handleDataSourceAdded} />
        )}

        {activeTab === 'query' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <NaturalLanguageQuery
                dataSourceId={selectedDataSource}
                onQueryResult={(result) => {
                  // Handle query result
                  console.log('Query result:', result)
                }}
              />
            </div>
            <div>
              <DataSourceSelector
                dataSources={dataSources}
                selectedDataSource={selectedDataSource}
                onSelect={setSelectedDataSource}
              />
            </div>
          </div>
        )}

        {activeTab === 'visualization' && (
          <DataVisualization dataSourceId={selectedDataSource} />
        )}

        {activeTab === 'monitoring' && (
          <MonitoringTab
            etlOperations={etlOperations}
            onRefresh={loadETLOperations}
          />
        )}
      </div>
    </div>
  )
}

// Overview Tab Component
const OverviewTab: React.FC<{
  dataSources: DataSource[]
  etlOperations: ETLOperation[]
  isLoading: boolean
}> = ({ dataSources, etlOperations, isLoading }) => {
  const stats = [
    {
      name: 'Total Data Sources',
      stat: dataSources.length.toString(),
      icon: CloudArrowUpIcon,
      change: '+12%',
      changeType: 'positive'
    },
    {
      name: 'Active Operations',
      stat: etlOperations.filter(op => op.status === 'running').length.toString(),
      icon: PlayIcon,
      change: '+5%',
      changeType: 'positive'
    },
    {
      name: 'Completed Today',
      stat: etlOperations.filter(op => op.status === 'completed').length.toString(),
      icon: CheckCircleIcon,
      change: '+18%',
      changeType: 'positive'
    },
    {
      name: 'Failed Operations',
      stat: etlOperations.filter(op => op.status === 'failed').length.toString(),
      icon: ExclamationTriangleIcon,
      change: '-8%',
      changeType: 'negative'
    },
  ]

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white p-6 rounded-lg shadow">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <div key={item.name} className="card">
            <div className="card-body">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <item.icon className="h-6 w-6 text-gray-400" aria-hidden="true" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">{item.name}</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">{item.stat}</div>
                      <div
                        className={`ml-2 flex items-baseline text-sm font-semibold ${
                          item.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {item.changeType === 'positive' ? '↗' : '↘'}
                        <span className="sr-only">
                          {item.changeType === 'positive' ? 'Increased' : 'Decreased'} by
                        </span>
                        {item.change}
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Data Sources */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Recent Data Sources</h3>
          </div>
          <div className="card-body">
            {dataSources.length === 0 ? (
              <div className="text-center py-6">
                <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-sm text-gray-500">No data sources yet</p>
                <p className="text-xs text-gray-400">Upload your first dataset to get started</p>
              </div>
            ) : (
              <div className="space-y-3">
                {dataSources.slice(0, 5).map((source) => (
                  <div key={source.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`w-2 h-2 rounded-full ${
                        source.status === 'completed' ? 'bg-green-400' :
                        source.status === 'processing' ? 'bg-yellow-400' : 'bg-red-400'
                      }`} />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{source.name}</p>
                        <p className="text-xs text-gray-500">{source.type} • {source.rowCount} rows</p>
                      </div>
                    </div>
                    <span className="text-xs text-gray-400">{source.lastUpdated}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">System Health</h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Backend Connection</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Healthy
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">AI Engine</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Active
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Data Processing</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Running
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Data Source Selector Component
const DataSourceSelector: React.FC<{
  dataSources: DataSource[]
  selectedDataSource?: string
  onSelect: (id: string) => void
}> = ({ dataSources, selectedDataSource, onSelect }) => (
  <div className="card">
    <div className="card-header">
      <h3 className="text-lg font-medium text-gray-900">Select Data Source</h3>
    </div>
    <div className="card-body">
      {dataSources.length === 0 ? (
        <div className="text-center py-6">
          <DocumentTextIcon className="mx-auto h-8 w-8 text-gray-400" />
          <p className="mt-2 text-sm text-gray-500">No data sources available</p>
        </div>
      ) : (
        <div className="space-y-2">
          {dataSources.map((source) => (
            <button
              key={source.id}
              onClick={() => onSelect(source.id)}
              className={`w-full text-left p-3 rounded-lg border transition-colors ${
                selectedDataSource === source.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">{source.name}</p>
                  <p className="text-xs text-gray-500">{source.type} • {source.rowCount} rows</p>
                </div>
                <div className={`w-2 h-2 rounded-full ${
                  source.status === 'completed' ? 'bg-green-400' :
                  source.status === 'processing' ? 'bg-yellow-400' : 'bg-red-400'
                }`} />
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  </div>
)

// Monitoring Tab Component
const MonitoringTab: React.FC<{
  etlOperations: ETLOperation[]
  onRefresh: () => void
}> = ({ etlOperations, onRefresh }) => (
  <div className="space-y-6">
    <div className="flex items-center justify-between">
      <h3 className="text-lg font-medium text-gray-900">ETL Operations Monitor</h3>
      <button onClick={onRefresh} className="btn-outline btn-sm">
        Refresh
      </button>
    </div>

    <div className="card">
      <div className="card-body">
        {etlOperations.length === 0 ? (
          <div className="text-center py-8">
            <CpuChipIcon className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-sm text-gray-500">No operations running</p>
          </div>
        ) : (
          <div className="space-y-4">
            {etlOperations.map((operation) => (
              <div key={operation.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      operation.status === 'completed' ? 'bg-green-400' :
                      operation.status === 'running' ? 'bg-blue-400 animate-pulse' :
                      operation.status === 'failed' ? 'bg-red-400' : 'bg-gray-400'
                    }`} />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{operation.type}</p>
                      <p className="text-xs text-gray-500">ID: {operation.id}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">{operation.status}</p>
                    <p className="text-xs text-gray-500">{operation.progress}% complete</p>
                  </div>
                </div>

                {operation.status === 'running' && (
                  <div className="mt-3">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${operation.progress}%` }}
                      />
                    </div>
                  </div>
                )}

                {operation.error && (
                  <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                    {operation.error}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  </div>
)

export default DashboardPage
