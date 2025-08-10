import { ref, onMounted } from 'vue'

export function usePerformance() {
  const metrics = ref({
    fcp: 0,
    lcp: 0,
    fid: 0,
    cls: 0
  })
  
  const isSlowConnection = ref(false)
  
  onMounted(() => {
    // Check connection speed
    if ('connection' in navigator) {
      const connection = navigator.connection
      isSlowConnection.value = connection.effectiveType === 'slow-2g' || 
                               connection.effectiveType === '2g' ||
                               connection.effectiveType === '3g'
    }
    
    // Monitor performance metrics
    if ('PerformanceObserver' in window) {
      // First Contentful Paint
      const fcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        if (entries.length > 0) {
          metrics.value.fcp = entries[0].startTime
        }
      })
      fcpObserver.observe({ entryTypes: ['paint'] })
      
      // Largest Contentful Paint
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        if (entries.length > 0) {
          metrics.value.lcp = entries[entries.length - 1].startTime
        }
      })
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] })
      
      // First Input Delay
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        if (entries.length > 0) {
          metrics.value.fid = entries[0].processingStart - entries[0].startTime
        }
      })
      fidObserver.observe({ entryTypes: ['first-input'] })
      
      // Cumulative Layout Shift
      const clsObserver = new PerformanceObserver((list) => {
        let clsValue = 0
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) {
            clsValue += entry.value
          }
        }
        metrics.value.cls = clsValue
      })
      clsObserver.observe({ entryTypes: ['layout-shift'] })
    }
  })
  
  const logPerformance = () => {
    console.log('Performance Metrics:', metrics.value)
    console.log('Slow Connection:', isSlowConnection.value)
  }
  
  return {
    metrics,
    isSlowConnection,
    logPerformance
  }
}
