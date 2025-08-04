<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div class="flex items-center">
            <h1 class="text-2xl font-serif font-bold text-gray-900">🎨 Exhibit Feed</h1>
          </div>
          <nav class="flex items-center space-x-4">
            <router-link to="/gallery" class="text-gray-600 hover:text-gray-900">
              Gallery
            </router-link>
            <router-link to="/profile" class="text-gray-600 hover:text-gray-900">
              Profile
            </router-link>
            <button @click="logout" class="text-gray-600 hover:text-gray-900">
              Logout
            </button>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading artworks...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="artworks.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">🎨</div>
        <h2 class="text-2xl font-serif font-bold mb-2">Welcome to the Exhibit!</h2>
        <p class="text-gray-600 mb-6">Ready to discover amazing artworks? Scroll down to start exploring!</p>
        <button @click="loadMoreArtworks" class="btn-primary">
          🎲 Start Exploring
        </button>
      </div>

      <!-- Instagram-style Feed -->
      <div v-else class="instagram-feed">
        <div
          v-for="artwork in artworks"
          :key="artwork.id"
          class="instagram-post bg-white rounded-lg shadow-sm border border-gray-200 mb-6"
        >
          <!-- Post Header -->
          <div class="post-header flex items-center justify-between p-4 border-b border-gray-200">
            <div class="font-semibold text-gray-900">{{ getSourceDisplayName(artwork.source) }}</div>
            <div class="text-gray-500">🎨</div>
          </div>

          <!-- Post Image Container -->
          <div class="post-image-container relative">
            <img
              :src="getOptimizedImageUrl(artwork.image_url, 'feed')"
              :alt="artwork.title"
              class="w-full h-96 object-cover"
              @dblclick="likeArtwork(artwork)"
              @error="handleImageError"
              :data-source="artwork.source"
              @load="handleImageLoad"
              @loadstart="handleImageStartLoad"
            >
            <!-- Double-tap overlay -->
            <div
              v-if="artwork.showHeart"
              class="absolute inset-0 flex items-center justify-center pointer-events-none"
            >
              <div class="text-6xl animate-heart-beat">❤️</div>
            </div>
          </div>

          <!-- Post Actions -->
          <div class="post-actions p-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div class="flex space-x-4">
                <button
                  @click="likeArtwork(artwork)"
                  class="flex items-center space-x-1 text-gray-600 hover:text-red-500 transition-colors"
                >
                  <span class="text-xl">❤️</span>
                  <span class="text-sm">Like</span>
                </button>
                <button
                  @click="showRatingModal = true; selectedArtwork = artwork"
                  class="flex items-center space-x-1 text-gray-600 hover:text-yellow-500 transition-colors"
                >
                  <span class="text-xl">⭐</span>
                  <span class="text-sm">Rate</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Post Info -->
          <div class="post-info p-4">
            <h3 class="font-serif font-bold text-lg mb-1">{{ artwork.title }}</h3>
            <p class="text-gray-600 mb-2">by {{ artwork.artist }}</p>
            <div class="text-sm text-gray-500 mb-4">
              📅 {{ artwork.date }} • 🌍 {{ artwork.origin }} • 🏛️ {{ artwork.department }}
            </div>
          </div>
        </div>

        <!-- Load More Trigger -->
        <div
          v-if="hasMore"
          ref="loadMoreTrigger"
          class="text-center py-8"
        >
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p class="mt-2 text-gray-600">Loading more artworks...</p>
        </div>

        <!-- End of Results -->
        <div v-else class="text-center py-8">
          <div class="text-4xl mb-4">🎉</div>
          <h3 class="text-lg font-semibold mb-2">You've reached the end of the exhibit!</h3>
          <p class="text-gray-600 mb-4">Check back later for more amazing artworks.</p>
          <button @click="resetExhibit" class="btn-primary">
            Reset Exhibit
          </button>
        </div>
      </div>
    </main>

    <!-- Rating Modal -->
    <div v-if="showRatingModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
        <h3 class="text-lg font-semibold mb-4">Rate this artwork</h3>
        <div class="flex justify-center space-x-2 mb-4">
          <button
            v-for="star in 5"
            :key="star"
            @click="rateArtwork(star)"
            class="text-2xl hover:text-yellow-400 transition-colors"
            :class="star <= selectedRating ? 'text-yellow-400' : 'text-gray-300'"
          >
            ⭐
          </button>
        </div>
        <div class="flex space-x-2">
          <button @click="showRatingModal = false" class="btn-secondary flex-1">
            Cancel
          </button>
          <button @click="submitRating" class="btn-primary flex-1">
            Submit
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useArtworkStore } from '@/stores/artwork'
import { getOptimizedImageUrl, getFallbackImageUrl } from '@/utils/imageUtils'

