/**
 * Registration page component
 */

import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { useAuthStore } from '@/stores/authStore'

const registerSchema = z.object({
  firstName: z.string().min(1, 'First name is required'),
  lastName: z.string().min(1, 'Last name is required'),
  username: z.string().min(3, 'Username must be at least 3 characters'),
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  passwordConfirm: z.string(),
  organization: z.string().optional(),
  role: z.enum(['analyst', 'developer', 'public']).default('public'),
}).refine((data) => data.password === data.passwordConfirm, {
  message: "Passwords don't match",
  path: ["passwordConfirm"],
})

type RegisterFormData = z.infer<typeof registerSchema>

const RegisterPage: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false)
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false)
  const navigate = useNavigate()
  const { register: registerUser, isLoading, error, clearError } = useAuthStore()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = async (data: RegisterFormData) => {
    try {
      clearError()
      await registerUser(data)
      toast.success('Account created successfully! Welcome to EETL AI!')
      navigate('/dashboard')
    } catch (error) {
      toast.error('Registration failed. Please try again.')
    }
  }

  return (
    <div>
      <div>
        <h2 className="mt-8 text-2xl font-bold leading-9 tracking-tight text-gray-900">
          Create your account
        </h2>
        <p className="mt-2 text-sm leading-6 text-gray-500">
          Already a member?{' '}
          <Link
            to="/auth/login"
            className="font-semibold text-primary-600 hover:text-primary-500"
          >
            Sign in to your account
          </Link>
        </p>
      </div>

      <div className="mt-10">
        <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {error && (
            <div className="rounded-md bg-error-50 p-4">
              <div className="text-sm text-error-700">{error}</div>
            </div>
          )}

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label htmlFor="firstName" className="block text-sm font-medium leading-6 text-gray-900">
                First name
              </label>
              <div className="mt-2">
                <input
                  {...register('firstName')}
                  type="text"
                  autoComplete="given-name"
                  className={`input ${errors.firstName ? 'input-error' : ''}`}
                  placeholder="Enter your first name"
                />
                {errors.firstName && (
                  <p className="mt-2 text-sm text-error-600">{errors.firstName.message}</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="lastName" className="block text-sm font-medium leading-6 text-gray-900">
                Last name
              </label>
              <div className="mt-2">
                <input
                  {...register('lastName')}
                  type="text"
                  autoComplete="family-name"
                  className={`input ${errors.lastName ? 'input-error' : ''}`}
                  placeholder="Enter your last name"
                />
                {errors.lastName && (
                  <p className="mt-2 text-sm text-error-600">{errors.lastName.message}</p>
                )}
              </div>
            </div>
          </div>

          <div>
            <label htmlFor="username" className="block text-sm font-medium leading-6 text-gray-900">
              Username
            </label>
            <div className="mt-2">
              <input
                {...register('username')}
                type="text"
                autoComplete="username"
                className={`input ${errors.username ? 'input-error' : ''}`}
                placeholder="Choose a username"
              />
              {errors.username && (
                <p className="mt-2 text-sm text-error-600">{errors.username.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium leading-6 text-gray-900">
              Email address
            </label>
            <div className="mt-2">
              <input
                {...register('email')}
                type="email"
                autoComplete="email"
                className={`input ${errors.email ? 'input-error' : ''}`}
                placeholder="Enter your email"
              />
              {errors.email && (
                <p className="mt-2 text-sm text-error-600">{errors.email.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="organization" className="block text-sm font-medium leading-6 text-gray-900">
              Organization (optional)
            </label>
            <div className="mt-2">
              <input
                {...register('organization')}
                type="text"
                autoComplete="organization"
                className="input"
                placeholder="Your company or organization"
              />
            </div>
          </div>

          <div>
            <label htmlFor="role" className="block text-sm font-medium leading-6 text-gray-900">
              Role
            </label>
            <div className="mt-2">
              <select
                {...register('role')}
                className="input"
              >
                <option value="public">Public User</option>
                <option value="analyst">Business Analyst</option>
                <option value="developer">Developer</option>
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium leading-6 text-gray-900">
              Password
            </label>
            <div className="mt-2 relative">
              <input
                {...register('password')}
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                className={`input pr-10 ${errors.password ? 'input-error' : ''}`}
                placeholder="Create a password"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 flex items-center pr-3"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                ) : (
                  <EyeIcon className="h-5 w-5 text-gray-400" />
                )}
              </button>
              {errors.password && (
                <p className="mt-2 text-sm text-error-600">{errors.password.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="passwordConfirm" className="block text-sm font-medium leading-6 text-gray-900">
              Confirm password
            </label>
            <div className="mt-2 relative">
              <input
                {...register('passwordConfirm')}
                type={showPasswordConfirm ? 'text' : 'password'}
                autoComplete="new-password"
                className={`input pr-10 ${errors.passwordConfirm ? 'input-error' : ''}`}
                placeholder="Confirm your password"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 flex items-center pr-3"
                onClick={() => setShowPasswordConfirm(!showPasswordConfirm)}
              >
                {showPasswordConfirm ? (
                  <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                ) : (
                  <EyeIcon className="h-5 w-5 text-gray-400" />
                )}
              </button>
              {errors.passwordConfirm && (
                <p className="mt-2 text-sm text-error-600">{errors.passwordConfirm.message}</p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full flex justify-center"
            >
              {isLoading ? (
                <>
                  <div className="loading-spinner mr-2" />
                  Creating account...
                </>
              ) : (
                'Create account'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RegisterPage
