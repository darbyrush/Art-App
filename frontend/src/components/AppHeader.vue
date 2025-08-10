<template>
  <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center py-3 sm:py-4">
        <!-- Left side: Logo and title -->
        <div class="flex items-center space-x-3">
          <router-link to="/" class="text-lg sm:text-2xl font-serif font-bold text-gray-900">
            🎨 Art Explorer
          </router-link>
          <slot name="title"></slot>
        </div>

        <!-- Center: Navigation -->
        <nav class="hidden md:flex items-center space-x-4">
          <router-link 
            to="/" 
            class="text-sm text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md transition-colors"
            :class="{ 'bg-gray-100 text-gray-900': $route.path === '/' }"
          >
            Exhibit
          </router-link>
          <router-link 
            to="/gallery" 
            class="text-sm text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md transition-colors"
            :class="{ 'bg-gray-100 text-gray-900': $route.path === '/gallery' }"
          >
            Gallery
          </router-link>
          <router-link 
            to="/boards" 
            class="text-sm text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md transition-colors"
            :class="{ 'bg-gray-100 text-gray-900': $route.path === '/boards' }"
          >
            Boards
          </router-link>
        </nav>

        <!-- Right side: User profile and actions -->
        <div class="flex items-center space-x-3">
          <!-- Additional actions slot -->
          <slot name="actions"></slot>
          
          <!-- User Profile Section -->
          <div class="flex items-center space-x-3">
            <!-- Profile Picture -->
            <div class="relative group">
              <div class="w-8 h-8 rounded-full overflow-hidden bg-gray-200 border-2 border-gray-300 cursor-pointer">
                <img 
                  v-if="user?.profile_picture" 
                  :src="getProfilePictureUrl(user.profile_picture)" 
                  :alt="user?.username"
                  class="w-full h-full object-cover"
                  @error="handleImageError"
                  @load="handleImageLoad"
                >
                <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
              
              <!-- Profile Dropdown -->
              <div class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <router-link 
                  to="/profile" 
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                >
                  👤 View Profile
                </router-link>
                <button 
                  @click="logout" 
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                >
                  🚪 Logout
                </button>
              </div>
            </div>
            
            <!-- Username (hidden on small screens) -->
            <span class="hidden sm:block text-sm font-medium text-gray-700">
              {{ user?.username }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)

const getProfilePictureUrl = (profilePicturePath) => {
  if (!profilePicturePath) return null
  // Handle both relative and absolute URLs
  if (profilePicturePath.startsWith('http')) {
    return profilePicturePath
  }
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${profilePicturePath}`
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const handleImageError = (event) => {
  console.error('Failed to load profile picture')
  // Hide the image and show fallback
  event.target.style.display = 'none'
  const fallback = event.target.parentElement.querySelector('div')
  if (fallback) {
    fallback.style.display = 'flex'
  }
}

const handleImageLoad = (event) => {
  // Hide fallback when image loads successfully
  const fallback = event.target.parentElement.querySelector('div')
  if (fallback) {
    fallback.style.display = 'none'
  }
}
</script>

<style scoped>
/* Ensure the dropdown appears above other content */
.group:hover .group-hover\:visible {
  visibility: visible;
}

/* Smooth transitions */
.transition-colors {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
</style>

