/**
 * Landing page for EETL AI Platform
 */

import React from 'react'
import { Link } from 'react-router-dom'
import {
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  CloudArrowUpIcon,
  CogIcon,
  SparklesIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline'

const features = [
  {
    name: 'Natural Language Querying',
    description: 'Ask questions about your data in plain English and get instant SQL queries and results.',
    icon: ChatBubbleLeftRightIcon,
  },
  {
    name: 'AI-Powered Data Cleaning',
    description: 'Automatically detect and fix data quality issues with intelligent recommendations.',
    icon: SparklesIcon,
  },
  {
    name: 'Multi-Source Integration',
    description: 'Connect to databases, APIs, files, and more with seamless data ingestion.',
    icon: CloudArrowUpIcon,
  },
  {
    name: 'Interactive Visualizations',
    description: 'Create beautiful charts and dashboards with our intuitive interface.',
    icon: ChartBarIcon,
  },
  {
    name: 'Automated ETL Pipelines',
    description: 'Build and schedule data workflows with AI assistance and monitoring.',
    icon: CogIcon,
  },
  {
    name: 'Enterprise Security',
    description: 'Role-based access control, encryption, and compliance-ready features.',
    icon: ShieldCheckIcon,
  },
]

const stats = [
  { name: 'Data Sources Supported', value: '50+' },
  { name: 'Queries Processed Daily', value: '100K+' },
  { name: 'Time Saved per Analysis', value: '80%' },
  { name: 'Customer Satisfaction', value: '99%' },
]

const HomePage: React.FC = () => {
  return (
    <div className="bg-white">
      {/* Header */}
      <header className="absolute inset-x-0 top-0 z-50">
        <nav className="flex items-center justify-between p-6 lg:px-8" aria-label="Global">
          <div className="flex lg:flex-1">
            <Link to="/" className="flex items-center space-x-2">
              <div className="h-8 w-8 bg-gradient-to-r from-primary-600 to-secondary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">E</span>
              </div>
              <span className="text-xl font-bold gradient-text">EETL AI</span>
            </Link>
          </div>
          <div className="flex lg:flex-1 lg:justify-end space-x-4">
            <Link
              to="/auth/login"
              className="text-sm font-semibold leading-6 text-gray-900 hover:text-primary-600"
            >
              Log in
            </Link>
            <Link
              to="/auth/register"
              className="btn-primary"
            >
              Get Started
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero section */}
      <div className="relative isolate px-6 pt-14 lg:px-8">
        <div
          className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80"
          aria-hidden="true"
        >
          <div
            className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-primary-400 to-secondary-600 opacity-30 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"
            style={{
              clipPath:
                'polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)',
            }}
          />
        </div>
        <div className="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              Talk to Your Data with{' '}
              <span className="gradient-text">AI Power</span>
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Transform your data interaction with our AI-powered ETL platform. 
              Ask questions in natural language, get instant insights, and automate 
              your data workflows with cutting-edge AI technology.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link to="/auth/register" className="btn-primary btn-lg">
                Start Free Trial
              </Link>
              <a href="#demo" className="text-sm font-semibold leading-6 text-gray-900">
                Watch Demo <span aria-hidden="true">→</span>
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Features section */}
      <div className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:text-center">
            <h2 className="text-base font-semibold leading-7 text-primary-600">
              Powerful Features
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Everything you need for modern data analysis
            </p>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Our platform combines the power of AI with intuitive design to make 
              data analysis accessible to everyone, from business analysts to data scientists.
            </p>
          </div>
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-4xl">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-2 lg:gap-y-16">
              {features.map((feature) => (
                <div key={feature.name} className="relative pl-16">
                  <dt className="text-base font-semibold leading-7 text-gray-900">
                    <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-primary-600">
                      <feature.icon className="h-6 w-6 text-white" aria-hidden="true" />
                    </div>
                    {feature.name}
                  </dt>
                  <dd className="mt-2 text-base leading-7 text-gray-600">
                    {feature.description}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>

      {/* Stats section */}
      <div className="bg-gray-50 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:max-w-none">
            <div className="text-center">
              <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
                Trusted by data teams worldwide
              </h2>
              <p className="mt-4 text-lg leading-8 text-gray-600">
                Join thousands of organizations using EETL AI to transform their data workflows
              </p>
            </div>
            <dl className="mt-16 grid grid-cols-1 gap-0.5 overflow-hidden rounded-2xl text-center sm:grid-cols-2 lg:grid-cols-4">
              {stats.map((stat) => (
                <div key={stat.name} className="flex flex-col bg-white p-8">
                  <dt className="text-sm font-semibold leading-6 text-gray-600">
                    {stat.name}
                  </dt>
                  <dd className="order-first text-3xl font-bold tracking-tight text-gray-900">
                    {stat.value}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>

      {/* Demo section */}
      <div id="demo" className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              See EETL AI in Action
            </h2>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Experience the power of natural language data interaction with our live demos
            </p>
          </div>
          <div className="mt-16 grid grid-cols-1 gap-8 lg:grid-cols-2">
            <div className="card">
              <div className="card-body">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  🧹 Data Cleaning Demo
                </h3>
                <p className="text-gray-600 mb-6">
                  Upload your dataset and get AI-powered quality assessment and cleaning recommendations.
                </p>
                <a
                  href="https://huggingface.co/spaces/adimiw/eetl-data-cleaning-demo"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary"
                >
                  Try Data Cleaning Demo
                </a>
              </div>
            </div>
            <div className="card">
              <div className="card-body">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  💬 Query Interface Demo
                </h3>
                <p className="text-gray-600 mb-6">
                  Ask questions about sample datasets in natural language and see instant results.
                </p>
                <a
                  href="https://huggingface.co/spaces/adimiw/eetl-query-interface-demo"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary"
                >
                  Try Query Demo
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA section */}
      <div className="bg-primary-600">
        <div className="px-6 py-24 sm:px-6 sm:py-32 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Ready to transform your data workflow?
            </h2>
            <p className="mx-auto mt-6 max-w-xl text-lg leading-8 text-primary-100">
              Start your free trial today and experience the future of data analysis with AI.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                to="/auth/register"
                className="rounded-md bg-white px-3.5 py-2.5 text-sm font-semibold text-primary-600 shadow-sm hover:bg-primary-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
              >
                Get Started Free
              </Link>
              <Link
                to="/auth/login"
                className="text-sm font-semibold leading-6 text-white"
              >
                Sign In <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white">
        <div className="mx-auto max-w-7xl px-6 py-12 md:flex md:items-center md:justify-between lg:px-8">
          <div className="flex justify-center space-x-6 md:order-2">
            <a href="#" className="text-gray-400 hover:text-gray-500">
              <span className="sr-only">GitHub</span>
              <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                <path
                  fillRule="evenodd"
                  d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                  clipRule="evenodd"
                />
              </svg>
            </a>
          </div>
          <div className="mt-8 md:order-1 md:mt-0">
            <p className="text-center text-xs leading-5 text-gray-500">
              &copy; 2024 EETL AI Platform. Built with ❤️ by{' '}
              <a href="https://github.com/adimiw" className="text-primary-600 hover:text-primary-500">
                adimiw
              </a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default HomePage
