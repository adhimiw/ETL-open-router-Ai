/**
 * Authentication store using Zustand
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: string
  email: string
  username: string
  firstName: string
  lastName: string
  fullName: string
  role: 'admin' | 'developer' | 'analyst' | 'public'
  organization?: string
  profilePicture?: string
  isVerified: boolean
  apiCallsCount: number
  dataProcessedMb: number
  createdAt: string
  lastLogin?: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
  updateProfile: (userData: Partial<User>) => Promise<void>
  clearError: () => void
  setLoading: (loading: boolean) => void
}

export interface RegisterData {
  username: string
  email: string
  password: string
  passwordConfirm: string
  firstName: string
  lastName: string
  organization?: string
  role?: string
}

type AuthStore = AuthState & AuthActions

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await fetch('/api/auth/login/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
          })

          if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || 'Login failed')
          }

          const data = await response.json()
          
          set({
            user: data.user,
            tokens: data.tokens,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Login failed',
            isLoading: false,
          })
          throw error
        }
      },

      register: async (userData: RegisterData) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await fetch('/api/auth/register/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
          })

          if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || 'Registration failed')
          }

          const data = await response.json()
          
          set({
            user: data.user,
            tokens: data.tokens,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Registration failed',
            isLoading: false,
          })
          throw error
        }
      },

      logout: () => {
        const { tokens } = get()
        
        // Call logout endpoint if tokens exist
        if (tokens?.refresh) {
          fetch('/api/auth/logout/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${tokens.access}`,
            },
            body: JSON.stringify({ refresh_token: tokens.refresh }),
          }).catch(() => {
            // Ignore errors on logout
          })
        }

        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
          error: null,
        })
      },

      refreshToken: async () => {
        const { tokens } = get()
        
        if (!tokens?.refresh) {
          throw new Error('No refresh token available')
        }

        try {
          const response = await fetch('/api/auth/token/refresh/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: tokens.refresh }),
          })

          if (!response.ok) {
            throw new Error('Token refresh failed')
          }

          const data = await response.json()
          
          set({
            tokens: {
              access: data.access,
              refresh: tokens.refresh,
            },
          })
        } catch (error) {
          // If refresh fails, logout user
          get().logout()
          throw error
        }
      },

      updateProfile: async (userData: Partial<User>) => {
        const { tokens } = get()
        
        if (!tokens?.access) {
          throw new Error('Not authenticated')
        }

        set({ isLoading: true, error: null })
        
        try {
          const response = await fetch('/api/auth/profile/', {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${tokens.access}`,
            },
            body: JSON.stringify(userData),
          })

          if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || 'Profile update failed')
          }

          const updatedUser = await response.json()
          
          set({
            user: updatedUser,
            isLoading: false,
            error: null,
          })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Profile update failed',
            isLoading: false,
          })
          throw error
        }
      },

      clearError: () => set({ error: null }),
      
      setLoading: (loading: boolean) => set({ isLoading: loading }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
