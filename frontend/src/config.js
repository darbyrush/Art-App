// Configuration for the application
// Updated for Railway backend deployment - Force Vercel redeploy
export const config = {
  // API base URL - use Railway backend URL
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'https://art-app-production.up.railway.app',
  
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
  // Force production API URL if not set
  if (!import.meta.env.VITE_API_BASE_URL) {
    config.apiBaseUrl = 'https://art-app-production.up.railway.app'
  }
}

// Debug logging (only in development)
if (import.meta.env.DEV) {
  console.log('Environment:', import.meta.env.MODE)
  console.log('API Base URL:', config.apiBaseUrl)
  console.log('VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL)
} 