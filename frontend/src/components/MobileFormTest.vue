<template>
  <div class="mobile-form-test bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
    <h3 class="text-lg font-semibold text-blue-800 mb-2">📱 Mobile Form Test</h3>
    
    <form @submit.prevent="testFormSubmission" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-blue-700">Test Username:</label>
        <input
          v-model="testForm.username"
          type="text"
          class="mt-1 block w-full px-3 py-2 border border-blue-300 rounded-md"
          placeholder="Enter test username"
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-blue-700">Test Password:</label>
        <input
          v-model="testForm.password"
          type="password"
          class="mt-1 block w-full px-3 py-2 border border-blue-300 rounded-md"
          placeholder="Enter test password"
        />
      </div>
      
      <button type="submit" class="btn-primary text-sm">
        Test Form Submission
      </button>
    </form>
    
    <div v-if="testResults.length > 0" class="mt-4">
      <h4 class="font-semibold mb-2">Test Results:</h4>
      <div class="space-y-2">
        <div 
          v-for="(result, index) in testResults" 
          :key="index"
          :class="result.success ? 'text-green-700' : 'text-red-700'"
          class="text-sm p-2 rounded border"
        >
          {{ result.message }}
        </div>
      </div>
    </div>
    
    <div class="mt-4 text-xs text-gray-600">
      <p><strong>Form Data:</strong> {{ JSON.stringify(testForm) }}</p>
      <p><strong>Submit Event:</strong> {{ submitEventInfo }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const testForm = ref({
  username: '',
  password: ''
})

const testResults = ref([])
const submitEventInfo = ref('')

const testFormSubmission = async (event) => {
  submitEventInfo.value = `Event type: ${event.type}, Target: ${event.target.tagName}`
  
  // Test 1: Basic form validation
  if (!testForm.value.username || !testForm.value.password) {
    testResults.value.push({
      success: false,
      message: '❌ Form validation failed - missing fields'
    })
    return
  }
  
  testResults.value.push({
    success: true,
    message: '✅ Form validation passed'
  })
  
  // Test 2: Form data structure
  const formData = new FormData(event.target)
  const formDataObj = {}
  for (let [key, value] of formData.entries()) {
    formDataObj[key] = value
  }
  
  testResults.value.push({
    success: true,
    message: `✅ FormData captured: ${JSON.stringify(formDataObj)}`
  })
  
  // Test 3: Test API call simulation
  try {
    // Simulate the exact request the auth store would make
    const formDataEncoded = new URLSearchParams()
    formDataEncoded.append('username', testForm.value.username)
    formDataEncoded.append('password', testForm.value.password)
    
    testResults.value.push({
      success: true,
      message: `✅ Form data encoded: ${formDataEncoded.toString()}`
    })
    
    // Test actual API call
    const response = await fetch('https://art-app-production.up.railway.app/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Origin': window.location.origin
      },
      body: JSON.stringify({
        username: `test_${Date.now()}`,
        password: 'testpass123'
      })
    })
    
    if (response.ok) {
      testResults.value.push({
        success: true,
        message: `✅ API call successful: ${response.status}`
      })
    } else {
      testResults.value.push({
        success: false,
        message: `❌ API call failed: ${response.status} - ${response.statusText}`
      })
    }
    
  } catch (error) {
    testResults.value.push({
      success: false,
      message: `❌ API call error: ${error.message}`
    })
  }
  
  // Test 4: Mobile-specific checks
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  const hasTouch = 'ontouchstart' in window
  
  testResults.value.push({
    success: true,
    message: `📱 Mobile detection: ${isMobile ? 'Yes' : 'No'}, Touch: ${hasTouch ? 'Yes' : 'No'}`
  })
  
  // Test 5: Viewport and screen info
  const viewport = `${window.innerWidth}x${window.innerHeight}`
  const screen = `${screen.width}x${screen.height}`
  
  testResults.value.push({
    success: true,
    message: `📐 Viewport: ${viewport}, Screen: ${screen}`
  })
}
</script>
