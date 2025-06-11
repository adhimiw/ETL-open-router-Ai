/**
 * Natural Language Query Interface Component
 * Allows users to query data using natural language
 */

import React, { useState, useRef, useEffect } from 'react'
import {
  PaperAirplaneIcon,
  SparklesIcon,
  ClockIcon,
  CodeBracketIcon,
  TableCellsIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline'
import { browserMCP, QueryResult } from '@/services/browserMcp'
import toast from 'react-hot-toast'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  queryResult?: QueryResult
  sql?: string
  executionTime?: number
}

interface NaturalLanguageQueryProps {
  dataSourceId?: string
  onQueryResult?: (result: QueryResult) => void
}

const NaturalLanguageQuery: React.FC<NaturalLanguageQueryProps> = ({
  dataSourceId,
  onQueryResult,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I\'m your AI data analyst. Ask me anything about your data in plain English. For example:\n\n• "Show me the top 10 customers by revenue"\n• "What are the sales trends over the last 6 months?"\n• "Find all orders with missing customer information"',
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [conversationId, setConversationId] = useState<string>()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    // Initialize conversation
    const initConversation = async () => {
      try {
        const id = await browserMCP.startConversation(dataSourceId)
        setConversationId(id)
      } catch (error) {
        console.error('Failed to start conversation:', error)
      }
    }

    initConversation()
  }, [dataSourceId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || isProcessing) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsProcessing(true)

    try {
      // Process natural language query
      const queryResult = await browserMCP.processNaturalLanguageQuery(
        userMessage.content,
        dataSourceId
      )

      // Send message to conversation if available
      if (conversationId) {
        await browserMCP.sendMessage(conversationId, userMessage.content)
      }

      // Create assistant response
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: generateResponseMessage(queryResult),
        timestamp: new Date(),
        queryResult,
        sql: queryResult.sql,
        executionTime: queryResult.executionTime,
      }

      setMessages(prev => [...prev, assistantMessage])

      // Notify parent component
      if (onQueryResult) {
        onQueryResult(queryResult)
      }

      toast.success('Query executed successfully!')
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'I apologize, but I encountered an error processing your query. Please try rephrasing your question or check if the data source is available.',
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, errorMessage])
      toast.error('Failed to process query')
    } finally {
      setIsProcessing(false)
    }
  }

  const generateResponseMessage = (result: QueryResult): string => {
    const { results, rowCount, executionTime, aiResponse } = result

    // Use AI response if available
    if (aiResponse) {
      return aiResponse
    }

    // Fallback to generated response
    if (rowCount === 0) {
      return 'No results found for your query. You might want to try a different question or check your data.'
    }

    let message = `I found ${rowCount} result${rowCount > 1 ? 's' : ''} for your query`

    if (executionTime) {
      message += ` (executed in ${executionTime.toFixed(2)}ms)`
    }

    message += '. Here\'s what I discovered:\n\n'

    // Add insights based on the data
    if (results.length > 0) {
      const firstRow = results[0]
      const columns = Object.keys(firstRow)

      if (columns.length > 0) {
        message += `The data includes ${columns.length} column${columns.length > 1 ? 's' : ''}: ${columns.join(', ')}.`
      }
    }

    return message
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as any)
    }
  }

  const suggestedQueries = [
    'Show me a summary of the data',
    'What are the top 10 records by value?',
    'Find any missing or null values',
    'Show me the data distribution',
    'What patterns do you see in this data?',
  ]

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center space-x-2">
          <SparklesIcon className="h-6 w-6 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            AI Data Analyst
          </h3>
          {dataSourceId && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Connected
            </span>
          )}
        </div>
        <p className="text-sm text-gray-500 mt-1">
          Ask questions about your data in natural language
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isProcessing && (
          <div className="flex items-center space-x-2 text-gray-500">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
            <span className="text-sm">Processing your query...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Queries */}
      {messages.length === 1 && !isProcessing && (
        <div className="border-t border-gray-200 p-4">
          <p className="text-sm font-medium text-gray-700 mb-2">
            Try asking:
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestedQueries.map((query, index) => (
              <button
                key={index}
                onClick={() => setInputValue(query)}
                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything about your data..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md resize-none focus:ring-primary-500 focus:border-primary-500"
              rows={1}
              style={{ minHeight: '40px', maxHeight: '120px' }}
            />
          </div>
          <button
            type="submit"
            disabled={!inputValue.trim() || isProcessing}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PaperAirplaneIcon className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  )
}

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const [showSQL, setShowSQL] = useState(false)
  const [showResults, setShowResults] = useState(false)

  return (
    <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-3xl rounded-lg px-4 py-2 ${
          message.type === 'user'
            ? 'bg-primary-600 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        <div className="whitespace-pre-wrap text-sm">{message.content}</div>

        {/* Query Results */}
        {message.queryResult && (
          <div className="mt-3 space-y-2">
            <div className="flex items-center space-x-4 text-xs">
              <div className="flex items-center space-x-1">
                <ClockIcon className="h-3 w-3" />
                <span>{message.executionTime?.toFixed(2)}ms</span>
              </div>
              <div className="flex items-center space-x-1">
                <TableCellsIcon className="h-3 w-3" />
                <span>{message.queryResult.rowCount} rows</span>
              </div>
            </div>

            <div className="flex space-x-2">
              {message.sql && (
                <button
                  onClick={() => setShowSQL(!showSQL)}
                  className="inline-flex items-center px-2 py-1 text-xs font-medium rounded bg-white bg-opacity-20 hover:bg-opacity-30 transition-colors"
                >
                  <CodeBracketIcon className="h-3 w-3 mr-1" />
                  {showSQL ? 'Hide' : 'Show'} SQL
                </button>
              )}

              {message.queryResult.results.length > 0 && (
                <button
                  onClick={() => setShowResults(!showResults)}
                  className="inline-flex items-center px-2 py-1 text-xs font-medium rounded bg-white bg-opacity-20 hover:bg-opacity-30 transition-colors"
                >
                  <ChartBarIcon className="h-3 w-3 mr-1" />
                  {showResults ? 'Hide' : 'Show'} Data
                </button>
              )}
            </div>

            {/* SQL Display */}
            {showSQL && message.sql && (
              <div className="mt-2 p-2 bg-gray-900 rounded text-green-400 text-xs font-mono overflow-x-auto">
                <pre>{message.sql}</pre>
              </div>
            )}

            {/* Results Display */}
            {showResults && message.queryResult.results.length > 0 && (
              <div className="mt-2 max-h-40 overflow-auto">
                <table className="min-w-full text-xs">
                  <thead>
                    <tr className="bg-white bg-opacity-20">
                      {Object.keys(message.queryResult.results[0]).map((key) => (
                        <th key={key} className="px-2 py-1 text-left font-medium">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {message.queryResult.results.slice(0, 5).map((row, index) => (
                      <tr key={index} className="border-t border-white border-opacity-20">
                        {Object.values(row).map((value, cellIndex) => (
                          <td key={cellIndex} className="px-2 py-1">
                            {String(value)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                {message.queryResult.results.length > 5 && (
                  <div className="text-center py-1 text-xs opacity-75">
                    ... and {message.queryResult.results.length - 5} more rows
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        <div className="text-xs opacity-75 mt-2">
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}

export default NaturalLanguageQuery
