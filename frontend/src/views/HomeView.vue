<template>
  <div class="min-h-screen bg-art-cream">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div class="flex items-center">
            <h1 class="text-2xl font-serif font-bold text-gray-900">🎨 Art Explorer</h1>
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
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex">
        <!-- Sidebar -->
        <aside class="w-64 pr-8">
          <div class="card p-6">
            <h3 class="text-lg font-semibold mb-4">🏛️ Museum Sources</h3>
            <div class="space-y-2">
              <label v-for="source in availableSources" :key="source" class="flex items-center">
                <input
                  type="checkbox"
                  :value="source"
                  v-model="selectedSources"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                >
                <span class="ml-2 text-sm">{{ getSourceDisplayName(source) }}</span>
              </label>
            </div>
            
            <div class="mt-6">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Your Stats</h4>
              <div class="grid grid-cols-2 gap-4">
                <div class="text-center">
                  <div class="text-2xl font-bold text-primary-600">{{ stats.liked_artworks || 0 }}</div>
                  <div class="text-xs text-gray-500">Liked</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-primary-600">{{ stats.unique_museums || 0 }}</div>
                  <div class="text-xs text-gray-500">Museums</div>
                </div>
              </div>
            </div>
          </div>
        </aside>

        <!-- Artwork Display -->
        <div class="flex-1">
          <div class="max-w-md mx-auto">
            <!-- Loading State -->
            <div v-if="loading" class="text-center py-12">
              <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p class="mt-4 text-gray-600">Loading artwork...</p>
            </div>

            <!-- Empty State -->
            <div v-else-if="!currentArtwork" class="text-center py-12">
              <div class="text-6xl mb-4">🎨</div>
              <h2 class="text-2xl font-serif font-bold mb-2">Welcome to Art Explorer!</h2>
              <p class="text-gray-600 mb-6">Ready to discover amazing artworks? Click the button below to start exploring!</p>
              <button @click="getRandomArtwork" class="btn-primary">
                🎲 Start Exploring
              </button>
            </div>

            <!-- Artwork Display -->
            <div v-else class="instagram-container">
              <!-- Artwork Header -->
              <div class="flex items-center justify-between p-4 border-b border-gray-200">
                <div class="font-semibold text-gray-900">{{ getSourceDisplayName(currentArtwork.source) }}</div>
                <div class="text-gray-500">🎨</div>
              </div>

              <!-- Artwork Image -->
              <div class="relative">
                <img
                  :src="currentArtwork.image_url"
                  :alt="currentArtwork.title"
                  class="w-full h-96 object-cover"
                  @dblclick="likeArtwork"
                >
                <!-- Double-tap overlay -->
                <div
                  v-if="showHeart"
                  class="absolute inset-0 flex items-center justify-center pointer-events-none"
                >
                  <div class="text-6xl animate-heart-beat">❤️</div>
                </div>
              </div>

              <!-- Artwork Info -->
              <div class="p-4">
                <h3 class="font-serif font-bold text-lg mb-1">{{ currentArtwork.title }}</h3>
                <p class="text-gray-600 mb-2">by {{ currentArtwork.artist }}</p>
                <div class="text-sm text-gray-500 mb-4">
                  📅 {{ currentArtwork.date }} • 🌍 {{ currentArtwork.origin }} • 🏛️ {{ currentArtwork.department }}
                </div>

                <!-- Action Buttons -->
                <div class="flex items-center justify-between">
                  <div class="flex space-x-4">
                    <button
                      @click="likeArtwork"
                      class="flex items-center space-x-1 text-gray-600 hover:text-red-500 transition-colors"
                    >
                      <span class="text-xl">❤️</span>
                      <span class="text-sm">Like</span>
                    </button>
                    <button
                      @click="showRatingModal = true"
                      class="flex items-center space-x-1 text-gray-600 hover:text-yellow-500 transition-colors"
                    >
                      <span class="text-xl">⭐</span>
                      <span class="text-sm">Rate</span>
                    </button>
                  </div>
                  <button
                    @click="getRandomArtwork"
                    class="btn-primary"
                  >
                    Next Artwork
                  </button>
                </div>
              </div>
            </div>
          </div>
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useArtworkStore } from '@/stores/artwork'

const router = useRouter()
const authStore = useAuthStore()
const artworkStore = useArtworkStore()

const loading = computed(() => artworkStore.loading)
const currentArtwork = computed(() => artworkStore.currentArtwork)
const selectedSources = computed({
  get: () => artworkStore.selectedSources,
  set: (value) => artworkStore.selectedSources = value
})
const availableSources = computed(() => artworkStore.availableSources)

const stats = ref({})
const showHeart = ref(false)
const showRatingModal = ref(false)
const selectedRating = ref(0)

const getRandomArtwork = async () => {
  try {
    await artworkStore.getRandomArtwork()
  } catch (error) {
    console.error('Error getting artwork:', error)
  }
}

const likeArtwork = async () => {
  if (!currentArtwork.value) return
  
  try {
    await artworkStore.likeArtwork(currentArtwork.value.id, true)
    showHeart.value = true
    setTimeout(() => {
      showHeart.value = false
    }, 600)
  } catch (error) {
    console.error('Error liking artwork:', error)
  }
}

const rateArtwork = (rating) => {
  selectedRating.value = rating
}

const submitRating = async () => {
  if (!currentArtwork.value || selectedRating.value === 0) return
  
  try {
    await artworkStore.rateArtwork(currentArtwork.value.id, selectedRating.value)
    showRatingModal.value = false
    selectedRating.value = 0
  } catch (error) {
    console.error('Error rating artwork:', error)
  }
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

const loadStats = async () => {
  try {
    stats.value = await artworkStore.getUserStats()
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script> 