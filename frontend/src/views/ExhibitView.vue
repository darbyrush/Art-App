<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <!-- Welcome Section -->
      <div class="text-center mb-12">
        <h1 class="text-4xl sm:text-6xl font-serif font-bold text-gray-900 mb-6">
          🎨 Welcome to Art Explorer
        </h1>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">
          Discover amazing artworks from world-renowned museums and galleries. 
          Start your art journey with a random masterpiece!
        </p>
      </div>
      
      <!-- Debug Info -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 class="text-lg font-semibold text-blue-800 mb-2">Debug Information</h3>
        <p class="text-blue-700">Component loaded successfully!</p>
        <p class="text-blue-700">Loading state: {{ loading }}</p>
        <p class="text-blue-700">Artworks count: {{ artworks.length }}</p>
        <p class="text-blue-700">Error: {{ error || 'None' }}</p>
        <p class="text-blue-700">Current route: {{ $route.path }}</p>
        <p class="text-blue-700">Route name: {{ $route.name }}</p>
        
        <!-- Test Navigation Buttons -->
        <div class="mt-4 space-x-2">
          <button @click="testNavigation('/exhibit')" class="px-3 py-1 bg-blue-500 text-white rounded text-sm">
            Test: Go to Exhibit
          </button>
          <button @click="testNavigation('/gallery')" class="px-3 py-1 bg-green-500 text-white rounded text-sm">
            Test: Go to Gallery
          </button>
          <button @click="testNavigation('/boards')" class="px-3 py-1 bg-purple-500 text-white rounded text-sm">
            Test: Go to Boards
          </button>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-8 sm:py-12">
        <div class="animate-spin rounded-full h-8 w-8 sm:h-12 sm:w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-2 sm:mt-4 text-sm sm:text-base text-gray-600">
          Loading artworks...
        </p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-8 sm:py-12">
        <div class="text-4xl mb-4">⚠️</div>
        <h2 class="text-xl sm:text-2xl font-serif font-bold mb-2">Something went wrong</h2>
        <p class="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6 px-4">{{ error }}</p>
        <button @click="loadArtworks" class="btn-primary text-sm sm:text-base px-4 py-2">
          Try Again
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="artworks.length === 0" class="text-center py-8 sm:py-12">
        <div class="text-4xl sm:text-6xl mb-4">🎨</div>
        <h2 class="text-xl sm:text-2xl font-serif font-bold mb-2">Welcome to the Exhibit!</h2>
        <p class="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6 px-4">Ready to discover amazing artworks? Click the button below to start exploring!</p>
        <button @click="loadArtworks" class="btn-primary text-sm sm:text-base px-4 py-2">
          🎲 Start Exploring
        </button>
      </div>

      <!-- Artworks Display -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="artwork in artworks" 
          :key="artwork.id"
          class="bg-white rounded-lg shadow-md overflow-hidden"
        >
          <div class="p-4">
            <h3 class="font-semibold text-lg mb-2">{{ artwork.title || 'Untitled' }}</h3>
            <p v-if="artwork.artist" class="text-gray-600 mb-2">by {{ artwork.artist }}</p>
            <p v-if="artwork.source" class="text-sm text-gray-500">{{ artwork.source }}</p>
            <button 
              @click="likeArtwork(artwork)"
              class="mt-3 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
            >
              ❤️ Like
            </button>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="artworks.length > 0 && hasMore" class="text-center mt-8">
        <button 
          @click="loadMoreArtworks" 
          :disabled="loading"
          class="btn-primary text-sm sm:text-base px-6 py-3"
        >
          {{ loading ? 'Loading...' : 'Load More Artworks' }}
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useArtworkStore } from '@/stores/artwork'

const router = useRouter()
const authStore = useAuthStore()
const artworkStore = useArtworkStore()

// Reactive data
const artworks = ref([])
const loading = ref(false)
const hasMore = ref(true)
const page = ref(1)
const error = ref(null)

