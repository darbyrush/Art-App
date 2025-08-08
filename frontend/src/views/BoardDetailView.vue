<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-3 sm:py-4">
          <div class="flex items-center space-x-2 sm:space-x-4">
            <button 
              @click="router.back()"
              class="text-gray-600 hover:text-gray-900"
            >
              ← Back
            </button>
            <h1 class="text-lg sm:text-2xl font-serif font-bold text-gray-900">
              {{ board?.name || 'Loading...' }}
            </h1>
          </div>
          <div class="flex items-center space-x-2">
            <button 
              @click="showEditModal = true"
              class="btn-secondary text-sm px-3 py-2"
            >
              Edit Board
            </button>
            <button 
              @click="router.push('/boards')"
              class="btn-primary text-sm px-3 py-2"
            >
              All Boards
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading board...</p>
      </div>

      <!-- Board Not Found -->
      <div v-else-if="!board" class="text-center py-12">
        <div class="text-6xl mb-4">❌</div>
        <h2 class="text-2xl font-serif font-bold mb-2">Board Not Found</h2>
        <p class="text-gray-600 mb-6">The board you're looking for doesn't exist or you don't have access to it.</p>
        <button @click="router.push('/boards')" class="btn-primary px-6 py-3">
          Go to Boards
        </button>
      </div>

      <!-- Board Content -->
      <div v-else>
        <!-- Board Info -->
        <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h2 class="text-2xl font-serif font-bold text-gray-900 mb-2">{{ board.name }}</h2>
              <p v-if="board.description" class="text-gray-600 mb-3">{{ board.description }}</p>
              <div class="flex items-center space-x-4 text-sm text-gray-500">
                <span>{{ board.artwork_count }} artwork{{ board.artwork_count !== 1 ? 's' : '' }}</span>
                <span class="visibility-badge" :class="board.is_public ? 'public' : 'private'">
                  {{ board.is_public ? 'Public' : 'Private' }}
                </span>
                <span>Created {{ formatDate(board.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Artworks Grid -->
        <div v-if="artworks.length > 0" class="artworks-grid">
          <div 
            v-for="artwork in artworks"
            :key="artwork.id"
            class="artwork-card"
          >
            <div class="artwork-image-container">
              <img 
                :src="getOptimizedImageUrl(artwork.image_url)"
                :alt="artwork.title"
                class="artwork-image"
                @error="handleImageError"
              >
              <div class="artwork-overlay">
                <button 
                  @click="removeFromBoard(artwork.id)"
                  class="remove-btn"
                  title="Remove from board"
                >
                  🗑️
                </button>
              </div>
            </div>
            <div class="artwork-info">
              <h3 class="artwork-title">{{ artwork.title }}</h3>
              <p v-if="artwork.artist" class="artwork-artist">{{ artwork.artist }}</p>
              <p v-if="artwork.date" class="artwork-date">{{ artwork.date }}</p>
              <span class="artwork-source">{{ artwork.source }}</span>
            </div>
          </div>
        </div>

        <!-- Empty Board -->
        <div v-else class="text-center py-12">
          <div class="text-6xl mb-4">🎨</div>
          <h2 class="text-2xl font-serif font-bold mb-2">Empty Board</h2>
          <p class="text-gray-600 mb-6">This board is empty. Add artworks from your gallery to get started!</p>
          <button @click="router.push('/gallery')" class="btn-primary px-6 py-3">
            Browse Gallery
          </button>
        </div>
      </div>
    </main>

    <!-- Edit Board Modal -->
    <div v-if="showEditModal && board" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold mb-4">Edit Board</h3>
        
        <form @submit.prevent="updateBoard">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Board Name</label>
            <input
              v-model="editingBoard.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
          </div>
          
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Description (Optional)</label>
            <textarea
              v-model="editingBoard.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            ></textarea>
          </div>
          
          <div class="mb-6">
            <label class="flex items-center">
              <input
                v-model="editingBoard.is_public"
                type="checkbox"
                class="mr-2"
              >
              <span class="text-sm text-gray-700">Make this board public</span>
            </label>
          </div>
          
          <div class="flex space-x-3">
            <button 
              type="button"
              @click="showEditModal = false"
              class="btn-secondary flex-1"
            >
              Cancel
            </button>
            <button 
              type="submit"
              class="btn-primary flex-1"
              :disabled="updating"
            >
              {{ updating ? 'Updating...' : 'Update Board' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBoardStore } from '@/stores/board'
import { getOptimizedImageUrl } from '@/utils/imageUtils'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const boardStore = useBoardStore()

// Reactive data
const loading = ref(false)
const updating = ref(false)
const showEditModal = ref(false)
const editingBoard = ref(null)

// Computed
const board = computed(() => boardStore.currentBoard)
const artworks = computed(() => boardStore.boardArtworks)

// Methods
const loadBoard = async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  const boardId = route.params.id
  if (!boardId) {
    router.push('/boards')
    return
  }
  
  loading.value = true
  try {
    await boardStore.loadBoard(boardId)
    await boardStore.loadBoardArtworks(boardId)
  } catch (error) {
    console.error('Error loading board:', error)
    // If board not found, redirect to boards list
    router.push('/boards')
  } finally {
    loading.value = false
  }
}

const updateBoard = async () => {
  if (!editingBoard.value.name.trim()) return
  
  updating.value = true
  try {
    await boardStore.updateBoard(editingBoard.value.id, {
      name: editingBoard.value.name.trim(),
      description: editingBoard.value.description.trim() || null,
      is_public: editingBoard.value.is_public
    })
    
    showEditModal.value = false
    editingBoard.value = null
  } catch (error) {
    console.error('Error updating board:', error)
  } finally {
    updating.value = false
  }
}

const removeFromBoard = async (artworkId) => {
  if (!confirm('Are you sure you want to remove this artwork from the board?')) {
    return
  }
  
  try {
    await boardStore.removeArtworkFromBoard(board.value.id, artworkId)
  } catch (error) {
    console.error('Error removing artwork from board:', error)
  }
}

const handleImageError = (event) => {
  event.target.src = `http://localhost:8001/placeholder/default.jpg?t=${Date.now()}`
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

// Lifecycle
onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  loadBoard()
})

// Watch for route changes
watch(() => route.params.id, () => {
  if (route.params.id) {
    loadBoard()
  }
})
</script>

<style scoped>
.btn-primary {
  @apply bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors;
}

.btn-secondary {
  @apply bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 transition-colors;
}

.visibility-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.visibility-badge.public {
  background: #dbeafe;
  color: #1e40af;
}

.visibility-badge.private {
  background: #f3f4f6;
  color: #6b7280;
}

.artworks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.artwork-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.artwork-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.artwork-image-container {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
}

.artwork-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.artwork-card:hover .artwork-image {
  transform: scale(1.05);
}

.artwork-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.artwork-card:hover .artwork-overlay {
  opacity: 1;
}

.remove-btn {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s ease;
}

.remove-btn:hover {
  background: rgba(255, 255, 255, 1);
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
}

.artwork-artist {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 2px;
}

.artwork-date {
  color: #9ca3af;
  font-size: 12px;
  margin-bottom: 8px;
}

.artwork-source {
  display: inline-block;
  background: #f3f4f6;
  color: #6b7280;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

/* Responsive Design */
@media (max-width: 640px) {
  .artworks-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .artwork-info {
    padding: 12px;
  }
  
  .artwork-title {
    font-size: 14px;
  }
}
</style> 