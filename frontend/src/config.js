// Configuration for different environments
const config = {
  development: {
    apiUrl: 'http://localhost:8000'
  },
  production: {
    apiUrl: 'https://art-app-production.up.railway.app'  // Hardcoded for now
  }
}

const environment = import.meta.env.MODE || 'development'
export const API_BASE_URL = config[environment].apiUrl

// Debug: Log the API URL being used
console.log('Environment:', environment)
console.log('API Base URL:', API_BASE_URL)
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL) 