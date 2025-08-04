<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div class="flex items-center space-x-4">
            <h1 class="text-2xl font-serif font-bold text-gray-900">🎨 Art Explorer</h1>
            <nav class="flex space-x-4">
              <router-link to="/exhibit" class="text-gray-600 hover:text-gray-900">Exhibit</router-link>
              <router-link to="/explorer" class="text-gray-600 hover:text-gray-900">Explorer</router-link>
              <router-link to="/profile" class="text-gray-600 hover:text-gray-900">Profile</router-link>
            </nav>
          </div>
        </div>
      </div>
    </header>

    <!-- Gallery Grid -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading State -->
      <div v-if="loading && likedArtworks.length === 0" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading your gallery...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="likedArtworks.length === 0 && !loading" class="text-center py-12">
        <div class="text-6xl mb-4">🖼️</div>
        <h2 class="text-2xl font-serif font-bold mb-2">Your Gallery is Empty</h2>
        <p class="text-gray-600 mb-6">Like some artworks in the Exhibit to see them here.</p>
        <router-link to="/exhibit" class="btn-primary">
          Browse Exhibit
        </router-link>
      </div>

      <!-- Gallery Grid -->
      <div v-else class="gallery-grid">
        <div 
          v-for="artwork in likedArtworks"
          :key="artwork.id"
          class="gallery-item"
          @click="openArtworkDetail(artwork)"
        >
          <!-- Image Container -->
          <div class="image-container">
            <img
              :src="getOptimizedImageUrl(artwork.image_url, 'gallery')"
              :alt="artwork.title"
              class="artwork-image"
              :data-source="artwork.source"
              @error="handleImageError"
              @load="handleImageLoad(artwork.id)"
              @loadstart="handleImageStartLoad(artwork.id)"
            >
            
            <!-- Like Button Overlay -->
            <button
              @click.stop="toggleLike(artwork.id)"
              class="like-button"
              :class="{ 'liked': isArtworkLiked(artwork.id) }"
            >
              <span class="like-icon">{{ isArtworkLiked(artwork.id) ? '❤️' : '🤍' }}</span>
            </button>
            
            <!-- Loading State -->
            <div v-if="imageLoading[artwork.id]" class="loading-overlay">
              <div class="loading-spinner"></div>
            </div>
          </div>
          
          <!-- Artwork Info -->
          <div class="artwork-info">
            <h3 class="artwork-title">{{ artwork.title }}</h3>
            <p class="artwork-artist">by {{ artwork.artist }}</p>
            <div class="artwork-meta">
              <span class="source-badge">{{ getSourceDisplayName(artwork.source) }}</span>
              <span class="date">{{ artwork.date }}</span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Artwork Detail Modal -->
    <div v-if="selectedArtwork" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-start mb-4">
            <h2 class="text-2xl font-serif font-bold">{{ selectedArtwork.title }}</h2>
            <button @click="selectedArtwork = null" class="text-gray-500 hover:text-gray-700">
              <span class="text-2xl">×</span>
            </button>
          </div>
          
          <img
            :src="getOptimizedImageUrl(selectedArtwork.image_url, 'detail')"
            :alt="selectedArtwork.title"
            class="w-full h-96 object-cover rounded-lg mb-4"
          >
          
          <div class="space-y-2">
            <p class="text-lg"><strong>Artist:</strong> {{ selectedArtwork.artist }}</p>
            <p class="text-gray-600"><strong>Date:</strong> {{ selectedArtwork.date }}</p>
            <p class="text-gray-600"><strong>Origin:</strong> {{ selectedArtwork.origin }}</p>
            <p class="text-gray-600"><strong>Department:</strong> {{ selectedArtwork.department }}</p>
            <p class="text-gray-600"><strong>Source:</strong> {{ getSourceDisplayName(selectedArtwork.source) }}</p>
          </div>
          
          <div class="flex space-x-2 mt-6">
            <button
              @click="toggleLike(selectedArtwork.id)"
              class="btn-secondary"
              :class="isArtworkLiked(selectedArtwork.id) ? 'bg-red-100 text-red-700' : ''"
            >
              {{ isArtworkLiked(selectedArtwork.id) ? '❤️ Liked' : '🤍 Like' }}
            </button>
            <button @click="selectedArtwork = null" class="btn-primary">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useArtworkStore } from '@/stores/artwork'
