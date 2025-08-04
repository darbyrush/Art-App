import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const apiClient = {
  // Auth endpoints
  async login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const response = await api.post('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  },

  async register(username, password, email = null) {
    const data = { username, password }
    if (email) data.email = email
    
    const response = await api.post('/register', data)
    return response.data
  },

  async getCurrentUser() {
    const response = await api.get('/users/me')
    return response.data
  },

  // Artwork endpoints
  async getRandomArtwork(sources = ['all']) {
    const params = {}
    if (sources && sources.length > 0 && !sources.includes('all')) {
      params.sources = sources.join(',')
    }
    
    const response = await api.get('/artworks/random', { params })
    return response.data
  },

  async likeArtwork(artworkId, liked = true) {
    const response = await api.post(`/artworks/${artworkId}/like`, { liked })
    return response.data
  },

  async rateArtwork(artworkId, rating) {
    const response = await api.post(`/artworks/${artworkId}/rate`, { rating })
    return response.data
  },

  async addNote(artworkId, note) {
    const response = await api.post(`/artworks/${artworkId}/note`, { note })
    return response.data
  },

  async getLikedArtworks() {
    const response = await api.get('/users/me/likes')
    return response.data
  },

  async getUserStats() {
    const response = await api.get('/users/me/stats')
    return response.data
  },

  async getArtworks(params = {}) {
    const { page = 1, sources = ['all'], sortBy = 'random' } = params
    const sourcesParam = sources.join(',')
    const response = await api.get('/artworks', {
      params: {
        page,
        sources: sourcesParam,
        sort_by: sortBy
      }
    })
    return response.data
  },

  async getGalleryArtworks(params = {}) {
    const { page = 1, sources = ['all'], sortBy = 'random' } = params
    const sourcesParam = sources.join(',')
    const response = await api.get('/artworks/gallery', {
      params: {
        page,
        sources: sourcesParam,
        sort_by: sortBy
      }
    })
    return response.data
  },

  async getRecommendations(limit = 10) {
    const response = await api.get('/artworks/recommendations', {
      params: { limit }
    })
    return response.data
  },

  async getPopularArtworks(limit = 10) {
    const response = await api.get('/artworks/popular', {
      params: { limit }
    })
    return response.data
  },

  // Health check
  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  }
} 