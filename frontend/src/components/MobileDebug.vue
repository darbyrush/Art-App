<template>
  <div class="mobile-debug bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
    <h3 class="text-lg font-semibold text-yellow-800 mb-2">🐛 Mobile Debug Info</h3>
    
    <div class="space-y-2 text-sm">
      <div><strong>User Agent:</strong> {{ userAgent }}</div>
      <div><strong>Screen Size:</strong> {{ screenSize }}</div>
      <div><strong>Viewport:</strong> {{ viewport }}</div>
      <div><strong>Touch Support:</strong> {{ touchSupport }}</div>
      <div><strong>Platform:</strong> {{ platform }}</div>
      <div><strong>Connection:</strong> {{ connection }}</div>
    </div>
    
    <div class="mt-4">
      <button 
        @click="testAuth" 
        class="btn-primary text-sm"
        :disabled="testing"
      >
        {{ testing ? 'Testing...' : 'Test Auth Endpoints' }}
      </button>
    </div>
    
    <div v-if="authTestResult" class="mt-4 p-3 bg-gray-100 rounded text-sm">
      <h4 class="font-semibold mb-2">Auth Test Results:</h4>
      <pre class="whitespace-pre-wrap">{{ authTestResult }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiClient } from '@/utils/apiClient'

const userAgent = ref('')
const screenSize = ref('')
const viewport = ref('')
const touchSupport = ref('')
const platform = ref('')
const connection = ref('')
const testing = ref(false)
const authTestResult = ref('')

onMounted(() => {
  // Get device info
  userAgent.value = navigator.userAgent
  screenSize.value = `${screen.width}x${screen.height}`
  viewport.value = `${window.innerWidth}x${window.innerHeight}`
  touchSupport.value = 'ontouchstart' in window ? 'Yes' : 'No'
  platform.value = navigator.platform
  
  // Get connection info
  if (navigator.connection) {
    connection.value = `${navigator.connection.effectiveType || 'unknown'} (${navigator.connection.downlink || 'unknown'} Mbps)`
  } else {
    connection.value = 'Not available'
  }
})

const testAuth = async () => {
  testing.value = true
  authTestResult.value = ''
  
  try {
    const results = []
    
    // Test 1: Check if we can reach the API
    try {
      const healthResponse = await apiClient.get('/health')
      results.push(`✅ Health check: ${healthResponse.status} - ${JSON.stringify(healthResponse.data)}`)
    } catch (error) {
      results.push(`❌ Health check failed: ${error.message}`)
    }
    
    // Test 2: Test CORS preflight
    try {
      const optionsResponse = await fetch('https://art-app-production.up.railway.app/auth/register', {
        method: 'OPTIONS',
        headers: {
          'Origin': window.location.origin,
          'Access-Control-Request-Method': 'POST',
          'Access-Control-Request-Headers': 'Content-Type'
        }
      })
      results.push(`✅ CORS preflight: ${optionsResponse.status}`)
    } catch (error) {
      results.push(`❌ CORS preflight failed: ${error.message}`)
    }
    
    // Test 3: Test registration endpoint
    try {
      const testUsername = `debug_${Date.now()}`
      const registerResponse = await apiClient.post('/auth/register', {
        username: testUsername,
        password: 'debugpass123'
      })
      results.push(`✅ Registration: ${registerResponse.status} - User: ${testUsername}`)
      
      // Test 4: Test login with the created user
      try {
        const loginResponse = await apiClient.post('/auth/login', 
          `username=${testUsername}&password=debugpass123`,
          {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            }
          }
        )
        results.push(`✅ Login: ${loginResponse.status} - Token: ${loginResponse.data.access_token ? 'Received' : 'Missing'}`)
      } catch (error) {
        results.push(`❌ Login failed: ${error.message}`)
      }
      
    } catch (error) {
      results.push(`❌ Registration failed: ${error.message}`)
    }
    
    authTestResult.value = results.join('\n')
    
  } catch (error) {
    authTestResult.value = `❌ Test failed: ${error.message}`
  } finally {
    testing.value = false
  }
}
</script>

<style scoped>
.mobile-debug {
  font-family: 'Courier New', monospace;
}

pre {
  font-size: 11px;
  line-height: 1.3;
}
</style>
