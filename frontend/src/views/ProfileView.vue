<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <!-- Profile Header -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div class="max-w-2xl mx-auto">
          <div class="mb-8">
            <h1 class="text-3xl font-serif font-bold text-gray-900 mb-2">Your Profile</h1>
            <p class="text-gray-600">Your art exploration journey</p>
          </div>

          <!-- User Info -->
          <div class="card p-6 mb-6">
            <h2 class="text-xl font-semibold mb-4">Account Information</h2>
            
            <div class="flex flex-col sm:flex-row gap-6">
              <!-- Profile Picture Section -->
              <div class="bg-white p-6 rounded-lg shadow-md">
                <h3 class="text-lg font-semibold mb-4">Profile Picture</h3>
                
                <div class="flex items-center space-x-6">
                  <!-- Profile Picture Display -->
                  <div class="relative">
                    <div v-if="uploading" class="absolute inset-0 flex items-center justify-center bg-gray-100 rounded-full">
                      <LoadingSkeleton type="avatar" size="xl" />
                    </div>
                    <img
                      v-else-if="user?.profile_picture"
                      :src="user.profile_picture"
                      alt="Profile Picture"
                      class="w-24 h-24 rounded-full object-cover border-4 border-gray-200"
                    />
                    <div
                      v-else
                      class="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center"
                    >
                      <span class="text-gray-500 text-2xl">👤</span>
                    </div>
                  </div>
                  
                  <!-- Upload Button Overlay -->
                  <button 
                    @click="triggerFileUpload"
                    :disabled="uploading"
                    class="absolute inset-0 bg-black bg-opacity-50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-white text-xs"
                  >
                    <span v-if="uploading" class="flex items-center">
                      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Uploading...
                    </span>
                    <span v-else>Change</span>
                  </button>
                </div>
                
                <!-- File Input (Hidden) -->
                <input 
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  @change="handleFileUpload"
                  class="hidden"
                >
                
                <!-- Profile Picture Actions -->
                <div class="flex space-x-2">
                  <button 
                    @click="triggerFileUpload"
                    :disabled="uploading"
                    class="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
                  >
                    {{ user?.profile_picture ? 'Change' : 'Upload' }}
                  </button>
                  <button 
                    v-if="user?.profile_picture"
                    @click="deleteProfilePicture"
                    :disabled="uploading"
                    class="text-xs bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 disabled:opacity-50 transition-colors"
                  >
                    Remove
                  </button>
                </div>
                
                <!-- Upload Progress -->
                <div v-if="uploading" class="w-full">
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" :style="{ width: uploadProgress + '%' }"></div>
                  </div>
                  <p class="text-xs text-gray-600 mt-1">{{ uploadProgress }}%</p>
                </div>
              </div>
              
              <!-- User Details -->
              <div class="flex-1 space-y-3">
                <div>
                  <span class="text-sm font-medium text-gray-500">Username:</span>
                  <span class="ml-2 text-gray-900">{{ user?.username }}</span>
                </div>
                <div v-if="user?.email">
                  <span class="text-sm font-medium text-gray-500">Email:</span>
                  <span class="ml-2 text-gray-900">{{ user.email }}</span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-500">Member since:</span>
                  <span class="ml-2 text-gray-900">{{ formatDate(user?.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Stats -->
          <div class="card p-6 mb-6">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-semibold">Your Art Journey</h2>
              <button 
                @click="loadStats" 
                :disabled="loading"
                class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50 transition-colors flex items-center"
              >
                <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ loading ? 'Loading...' : '🔄 Refresh' }}
              </button>
            </div>
            
            <!-- Error State -->
            <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <div class="flex items-center">
                <span class="text-red-600 text-sm">⚠️ {{ error }}</span>
                <button @click="loadStats" class="ml-2 text-red-600 hover:text-red-800 text-sm underline">
                  Try Again
                </button>
              </div>
            </div>
            
            <!-- Loading State -->
            <div v-if="loading" class="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div v-for="i in 5" :key="i" class="text-center">
                <div class="text-3xl font-bold text-gray-300 animate-pulse">---</div>
                <div class="text-sm text-gray-400">Loading...</div>
              </div>
            </div>
            
            <!-- Stats Content -->
            <div v-else class="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div class="text-center">
                <div class="text-3xl font-bold text-primary-600">{{ stats.liked_artworks || 0 }}</div>
                <div class="text-sm text-gray-500">❤️ Liked Artworks</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-primary-600">{{ stats.unique_museums || 0 }}</div>
                <div class="text-sm text-gray-500">🏛️ Museums Explored</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-primary-600">{{ stats.total_ratings || 0 }}</div>
                <div class="text-sm text-gray-500">⭐ Artworks Rated</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-primary-600">{{ stats.total_notes || 0 }}</div>
                <div class="text-sm text-gray-500">📝 Notes Written</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-primary-600">{{ stats.total_boards || 0 }}</div>
                <div class="text-sm text-gray-500">📋 Boards Created</div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="card p-6">
            <h2 class="text-xl font-semibold mb-4">Quick Actions</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <router-link to="/" class="btn-primary text-center">
                🎲 Explore More Art
              </router-link>
              <router-link to="/gallery" class="btn-secondary text-center">
                🖼️ View Gallery
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useArtworkStore } from '@/stores/artwork'
import { apiClient } from '@/utils/apiClient'
import { useToast } from '@/composables/useToast'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'
import { config } from '@/config'

