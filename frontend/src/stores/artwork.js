import { defineStore } from 'pinia'
import { ref, computed, shallowRef } from 'vue'
import { apiClient } from '@/utils/apiClient'
import { createLRUCache, debounce } from '@/utils/performance'

export const useArtworkStore = defineStore('artwork', () => {
  // State
  const artworks = ref([])
  const favorites = ref(new Set())
  const isLoading = ref(false)
  const error = ref(null)
  const currentPage = ref(1)
  const totalPages = ref(1)
  const hasMore = ref(true)
  
  // Enhanced caching with LRU
  const cache = createLRUCache(200) // Increased cache size
  const lastFetchTime = ref(null)
  
  // Request deduplication
  const pendingRequests = new Map()
  
  // Cache configuration
  const CACHE_DURATION = 10 * 60 * 1000 // 10 minutes (increased)
  const SEARCH_CACHE_DURATION = 5 * 60 * 1000 // 5 minutes for search results

  // Computed
  const favoriteArtworks = computed(() => 
    artworks.value.filter(artwork => favorites.value.has(artwork.id))
  )

  const isFavorited = (artworkId) => favorites.value.has(artworkId)

  // Actions
  const clearError = () => {
    error.value = null
  }

  const clearCache = () => {
    cache.clear()
    lastFetchTime.value = null
  }

  const isCacheValid = (key, duration = CACHE_DURATION) => {
    const cached = cache.get(key)
    if (!cached) return false
    
    const now = Date.now()
    return (now - cached.timestamp) < duration
  }

  const getCachedData = (key) => {
    const cached = cache.get(key)
    return cached ? cached.data : null
  }

  const setCachedData = (key, data, duration = CACHE_DURATION) => {
    cache.set(key, {
      data,
      timestamp: Date.now(),
      duration
    })
  }

  // Request deduplication helper
  const deduplicateRequest = async (key, requestFn) => {
    if (pendingRequests.has(key)) {
      return pendingRequests.get(key)
    }
    
    const promise = requestFn()
    pendingRequests.set(key, promise)
    
    try {
      const result = await promise
      return result
    } finally {
      pendingRequests.delete(key)
    }
  }

  const fetchArtworks = async (page = 1, limit = 20, source = null, forceRefresh = false) => {
    const cacheKey = `artworks_${page}_${limit}_${source || 'all'}`
    
    // Check cache first
    if (!forceRefresh && isCacheValid(cacheKey)) {
      const cachedData = getCachedData(cacheKey)
      artworks.value = cachedData.artworks
      totalPages.value = cachedData.total_pages
      hasMore.value = cachedData.has_more
      currentPage.value = page
      return cachedData
    }
    
    return deduplicateRequest(cacheKey, async () => {
      try {
        isLoading.value = true
        error.value = null
        
        const params = { page, limit }
        if (source) params.source = source
        
        const response = await apiClient.get('/artworks', { params })
        
        const data = response.data
        artworks.value = data.artworks || data
        totalPages.value = data.total_pages || 1
        hasMore.value = data.has_more !== false
        currentPage.value = page
        lastFetchTime.value = Date.now()
        
        // Cache the result
        setCachedData(cacheKey, {
          artworks: artworks.value,
          total_pages: totalPages.value,
          has_more: hasMore.value
        })
        
        return data
      } catch (err) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch artworks'
        error.value = errorMessage
        throw new Error(errorMessage)
      } finally {
        isLoading.value = false
      }
    })
  }

  const fetchMoreArtworks = async (limit = 20) => {
    if (!hasMore.value || isLoading.value) return null
    
    const nextPage = currentPage.value + 1
    return await fetchArtworks(nextPage, limit)
  }

  // Debounced search to reduce API calls
  const debouncedSearch = debounce(async (query, page = 1, limit = 20) => {
    try {
      isLoading.value = true
      error.value = null
      
      const cacheKey = `search_${query}_${page}_${limit}`
      
      // Check cache first
      if (isCacheValid(cacheKey, SEARCH_CACHE_DURATION)) {
        const cachedData = getCachedData(cacheKey)
        artworks.value = cachedData.artworks
        totalPages.value = cachedData.total_pages
        hasMore.value = cachedData.has_more
        currentPage.value = page
        return cachedData
      }
      
      const params = { q: query, page, limit }
      const response = await apiClient.get('/artworks/search', { params })
      
      const data = response.data
      artworks.value = data.artworks || data
      totalPages.value = data.total_pages || 1
      hasMore.value = data.has_more !== false
      currentPage.value = page
      
      // Cache the result with shorter duration for search
      setCachedData(cacheKey, {
        artworks: artworks.value,
        total_pages: totalPages.value,
        has_more: hasMore.value
      }, SEARCH_CACHE_DURATION)
      
      return data
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Search failed'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      isLoading.value = false
    }
  }, 300) // 300ms debounce

  const searchArtworks = async (query, page = 1, limit = 20) => {
    return debouncedSearch(query, page, limit)
  }

  const fetchArtworkById = async (id) => {
    const cacheKey = `artwork_${id}`
    
    // Check cache first
    if (isCacheValid(cacheKey)) {
      return getCachedData(cacheKey)
    }
    
    return deduplicateRequest(cacheKey, async () => {
      try {
        const response = await apiClient.get(`/artworks/${id}`)
        const artwork = response.data
        
        // Cache the result
        setCachedData(cacheKey, artwork)
        
        return artwork
      } catch (err) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch artwork'
        throw new Error(errorMessage)
      }
    })
  }

  const addFavorite = async (artworkId) => {
    try {
      await apiClient.post(`/artworks/${artworkId}/favorite`)
      favorites.value.add(artworkId)
      
      // Update artwork in list if it exists
      const artworkIndex = artworks.value.findIndex(a => a.id === artworkId)
      if (artworkIndex !== -1) {
        artworks.value[artworkIndex] = { ...artworks.value[artworkIndex], is_favorited: true }
      }
      
      // Invalidate related caches
      cache.clear()
      
      return true
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to add favorite'
      throw new Error(errorMessage)
    }
  }

  const removeFavorite = async (artworkId) => {
    try {
      await apiClient.delete(`/artworks/${artworkId}/favorite`)
      favorites.value.delete(artworkId)
      
      // Update artwork in list if it exists
      const artworkIndex = artworks.value.findIndex(a => a.id === artworkId)
      if (artworkIndex !== -1) {
        artworks.value[artworkIndex] = { ...artworks.value[artworkIndex], is_favorited: false }
      }
      
      // Invalidate related caches
      cache.clear()
      
      return true
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to remove favorite'
      throw new Error(errorMessage)
    }
  }

  const fetchFavorites = async () => {
    const cacheKey = 'favorites'
    
    // Check cache first
    if (isCacheValid(cacheKey)) {
      const cachedData = getCachedData(cacheKey)
      return cachedData
    }
    
    return deduplicateRequest(cacheKey, async () => {
      try {
        isLoading.value = true
        error.value = null
        
        const response = await apiClient.get('/artworks/favorites')
        const favoriteArtworks = response.data.artworks || response.data
        
        // Update favorites set
        favorites.value.clear()
        favoriteArtworks.forEach(artwork => {
          if (artwork.id) {
            favorites.value.add(artwork.id)
          }
        })
        
        // Cache the result
        setCachedData(cacheKey, favoriteArtworks)
        
        return favoriteArtworks
      } catch (err) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch favorites'
        error.value = errorMessage
        throw new Error(errorMessage)
      } finally {
        isLoading.value = false
      }
    })
  }

  // New methods for enhanced functionality
  const likeArtwork = async (artworkId, liked = true) => {
    try {
      if (liked) {
        await apiClient.post(`/artworks/${artworkId}/like`)
        favorites.value.add(artworkId)
      } else {
        await apiClient.delete(`/artworks/${artworkId}/like`)
        favorites.value.delete(artworkId)
      }
      
      // Update artwork in list if it exists
      const artworkIndex = artworks.value.findIndex(a => a.id === artworkId)
      if (artworkIndex !== -1) {
        artworks.value[artworkIndex] = { ...artworks.value[artworkIndex], is_favorited: liked }
      }
      
      return true
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to update like status'
      throw new Error(errorMessage)
    }
  }

  const loadLikedArtworks = async (filters = {}) => {
    try {
      const response = await apiClient.get('/artworks/liked', { params: filters })
      const likedArtworks = response.data.artworks || response.data
      
      // Update artworks list
      artworks.value = likedArtworks
      
      // Update favorites set
      favorites.value.clear()
      likedArtworks.forEach(artwork => {
        if (artwork.id) {
          favorites.value.add(artwork.id)
        }
      })
      
      return likedArtworks
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load liked artworks'
      error.value = errorMessage
      throw new Error(errorMessage)
    }
  }

  const getGalleryArtworks = async (params = {}) => {
    try {
      const response = await apiClient.get('/artworks/gallery', { params })
      return response.data
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to get gallery artworks'
      error.value = errorMessage
      throw new Error(errorMessage)
    }
  }

  const getLikedArtworksFilterOptions = async () => {
    try {
      const response = await apiClient.get('/artworks/liked/filters')
      return response.data
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to get filter options'
      throw new Error(errorMessage)
    }
  }

  const resetPagination = () => {
    currentPage.value = 1
    totalPages.value = 1
    hasMore.value = true
  }

  const refreshArtworks = async () => {
    clearCache()
    resetPagination()
    return await fetchArtworks(1, 20)
  }

  // Performance monitoring
  const getCacheStats = () => {
    return {
      cacheSize: cache.size(),
      lastFetch: lastFetchTime.value,
      pendingRequests: pendingRequests.size
    }
  }

  return {
    // State
    artworks,
    favorites,
    isLoading,
    error,
    currentPage,
    totalPages,
    hasMore,
    
    // Computed
    favoriteArtworks,
    isFavorited,
    
    // Actions
    fetchArtworks,
    fetchMoreArtworks,
    searchArtworks,
    fetchArtworkById,
    addFavorite,
    removeFavorite,
    fetchFavorites,
    likeArtwork,
    loadLikedArtworks,
    getGalleryArtworks,
    getLikedArtworksFilterOptions,
    resetPagination,
    refreshArtworks,
    clearError,
    clearCache,
    getCacheStats
  }
}) 