// Simple load artworks function
const loadArtworks = async () => {
  try {
    console.log('Loading artworks...')
    loading.value = true
    error.value = null
    
    const response = await artworkStore.getGalleryArtworks({
      page: 1,
      sources: ['all'],
      sort_by: 'random'
    })
    
    console.log('Gallery response:', response)
    
    if (response && response.artworks) {
      artworks.value = response.artworks
      hasMore.value = response.has_more || false
      console.log(`Loaded ${artworks.value.length} artworks`)
    } else if (Array.isArray(response)) {
      artworks.value = response
      hasMore.value = response.length === 12
      console.log(`Loaded ${artworks.value.length} artworks (array response)`)
    } else {
      console.log('Unexpected response format:', response)
      artworks.value = []
      hasMore.value = false
    }
    
  } catch (err) {
    console.error('Error loading artworks:', err)
    error.value = err.message || 'Failed to load artworks'
    artworks.value = []
  } finally {
    loading.value = false
  }
}

// Load more artworks
const loadMoreArtworks = async () => {
  if (loading.value || !hasMore.value) return
  
  try {
    loading.value = true
    page.value++
    
    const response = await artworkStore.getGalleryArtworks({
      page: page.value,
      sources: ['all'],
      sort_by: 'random'
    })
    
    const newArtworks = response.artworks || response
    if (newArtworks && newArtworks.length > 0) {
      artworks.value.push(...newArtworks)
      hasMore.value = newArtworks.length === 12
    } else {
      hasMore.value = false
    }
    
  } catch (err) {
    console.error('Error loading more artworks:', err)
    error.value = err.message || 'Failed to load more artworks'
    page.value--
  } finally {
    loading.value = false
  }
}

// Like artwork function
const likeArtwork = async (artwork) => {
  // Check if user is authenticated
  if (!authStore.isAuthenticated) {
    if (confirm('You need to log in to like artworks. Would you like to go to the login page?')) {
      router.push('/login')
    }
    return
  }
  
  try {
    await artworkStore.likeArtwork(artwork.id, true)
    console.log('Artwork liked successfully')
  } catch (error) {
    console.error('Error liking artwork:', error)
    alert('Failed to like artwork. Please try again.')
  }
}

// Test navigation function
const testNavigation = (path) => {
  console.log('Navigating to:', path)
  router.push(path)
}

// Lifecycle
onMounted(() => {
  console.log('ExhibitView mounted successfully!')
  console.log('Current route:', router.currentRoute.value)
  console.log('Auth state:', authStore.isAuthenticated)
  console.log('User:', authStore.user)
  // Don't auto-load artworks, let user click the button
})
</script>

<style scoped>
.instagram-feed {
  max-width: 600px;
  margin: 0 auto;
}

.instagram-post {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
}

@media (min-width: 640px) {
  .instagram-post {
    margin-bottom: 24px;
  }
}

.post-header {
  padding: 12px 16px;
  border-bottom: 1px solid #efefef;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

@media (min-width: 640px) {
  .post-header {
    padding: 16px;
  }
}

.post-image-container {
  position: relative;
  width: 100%;
}

.post-image-container img {
  width: 100%;
  height: 256px;
  object-fit: cover;
}

@media (min-width: 640px) {
  .post-image-container img {
    height: 400px;
  }
}

.post-actions {
  padding: 12px 16px;
  border-bottom: 1px solid #efefef;
}

@media (min-width: 640px) {
  .post-actions {
    padding: 16px;
  }
}

.post-info {
  padding: 12px 16px;
}

@media (min-width: 640px) {
  .post-info {
    padding: 16px;
  }
}

.animate-heart-beat {
  animation: heartBeat 0.6s ease-in-out;
}

@keyframes heartBeat {
  0% { transform: scale(1); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

.btn-primary {
  @apply bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 transition-colors;
}

@media (min-width: 640px) {
  .btn-primary {
    @apply px-4 py-2;
  }
}

.btn-secondary {
  @apply bg-gray-200 text-gray-800 px-3 py-2 rounded-lg hover:bg-gray-300 transition-colors;
}

@media (min-width: 640px) {
  .btn-secondary {
    @apply px-4 py-2;
  }
}

/* Filter panel transitions */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Mobile-specific improvements */
@media (max-width: 639px) {
  .instagram-feed {
    padding: 0 8px;
  }
  
  .instagram-post {
    border-radius: 6px;
  }
  
  .post-image-container img {
    border-radius: 0;
  }
}
</style> 