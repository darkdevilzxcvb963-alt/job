import { createContext, useContext, useState, useEffect } from 'react'
// Use full auth service
import { login, googleAuth, signup, logout, getCurrentUser, verifyEmail, forgotPassword, resetPassword } from '../services/api'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const response = await getCurrentUser()
        setUser(response.data)
        setIsAuthenticated(true)
        localStorage.setItem('user', JSON.stringify(response.data))
      } catch (error) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        setUser(null)
        setIsAuthenticated(false)
      }
    }
    setLoading(false)
  }

  const handleLogin = async (email, password) => {
    try {
      const response = await login({ email, password })
      // Handle MFA requirement
      if (response.data.mfa_required) {
        return { 
          success: true, 
          mfa_required: true, 
          mfa_token: response.data.mfa_token,
          user: response.data.user 
        }
      }

      const { access_token, refresh_token, user: userData } = response.data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      // Use user data from login response if available, otherwise fetch it
      if (userData) {
        setUser(userData)
        setIsAuthenticated(true)
        localStorage.setItem('user', JSON.stringify(userData))
        return { success: true, user: userData }
      }

      // Fallback: Get user info if not in login response
      try {
        const userResponse = await getCurrentUser()
        setUser(userResponse.data)
        setIsAuthenticated(true)
        localStorage.setItem('user', JSON.stringify(userResponse.data))
        return { success: true, user: userResponse.data }
      } catch (userError) {
        // If getCurrentUser fails, still allow login with token
        console.warn('Could not fetch user info:', userError)
        setIsAuthenticated(true)
        return { success: true, user: { email } }
      }
    } catch (error) {
      console.error('Login error detail:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
        url: error.config?.url
      })
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed. Please check your credentials.'
      return {
        success: false,
        error: errorMessage
      }
    }
  }

  const handleGoogleLogin = async (idToken, role = 'job_seeker') => {
    try {
      const response = await googleAuth({ id_token: idToken, role })
      if (response.data.mfa_required) {
        return { 
          success: true, 
          mfa_required: true, 
          mfa_token: response.data.mfa_token,
          user: response.data.user
        }
      }

      const { access_token, refresh_token, user: userData } = response.data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      if (userData) {
        setUser(userData)
        setIsAuthenticated(true)
        localStorage.setItem('user', JSON.stringify(userData))
        return { success: true, user: userData }
      }

      // Fallback: Get user info if not in response
      const userResponse = await getCurrentUser()
      setUser(userResponse.data)
      setIsAuthenticated(true)
      localStorage.setItem('user', JSON.stringify(userResponse.data))
      return { success: true, user: userResponse.data }
    } catch (error) {
      console.error('Google Auth error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Google authentication failed.'
      return {
        success: false,
        error: errorMessage
      }
    }
  }

  const handleSignup = async (userData) => {
    try {
      // Clean up phone if empty
      const cleanedData = {
        ...userData,
        phone: userData.phone && userData.phone.trim() ? userData.phone.trim() : null
      }

      const response = await signup(cleanedData)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Signup error:', error)

      // Handle network errors
      if (!error.response) {
        return {
          success: false,
          error: 'Network error: Unable to connect to server. Please check if the backend is running on http://127.0.0.1:8001'
        }
      }

      // Handle specific error responses
      const errorMessage = error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Signup failed. Please try again.'
      return {
        success: false,
        error: errorMessage
      }
    }
  }

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      setUser(null)
      setIsAuthenticated(false)
    }
  }

  const handleVerifyEmail = async (token) => {
    try {
      await verifyEmail(token)
      if (user) {
        const updatedUser = { ...user, is_verified: true }
        setUser(updatedUser)
        localStorage.setItem('user', JSON.stringify(updatedUser))
      }
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Verification failed'
      }
    }
  }

  const handleForgotPassword = async (email) => {
    try {
      const response = await forgotPassword(email)
      return { success: true, ...response.data }
    } catch (error) {
      console.error('Forgot password error:', error.response?.data || error.message)
      return {
        success: false,
        error: error.response?.data?.detail || 'Request failed. Please try again later.'
      }
    }
  }

  const handleResetPassword = async (token, newPassword) => {
    try {
      const response = await resetPassword(token, newPassword)
      return { success: true, ...response.data }
    } catch (error) {
      console.error('Reset password error:', error.response?.data || error.message)
      return {
        success: false,
        error: error.response?.data?.detail || 'Reset failed. Please try again.'
      }
    }
  }

  const value = {
    user,
    loading,
    isAuthenticated,
    login: handleLogin,
    loginWithGoogle: handleGoogleLogin,
    signup: handleSignup,
    logout: handleLogout,
    verifyEmail: handleVerifyEmail,
    forgotPassword: handleForgotPassword,
    resetPassword: handleResetPassword,
    refreshUser: checkAuth,
    checkAuth
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