import { getOptimizedImageUrl, getFallbackImageUrl } from '@/utils/imageUtils'

const router = useRouter()
const authStore = useAuthStore()
const artworkStore = useArtworkStore()

// State
const likedArtworks = ref([])
const loading = ref(false)
const selectedArtwork = ref(null)
const imageLoading = ref({})

// Methods
const loadLikedArtworks = async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  loading.value = true
  try {
    // Get all artworks and filter for liked ones
    const allArtworks = await artworkStore.getArtworks({ page: 1, limit: 100 })
    likedArtworks.value = allArtworks.filter(artwork => isArtworkLiked(artwork.id))
  } catch (error) {
    console.error('Error loading liked artworks:', error)
  } finally {
    loading.value = false
  }
}

const isArtworkLiked = (artworkId) => {
  return artworkStore.likedArtworks.includes(artworkId)
}

const toggleLike = async (artworkId) => {
  try {
    if (isArtworkLiked(artworkId)) {
      await artworkStore.unlikeArtwork(artworkId)
      // Remove from liked artworks list
      likedArtworks.value = likedArtworks.value.filter(art => art.id !== artworkId)
    } else {
      await artworkStore.likeArtwork(artworkId)
      // Add to liked artworks list if not already there
      const artwork = likedArtworks.value.find(art => art.id === artworkId)
      if (!artwork) {
        const allArtworks = await artworkStore.getArtworks({ page: 1, limit: 100 })
        const foundArtwork = allArtworks.find(art => art.id === artworkId)
        if (foundArtwork) {
          likedArtworks.value.push(foundArtwork)
        }
      }
    }
  } catch (error) {
    console.error('Error toggling like:', error)
  }
}

const openArtworkDetail = (artwork) => {
  selectedArtwork.value = artwork
}

const handleImageError = (event) => {
  const fallbackUrl = getFallbackImageUrl(event.target.dataset.source)
  if (event.target.src !== fallbackUrl) {
    event.target.src = fallbackUrl
  }
}

const handleImageLoad = (artworkId) => {
  imageLoading.value[artworkId] = false
}

const handleImageStartLoad = (artworkId) => {
  imageLoading.value[artworkId] = true
}

const getSourceDisplayName = (source) => {
  const displayNames = {
    'met': 'Metropolitan Museum of Art',
    'cleveland': 'Cleveland Museum of Art',
    'chicago': 'Art Institute of Chicago',
    'harvard': 'Harvard Art Museums',
    'smithsonian': 'Smithsonian Institution',
    'national_gallery': 'National Gallery of Art',
    'walters': 'Walters Art Museum'
  }
  return displayNames[source] || source
}

// Lifecycle
onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  loadLikedArtworks()
})
</script>

<style scoped>
.btn-primary {
  @apply bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors;
}

.btn-secondary {
  @apply bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 transition-colors;
}

/* Gallery Grid */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.gallery-item {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.gallery-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.image-container {
  position: relative;
  width: 100%;
  height: 300px;
  overflow: hidden;
}

.artwork-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.gallery-item:hover .artwork-image {
  transform: scale(1.05);
}

.like-button {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
}

.like-button:hover {
  background: rgba(255, 255, 255, 1);
  transform: scale(1.1);
}

.like-button.liked {
  background: rgba(239, 68, 68, 0.9);
}

.like-icon {
  font-size: 18px;
  transition: transform 0.2s ease;
}

.like-button:hover .like-icon {
  transform: scale(1.2);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.artwork-info {
  padding: 16px;
}

.artwork-title {
  font-family: 'Georgia', serif;
  font-weight: bold;
  font-size: 16px;
  color: #1f2937;
  margin-bottom: 4px;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.artwork-artist {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 8px;
}

.artwork-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.source-badge {
  background: #f3f4f6;
  color: #374151;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.date {
  color: #9ca3af;
}

/* Responsive Design */
@media (max-width: 640px) {
  .gallery-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px;
    padding: 16px 0;
  }
  
  .image-container {
    height: 250px;
  }
  
  .artwork-info {
    padding: 12px;
  }
}

@media (max-width: 480px) {
  .gallery-grid {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 12px 0;
  }
  
  .image-container {
    height: 200px;
  }
}
</style> 