/**
 * Dashboard page component
 */

import React from 'react'
import { Link } from 'react-router-dom'
import {
  ChartBarIcon,
  ChatBubbleLeftRightIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  UsersIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline'
import { useAuthStore } from '@/stores/authStore'

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

  return (
    <div>
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.firstName}! 👋
        </h1>
        <p className="mt-2 text-gray-600">
          Here's what's happening with your data today.
        </p>
      </div>

      {/* Stats */}
      <div className="mb-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Overview</h2>
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
                          {item.changeType === 'positive' ? (
                            <svg
                              className="self-center flex-shrink-0 h-5 w-5 text-green-500"
                              fill="currentColor"
                              viewBox="0 0 20 20"
                              aria-hidden="true"
                            >
                              <path
                                fillRule="evenodd"
                                d="M10 17a.75.75 0 01-.75-.75V5.612L5.29 9.77a.75.75 0 01-1.08-1.04l5.25-5.5a.75.75 0 011.08 0l5.25 5.5a.75.75 0 11-1.08 1.04L10.75 5.612V16.25A.75.75 0 0110 17z"
                                clipRule="evenodd"
                              />
                            </svg>
                          ) : (
                            <svg
                              className="self-center flex-shrink-0 h-5 w-5 text-red-500"
                              fill="currentColor"
                              viewBox="0 0 20 20"
                              aria-hidden="true"
                            >
                              <path
                                fillRule="evenodd"
                                d="M10 3a.75.75 0 01.75.75v10.638l3.96-4.158a.75.75 0 111.08 1.04l-5.25 5.5a.75.75 0 01-1.08 0l-5.25-5.5a.75.75 0 111.08-1.04l3.96 4.158V3.75A.75.75 0 0110 3z"
                                clipRule="evenodd"
                              />
                            </svg>
                          )}
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
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Quick Actions */}
        <div>
          <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {quickActions.map((action) => (
              <Link
                key={action.name}
                to={action.href}
                className="card hover:shadow-md transition-shadow duration-200"
              >
                <div className="card-body">
                  <div className="flex items-center">
                    <div className={`flex-shrink-0 p-3 rounded-lg ${action.color}`}>
                      <action.icon className="h-6 w-6 text-white" aria-hidden="true" />
                    </div>
                    <div className="ml-4">
                      <h3 className="text-sm font-medium text-gray-900">{action.name}</h3>
                      <p className="text-sm text-gray-500">{action.description}</p>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div>
          <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h2>
          <div className="card">
            <div className="card-body">
              <div className="flow-root">
                <ul role="list" className="-mb-8">
                  {recentActivity.map((activity, activityIdx) => (
                    <li key={activity.id}>
                      <div className="relative pb-8">
                        {activityIdx !== recentActivity.length - 1 ? (
                          <span
                            className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200"
                            aria-hidden="true"
                          />
                        ) : null}
                        <div className="relative flex space-x-3">
                          <div>
                            <span className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center ring-8 ring-white">
                              <activity.icon className="h-4 w-4 text-gray-500" aria-hidden="true" />
                            </span>
                          </div>
                          <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                            <div>
                              <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                              <p className="text-sm text-gray-500">{activity.description}</p>
                            </div>
                            <div className="whitespace-nowrap text-right text-sm text-gray-500">
                              <time>{activity.time}</time>
                            </div>
                          </div>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Insights */}
      <div className="mt-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4">AI Insights</h2>
        <div className="card">
          <div className="card-body">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <CpuChipIcon className="h-6 w-6 text-primary-600" />
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-medium text-gray-900 mb-2">
                  💡 Data Quality Insights
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Your sales data shows 95% completeness with minor issues in the customer_age column. 
                  Consider implementing data validation rules for future uploads.
                </p>
                <div className="flex space-x-3">
                  <Link to="/data-sources" className="btn-primary btn-sm">
                    View Details
                  </Link>
                  <button className="btn-outline btn-sm">
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
