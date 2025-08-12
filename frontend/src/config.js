// Configuration for the application
// OPTIMIZED: Vercel-Railway Native Connection
// Version: 2024-01-XX - Railway Backend Integration
export const config = {
  // API base URL - prioritize Vercel-Railway native connection
  apiBaseUrl: import.meta.env.VERCEL_RAILWAY_URL || 
               import.meta.env.RAILWAY_URL ||
               import.meta.env.VITE_API_BASE_URL ||
               'https://art-app-production.up.railway.app',
  
  // App settings
  appName: 'Art Explorer',
  version: '1.0.0',
  
  // Feature flags
  features: {
    imageOptimization: true,
    virtualScrolling: true,
    keyboardShortcuts: true
  }
}

// Environment-specific overrides
if (import.meta.env.PROD) {
  // Production settings
  config.features.imageOptimization = true
  config.features.virtualScrolling = true
  
  // Vercel-Railway native connection priority
  if (import.meta.env.VERCEL_RAILWAY_URL) {
    config.apiBaseUrl = import.meta.env.VERCEL_RAILWAY_URL
    console.log('🚀 Using Vercel-Railway native connection')
  } else if (import.meta.env.RAILWAY_URL) {
    config.apiBaseUrl = import.meta.env.RAILWAY_URL
    console.log('🚂 Using Railway direct connection')
  } else if (import.meta.env.VITE_API_BASE_URL) {
    config.apiBaseUrl = import.meta.env.VITE_API_BASE_URL
    console.log('🔗 Using custom API base URL')
  } else {
    config.apiBaseUrl = 'https://art-app-production.up.railway.app'
    console.log('🌐 Using fallback Railway URL')
  }
}

// Debug logging (only in development)
if (import.meta.env.DEV) {
  console.log('Environment:', import.meta.env.MODE)
  console.log('API Base URL:', config.apiBaseUrl)
  console.log('VERCEL_RAILWAY_URL:', import.meta.env.VERCEL_RAILWAY_URL)
  console.log('RAILWAY_URL:', import.meta.env.RAILWAY_URL)
  console.log('VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL)
} 