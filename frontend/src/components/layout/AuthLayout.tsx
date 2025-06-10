/**
 * Layout component for authentication pages
 */

import React from 'react'
import { Outlet } from 'react-router-dom'

const AuthLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:flex-1 lg:flex-col lg:justify-center lg:px-8 lg:py-12 bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-800">
        <div className="mx-auto max-w-md">
          <div className="text-center">
            <div className="mx-auto h-16 w-16 bg-white rounded-2xl flex items-center justify-center mb-8">
              <span className="text-2xl font-bold text-primary-600">E</span>
            </div>
            <h1 className="text-4xl font-bold text-white mb-4">
              EETL AI Platform
            </h1>
            <p className="text-xl text-primary-100 mb-8">
              Talk to your data with AI-powered natural language processing
            </p>
          </div>
          
          <div className="space-y-6">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-3">
                🤖 AI-Powered Analysis
              </h3>
              <p className="text-primary-100">
                Ask questions about your data in plain English and get instant insights, 
                SQL queries, and visualizations.
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-3">
                🔧 Smart Data Cleaning
              </h3>
              <p className="text-primary-100">
                Automatically detect data quality issues and get AI-generated 
                recommendations for cleaning and transformation.
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-3">
                📊 Interactive Dashboards
              </h3>
              <p className="text-primary-100">
                Create beautiful visualizations and reports with our intuitive 
                drag-and-drop interface.
              </p>
            </div>
          </div>
          
          <div className="mt-8 text-center">
            <p className="text-primary-200 text-sm">
              Trusted by data teams worldwide
            </p>
            <div className="flex justify-center space-x-4 mt-4">
              <div className="h-8 w-8 bg-white/20 rounded-full"></div>
              <div className="h-8 w-8 bg-white/20 rounded-full"></div>
              <div className="h-8 w-8 bg-white/20 rounded-full"></div>
              <div className="h-8 w-8 bg-white/20 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Auth forms */}
      <div className="flex flex-1 flex-col justify-center px-4 py-12 sm:px-6 lg:flex-none lg:px-20 xl:px-24">
        <div className="mx-auto w-full max-w-sm lg:w-96">
          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="mx-auto h-12 w-12 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-xl flex items-center justify-center mb-4">
              <span className="text-xl font-bold text-white">E</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900">
              EETL AI Platform
            </h1>
            <p className="text-gray-600 mt-2">
              Talk to your data with AI
            </p>
          </div>

          {/* Auth form content */}
          <Outlet />
          
          {/* Footer */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-500">
              By continuing, you agree to our{' '}
              <a href="#" className="text-primary-600 hover:text-primary-500">
                Terms of Service
              </a>{' '}
              and{' '}
              <a href="#" className="text-primary-600 hover:text-primary-500">
                Privacy Policy
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AuthLayout
