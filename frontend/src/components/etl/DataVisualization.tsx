/**
 * Data Visualization Dashboard Component
 * Interactive charts and data visualization
 */

import React, { useState, useEffect } from 'react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
} from 'recharts'
import {
  ChartBarIcon,
  PresentationChartLineIcon,
  ChartPieIcon,
  TableCellsIcon,
  ArrowDownTrayIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline'
import { browserMCP } from '@/services/browserMcp'
import toast from 'react-hot-toast'

interface DataVisualizationProps {
  dataSourceId?: string
  queryResult?: any
}

interface ChartConfig {
  type: 'bar' | 'line' | 'pie' | 'scatter' | 'table'
  xAxis?: string
  yAxis?: string
  groupBy?: string
  aggregation?: 'sum' | 'avg' | 'count' | 'max' | 'min'
}

const COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#6B7280']

const DataVisualization: React.FC<DataVisualizationProps> = ({
  dataSourceId,
  queryResult,
}) => {
  const [data, setData] = useState<any[]>([])
  const [chartConfig, setChartConfig] = useState<ChartConfig>({
    type: 'bar',
    aggregation: 'count',
  })
  const [availableColumns, setAvailableColumns] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showConfig, setShowConfig] = useState(false)

  useEffect(() => {
    if (queryResult?.results) {
      setData(queryResult.results)
      if (queryResult.results.length > 0) {
        const columns = Object.keys(queryResult.results[0])
        setAvailableColumns(columns)
        
        // Auto-configure chart based on data
        autoConfigureChart(queryResult.results, columns)
      }
    } else if (dataSourceId) {
      loadDataPreview()
    }
  }, [queryResult, dataSourceId])

  const loadDataPreview = async () => {
    if (!dataSourceId) return

    setIsLoading(true)
    try {
      const preview = await browserMCP.getDataPreview(dataSourceId, { limit: 100 })
      setData(preview.data)
      setAvailableColumns(preview.columns)
      
      if (preview.data.length > 0) {
        autoConfigureChart(preview.data, preview.columns)
      }
    } catch (error) {
      toast.error('Failed to load data preview')
    } finally {
      setIsLoading(false)
    }
  }

  const autoConfigureChart = async (data: any[], columns: string[]) => {
    if (columns.length === 0) return

    try {
      // Get AI-powered visualization suggestions
      const suggestions = await browserMCP.suggestVisualizations(data)

      // Use the best suggestion if available
      const bestSuggestion = suggestions.suggestions?.find(
        (s: any) => s.suitability === 'high'
      ) || suggestions.suggestions?.[0]

      if (bestSuggestion) {
        const config: ChartConfig = {
          type: bestSuggestion.type,
          aggregation: 'count'
        }

        if (bestSuggestion.x_column) config.xAxis = bestSuggestion.x_column
        if (bestSuggestion.y_column) config.yAxis = bestSuggestion.y_column
        if (bestSuggestion.type === 'pie' && bestSuggestion.x_column) {
          config.groupBy = bestSuggestion.x_column
        }

        setChartConfig(config)
        return
      }
    } catch (error) {
      console.warn('Failed to get AI suggestions, falling back to basic logic:', error)
    }

    // Fallback to basic auto-configuration
    const numericColumns = columns.filter(col => {
      const sample = data.slice(0, 10).map(row => row[col])
      return sample.every(val => !isNaN(Number(val)) && val !== null && val !== '')
    })

    const categoricalColumns = columns.filter(col => !numericColumns.includes(col))

    // Auto-configure based on data types
    if (numericColumns.length >= 1 && categoricalColumns.length >= 1) {
      setChartConfig({
        type: 'bar',
        xAxis: categoricalColumns[0],
        yAxis: numericColumns[0],
        aggregation: 'sum',
      })
    } else if (numericColumns.length >= 2) {
      setChartConfig({
        type: 'scatter',
        xAxis: numericColumns[0],
        yAxis: numericColumns[1],
        aggregation: 'count',
      })
    } else if (categoricalColumns.length >= 1) {
      setChartConfig({
        type: 'pie',
        groupBy: categoricalColumns[0],
        aggregation: 'count',
      })
    }
  }

  const processDataForChart = () => {
    if (!data.length) return []

    const { type, xAxis, yAxis, groupBy, aggregation } = chartConfig

    if (type === 'table') {
      return data.slice(0, 50) // Limit table rows
    }

    if (type === 'pie') {
      if (!groupBy) return []
      
      // Group by category and aggregate
      const grouped = data.reduce((acc, row) => {
        const key = row[groupBy]
        if (!acc[key]) acc[key] = []
        acc[key].push(row)
        return acc
      }, {})

      return Object.entries(grouped).map(([name, items]) => ({
        name,
        value: (items as any[]).length,
      }))
    }

    if (type === 'scatter') {
      if (!xAxis || !yAxis) return []
      
      return data.map((row, index) => ({
        x: Number(row[xAxis]) || 0,
        y: Number(row[yAxis]) || 0,
        name: `Point ${index + 1}`,
      }))
    }

    // Bar and Line charts
    if (!xAxis || !yAxis) return []

    const grouped = data.reduce((acc, row) => {
      const key = row[xAxis]
      if (!acc[key]) acc[key] = []
      acc[key].push(Number(row[yAxis]) || 0)
      return acc
    }, {})

    return Object.entries(grouped).map(([name, values]) => {
      const numericValues = values as number[]
      let value = 0
      switch (aggregation) {
        case 'sum':
          value = numericValues.reduce((a, b) => a + b, 0)
          break
        case 'avg':
          value = numericValues.reduce((a, b) => a + b, 0) / numericValues.length
          break
        case 'count':
          value = numericValues.length
          break
        case 'max':
          value = Math.max(...numericValues)
          break
        case 'min':
          value = Math.min(...numericValues)
          break
      }
      
      return { name, value }
    })
  }

  const renderChart = () => {
    const chartData = processDataForChart()
    
    if (!chartData.length) {
      return (
        <div className="flex items-center justify-center h-64 text-gray-500">
          <div className="text-center">
            <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2">No data available for visualization</p>
            <p className="text-sm">Configure chart settings or load data</p>
          </div>
        </div>
      )
    }

    switch (chartConfig.type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill={COLORS[0]} />
            </BarChart>
          </ResponsiveContainer>
        )

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke={COLORS[0]} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        )

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        )

      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart data={chartData}>
              <CartesianGrid />
              <XAxis dataKey="x" />
              <YAxis dataKey="y" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter dataKey="y" fill={COLORS[0]} />
            </ScatterChart>
          </ResponsiveContainer>
        )

      case 'table':
        return (
          <div className="overflow-auto max-h-96">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {availableColumns.map((column) => (
                    <th
                      key={column}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {chartData.map((row, index) => (
                  <tr key={index}>
                    {availableColumns.map((column) => (
                      <td key={column} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {String(row[column] || '')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )

      default:
        return null
    }
  }

  const exportChart = async () => {
    try {
      if (dataSourceId) {
        const blob = await browserMCP.exportData(dataSourceId, 'csv')
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'data-export.csv'
        a.click()
        URL.revokeObjectURL(url)
        toast.success('Data exported successfully!')
      }
    } catch (error) {
      toast.error('Failed to export data')
    }
  }

  const chartTypes = [
    { type: 'bar', name: 'Bar Chart', icon: ChartBarIcon },
    { type: 'line', name: 'Line Chart', icon: PresentationChartLineIcon },
    { type: 'pie', name: 'Pie Chart', icon: ChartPieIcon },
    { type: 'scatter', name: 'Scatter Plot', icon: ChartBarIcon },
    { type: 'table', name: 'Data Table', icon: TableCellsIcon },
  ]

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Data Visualization</h3>
          <div className="flex space-x-2">
            <button
              onClick={() => setShowConfig(!showConfig)}
              className="btn-outline btn-sm"
            >
              <Cog6ToothIcon className="h-4 w-4 mr-1" />
              Configure
            </button>
            <button onClick={exportChart} className="btn-outline btn-sm">
              <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
              Export
            </button>
          </div>
        </div>

        {/* Chart Type Selector */}
        <div className="flex space-x-2 mt-4">
          {chartTypes.map(({ type, name, icon: Icon }) => (
            <button
              key={type}
              onClick={() => setChartConfig({ ...chartConfig, type: type as any })}
              className={`
                inline-flex items-center px-3 py-1 rounded-md text-sm font-medium
                ${chartConfig.type === type
                  ? 'bg-primary-100 text-primary-700 border border-primary-200'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
              `}
            >
              <Icon className="h-4 w-4 mr-1" />
              {name}
            </button>
          ))}
        </div>
      </div>

      {/* Configuration Panel */}
      {showConfig && (
        <div className="border-b border-gray-200 p-4 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {chartConfig.type !== 'table' && chartConfig.type !== 'pie' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    X-Axis
                  </label>
                  <select
                    value={chartConfig.xAxis || ''}
                    onChange={(e) => setChartConfig({ ...chartConfig, xAxis: e.target.value })}
                    className="input"
                  >
                    <option value="">Select column</option>
                    {availableColumns.map((col) => (
                      <option key={col} value={col}>
                        {col}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Y-Axis
                  </label>
                  <select
                    value={chartConfig.yAxis || ''}
                    onChange={(e) => setChartConfig({ ...chartConfig, yAxis: e.target.value })}
                    className="input"
                  >
                    <option value="">Select column</option>
                    {availableColumns.map((col) => (
                      <option key={col} value={col}>
                        {col}
                      </option>
                    ))}
                  </select>
                </div>
              </>
            )}

            {chartConfig.type === 'pie' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Group By
                </label>
                <select
                  value={chartConfig.groupBy || ''}
                  onChange={(e) => setChartConfig({ ...chartConfig, groupBy: e.target.value })}
                  className="input"
                >
                  <option value="">Select column</option>
                  {availableColumns.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {chartConfig.type !== 'table' && chartConfig.type !== 'scatter' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Aggregation
                </label>
                <select
                  value={chartConfig.aggregation}
                  onChange={(e) => setChartConfig({ ...chartConfig, aggregation: e.target.value as any })}
                  className="input"
                >
                  <option value="count">Count</option>
                  <option value="sum">Sum</option>
                  <option value="avg">Average</option>
                  <option value="max">Maximum</option>
                  <option value="min">Minimum</option>
                </select>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="p-6">
        {renderChart()}
      </div>
    </div>
  )
}

export default DataVisualization
