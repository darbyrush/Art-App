import axios from 'axios'
import { config } from '../config.js'

// API client configuration
const API_BASE_URL = config.apiBaseUrl

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL || config.apiBaseUrl,
  timeout: 15000, // Increased timeout
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request cache for GET requests
const requestCache = new Map()
const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

// Request queue for rate limiting
const requestQueue = []
const MAX_CONCURRENT_REQUESTS = 6
let activeRequests = 0

// Retry configuration
const RETRY_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000,
  retryStatuses: [408, 429, 500, 502, 503, 504]
}

// Request interceptor for authentication and rate limiting
apiClient.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Add cache busting for non-GET requests
    if (config.method !== 'get') {
      config.params = { ...config.params, _t: Date.now() }
    }
    
    // Add request ID for tracking
    config.requestId = Date.now() + Math.random()
    
    // Queue request if at capacity
    if (activeRequests >= MAX_CONCURRENT_REQUESTS) {
      await new Promise(resolve => {
        requestQueue.push(resolve)
      })
    }
    
    activeRequests++
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling, caching, and retry logic
apiClient.interceptors.response.use(
  (response) => {
    // Cache successful GET responses
    if (response.config.method === 'get' && response.status === 200) {
      const cacheKey = getCacheKey(response.config)
      if (cacheKey) {
        setCacheData(cacheKey, response.data)
      }
    }
    
    // Process queue
    activeRequests--
    if (requestQueue.length > 0) {
      const resolve = requestQueue.shift()
      resolve()
    }
    
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // Process queue on error
    activeRequests--
    if (requestQueue.length > 0) {
      const resolve = requestQueue.shift()
      resolve()
    }
    
    // Handle retry logic
    if (shouldRetry(error) && !originalRequest._retry) {
      return handleRetry(originalRequest, error)
    }
    
    // Handle 401 errors and token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const token = localStorage.getItem('token')
        if (token) {
          // Try to refresh the token
          const refreshResponse = await axios.post(
            `${apiClient.defaults.baseURL}/auth/refresh`,
            {},
            { headers: { Authorization: `Bearer ${token}` } }
          )
          
          if (refreshResponse.data.access_token) {
            localStorage.setItem('token', refreshResponse.data.access_token)
            originalRequest.headers.Authorization = `Bearer ${refreshResponse.data.access_token}`
            return apiClient(originalRequest)
          }
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError)
        // Clear invalid token
        localStorage.removeItem('token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

// Retry logic helpers
const shouldRetry = (error) => {
  return (
    RETRY_CONFIG.retryStatuses.includes(error.response?.status) ||
    error.code === 'ECONNABORTED' ||
    error.message.includes('Network Error')
  )
}

const handleRetry = async (config, error) => {
  if (!config._retryCount) {
    config._retryCount = 0
  }
  
  if (config._retryCount >= RETRY_CONFIG.maxRetries) {
    return Promise.reject(error)
  }
  
  config._retryCount++
  
  // Exponential backoff
  const delay = RETRY_CONFIG.retryDelay * Math.pow(2, config._retryCount - 1)
  
  await new Promise(resolve => setTimeout(resolve, delay))
  
  console.log(`Retrying request (${config._retryCount}/${RETRY_CONFIG.maxRetries}):`, config.url)
  
  return apiClient(config)
}

// Cache utilities
const getCacheKey = (config) => {
  if (config.method !== 'get') return null
  
  const url = config.url
  const params = config.params ? JSON.stringify(config.params) : ''
  return `${url}${params ? `?${params}` : ''}`
}

const setCacheData = (key, data) => {
  requestCache.set(key, {
    data,
    timestamp: Date.now()
  })
}

const getCacheData = (key) => {
  const cached = requestCache.get(key)
  if (!cached) return null
  
  const now = Date.now()
  if (now - cached.timestamp > CACHE_DURATION) {
    requestCache.delete(key)
    return null
  }
  
  return cached.data
}

const clearCache = () => {
  requestCache.clear()
}

// Enhanced API methods with caching and better error handling
const enhancedGet = async (url, config = {}) => {
  const cacheKey = getCacheKey({ method: 'get', url, params: config.params })
  
  // Check cache first
  if (cacheKey) {
    const cachedData = getCacheData(cacheKey)
    if (cachedData) {
      return { data: cachedData, fromCache: true }
    }
  }
  
  try {
    const response = await apiClient.get(url, config)
    return { data: response.data, fromCache: false }
  } catch (error) {
    // Enhanced error handling
    const enhancedError = enhanceError(error, url, 'GET')
    throw enhancedError
  }
}

// Error enhancement
const enhanceError = (error, url, method) => {
  const enhancedError = new Error()
  
  if (error.response) {
    // Server responded with error status
    enhancedError.message = error.response.data?.detail || error.response.data?.message || 'Request failed'
    enhancedError.status = error.response.status
    enhancedError.statusText = error.response.statusText
    enhancedError.data = error.response.data
  } else if (error.request) {
    // Request made but no response
    enhancedError.message = 'No response from server. Please check your connection.'
    enhancedError.status = 0
    enhancedError.statusText = 'NETWORK_ERROR'
  } else {
    // Something else happened
    enhancedError.message = error.message || 'An unexpected error occurred'
    enhancedError.status = 0
    enhancedError.statusText = 'UNKNOWN_ERROR'
  }
  
  enhancedError.url = url
  enhancedError.method = method
  enhancedError.originalError = error
  
  return enhancedError
}

// Public API methods
export const apiClientEnhanced = {
  // GET with caching
  get: enhancedGet,
  
  // POST
  post: async (url, data, config) => {
    try {
      const response = await apiClient.post(url, data, config)
      return response
    } catch (error) {
      throw enhanceError(error, url, 'POST')
    }
  },
  
  // PUT
  put: async (url, data, config) => {
    try {
      const response = await apiClient.put(url, data, config)
      return response
    } catch (error) {
      throw enhanceError(error, url, 'PUT')
    }
  },
  
  // DELETE
  delete: async (url, config) => {
    try {
      const response = await apiClient.delete(url, config)
      return response
    } catch (error) {
      throw enhanceError(error, url, 'DELETE')
    }
  },
  
  // PATCH
  patch: async (url, data, config) => {
    try {
      const response = await apiClient.patch(url, data, config)
      return response
    } catch (error) {
      throw enhanceError(error, url, 'PATCH')
    }
  },
  
  // Cache management
  clearCache,
  
  // Utility methods
  isCached: (url, params) => {
    const cacheKey = getCacheKey({ method: 'get', url, params })
    return cacheKey ? !!getCacheData(cacheKey) : false
  },
  
  // Performance monitoring
  getStats: () => ({
    activeRequests,
    queuedRequests: requestQueue.length,
    cacheSize: requestCache.size
  })
}

// Legacy methods for backward compatibility
export const login = async (username, password) => {
  try {
    const response = await apiClient.post('/auth/login', { username, password })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Login failed')
  }
}

export const register = async (username, password) => {
  try {
    const response = await apiClient.post('/auth/register', { username, password })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Registration failed')
  }
}

export const getCurrentUser = async () => {
  try {
    const response = await apiClient.get('/users/me')
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to get user')
  }
}

export const getRandomArtwork = async (sources = ['all']) => {
  try {
    const params = sources.length > 0 && sources[0] !== 'all' ? { sources: sources.join(',') } : {}
    const response = await apiClient.get('/artworks/random', { params })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to get random artwork')
  }
}

export const likeArtwork = async (artworkId, liked = true) => {
  try {
    if (liked) {
      await apiClient.post(`/artworks/${artworkId}/like`)
    } else {
      await apiClient.delete(`/artworks/${artworkId}/like`)
    }
    return true
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to update like status')
  }
}

export const rateArtwork = async (artworkId, rating) => {
  try {
    await apiClient.post(`/artworks/${artworkId}/rate`, { rating })
    return true
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to rate artwork')
  }
}

export const addNote = async (artworkId, note) => {
  try {
    await apiClient.post(`/artworks/${artworkId}/notes`, { note })
    return true
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to add note')
  }
}

export const getLikedArtworks = async (filters = {}) => {
  try {
    const response = await apiClient.get('/artworks/liked', { params: filters })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to get liked artworks')
  }
}

export const getLikedArtworksFilterOptions = async () => {
  try {
    const response = await apiClient.get('/artworks/liked/filters')
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to get filter options')
  }
}

export const getUserStats = async () => {
  try {
    const response = await apiClient.get('/users/stats')
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to get user stats')
  }
}

export const getArtworks = async (params = {}) => {
  try {
    const response = await apiClient.get('/artworks', { params })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to get artworks')
  }
}

export const getGalleryArtworks = async (params = {}) => {
  try {
    const response = await apiClient.get('/artworks/gallery', { params })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to get gallery artworks')
  }
}

export const getRecommendations = async (limit = 10) => {
  try {
    const response = await apiClient.get('/artworks/recommendations', { params: { limit } })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to get recommendations')
  }
}

export const getPopularArtworks = async (limit = 10) => {
  try {
    const response = await apiClient.get('/artworks/popular', { params: { limit } })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || error.message || 'Failed to get popular artworks')
  }
}

// Export both the enhanced client and the original axios instance
export { apiClient }
export default apiClientEnhanced 