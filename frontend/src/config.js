// Configuration for different environments
const config = {
  development: {
    apiUrl: 'http://localhost:8000'
  },
  production: {
    apiUrl: process.env.VITE_API_URL || 'https://your-backend-url.railway.app'
  }
}

const environment = import.meta.env.MODE || 'development'
export const API_BASE_URL = config[environment].apiUrl 