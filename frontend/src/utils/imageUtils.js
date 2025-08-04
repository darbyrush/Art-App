/**
 * Image utility functions for standardizing artwork images
 */

// Standard image dimensions for consistent display
export const IMAGE_SIZES = {
  THUMBNAIL: { width: 300, height: 300 },
  MEDIUM: { width: 600, height: 600 },
  LARGE: { width: 800, height: 800 },
  GALLERY: { width: 400, height: 400 },
  FEED: { width: 600, height: 500 }
}

/**
 * Standardize image URL to ensure consistent sizing
 * @param {string} originalUrl - Original image URL
 * @param {string} size - Size key from IMAGE_SIZES
 * @returns {string} - Standardized image URL
 */
export function standardizeImageUrl(originalUrl, size = 'MEDIUM') {
  if (!originalUrl) return null
  
  const dimensions = IMAGE_SIZES[size]
  
  // Handle different image URL patterns
  if (originalUrl.includes('images.metmuseum.org')) {
    // Met Museum images
    return originalUrl.replace(/\/full\//, `/${dimensions.width},${dimensions.height}/`)
  } else if (originalUrl.includes('clevelandart.org')) {
    // Cleveland Museum images
    return originalUrl.replace(/\/full\//, `/${dimensions.width}x${dimensions.height}/`)
  } else if (originalUrl.includes('artic.edu')) {
    // Art Institute of Chicago images
    return originalUrl.replace(/\/full\//, `/${dimensions.width},${dimensions.height}/`)
  } else if (originalUrl.includes('harvardartmuseums.org')) {
    // Harvard Art Museums images
    return originalUrl.replace(/\/full\//, `/${dimensions.width}x${dimensions.height}/`)
  } else if (originalUrl.includes('si.edu')) {
    // Smithsonian images
    return originalUrl.replace(/\/full\//, `/${dimensions.width}x${dimensions.height}/`)
  } else if (originalUrl.includes('nga.gov')) {
    // National Gallery of Art images
    return originalUrl.replace(/\/full\//, `/${dimensions.width}x${dimensions.height}/`)
  } else if (originalUrl.includes('thewalters.org')) {
    // Walters Art Museum images
    return originalUrl.replace(/\/full\//, `/${dimensions.width}x${dimensions.height}/`)
  }
  
  // Default: return original URL if no pattern matches
  return originalUrl
}

/**
 * Get optimized image URL for different use cases
 * @param {string} originalUrl - Original image URL
 * @param {string} useCase - 'thumbnail', 'gallery', 'detail', 'full'
 * @returns {string} - Optimized image URL
 */
export function getOptimizedImageUrl(originalUrl, useCase = 'gallery') {
  const sizeMap = {
    'thumbnail': 'THUMBNAIL',
    'gallery': 'GALLERY',
    'detail': 'MEDIUM',
    'full': 'LARGE',
    'feed': 'FEED'
  }
  
  const size = sizeMap[useCase] || 'MEDIUM'
  return standardizeImageUrl(originalUrl, size)
}

/**
 * Check if image URL is valid and accessible
 * @param {string} url - Image URL to check
 * @returns {Promise<boolean>} - Whether image is accessible
 */
export async function isImageAccessible(url) {
  if (!url) return false
  
  try {
    const response = await fetch(url, { method: 'HEAD' })
    return response.ok
  } catch (error) {
    console.warn('Image accessibility check failed:', error)
    return false
  }
}

/**
 * Get fallback image URL if original fails
 * @param {string} source - Art source name
 * @returns {string} - Fallback image URL
 */
export function getFallbackImageUrl(source) {
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  
  const fallbackImages = {
    'met': `${API_BASE_URL}/placeholder/met.jpg`,
    'cleveland': `${API_BASE_URL}/placeholder/cleveland.jpg`,
    'chicago': `${API_BASE_URL}/placeholder/chicago.jpg`,
    'harvard': `${API_BASE_URL}/placeholder/harvard.jpg`,
    'smithsonian': `${API_BASE_URL}/placeholder/smithsonian.jpg`,
    'national_gallery': `${API_BASE_URL}/placeholder/nga.jpg`,
    'walters': `${API_BASE_URL}/placeholder/walters.jpg`
  }
  
  return fallbackImages[source] || `${API_BASE_URL}/placeholder/default.jpg`
}

/**
 * Create image loading state
 * @param {string} url - Image URL
 * @param {string} alt - Image alt text
 * @param {string} useCase - Image use case
 * @returns {Object} - Image object with loading state
 */
export function createImageObject(url, alt, useCase = 'gallery') {
  return {
    originalUrl: url,
    optimizedUrl: getOptimizedImageUrl(url, useCase),
    fallbackUrl: getFallbackImageUrl(alt),
    alt: alt,
    loading: true,
    error: false,
    loaded: false
  }
} 