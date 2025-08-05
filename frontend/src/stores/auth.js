import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/utils/apiClient'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token') || null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  const initializeAuth = () => {
    const savedToken = localStorage.getItem('access_token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken) {
      token.value = savedToken
    }
    
    if (savedUser) {
      user.value = JSON.parse(savedUser)
    }
  }

  const login = async (username, password) => {
    loading.value = true
    try {
      const response = await apiClient.login(username, password)
      if (response.access_token) {
        token.value = response.access_token
        localStorage.setItem('access_token', response.access_token)
        
        // Get user info
        const userInfo = await apiClient.getCurrentUser()
        user.value = userInfo
        localStorage.setItem('user', JSON.stringify(userInfo))
        
        return { success: true }
      }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  const register = async (username, password) => {
    loading.value = true
    try {
      const response = await apiClient.register(username, password)
      if (response.id) {
        // Auto-login after registration
        return await login(username, password)
      }
    } catch (error) {
      console.error('Registration error:', error)
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    initializeAuth,
    login,
    register,
    logout
  }
}) 