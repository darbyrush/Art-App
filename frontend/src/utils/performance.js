// Performance optimization utilities

// Debounce function calls
export const debounce = (func, wait, immediate = false) => {
  let timeout
  
  return function executedFunction(...args) {
    const later = () => {
      timeout = null
      if (!immediate) func(...args)
    }
    
    const callNow = immediate && !timeout
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    
    if (callNow) func(...args)
  }
}

// Throttle function calls
export const throttle = (func, limit) => {
  let inThrottle
  
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// Request animation frame wrapper
export const rafThrottle = (func) => {
  let ticking = false
  
  return function executedFunction(...args) {
    if (!ticking) {
      requestAnimationFrame(() => {
        func.apply(this, args)
        ticking = false
      })
      ticking = true
    }
  }
}

// Intersection Observer wrapper for lazy loading
export const createIntersectionObserver = (callback, options = {}) => {
  if (typeof IntersectionObserver === 'undefined') {
    return null
  }
  
  const defaultOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1,
    ...options
  }
  
  return new IntersectionObserver(callback, defaultOptions)
}

// Virtual scrolling helper
export const createVirtualScroller = (itemHeight, containerHeight, overscan = 5) => {
  return {
    getVisibleRange(scrollTop, itemCount) {
      const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan)
      const endIndex = Math.min(
        itemCount - 1,
        Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
      )
      
      return { startIndex, endIndex }
    },
    
    getTotalHeight(itemCount) {
      return itemCount * itemHeight
    },
    
    getItemOffset(index) {
      return index * itemHeight
    }
  }
}

// Memory management utilities
export const createWeakCache = () => {
  return new WeakMap()
}

export const createLRUCache = (maxSize = 100) => {
  const cache = new Map()
  
  return {
    get(key) {
      if (cache.has(key)) {
        const value = cache.get(key)
        cache.delete(key)
        cache.set(key, value)
        return value
      }
      return null
    },
    
    set(key, value) {
      if (cache.has(key)) {
        cache.delete(key)
      } else if (cache.size >= maxSize) {
        const firstKey = cache.keys().next().value
        cache.delete(firstKey)
      }
      cache.set(key, value)
    },
    
    clear() {
      cache.clear()
    },
    
    size() {
      return cache.size
    }
  }
}

// Performance monitoring
export const createPerformanceMonitor = () => {
  const metrics = {
    renderTimes: [],
    apiCallTimes: [],
    memoryUsage: []
  }
  
  return {
    startTimer() {
      return performance.now()
    },
    
    endTimer(startTime) {
      return performance.now() - startTime
    },
    
    measureRenderTime(componentName, renderTime) {
      metrics.renderTimes.push({
        component: componentName,
        time: renderTime,
        timestamp: Date.now()
      })
      
      // Keep only last 100 measurements
      if (metrics.renderTimes.length > 100) {
        metrics.renderTimes.shift()
      }
    },
    
    measureApiCallTime(endpoint, callTime) {
      metrics.apiCallTimes.push({
        endpoint,
        time: callTime,
        timestamp: Date.now()
      })
      
      if (metrics.apiCallTimes.length > 100) {
        metrics.apiCallTimes.shift()
      }
    },
    
    getMetrics() {
      return {
        ...metrics,
        averageRenderTime: this.calculateAverage(metrics.renderTimes.map(m => m.time)),
        averageApiCallTime: this.calculateAverage(metrics.apiCallTimes.map(m => m.time))
      }
    },
    
    calculateAverage(values) {
      if (values.length === 0) return 0
      return values.reduce((sum, val) => sum + val, 0) / values.length
    },
    
    clearMetrics() {
      metrics.renderTimes = []
      metrics.apiCallTimes = []
      metrics.memoryUsage = []
    }
  }
}

// Image optimization helpers
export const createImageOptimizer = () => {
  return {
    // Generate responsive image sizes
    generateSizes(baseUrl, sizes = [320, 640, 960, 1280]) {
      return sizes.map(size => ({
        width: size,
        url: `${baseUrl}?w=${size}`,
        descriptor: `${size}w`
      }))
    },
    
    // Create srcset string
    createSrcSet(sizes) {
      return sizes.map(size => `${size.url} ${size.descriptor}`).join(', ')
    },
    
    // Preload critical images
    preloadImages(urls, priority = 'low') {
      urls.forEach(url => {
        const link = document.createElement('link')
        link.rel = 'preload'
        link.as = 'image'
        link.href = url
        if (priority === 'high') {
          link.fetchPriority = 'high'
        }
        document.head.appendChild(link)
      })
    }
  }
}

// Component performance wrapper
export const withPerformanceTracking = (component, options = {}) => {
  const monitor = createPerformanceMonitor()
  
  return {
    ...component,
    mounted() {
      if (component.mounted) {
        const startTime = monitor.startTimer()
        component.mounted.call(this)
        const renderTime = monitor.endTimer(startTime)
        monitor.measureRenderTime(component.name || 'Unknown', renderTime)
      }
    },
    
    updated() {
      if (component.updated) {
        const startTime = monitor.startTimer()
        component.updated.call(this)
        const renderTime = monitor.endTimer(startTime)
        monitor.measureRenderTime(component.name || 'Unknown', renderTime)
      }
    }
  }
}

// Bundle size analyzer
export const analyzeBundleSize = () => {
  if (typeof window !== 'undefined' && window.performance && window.performance.memory) {
    const memory = window.performance.memory
    return {
      usedJSHeapSize: memory.usedJSHeapSize,
      totalJSHeapSize: memory.totalJSHeapSize,
      jsHeapSizeLimit: memory.jsHeapSizeLimit,
      usagePercentage: (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100
    }
  }
  return null
}

// Network performance monitoring
export const createNetworkMonitor = () => {
  const metrics = {
    requests: [],
    errors: []
  }
  
  return {
    trackRequest(url, method, startTime) {
      const request = {
        url,
        method,
        startTime,
        endTime: null,
        duration: null,
        status: null,
        success: false
      }
      
      metrics.requests.push(request)
      return request
    },
    
    completeRequest(request, endTime, status) {
      request.endTime = endTime
      request.duration = endTime - request.startTime
      request.status = status
      request.success = status >= 200 && status < 300
    },
    
    trackError(url, method, error) {
      metrics.errors.push({
        url,
        method,
        error: error.message,
        timestamp: Date.now()
      })
    },
    
    getNetworkMetrics() {
      const successfulRequests = metrics.requests.filter(r => r.success)
      const failedRequests = metrics.requests.filter(r => !r.success)
      
      return {
        totalRequests: metrics.requests.length,
        successfulRequests: successfulRequests.length,
        failedRequests: failedRequests.length,
        averageResponseTime: this.calculateAverage(successfulRequests.map(r => r.duration)),
        errorRate: metrics.errors.length / metrics.requests.length
      }
    },
    
    calculateAverage(values) {
      if (values.length === 0) return 0
      return values.reduce((sum, val) => sum + val, 0) / values.length
    }
  }
}

// Export all utilities
export default {
  debounce,
  throttle,
  rafThrottle,
  createIntersectionObserver,
  createVirtualScroller,
  createWeakCache,
  createLRUCache,
  createPerformanceMonitor,
  createImageOptimizer,
  withPerformanceTracking,
  analyzeBundleSize,
  createNetworkMonitor
}
