/**
 * Advanced Image Utilities for Art Explorer
 * Uses optimized backend endpoints for better performance
 */

// Image optimization and utility functions
export const IMAGE_STATES = {
  LOADING: 'loading',
  LOADED: 'loaded',
  ERROR: 'error',
  FALLBACK: 'fallback'
}

// Image cache for performance
const imageCache = new Map()
const CACHE_DURATION = 10 * 60 * 1000 // 10 minutes

// Lazy loading observer
let lazyLoadObserver = null

// Initialize lazy loading observer
const initLazyLoadObserver = () => {
  if (typeof IntersectionObserver === 'undefined') return null
  
  if (!lazyLoadObserver) {
    lazyLoadObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target
          const src = img.dataset.src
          if (src) {
            img.src = src
            img.removeAttribute('data-src')
            lazyLoadObserver.unobserve(img)
          }
        }
      })
    }, {
      rootMargin: '50px 0px',
      threshold: 0.01
    })
  }
  
  return lazyLoadObserver
}

// Get optimized image URL based on context
export const getOptimizedImageUrl = (originalUrl, context = 'default', size = 'medium') => {
  if (!originalUrl) return null
  
  // Handle different image sources and optimization strategies
  if (originalUrl.includes('metmuseum.org')) {
    // Met Museum images can be optimized
    return originalUrl.replace(/\/original\//, '/web-large/')
  }
  
  if (originalUrl.includes('clevelandart.org')) {
    // Cleveland Museum images
    return originalUrl
  }
  
  if (originalUrl.includes('artic.edu')) {
    // Art Institute of Chicago images
    return originalUrl
  }
  
  // Default: return original URL
  return originalUrl
}

// Get fallback image URL for failed loads
export const getFallbackImageUrl = (source = 'default') => {
  const fallbackImages = {
    met: '/images/fallback-met.png',
    cleveland: '/images/fallback-cleveland.png',
    chicago: '/images/fallback-chicago.png',
    walters: '/images/fallback-walters.png',
    national_gallery: '/images/fallback-nga.png',
    smithsonian: '/images/fallback-smithsonian.png',
    harvard: '/images/fallback-harvard.png',
    default: '/images/fallback-default.png'
  }
  
  return fallbackImages[source] || fallbackImages.default
}

// Progressive image loading with fallback
export const loadImageWithFallback = async (originalUrl, source = 'default', context = 'default') => {
  try {
    // Try optimized URL first
    const optimizedUrl = getOptimizedImageUrl(originalUrl, context)
    
    if (await testImageUrl(optimizedUrl)) {
      return {
        state: IMAGE_STATES.LOADED,
        url: optimizedUrl,
        error: null,
        optimized: true
      }
    }
    
    // Fallback to original URL
    if (await testImageUrl(originalUrl)) {
      return {
        state: IMAGE_STATES.LOADED,
        url: originalUrl,
        error: null,
        optimized: false
      }
    }
    
    // Use fallback image
    return {
      state: IMAGE_STATES.FALLBACK,
      url: getFallbackImageUrl(source),
      error: null,
      optimized: false
    }
    
  } catch (error) {
    return {
      state: IMAGE_STATES.ERROR,
      url: getFallbackImageUrl(source),
      error: error.message,
      optimized: false
    }
  }
}

// Test if image URL is accessible
export const testImageUrl = (url) => {
  return new Promise((resolve) => {
    if (!url) {
      resolve(false)
      return
    }
    
    const img = new Image()
    img.onload = () => resolve(true)
    img.onerror = () => resolve(false)
    img.src = url
  })
}

// Preload image for better performance
export const preloadImage = (url, priority = 'low') => {
  if (!url) return Promise.resolve()
  
  return new Promise((resolve, reject) => {
    const img = new Image()
    
    if (priority === 'high') {
      img.fetchPriority = 'high'
    }
    
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = url
  })
}

// Batch preload images
export const preloadImages = async (urls, maxConcurrent = 3) => {
  const results = []
  
  for (let i = 0; i < urls.length; i += maxConcurrent) {
    const batch = urls.slice(i, i + maxConcurrent)
    const batchPromises = batch.map(url => preloadImage(url).catch(() => null))
    const batchResults = await Promise.allSettled(batchPromises)
    results.push(...batchResults)
  }
  
  return results
}

// Lazy load image element
export const lazyLoadImage = (imgElement, src, fallbackSrc = null) => {
  if (!imgElement) return
  
  const observer = initLazyLoadObserver()
  if (!observer) {
    // Fallback for browsers without IntersectionObserver
    imgElement.src = src
    return
  }
  
  // Set placeholder or low-quality image
  if (fallbackSrc) {
    imgElement.src = fallbackSrc
  }
  
  // Set data-src for lazy loading
  imgElement.dataset.src = src
  
  // Observe the image
  observer.observe(imgElement)
}

// Get image dimensions without loading
export const getImageDimensions = (url) => {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      resolve({
        width: img.naturalWidth,
        height: img.naturalHeight,
        aspectRatio: img.naturalWidth / img.naturalHeight
      })
    }
    img.onerror = () => resolve(null)
    img.src = url
  })
}

// Generate responsive image srcset
export const generateSrcSet = (baseUrl, widths = [320, 640, 960, 1280]) => {
  if (!baseUrl) return ''
  
  return widths
    .map(width => `${baseUrl}?w=${width} ${width}w`)
    .join(', ')
}

// Compress image data (for uploads)
export const compressImage = async (file, maxWidth = 1920, quality = 0.8) => {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    const img = new Image()
    
    img.onload = () => {
      // Calculate new dimensions
      let { width, height } = img
      
      if (width > maxWidth) {
        height = (height * maxWidth) / width
        width = maxWidth
      }
      
      canvas.width = width
      canvas.height = height
      
      // Draw and compress
      ctx.drawImage(img, 0, 0, width, height)
      
      canvas.toBlob(resolve, 'image/jpeg', quality)
    }
    
    img.src = URL.createObjectURL(file)
  })
}

// Get cached image data
export const getCachedImage = (key) => {
  const cached = imageCache.get(key)
  if (!cached) return null
  
  const now = Date.now()
  if (now - cached.timestamp > CACHE_DURATION) {
    imageCache.delete(key)
    return null
  }
  
  return cached.data
}

// Set cached image data
export const setCachedImage = (key, data) => {
  imageCache.set(key, {
    data,
    timestamp: Date.now()
  })
}

// Clear image cache
export const clearImageCache = () => {
  imageCache.clear()
}

// Get image loading state
export const getImageLoadingState = (url) => {
  if (!url) return IMAGE_STATES.ERROR
  
  const cached = getCachedImage(url)
  if (cached) return IMAGE_STATES.LOADED
  
  return IMAGE_STATES.LOADING
}

// Utility function to check if image is in viewport
export const isImageInViewport = (element) => {
  if (!element) return false
  
  const rect = element.getBoundingClientRect()
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  )
}

// Debounced image loading for performance
export const debouncedImageLoad = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Export utility functions
export default {
  IMAGE_STATES,
  getOptimizedImageUrl,
  getFallbackImageUrl,
  loadImageWithFallback,
  testImageUrl,
  preloadImage,
  preloadImages,
  lazyLoadImage,
  getImageDimensions,
  generateSrcSet,
  compressImage,
  getCachedImage,
  setCachedImage,
  clearImageCache,
  getImageLoadingState,
  isImageInViewport,
  debouncedImageLoad
} 