import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

// Import Vercel Analytics for mobile debugging
import { inject } from '@vercel/analytics'

// Import error monitoring
import { errorMonitor } from './utils/errorMonitoring.js'

const app = createApp(App)

// Initialize Vercel Analytics
inject()

// Initialize error monitoring before mounting
errorMonitor.init(app, router)

// Add global error handler for Vue
app.config.errorHandler = (error, instance, info) => {
  errorMonitor.captureError(error, {
    type: 'vue_global_error',
    component: instance?.$options?.name || 'unknown',
    info: info,
    stack: error?.stack,
  });
  
  // Log to console in development
  if (import.meta.env.DEV) {
    console.error('🚨 Vue Global Error:', error, instance, info);
  }
}

// Add global property for error monitoring
app.config.globalProperties.$errorMonitor = errorMonitor

// Add global error boundary wrapper
app.config.globalProperties.$withErrorBoundary = (component) => {
  return {
    components: { ErrorBoundary: () => import('./components/ErrorBoundary.vue') },
    template: `
      <ErrorBoundary>
        <component :is="component" v-bind="$attrs" />
      </ErrorBoundary>
    `,
    setup() {
      return { component }
    }
  }
}

app.use(createPinia())
app.use(router)

// Add performance monitoring
if ('performance' in window) {
  // Monitor page load performance
  window.addEventListener('load', () => {
    const perf = performance.getEntriesByType('navigation')[0];
    if (perf) {
      errorMonitor.capturePerformanceMetric('Page Load Complete', 
        perf.loadEventEnd - perf.loadEventStart);
      
      errorMonitor.capturePerformanceMetric('DOM Content Loaded', 
        perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart);
    }
    
    // Monitor Core Web Vitals
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.name === 'first-paint') {
              errorMonitor.capturePerformanceMetric('First Paint', entry.startTime);
            }
            if (entry.name === 'first-contentful-paint') {
              errorMonitor.capturePerformanceMetric('First Contentful Paint', entry.startTime);
            }
          }
        });
        observer.observe({ entryTypes: ['paint'] });
      } catch (e) {
        console.warn('Performance monitoring not supported:', e);
      }
    }
  });
}

// Monitor unhandled errors
window.addEventListener('error', (event) => {
  errorMonitor.captureError(event.error || event.message, {
    type: 'window_error',
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    stack: event.error?.stack,
  });
});

// Monitor unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  errorMonitor.captureError(event.reason, {
    type: 'unhandled_promise_rejection',
    stack: event.reason?.stack,
  });
});

// Monitor network errors
window.addEventListener('offline', () => {
  errorMonitor.addBreadcrumb('User went offline', 'network', { status: 'offline' });
});

window.addEventListener('online', () => {
  errorMonitor.addBreadcrumb('User came back online', 'network', { status: 'online' });
});

// Monitor visibility changes (user switching tabs)
document.addEventListener('visibilitychange', () => {
  errorMonitor.addBreadcrumb(`Page ${document.hidden ? 'hidden' : 'visible'}`, 'user_behavior');
});

// Monitor beforeunload (user leaving page)
window.addEventListener('beforeunload', () => {
  errorMonitor.addBreadcrumb('User leaving page', 'user_behavior', { 
    url: window.location.href,
    timestamp: new Date().toISOString()
  });
});

app.mount('#app')

// Export for debugging
if (import.meta.env.DEV) {
  window.errorMonitor = errorMonitor;
  console.log('🔍 Error monitoring initialized. Access via window.errorMonitor');
} 