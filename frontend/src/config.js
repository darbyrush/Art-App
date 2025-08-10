// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Frontend Configuration
export const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL || 'http://localhost:5173'

// CORS Configuration
export const CORS_ORIGINS = [
  FRONTEND_URL,
  'http://localhost:3000',
  'http://localhost:3001'
]

// Debug: Log the API URL being used
console.log('API Base URL:', API_BASE_URL)
console.log('Frontend URL:', FRONTEND_URL) 