// API Configuration
export const API_BASE_URL = 'http://localhost:8000'

// Frontend Configuration
export const FRONTEND_URL = 'http://localhost:5173'

// CORS Configuration
export const CORS_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://localhost:3002',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
    'http://127.0.0.1:3002',
    'http://127.0.0.1:5173'
]

// Debug: Log the API URL being used
console.log('API Base URL:', API_BASE_URL)
console.log('Frontend URL:', FRONTEND_URL) 