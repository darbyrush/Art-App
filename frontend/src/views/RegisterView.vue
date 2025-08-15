<template>
  <div class="min-h-screen bg-art-cream flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="text-center">
          <h1 class="text-4xl font-serif font-bold text-gray-900 mb-2">🎨 My Assemblage</h1>
          <h2 class="text-2xl font-semibold text-gray-900">Create your account</h2>
          <p class="mt-2 text-sm text-gray-600">
            Or
            <router-link to="/login" class="font-medium text-primary-600 hover:text-primary-500">
              sign in to your existing account
            </router-link>
          </p>
        </div>
      </div>
      
      <!-- Mobile Debug Component (only show in development) -->
      <MobileDebug v-if="isDevelopment" />
      
      <div class="card p-8">
        <form @submit.prevent="handleRegister" class="space-y-6">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">
              Username
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              @focus="trackFieldInteraction('username', 'focus')"
              @blur="trackFieldInteraction('username', 'blur')"
              @input="trackFieldInteraction('username', 'input')"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="Choose a username"
            >
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              @focus="trackFieldInteraction('password', 'focus')"
              @blur="trackFieldInteraction('password', 'blur')"
              @input="trackFieldInteraction('password', 'input')"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="Choose a password"
            >
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              required
              @focus="trackFieldInteraction('confirmPassword', 'focus')"
              @blur="trackFieldInteraction('confirmPassword', 'blur')"
              @input="trackFieldInteraction('confirmPassword', 'input')"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="Confirm your password"
            >
          </div>

          <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <span class="text-red-400">⚠️</span>
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-800">{{ error }}</p>
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading || !passwordsMatch"
              class="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="loading" class="flex items-center justify-center">
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Creating account...
              </span>
              <span v-else>Create account</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import MobileDebug from '@/components/MobileDebug.vue'
import { track } from '@vercel/analytics'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

const error = ref('')
const loading = computed(() => authStore.loading)
const passwordsMatch = computed(() => form.value.password === form.value.confirmPassword)
const isDevelopment = computed(() => import.meta.env.DEV)

// Track mobile session on component mount
onMounted(() => {
  // Track page view
  track('page_view', {
    page: 'register',
    url: window.location.href,
    userAgent: navigator.userAgent,
    isMobile: /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent),
    isSafari: /^((?!chrome|android).)*safari/i.test(navigator.userAgent),
    isIOS: /iPad|iPhone|iPod/.test(navigator.userAgent)
  });
});

const handleRegister = async () => {
  error.value = ''
  
  if (!passwordsMatch.value) {
    // Track password mismatch error
    track('register_password_mismatch', {
      passwordLength: form.value.password?.length || 0,
      confirmPasswordLength: form.value.confirmPassword?.length || 0,
      userAgent: navigator.userAgent
    });
    
    error.value = 'Passwords do not match.'
    return
  }
  
  // Track registration attempt
  const credentials = {
    username: form.value.username,
    password: form.value.password
  };
  
  try {
    // Track form submission start
    track('register_form_submit', {
      hasUsername: !!form.value.username,
      hasPassword: !!form.value.password,
      hasConfirmPassword: !!form.value.confirmPassword,
      passwordsMatch: passwordsMatch.value,
      formValid: form.value.username && form.value.password && passwordsMatch.value,
      userAgent: navigator.userAgent,
      isMobile: /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent),
      isSafari: /^((?!chrome|android).)*safari/i.test(navigator.userAgent),
      isIOS: /iPad|iPhone|iPod/.test(navigator.userAgent)
    });
    
    const result = await authStore.register({
      username: form.value.username,
      password: form.value.password
    })
    
    if (result.success) {
      // Track successful registration
      track('register_success', {
        username: form.value.username,
        redirectTo: '/',
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
      });
      
      router.push('/')
    } else {
      // Track failed registration
      track('register_failure', {
        username: form.value.username,
        error: result.error || 'Registration failed',
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
      });
      
      error.value = result.error || 'Registration failed. Please try again.'
    }
  } catch (err) {
    // Track unexpected errors
    track('register_error', {
      username: form.value.username,
      error: err.message || err.toString(),
      errorType: err.name || 'Unknown',
      stack: err.stack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent
    });
    
    error.value = 'An error occurred. Please try again.'
  }
}

// Track form field interactions
const trackFieldInteraction = (fieldName, action) => {
  track('form_field_interaction', {
    field: fieldName,
    action: action, // 'focus', 'blur', 'input', 'validation'
    hasValue: !!form.value[fieldName],
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent
  });
};

// Track form validation
const trackValidation = (fieldName, isValid, errorMessage = '') => {
  track('form_validation', {
    field: fieldName,
    isValid,
    errorMessage,
    value: form.value[fieldName],
    userAgent: navigator.userAgent
  });
};
</script> 