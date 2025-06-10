/**
 * Sidebar navigation component
 */

import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { clsx } from 'clsx'
import {
  HomeIcon,
  ChartBarIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  CogIcon,
  UserIcon,
  CloudArrowUpIcon,
  BeakerIcon,
} from '@heroicons/react/24/outline'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Data Sources', href: '/data-sources', icon: CloudArrowUpIcon },
  { name: 'Chat with Data', href: '/chat', icon: ChatBubbleLeftRightIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Reports', href: '/reports', icon: DocumentTextIcon },
  { name: 'Experiments', href: '/experiments', icon: BeakerIcon },
]

const secondaryNavigation = [
  { name: 'Profile', href: '/profile', icon: UserIcon },
  { name: 'Settings', href: '/settings', icon: CogIcon },
]

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation()

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white border-r border-gray-200 px-6 pb-4">
          {/* Logo */}
          <div className="flex h-16 shrink-0 items-center">
            <Link to="/dashboard" className="flex items-center space-x-2">
              <div className="h-8 w-8 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">E</span>
              </div>
              <span className="text-xl font-bold gradient-text">
                EETL AI
              </span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => {
                    const isActive = location.pathname === item.href
                    return (
                      <li key={item.name}>
                        <Link
                          to={item.href}
                          className={clsx(
                            isActive
                              ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                              : 'text-gray-700 hover:text-primary-700 hover:bg-gray-50',
                            'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-medium transition-colors duration-200'
                          )}
                        >
                          <item.icon
                            className={clsx(
                              isActive ? 'text-primary-600' : 'text-gray-400 group-hover:text-primary-600',
                              'h-6 w-6 shrink-0'
                            )}
                            aria-hidden="true"
                          />
                          {item.name}
                        </Link>
                      </li>
                    )
                  })}
                </ul>
              </li>

              {/* Secondary navigation */}
              <li className="mt-auto">
                <div className="text-xs font-semibold leading-6 text-gray-400 uppercase tracking-wide">
                  Account
                </div>
                <ul role="list" className="-mx-2 mt-2 space-y-1">
                  {secondaryNavigation.map((item) => {
                    const isActive = location.pathname === item.href
                    return (
                      <li key={item.name}>
                        <Link
                          to={item.href}
                          className={clsx(
                            isActive
                              ? 'bg-primary-50 text-primary-700'
                              : 'text-gray-700 hover:text-primary-700 hover:bg-gray-50',
                            'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-medium'
                          )}
                        >
                          <item.icon
                            className={clsx(
                              isActive ? 'text-primary-600' : 'text-gray-400 group-hover:text-primary-600',
                              'h-6 w-6 shrink-0'
                            )}
                            aria-hidden="true"
                          />
                          {item.name}
                        </Link>
                      </li>
                    )
                  })}
                </ul>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* Mobile sidebar */}
      <div
        className={clsx(
          'fixed inset-y-0 z-50 flex w-64 flex-col transition-transform duration-300 ease-in-out lg:hidden',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 shadow-xl">
          {/* Mobile header */}
          <div className="flex h-16 shrink-0 items-center justify-between">
            <Link to="/dashboard" className="flex items-center space-x-2">
              <div className="h-8 w-8 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">E</span>
              </div>
              <span className="text-xl font-bold gradient-text">
                EETL AI
              </span>
            </Link>
            <button
              type="button"
              className="text-gray-400 hover:text-gray-600"
              onClick={onClose}
            >
              <span className="sr-only">Close sidebar</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Mobile navigation */}
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => {
                    const isActive = location.pathname === item.href
                    return (
                      <li key={item.name}>
                        <Link
                          to={item.href}
                          onClick={onClose}
                          className={clsx(
                            isActive
                              ? 'bg-primary-50 text-primary-700'
                              : 'text-gray-700 hover:text-primary-700 hover:bg-gray-50',
                            'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-medium'
                          )}
                        >
                          <item.icon
                            className={clsx(
                              isActive ? 'text-primary-600' : 'text-gray-400 group-hover:text-primary-600',
                              'h-6 w-6 shrink-0'
                            )}
                            aria-hidden="true"
                          />
                          {item.name}
                        </Link>
                      </li>
                    )
                  })}
                </ul>
              </li>

              <li className="mt-auto">
                <div className="text-xs font-semibold leading-6 text-gray-400 uppercase tracking-wide">
                  Account
                </div>
                <ul role="list" className="-mx-2 mt-2 space-y-1">
                  {secondaryNavigation.map((item) => {
                    const isActive = location.pathname === item.href
                    return (
                      <li key={item.name}>
                        <Link
                          to={item.href}
                          onClick={onClose}
                          className={clsx(
                            isActive
                              ? 'bg-primary-50 text-primary-700'
                              : 'text-gray-700 hover:text-primary-700 hover:bg-gray-50',
                            'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-medium'
                          )}
                        >
                          <item.icon
                            className={clsx(
                              isActive ? 'text-primary-600' : 'text-gray-400 group-hover:text-primary-600',
                              'h-6 w-6 shrink-0'
                            )}
                            aria-hidden="true"
                          />
                          {item.name}
                        </Link>
                      </li>
                    )
                  })}
                </ul>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </>
  )
}

export default Sidebar
