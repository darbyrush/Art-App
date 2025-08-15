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
import { mobileAnalytics } from '@/utils/mobileAnalytics'

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
  if (mobileAnalytics.isProblematicDevice()) {
    console.log('🔍 Mobile Safari iOS device detected - enhanced tracking enabled');
  }
});

const handleRegister = async () => {
  error.value = ''
  
  if (!passwordsMatch.value) {
    // Track password mismatch error
    mobileAnalytics.trackFormIssue('register', 'password_mismatch', {
      passwordLength: form.value.password?.length || 0,
      confirmPasswordLength: form.value.confirmPassword?.length || 0
    });
    
    error.value = 'Passwords do not match.'
    return
  }
  
  // Track registration attempt with mobile analytics
  const credentials = {
    username: form.value.username,
    password: form.value.password
  };
  
  try {
    // Track form submission start
    mobileAnalytics.trackMobileBehavior('register_form_submit', {
      hasUsername: !!form.value.username,
      hasPassword: !!form.value.password,
      hasConfirmPassword: !!form.value.confirmPassword,
      passwordsMatch: passwordsMatch.value,
      formValid: form.value.username && form.value.password && passwordsMatch.value
    });
    
    const result = await authStore.register({
      username: form.value.username,
      password: form.value.password
    })
    
    if (result.success) {
      // Track successful registration
      mobileAnalytics.trackRegistrationAttempt(credentials, true);
      mobileAnalytics.trackMobileBehavior('register_success', {
        redirectTo: '/',
        timestamp: new Date().toISOString()
      });
      
      router.push('/')
    } else {
      // Track failed registration
      const registerError = new Error(result.error || 'Registration failed');
      mobileAnalytics.trackRegistrationAttempt(credentials, false, registerError);
      mobileAnalytics.trackFormIssue('register', 'auth_failure', {
        error: result.error,
        username: form.value.username
      });
      
      error.value = result.error || 'Registration failed. Please try again.'
    }
  } catch (err) {
    // Track unexpected errors
    mobileAnalytics.trackRegistrationAttempt(credentials, false, err);
    mobileAnalytics.trackFormIssue('register', 'unexpected_error', {
      error: err.message || err.toString(),
      errorType: err.name || 'Unknown',
      stack: err.stack
    });
    mobileAnalytics.trackMobileError(err, {
      component: 'RegisterView',
      action: 'handleRegister',
      formData: { username: form.value.username }
    });
    
    error.value = 'An error occurred. Please try again.'
  }
}

// Track form field interactions
const trackFieldInteraction = (fieldName, action) => {
  mobileAnalytics.trackMobileBehavior('form_field_interaction', {
    field: fieldName,
    action: action, // 'focus', 'blur', 'input', 'validation'
    hasValue: !!form.value[fieldName],
    timestamp: new Date().toISOString()
  });
};

// Track form validation
const trackValidation = (fieldName, isValid, errorMessage = '') => {
  mobileAnalytics.trackFormIssue('register', 'validation_error', {
    field: fieldName,
    isValid,
    errorMessage,
    value: form.value[fieldName]
  });
};
</script> 