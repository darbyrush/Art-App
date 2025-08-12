<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <!-- Header Actions -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl sm:text-3xl font-serif font-bold text-gray-900">Your Boards</h1>
        <button 
          @click="showCreateModal = true"
          class="btn-primary text-sm sm:text-base px-3 py-2"
        >
          + New Board
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading && boards.length === 0" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading your boards...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="boards.length === 0 && !loading" class="text-center py-12">
        <div class="text-6xl mb-4">📋</div>
        <h2 class="text-2xl font-serif font-bold mb-2">No Boards Yet</h2>
        <p class="text-gray-600 mb-6">Create your first board to organize your favorite artworks!</p>
        <button @click="showCreateModal = true" class="btn-primary px-6 py-3">
          Create Your First Board
        </button>
      </div>

      <!-- Boards Grid -->
      <div v-else class="boards-grid">
        <div 
          v-for="board in boards"
          :key="board.id"
          class="board-card"
          @click="openBoard(board)"
        >
          <div class="board-header">
            <h3 class="board-title">{{ board.name }}</h3>
            <div class="board-actions">
              <button 
                @click.stop="editBoard(board)"
                class="action-btn"
                title="Edit board"
              >
                ✏️
              </button>
              <button 
                @click.stop="deleteBoard(board.id)"
                class="action-btn text-red-500"
                title="Delete board"
              >
                🗑️
              </button>
            </div>
          </div>
          
          <div class="board-content">
            <p v-if="board.description" class="board-description">{{ board.description }}</p>
            <div class="board-meta">
              <span class="artwork-count">{{ board.artwork_count }} artwork{{ board.artwork_count !== 1 ? 's' : '' }}</span>
              <span class="visibility-badge" :class="board.is_public ? 'public' : 'private'">
                {{ board.is_public ? 'Public' : 'Private' }}
              </span>
            </div>
            <div class="board-date">
              Created {{ formatDate(board.created_at) }}
            </div>
          </div>
        </div>
      </div>
    </main>

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

    <!-- Edit Board Modal -->
    <div v-if="showEditModal && editingBoard" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
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
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBoardStore } from '@/stores/board'

const router = useRouter()
const authStore = useAuthStore()
const boardStore = useBoardStore()

// Reactive data
const loading = ref(false)
const creating = ref(false)
const updating = ref(false)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingBoard = ref(null)

const newBoard = ref({
  name: '',
  description: '',
  is_public: false
})

// Computed
const boards = computed(() => boardStore.boards)

// Methods
const loadBoards = async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  loading.value = true
  try {
    await boardStore.loadUserBoards()
  } catch (error) {
    console.error('Error loading boards:', error)
  } finally {
    loading.value = false
  }
}

const createBoard = async () => {
  if (!newBoard.value.name.trim()) return
  
  creating.value = true
  try {
    await boardStore.createBoard({
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
  } catch (error) {
    console.error('Error creating board:', error)
  } finally {
    creating.value = false
  }
}

const editBoard = (board) => {
  editingBoard.value = {
    id: board.id,
    name: board.name,
    description: board.description || '',
    is_public: board.is_public
  }
  showEditModal.value = true
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

const deleteBoard = async (boardId) => {
  if (!confirm('Are you sure you want to delete this board? This action cannot be undone.')) {
    return
  }
  
  try {
    await boardStore.deleteBoard(boardId)
  } catch (error) {
    console.error('Error deleting board:', error)
  }
}

const openBoard = (board) => {
  router.push(`/boards/${board.id}`)
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
  loadBoards()
})
</script>

<style scoped>
.btn-primary {
  @apply bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors;
}

.btn-secondary {
  @apply bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 transition-colors;
}

.boards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.board-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.board-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.board-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.board-title {
  font-family: 'Georgia', serif;
  font-weight: bold;
  font-size: 18px;
  color: #1f2937;
  margin: 0;
}

.board-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: none;
  border: none;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.action-btn:hover {
  background-color: #f3f4f6;
}

.board-content {
  padding: 16px 20px;
}

.board-description {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 12px;
  line-height: 1.4;
}

.board-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.artwork-count {
  color: #374151;
  font-size: 14px;
  font-weight: 500;
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

.board-date {
  color: #9ca3af;
  font-size: 12px;
}

/* Responsive Design */
@media (max-width: 640px) {
  .boards-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .board-header {
    padding: 12px 16px;
  }
  
  .board-content {
    padding: 12px 16px;
  }
  
  .board-title {
    font-size: 16px;
  }
}
</style> 