const router = useRouter()
const authStore = useAuthStore()
const artworkStore = useArtworkStore()

// Reactive data
const artworks = ref([])
const loading = ref(false)
const hasMore = ref(true)
const page = ref(1)
const selectedSources = ref(['all'])
const sortBy = ref('random')
const imageLoading = ref({})

// Modal state
const showRatingModal = ref(false)
const selectedArtwork = ref(null)
const selectedRating = ref(0)

// Intersection Observer for infinite scrolling
const loadMoreTrigger = ref(null)
let observer = null

// Computed properties
const availableSources = computed(() => artworkStore.availableSources)

// Methods
const loadMoreArtworks = async () => {
  if (loading.value || !hasMore.value) return
  
  try {
    loading.value = true
    const newArtworks = await artworkStore.getGalleryArtworks({
      page: page.value,
      sources: selectedSources.value,
      sort_by: sortBy.value
    })
    
    if (newArtworks && newArtworks.length > 0) {
      artworks.value.push(...newArtworks)
      page.value++
    } else {
      hasMore.value = false
    }
  } catch (error) {
    console.error('Error loading artworks:', error)
    if (error.response?.status === 401) {
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}

const likeArtwork = async (artwork) => {
  try {
    await artworkStore.likeArtwork(artwork.id, true)
    artwork.showHeart = true
    setTimeout(() => {
      artwork.showHeart = false
    }, 600)
  } catch (error) {
    console.error('Error liking artwork:', error)
  }
}

const rateArtwork = (rating) => {
  selectedRating.value = rating
}

const submitRating = async () => {
  if (!selectedArtwork.value || selectedRating.value === 0) return
  
  try {
    await artworkStore.rateArtwork(selectedArtwork.value.id, selectedRating.value)
    showRatingModal.value = false
    selectedRating.value = 0
    selectedArtwork.value = null
  } catch (error) {
    console.error('Error rating artwork:', error)
  }
}

const handleImageError = (event) => {
  const fallbackUrl = getFallbackImageUrl(event.target.dataset.source)
  if (event.target.src !== fallbackUrl) {
    event.target.src = fallbackUrl
  }
}

const handleImageLoad = (event) => {
  const source = event.target.dataset.source
  if (imageLoading.value[source]) {
    imageLoading.value[source] = false
  }
}

const handleImageStartLoad = (event) => {
  const source = event.target.dataset.source
  imageLoading.value[source] = true
}

const resetExhibit = () => {
  artworks.value = []
  page.value = 1
  hasMore.value = true
  loadMoreArtworks()
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const getSourceDisplayName = (source) => {
  const displayNames = {
    'cleveland': 'Cleveland Museum of Art',
    'met': 'Metropolitan Museum of Art',
    'chicago': 'Art Institute of Chicago',
    'walters': 'Walters Art Museum',
    'national_gallery': 'National Gallery of Art',
    'smithsonian': 'Smithsonian American Art Museum',
    'harvard': 'Harvard Art Museums'
  }
  return displayNames[source] || source
}

// Setup intersection observer for infinite scrolling
const setupIntersectionObserver = () => {
  if (observer) {
    observer.disconnect()
  }
  
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && hasMore.value && !loading.value) {
          loadMoreArtworks()
        }
      })
    },
    { threshold: 0.1 }
  )
  
  if (loadMoreTrigger.value) {
    observer.observe(loadMoreTrigger.value)
  }
}

// Lifecycle
onMounted(() => {
  // Check authentication first
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  // Load initial artworks
  loadMoreArtworks()
  
  // Setup intersection observer after initial load
  nextTick(() => {
    setupIntersectionObserver()
  })
})

// Watch for changes in loadMoreTrigger
watch(loadMoreTrigger, () => {
  nextTick(() => {
    setupIntersectionObserver()
  })
})

// Cleanup observer on unmount
onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
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
  margin-bottom: 24px;
}

.post-header {
  padding: 16px;
  border-bottom: 1px solid #efefef;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.post-image-container {
  position: relative;
  width: 100%;
}

.post-image-container img {
  width: 100%;
  height: 400px;
  object-fit: cover;
}

.post-actions {
  padding: 16px;
  border-bottom: 1px solid #efefef;
}

.post-info {
  padding: 16px;
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
  @apply bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors;
}

.btn-secondary {
  @apply bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors;
}
</style> 