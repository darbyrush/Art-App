import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/utils/apiClient'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const isLoading = ref(false)
  const error = ref(null)
  const lastLoginTime = ref(null)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isTokenExpired = computed(() => {
    if (!lastLoginTime.value) return false
    // Check if token is older than 24 hours
    const tokenAge = Date.now() - lastLoginTime.value
    return tokenAge > 24 * 60 * 60 * 1000
  })

  // Actions
  const setToken = (newToken) => {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
      lastLoginTime.value = Date.now()
    } else {
      localStorage.removeItem('token')
      lastLoginTime.value = null
    }
  }

  const setUser = (userData) => {
    user.value = userData
  }

  const clearError = () => {
    error.value = null
  }

  const login = async (credentials) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiClient.post('/auth/login', credentials)
      
      if (response.data.access_token) {
        setToken(response.data.access_token)
        setUser(response.data.user)
        return { success: true, user: response.data.user }
      } else {
        throw new Error('Invalid response format')
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Login failed'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiClient.post('/auth/register', userData)
      
      if (response.data.access_token) {
        setToken(response.data.access_token)
        setUser(response.data.user)
        return { success: true, user: response.data.user }
      } else {
        throw new Error('Invalid response format')
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Registration failed'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    error.value = null
  }

  const fetchUserProfile = async () => {
    if (!token.value) return null
    
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiClient.get('/users/me')
      setUser(response.data)
      return response.data
    } catch (err) {
      console.error('Failed to fetch user profile:', err)
      // If token is invalid, clear it
      if (err.response?.status === 401) {
        logout()
      }
      return null
    } finally {
      isLoading.value = false
    }
  }

  const updateProfile = async (profileData) => {
    if (!token.value) throw new Error('Not authenticated')
    
    try {
      isLoading.value = true
      error.value = null
      
      const response = await apiClient.put('/users/me', profileData)
      setUser(response.data)
      return response.data
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Profile update failed'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  const updateProfilePicture = async (file) => {
    if (!token.value) throw new Error('Not authenticated')
    
    try {
      isLoading.value = true
      error.value = null
      
      const formData = new FormData()
      formData.append('file', file)  // Changed from 'profile_picture' to 'file'
      
      const response = await apiClient.post('/users/me/profile-picture', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      // Update user with new profile picture
      if (response.data.user && response.data.user.profile_picture) {
        setUser({ ...user.value, profile_picture: response.data.user.profile_picture })
      }
      
      return response.data
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Profile picture update failed'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  const deleteProfilePicture = async () => {
    if (!token.value) throw new Error('Not authenticated')
    
    try {
      isLoading.value = true
      error.value = null
      
      await apiClient.delete('/users/me/profile-picture')
      
      // Remove profile picture from user
      setUser({ ...user.value, profile_picture: null })
      
      return { success: true }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Profile picture deletion failed'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  const refreshToken = async () => {
    if (!token.value) return false
    
    try {
      const response = await apiClient.post('/auth/refresh')
      if (response.data.access_token) {
        setToken(response.data.access_token)
        return true
      }
      return false
    } catch (err) {
      console.error('Token refresh failed:', err)
      logout()
      return false
    }
  }

  // Initialize user if token exists
  const initializeAuth = async () => {
    if (token.value && !user.value) {
      await fetchUserProfile()
    }
    
    // Check if token is expired and refresh if needed
    if (isTokenExpired.value && token.value) {
      const refreshed = await refreshToken()
      if (!refreshed) {
        logout()
      }
    }
  }

  return {
    // State
    user,
    token,
    isLoading,
    error,
    
    // Computed
    isAuthenticated,
    isTokenExpired,
    
    // Actions
    login,
    register,
    logout,
    fetchUserProfile,
    updateProfile,
    updateProfilePicture,
    deleteProfilePicture,
    refreshToken,
    initializeAuth,
    clearError,
    setToken,
    setUser
  }
}) 