/**
 * Advanced Image Utilities for Art Explorer
 * Uses optimized backend endpoints for better performance
 */

// Standard image dimensions for consistent display
export const IMAGE_SIZES = {
  THUMBNAIL: { width: 200, height: 200 },
  MEDIUM: { width: 400, height: 400 },
  LARGE: { width: 800, height: 800 },
  GALLERY: { width: 400, height: 400 },
  FEED: { width: 300, height: 300 }
}

// Image loading states
export const IMAGE_STATES = {
  LOADING: 'loading',
  LOADED: 'loaded',
  ERROR: 'error',
  FALLBACK: 'fallback'
}

// API base URL
const API_BASE_URL = 'http://localhost:8001'

// Image validation cache
const imageValidationCache = new Map()
const imageLoadCache = new Map()

/**
 * Get optimized image URL from backend
 * @param {string} originalUrl - Original image URL
 * @param {string} useCase - 'thumbnail', 'gallery', 'detail', 'full'
 * @returns {string} - Optimized image URL
 */
export function getOptimizedImageUrl(originalUrl, useCase = 'gallery') {
  if (!originalUrl) {
    return getFallbackImageUrl('default')
  }
  
  // Use cached image endpoint instead of optimize
  const encodedUrl = encodeURIComponent(originalUrl)
  return `${API_BASE_URL}/images/cached/${encodedUrl}`
}

/**
 * Get fallback image URL with optimization
 * @param {string} source - Art source name
 * @param {string} style - 'modern', 'minimal', 'classic'
 * @returns {string} - Optimized fallback image URL
 */
export function getFallbackImageUrl(source, style = 'modern') {
  const params = new URLSearchParams({
    width: 400,
    height: 400,
    style: style
  })
  
  return `${API_BASE_URL}/images/placeholder/${source}?${params.toString()}`
}

/**
 * Progressive image loading with multiple fallback strategies
 * @param {string} originalUrl - Original image URL
 * @param {string} source - Art source name
 * @param {string} useCase - Image use case
 * @returns {Promise<Object>} - Image loading result
 */
export async function loadImageWithFallback(originalUrl, source, useCase = 'gallery') {
  const cacheKey = `${originalUrl}:${useCase}`
  
  // Check cache first
  if (imageLoadCache.has(cacheKey)) {
    return imageLoadCache.get(cacheKey)
  }
  
  const result = {
    state: IMAGE_STATES.LOADING,
    url: null,
    error: null,
    optimized: false
  }
  
  try {
    // Try optimized image first
    const optimizedUrl = getOptimizedImageUrl(originalUrl, useCase)
    const optimizedImage = await loadImage(optimizedUrl)
    
    if (optimizedImage.success) {
      result.state = IMAGE_STATES.LOADED
      result.url = optimizedUrl
      result.optimized = true
    } else {
      // Try original URL
      const originalImage = await loadImage(originalUrl)
      
      if (originalImage.success) {
        result.state = IMAGE_STATES.LOADED
        result.url = originalUrl
      } else {
        // Use fallback
        const fallbackUrl = getFallbackImageUrl(source)
        const fallbackImage = await loadImage(fallbackUrl)
        
        if (fallbackImage.success) {
          result.state = IMAGE_STATES.FALLBACK
          result.url = fallbackUrl
        } else {
          result.state = IMAGE_STATES.ERROR
          result.error = 'All image loading strategies failed'
        }
      }
    }
  } catch (error) {
    result.state = IMAGE_STATES.ERROR
    result.error = error.message
  }
  
  // Cache result
  imageLoadCache.set(cacheKey, result)
  return result
}

/**
 * Load image with timeout and error handling
 * @param {string} url - Image URL
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Promise<Object>} - Loading result
 */
async function loadImage(url, timeout = 10000) {
  return new Promise((resolve) => {
    const img = new Image()
    const timer = setTimeout(() => {
      img.src = ''
      resolve({ success: false, error: 'Timeout' })
    }, timeout)
    
    img.onload = () => {
      clearTimeout(timer)
      resolve({ success: true })
    }
    
    img.onerror = () => {
      clearTimeout(timer)
      resolve({ success: false, error: 'Load failed' })
    }
    
    img.src = url
  })
}

/**
 * Validate image URL accessibility
 * @param {string} url - Image URL to validate
 * @returns {Promise<boolean>} - Whether image is accessible
 */
export async function validateImageUrl(url) {
  // Check cache first
  if (imageValidationCache.has(url)) {
    return imageValidationCache.get(url)
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/images/info?url=${encodeURIComponent(url)}`)
    const info = await response.json()
    
    const isValid = !info.error && info.width && info.height
    imageValidationCache.set(url, isValid)
    return isValid
  } catch (error) {
    console.warn('Image validation failed:', error)
    imageValidationCache.set(url, false)
    return false
  }
}

/**
 * Validate multiple image URLs
 * @param {Array<string>} urls - Array of image URLs
 * @returns {Promise<Object>} - Validation results
 */
export async function validateMultipleImages(urls) {
  try {
    const response = await fetch(`${API_BASE_URL}/images/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(urls)
    })
    return await response.json()
  } catch (error) {
    console.error('Batch image validation failed:', error)
    return {}
  }
}

/**
 * Clear image caches
 */
export function clearImageCaches() {
  imageValidationCache.clear()
  imageLoadCache.clear()
}

/**
 * Get image loading statistics
 * @returns {Object} - Cache statistics
 */
export function getImageCacheStats() {
  return {
    validationCacheSize: imageValidationCache.size,
    loadCacheSize: imageLoadCache.size
  }
} 