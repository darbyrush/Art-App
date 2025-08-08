<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-3 sm:py-4">
          <div class="flex items-center space-x-2 sm:space-x-4">
            <h1 class="text-lg sm:text-2xl font-serif font-bold text-gray-900">🖼️ Gallery</h1>
            <nav class="flex space-x-2 sm:space-x-4">
              <router-link to="/" class="text-sm sm:text-base text-gray-600 hover:text-gray-900 px-2 py-1 rounded">Exhibit</router-link>
              <router-link to="/boards" class="text-sm sm:text-base text-gray-600 hover:text-gray-900 px-2 py-1 rounded">Boards</router-link>
              <router-link to="/profile" class="text-sm sm:text-base text-gray-600 hover:text-gray-900 px-2 py-1 rounded">Profile</router-link>
            </nav>
          </div>
          <div class="flex items-center space-x-2">
            <button 
              @click="showBoardModal = true"
              class="btn-primary text-sm px-3 py-2"
            >
              Add to Board
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
        <p class="mt-4 text-gray-600">Loading your gallery...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="artworks.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">🎨</div>
        <h2 class="text-2xl font-serif font-bold mb-2">No Liked Artworks</h2>
        <p class="text-gray-600 mb-6">Start exploring and liking artworks to build your gallery!</p>
        <router-link to="/" class="btn-primary px-6 py-3">
          Start Exploring
        </router-link>
      </div>

      <!-- Artworks Grid -->
      <div v-else class="artworks-grid">
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
              <div class="overlay-actions">
                <button 
                  @click="likeArtwork(artwork.id, false)"
                  class="action-btn"
                  title="Unlike artwork"
                >
                  ❌
                </button>
                <button 
                  @click="addToBoard(artwork)"
                  class="action-btn"
                  title="Add to board"
                >
                  📋
                </button>
              </div>
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
    </main>

    <!-- Add to Board Modal -->
    <div v-if="showBoardModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold mb-4">Add to Board</h3>
        
        <div v-if="selectedArtwork" class="mb-4 p-3 bg-gray-50 rounded">
          <p class="text-sm text-gray-600">Adding: <strong>{{ selectedArtwork.title }}</strong></p>
        </div>
        
        <div v-if="boards.length === 0" class="text-center py-4">
          <p class="text-gray-600 mb-4">You don't have any boards yet.</p>
          <button 
            @click="createNewBoard"
            class="btn-primary px-4 py-2"
          >
            Create Your First Board
          </button>
        </div>
        
        <div v-else class="space-y-2 max-h-60 overflow-y-auto">
          <div 
            v-for="board in boards"
            :key="board.id"
            @click="addArtworkToBoard(board.id)"
            class="board-option"
          >
            <div class="flex justify-between items-center">
              <div>
                <h4 class="font-medium text-gray-900">{{ board.name }}</h4>
                <p v-if="board.description" class="text-sm text-gray-600">{{ board.description }}</p>
                <span class="text-xs text-gray-500">{{ board.artwork_count }} artwork{{ board.artwork_count !== 1 ? 's' : '' }}</span>
              </div>
              <span class="visibility-badge" :class="board.is_public ? 'public' : 'private'">
                {{ board.is_public ? 'Public' : 'Private' }}
              </span>
            </div>
          </div>
        </div>
        
        <div class="flex space-x-3 mt-6">
          <button 
            @click="showBoardModal = false"
            class="btn-secondary flex-1"
          >
            Cancel
          </button>
          <button 
            @click="createNewBoard"
            class="btn-primary flex-1"
          >
            New Board
          </button>
        </div>
      </div>
    </div>

    <!-- Create Board Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold mb-4">Create New Board</h3>
        
        <form @submit.prevent="createBoard">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Board Name</label>
            <input
              v-model="newBoard.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Enter board name..."
            >
          </div>
          
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Description (Optional)</label>
            <textarea
              v-model="newBoard.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Describe your board..."
            ></textarea>
          </div>
          
          <div class="mb-6">
            <label class="flex items-center">
              <input
                v-model="newBoard.is_public"
                type="checkbox"
                class="mr-2"
              >
              <span class="text-sm text-gray-700">Make this board public</span>
            </label>
          </div>
          
          <div class="flex space-x-3">
            <button 
              type="button"
              @click="showCreateModal = false"
              class="btn-secondary flex-1"
            >
              Cancel
            </button>
            <button 
              type="submit"
              class="btn-primary flex-1"
              :disabled="creating"
            >
              {{ creating ? 'Creating...' : 'Create Board' }}
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
import { useArtworkStore } from '@/stores/artwork'
import { useBoardStore } from '@/stores/board'
import { getOptimizedImageUrl } from '@/utils/imageUtils'

const router = useRouter()
const authStore = useAuthStore()
const artworkStore = useArtworkStore()
const boardStore = useBoardStore()

// Reactive data
const loading = ref(false)
const creating = ref(false)
const showBoardModal = ref(false)
const showCreateModal = ref(false)
const selectedArtwork = ref(null)

const newBoard = ref({
  name: '',
  description: '',
  is_public: false
})

// Computed
const artworks = computed(() => artworkStore.likedArtworks)
const boards = computed(() => boardStore.boards)

// Methods
const loadData = async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  loading.value = true
  try {
    await Promise.all([
      artworkStore.loadLikedArtworks(),
      boardStore.loadUserBoards()
    ])
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

const likeArtwork = async (artworkId, liked) => {
  try {
    await artworkStore.likeArtwork(artworkId, liked)
  } catch (error) {
    console.error('Error updating like:', error)
  }
}

const addToBoard = (artwork) => {
  selectedArtwork.value = artwork
  showBoardModal.value = true
}

const addArtworkToBoard = async (boardId) => {
  if (!selectedArtwork.value) return
  
  try {
    await boardStore.addArtworkToBoard(boardId, selectedArtwork.value.id)
    showBoardModal.value = false
    selectedArtwork.value = null
  } catch (error) {
    console.error('Error adding artwork to board:', error)
  }
}

const createNewBoard = () => {
  showBoardModal.value = false
  showCreateModal.value = true
}

const createBoard = async () => {
  if (!newBoard.value.name.trim()) return
  
  creating.value = true
  try {
    const newBoardData = await boardStore.createBoard({
      name: newBoard.value.name.trim(),
      description: newBoard.value.description.trim() || null,
      is_public: newBoard.value.is_public
    })
    
    // Reset form
    newBoard.value = {
      name: '',
      description: '',
      is_public: false
    }
    showCreateModal.value = false
    
    // If we have a selected artwork, add it to the new board
    if (selectedArtwork.value) {
      await boardStore.addArtworkToBoard(newBoardData.id, selectedArtwork.value.id)
      selectedArtwork.value = null
    }
  } catch (error) {
    console.error('Error creating board:', error)
  } finally {
    creating.value = false
  }
}

const handleImageError = (event) => {
  event.target.src = `http://localhost:8001/placeholder/default.jpg?t=${Date.now()}`
}

// Lifecycle
onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  loadData()
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

.overlay-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s ease;
}

.action-btn:hover {
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

.board-option {
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.board-option:hover {
  background-color: #f9fafb;
  border-color: #d1d5db;
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