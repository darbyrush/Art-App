import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

// Import Vercel Analytics for mobile debugging
import { inject, track } from '@vercel/analytics'

const app = createApp(App)

// Initialize Vercel Analytics
inject()

// Add global error handler for Vue
app.config.errorHandler = (error, instance, info) => {
  // Track errors with Vercel Analytics
  track('vue_error', {
    error: error.message || error.toString(),
    component: instance?.$options?.name || 'unknown',
    info: info,
    stack: error?.stack,
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString()
  });
  
  // Log to console in development
  if (import.meta.env.DEV) {
    console.error('🚨 Vue Global Error:', error, instance, info);
  }
}

app.use(createPinia())
app.use(router)

// Add performance monitoring with Vercel Analytics
if ('performance' in window) {
  // Monitor page load performance
  window.addEventListener('load', () => {
    const perf = performance.getEntriesByType('navigation')[0];
    if (perf) {
      track('performance_metric', {
        name: 'Page Load Complete',
        value: perf.loadEventEnd - perf.loadEventStart,
        unit: 'ms'
      });
      
      track('performance_metric', {
        name: 'DOM Content Loaded',
        value: perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart,
        unit: 'ms'
      });
    }
    
    // Monitor Core Web Vitals
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.name === 'first-paint') {
              track('performance_metric', {
                name: 'First Paint',
                value: entry.startTime,
                unit: 'ms'
              });
            }
            if (entry.name === 'first-contentful-paint') {
              track('performance_metric', {
                name: 'First Contentful Paint',
                value: entry.startTime,
                unit: 'ms'
              });
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

// Monitor unhandled errors with Vercel Analytics
window.addEventListener('error', (event) => {
  track('window_error', {
    error: event.error?.message || event.message || 'Unknown error',
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    stack: event.error?.stack,
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString()
  });
});

// Monitor unhandled promise rejections with Vercel Analytics
window.addEventListener('unhandledrejection', (event) => {
  track('unhandled_promise_rejection', {
    error: event.reason?.message || event.reason?.toString() || 'Unknown rejection',
    stack: event.reason?.stack,
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString()
  });
});

// Monitor network status changes
window.addEventListener('offline', () => {
  track('network_status', { status: 'offline' });
});

window.addEventListener('online', () => {
  track('network_status', { status: 'online' });
});

// Monitor page visibility changes
document.addEventListener('visibilitychange', () => {
  track('page_visibility', { 
    hidden: document.hidden,
    url: window.location.href
  });
});

// Monitor beforeunload (user leaving page)
window.addEventListener('beforeunload', () => {
  track('page_unload', { 
    url: window.location.href,
    timestamp: new Date().toISOString()
  });
});

app.mount('#app')

// Export for debugging
if (import.meta.env.DEV) {
  window.vercelTrack = track;
  console.log('🔍 Vercel Analytics initialized. Access via window.vercelTrack');
} 