const router = useRouter()
const authStore = useAuthStore()
const artworkStore = useArtworkStore()

const user = computed(() => authStore.user)
const stats = ref({})
const loading = ref(false)
const error = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const fileInput = ref(null)

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getProfilePictureUrl = (profilePicturePath) => {
  if (!profilePicturePath) return null
  // Handle both relative and absolute URLs
  if (profilePicturePath.startsWith('http')) {
    return profilePicturePath
  }
      return `${import.meta.env.VITE_API_BASE_URL || config.apiBaseUrl}${profilePicturePath}`
}

const loadStats = async () => {
  try {
    loading.value = true
    error.value = null
    stats.value = await artworkStore.getUserStats()
  } catch (err) {
    console.error('Error loading stats:', err)
    error.value = 'Failed to load user statistics'
    // Provide default stats on error
    stats.value = {
      liked_artworks: 0,
      unique_museums: 0,
      total_ratings: 0,
      total_notes: 0,
      total_boards: 0
    }
  } finally {
    loading.value = false
  }
}

const triggerFileUpload = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Validate file type
  if (!file.type.startsWith('image/')) {
    show('Please select an image file', 'error')
    return
  }
  
  // Validate file size (5MB limit)
  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.size > maxSize) {
    show('File size must be less than 5MB', 'error')
    return
  }
  
  try {
    uploading.value = true
    uploadProgress.value = 0
    
    // Simulate upload progress
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 100)
    
    // Use the auth store method instead of apiClient
    const result = await authStore.updateProfilePicture(file)
    
    clearInterval(progressInterval)
    uploadProgress.value = 100
    
    show('Profile picture uploaded successfully!', 'success')
    
    // Reset progress after a delay
    setTimeout(() => {
      uploadProgress.value = 0
    }, 1000)
    
  } catch (error) {
    console.error('Error uploading profile picture:', error)
    show('Failed to upload profile picture. Please try again.', 'error')
  } finally {
    uploading.value = false
    // Clear the file input
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

async function deleteProfilePicture() {
  if (!confirm('Are you sure you want to remove your profile picture?')) {
    return
  }

  try {
    uploading.value = true
    // Use the auth store method instead of apiClient
    const result = await authStore.deleteProfilePicture()
    
    show('Profile picture removed successfully!', 'success')
  } catch (error) {
    console.error('Error deleting profile picture:', error)
    show('Failed to remove profile picture. Please try again.', 'error')
  } finally {
    uploading.value = false
  }
}

const handleImageError = (event) => {
  console.error('Failed to load profile picture')
  // Set a default fallback
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

const showNotification = (message, type = 'info') => {
  // Simple notification system - you could enhance this with a toast library
  const notification = document.createElement('div')
  notification.className = `fixed top-4 right-4 p-4 rounded-md text-white z-50 transition-all duration-300 ${
    type === 'success' ? 'bg-green-500' : 
    type === 'error' ? 'bg-red-500' : 
    'bg-blue-500'
  }`
  notification.textContent = message
  
  document.body.appendChild(notification)
  
  // Auto-remove after 3 seconds
  setTimeout(() => {
    notification.remove()
  }, 3000)
}

onMounted(() => {
  loadStats()
})
</script> 