<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Filters Section -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between py-3">
          <div class="flex items-center space-x-4">
            <button 
              @click="showFilters = !showFilters"
              class="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <span class="text-sm font-medium">🔍 Filters</span>
              <span :class="showFilters ? 'rotate-180' : ''" class="transition-transform duration-200">▼</span>
            </button>
            <div v-if="hasActiveFilters" class="flex items-center space-x-2">
              <span class="text-xs text-gray-500">Active filters:</span>
              <div class="flex space-x-1">
                <span v-if="filters.sources && filters.sources.length > 0 && !filters.sources.includes('all')" 
                      class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                  {{ filters.sources.length === 1 ? filters.sources[0] : `${filters.sources.length} sources` }}
                </span>
                <span v-if="filters.artist" 
                      class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                  {{ filters.artist }}
                </span>
                <span v-if="filters.dateFrom || filters.dateTo" 
                      class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-800">
                  Date range
                </span>
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <button 
              @click="showBoardModal = true"
              class="btn-primary text-sm px-3 py-2"
            >
              Add to Board
            </button>
            <span class="text-sm text-gray-500">{{ filteredCount }} artworks</span>
            <button 
              v-if="hasActiveFilters"
              @click="clearAllFilters"
              class="text-xs text-red-600 hover:text-red-800 transition-colors"
            >
              Clear all
            </button>
          </div>
        </div>
        
        <!-- Filter Panel -->
        <div v-if="showFilters" class="pb-4 border-t border-gray-100 pt-4 transition-all duration-300">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            
            <!-- Source Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Museum/Source</label>
              <select 
                v-model="filters.sources" 
                multiple
                class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
              >
                <option value="all">All Sources</option>
                <option v-for="source in filterOptions.sources" :key="source" :value="source">
                  {{ source }}
                </option>
              </select>
              <p class="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple</p>
            </div>
            
            <!-- Artist Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Artist</label>
              <select 
                v-model="filters.artist" 
                class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
              >
                <option value="">All Artists</option>
                <option v-for="artist in filterOptions.artists" :key="artist" :value="artist">
                  {{ artist }}
                </option>
              </select>
            </div>
            
            <!-- Date Range Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
              <div class="space-y-2">
                <input 
                  v-model="filters.dateFrom" 
                  type="number" 
                  :min="filterOptions.dateRange?.min" 
                  :max="filterOptions.dateRange?.max"
                  placeholder="From year"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
                >
                <input 
                  v-model="filters.dateTo" 
                  type="number" 
                  :min="filters.dateFrom || filterOptions.dateRange?.min" 
                  :max="filterOptions.dateRange?.max"
                  placeholder="To year"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
                >
              </div>
            </div>
            
            <!-- Sort Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
              <select 
                v-model="filters.sortBy" 
                @change="onSortChange"
                class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
              >
                <option v-for="option in filterOptions.sortOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>
            
          </div>
          
          <!-- Filter Actions -->
          <div class="flex justify-between items-center mt-4 pt-4 border-t border-gray-100">
            <div class="text-xs text-gray-500">
              Available: {{ filterOptions.totalCount }} total artworks
            </div>
            <div class="flex space-x-2">
              <button 
                @click="clearAllFilters"
                class="px-3 py-1 text-xs text-gray-600 hover:text-gray-800 transition-colors"
              >
                Reset
              </button>
              <button 
                @click="applyFilters"
                class="px-4 py-1 bg-primary-600 text-white text-xs rounded-md hover:bg-primary-700 transition-colors"
              >
                Apply Filters
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">{{ loadingMessage }}</p>
      </div>

      <!-- Empty State -->
              <div v-else-if="artworks && artworks.length === 0 && !loading" class="text-center py-12">
        <div class="text-6xl mb-4">{{ hasActiveFilters ? '🔍' : '🎨' }}</div>
        <h2 class="text-2xl font-serif font-bold mb-2">
          {{ hasActiveFilters ? 'No Matching Artworks' : 'No Liked Artworks' }}
        </h2>
        <p class="text-gray-600 mb-6">
          {{ hasActiveFilters 
            ? 'Try adjusting your filters to see more artworks.' 
            : 'Start exploring and liking artworks to build your gallery!' 
          }}
        </p>
        <div class="space-x-3">
          <button 
            v-if="hasActiveFilters"
            @click="clearAllFilters"
            class="btn-secondary px-6 py-3"
          >
            Clear Filters
          </button>
          <router-link to="/" class="btn-primary px-6 py-3">
            {{ hasActiveFilters ? 'Browse All Art' : 'Start Exploring' }}
          </router-link>
        </div>
      </div>

      <!-- Artworks Grid -->
      <div v-else-if="artworks" class="artworks-container">
        <!-- Use Virtual Scroller for large lists -->
        <VirtualScroller
          v-if="artworks && artworks.length > 50"
          :items="artworks || []"
          :item-height="320"
          :container-height="600"
          :overscan="10"
          class="virtual-artworks-grid"
        >
          <template #default="{ item: artwork }">
            <div class="artwork-card-wrapper">
              <div class="artwork-card">
                <div class="artwork-image-container">
                  <OptimizedImage
                    :src="artwork.image_url"
                    :alt="artwork.title"
                    aspect-ratio="1"
                    :lazy="true"
                    :priority="'normal'"
                    @error="handleImageError"
                  />
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
          </template>
        </VirtualScroller>
        
        <!-- Regular grid for smaller lists -->
        <div v-else class="artworks-grid">
          <div 
            v-for="artwork in (artworks || [])"
            :key="artwork.id"
            class="artwork-card"
          >
            <div class="artwork-image-container">
              <OptimizedImage
                :src="artwork.image_url"
                :alt="artwork.title"
                aspect-ratio="1"
                :lazy="true"
                :priority="'normal'"
                @error="handleImageError"
              />
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
                  <button 
                    @click="showRatingModal = true; selectedArtwork = artwork"
                    class="action-btn"
                    title="Rate artwork"
                  >
                    ⭐
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
          <div class="text-4xl mb-3">📋</div>
          <p class="text-gray-600 mb-4">You don't have any boards yet.</p>
          <button 
            @click="createNewBoard"
            class="btn-primary px-4 py-2"
          >
            Create Your First Board
          </button>
        </div>
        
        <div v-else>
          <div class="flex justify-between items-center mb-3">
            <p class="text-sm text-gray-600">Choose from {{ filteredBoards.length }} board{{ filteredBoards.length !== 1 ? 's' : '' }}:</p>
            <button 
              @click="createNewBoard" 
              class="text-xs text-blue-600 hover:text-blue-800"
              :disabled="creating"
            >
              + New Board
            </button>
          </div>
          
          <!-- Board Search -->
          <div v-if="boards.length > 3" class="mb-3">
            <input
              v-model="boardSearch"
              type="text"
              placeholder="Search boards..."
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
          </div>
          <div class="space-y-2 max-h-60 overflow-y-auto">
            <div 
              v-for="board in filteredBoards"
              :key="board.id"
              @click="!creating && addArtworkToBoard(board.id)"
              class="board-option"
              :class="{ 'opacity-50 cursor-not-allowed': creating }"
            >
              <div class="flex justify-between items-center">
                <div>
                  <h4 class="font-medium text-gray-900">{{ board.name }}</h4>
                  <p v-if="board.description" class="text-sm text-gray-600">{{ board.description }}</p>
                  <span class="text-xs text-gray-500">{{ board.artwork_count }} artwork{{ board.artwork_count !== 1 ? 's' : '' }}</span>
                </div>
                <div class="flex items-center space-x-2">
                  <span v-if="creating" class="text-xs text-blue-600">Adding...</span>
                  <span class="visibility-badge" :class="board.is_public ? 'public' : 'private'">
                    {{ board.is_public ? 'Public' : 'Private' }}
                  </span>
                </div>
              </div>
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
      <div class="bg-white rounded-lg p-6 max-w-lg w-full">
        <h3 class="text-lg font-semibold mb-4">Create New Board</h3>
        
        <!-- Board Templates -->
        <div class="mb-6">
          <p class="text-sm font-medium text-gray-700 mb-3">Quick Templates:</p>
          <div class="grid grid-cols-2 gap-2">
            <button 
              type="button"
              @click="applyTemplate('favorites')"
              class="template-btn"
            >
              ❤️ Favorites
            </button>
            <button 
              type="button"
              @click="applyTemplate('inspiration')"
              class="template-btn"
            >
              ✨ Inspiration
            </button>
            <button 
              type="button"
              @click="applyTemplate('study')"
              class="template-btn"
            >
              📚 Study Collection
            </button>
            <button 
              type="button"
              @click="applyTemplate('mood')"
              class="template-btn"
            >
              🎨 Mood Board
            </button>
          </div>
        </div>
        
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
                type="checkbox"
                v-model="newBoard.is_public"
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

    <!-- Rating Modal -->
    <div v-if="showRatingModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg p-6 max-w-md w-full modal-content">
        <h3 class="text-lg font-semibold mb-4">Rate Artwork</h3>
        
        <div v-if="selectedArtwork" class="mb-4 p-3 bg-gray-50 rounded">
          <p class="text-sm text-gray-600">Rating: <strong>{{ selectedArtwork.title }}</strong></p>
        </div>
        
        <!-- Star Rating -->
        <div class="flex justify-center space-x-2 mb-6">
          <button
            v-for="star in 5"
            :key="star"
            @click="rateArtwork(star)"
            class="star-btn text-3xl transition-colors duration-200 hover:scale-110"
            :class="star <= selectedRating ? 'text-yellow-400' : 'text-gray-300'"
          >
            ⭐
          </button>
        </div>
        
        <div class="flex space-x-3">
          <button @click="showRatingModal = false" class="btn-secondary flex-1 text-sm sm:text-base">
            Cancel
          </button>
          <button @click="submitRating" class="btn-primary flex-1 text-sm sm:text-base">
            Submit Rating
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useArtworkStore } from '@/stores/artwork'
import { useBoardStore } from '@/stores/board'
import { getOptimizedImageUrl } from '@/utils/imageUtils'
import AppHeader from '@/components/AppHeader.vue'
import VirtualScroller from '@/components/VirtualScroller.vue'
import OptimizedImage from '@/components/OptimizedImage.vue'
import { config } from '@/config'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const artworkStore = useArtworkStore()
const boardStore = useBoardStore()

// Reactive data
const loading = ref(false)
const creating = ref(false)
const showBoardModal = ref(false)
const showCreateModal = ref(false)
const showRatingModal = ref(false)
const selectedArtwork = ref(null)
const selectedRating = ref(0)
const boardSearch = ref('')

const newBoard = ref({
  name: '',
  description: '',
  is_public: false
})

// Filter-related reactive data
const showFilters = ref(false)
const loadingMessage = ref('Loading your gallery...')
const filterOptions = ref({
  artists: [],
  sources: [],
  dateRange: { min: null, max: null },
  sortOptions: [
    { value: 'date_liked', label: 'Recently Liked' },
    { value: 'title', label: 'Title (A-Z)' },
    { value: 'artist', label: 'Artist (A-Z)' },
    { value: 'date', label: 'Date Created' },
    { value: 'source', label: 'Museum/Source' }
  ],
  totalCount: 0
})
const filteredCount = ref(0)
const filters = ref({
  sources: [],
  artist: '',
  dateFrom: '',
  dateTo: '',
  sortBy: 'date_liked'
})

// Computed
const artworks = computed(() => artworkStore.artworks || [])
const boards = computed(() => {
  // Defensive check for boardStore.boards
  if (!boardStore.boards || !Array.isArray(boardStore.boards)) {
    return []
  }
  
  // Sort boards by recently updated, then by name
  return [...boardStore.boards].sort((a, b) => {
    // Defensive checks for required properties
    if (!a || !b) return 0
    
    // First, sort by updated_at (most recent first)
    const dateA = new Date(a.updated_at || a.created_at || 0)
    const dateB = new Date(b.updated_at || b.created_at || 0)
    if (dateB - dateA !== 0) {
      return dateB - dateA
    }
    // If dates are equal, sort by name
    return (a.name || '').localeCompare(b.name || '')
  })
})

const filteredBoards = computed(() => {
  if (!boardSearch.value || !boardSearch.value.trim()) {
    return boards.value || []
  }
  
  const searchTerm = boardSearch.value.toLowerCase()
  return (boards.value || []).filter(board => {
    if (!board) return false
    
    const name = (board.name || '').toLowerCase()
    const description = (board.description || '').toLowerCase()
    
    return name.includes(searchTerm) || description.includes(searchTerm)
  })
})

// Filter-related computed properties
const hasActiveFilters = computed(() => {
  return (
    (filters.value.sources && filters.value.sources.length > 0 && !filters.value.sources.includes('all')) ||
    filters.value.artist ||
    filters.value.dateFrom ||
    filters.value.dateTo ||
    filters.value.sortBy !== 'date_liked'
  )
})

// Methods
const loadData = async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  try {
    loading.value = true
    loadingMessage.value = 'Loading your gallery...'
    
    // Load filter options and artworks in parallel
    await Promise.all([
      loadFilterOptions(),
      loadArtworksWithFilters(),
      boardStore.loadUserBoards()
    ])
  } catch (error) {
    console.error('Error loading data:', error)
    if (error.response?.status === 401) {
      authStore.logout()
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}

const loadFilterOptions = async () => {
  try {
    const options = await artworkStore.getLikedArtworksFilterOptions()
    console.log('Loaded filter options:', options)
    
    // Merge with existing options to preserve sort options fallback
    filterOptions.value = {
      ...filterOptions.value,
      ...options
    }
    filteredCount.value = options.totalCount
  } catch (error) {
    console.error('Error loading filter options:', error)
  }
}

const loadArtworksWithFilters = async () => {
  try {
    loadingMessage.value = hasActiveFilters.value ? 'Applying filters...' : 'Loading your gallery...'
    
    // Clean the filters to ensure proper formatting
    const cleanFilters = {
      sources: filters.value.sources || [],
      artist: filters.value.artist || '',
      dateFrom: filters.value.dateFrom || '',
      dateTo: filters.value.dateTo || '',
      sortBy: filters.value.sortBy || 'date_liked'
    }
    
    console.log('Loading artworks with clean filters:', cleanFilters)
    const artworks = await artworkStore.loadLikedArtworks(cleanFilters)
    console.log('Loaded artworks count:', artworks.length)
    console.log('First artwork title:', artworks[0]?.title)
    filteredCount.value = artworks.length
  } catch (error) {
    console.error('Error loading artworks:', error)
    throw error
  }
}

const applyFilters = async () => {
  loading.value = true
  await loadArtworksWithFilters()
  loading.value = false
}

const clearAllFilters = () => {
  filters.value = {
    sources: [],
    artist: '',
    dateFrom: '',
    dateTo: '',
    sortBy: 'date_liked'
  }
  updateUrlParams()
  applyFilters()
}

const onSortChange = (event) => {
  console.log('🔄 Sort changed to:', event.target.value)
  filters.value.sortBy = event.target.value
  console.log('🔍 Current filters after sort change:', filters.value)
  updateUrlParams()
  applyFilters()
}

// Manual test function for debugging
const testSorting = async (sortType) => {
  console.log('🧪 Manual test - sorting by:', sortType)
  filters.value.sortBy = sortType
  await applyFilters()
}

// URL persistence methods
const updateUrlParams = () => {
  const query = {}
  
  if (filters.value.sources && filters.value.sources.length > 0 && !filters.value.sources.includes('all')) {
    query.sources = filters.value.sources.join(',')
  }
  if (filters.value.artist) {
    query.artist = filters.value.artist
  }
  if (filters.value.dateFrom) {
    query.dateFrom = filters.value.dateFrom
  }
  if (filters.value.dateTo) {
    query.dateTo = filters.value.dateTo
  }
  if (filters.value.sortBy !== 'date_liked') {
    query.sortBy = filters.value.sortBy
  }
  
  // Update URL without triggering navigation
  router.replace({ query })
}

const loadFiltersFromUrl = () => {
  const query = route.query
  
  filters.value = {
    sources: query.sources ? query.sources.split(',') : [],
    artist: query.artist || '',
    dateFrom: query.dateFrom || '',
    dateTo: query.dateTo || '',
    sortBy: query.sortBy || 'date_liked'
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
  boardSearch.value = '' // Clear any previous search
  showBoardModal.value = true
}

const addArtworkToBoard = async (boardId) => {
  if (!selectedArtwork.value) return
  
  try {
    // Add loading state
    creating.value = true
    await boardStore.addArtworkToBoard(boardId, selectedArtwork.value.id)
    
    // Show success message
    alert(`Successfully added "${selectedArtwork.value.title}" to board!`)
    
    showBoardModal.value = false
    selectedArtwork.value = null
  } catch (error) {
    console.error('Error adding artwork to board:', error)
    // Show specific error message to user
    alert(error.message || 'Failed to add artwork to board. Please try again.')
  } finally {
    creating.value = false
  }
}

const createNewBoard = () => {
  showBoardModal.value = false
  showCreateModal.value = true
}

const applyTemplate = (templateType) => {
  const templates = {
    favorites: {
      name: 'My Favorites',
      description: 'A collection of my most loved artworks',
      is_public: false
    },
    inspiration: {
      name: 'Daily Inspiration',
      description: 'Artworks that inspire and motivate me',
      is_public: true
    },
    study: {
      name: 'Art Study Collection',
      description: 'Artworks for learning and analysis',
      is_public: false
    },
    mood: {
      name: 'Mood Board',
      description: 'Visual inspiration for creative projects',
      is_public: false
    }
  }
  
  const template = templates[templateType]
  if (template) {
    newBoard.value = { ...template }
  }
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
    show('Rating submitted successfully!', 'success')
  } catch (error) {
    console.error('Error rating artwork:', error)
    show('Failed to submit rating. Please try again.', 'error')
  }
}

const handleImageError = (event) => {
          event.target.src = `${config.apiBaseUrl}/placeholder/default.jpg?t=${Date.now()}`
}

// Watchers
watch(showBoardModal, (newValue) => {
  if (!newValue) {
    // Clear search when modal closes
    boardSearch.value = ''
    selectedArtwork.value = null
  }
})

// Watch for filter changes and auto-apply
watch(
  () => [filters.value.sources, filters.value.artist, filters.value.dateFrom, filters.value.dateTo, filters.value.sortBy],
  (newValues, oldValues) => {
    // Skip initial load when oldValues is undefined
    if (!oldValues) return
    
    console.log('Filter changed:', { 
      sources: filters.value.sources, 
      artist: filters.value.artist, 
      sortBy: filters.value.sortBy 
    })
    
    // Update URL params immediately
    updateUrlParams()
    
    // Apply filters immediately for sort changes, debounce others
    if (newValues[4] !== oldValues[4]) { // sortBy changed
      applyFilters()
    } else {
      // Debounce other filter changes
      clearTimeout(window.filterTimeout)
      window.filterTimeout = setTimeout(() => {
        applyFilters()
      }, 500)
    }
  },
  { deep: true }
)

// Lifecycle
onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  // Load filters from URL first
  loadFiltersFromUrl()
  
  // Then load data
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

.template-btn {
  @apply px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition-colors text-left;
}

.template-btn:hover {
  @apply border-blue-300 bg-blue-50;
}

.artworks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.artworks-container {
  width: 100%;
}

.virtual-artworks-grid {
  width: 100%;
}

.artwork-card-wrapper {
  padding: 10px;
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

.artwork-card:hover .artwork-overlay,
.artwork-card:focus-within .artwork-overlay {
  opacity: 1;
}

/* Mobile: Always show overlay on touch devices */
@media (hover: none) and (pointer: coarse) {
  .artwork-card .artwork-overlay {
    opacity: 1;
  }
  
  /* Make action buttons more prominent on mobile */
  .action-btn {
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }
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
  touch-action: manipulation;
  min-height: 44px;
  min-width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover,
.action-btn:active {
  background: rgba(255, 255, 255, 1);
}

/* Mobile touch feedback */
@media (hover: none) and (pointer: coarse) {
  .action-btn:active {
    background: rgba(255, 255, 255, 1);
    transform: scale(0.95);
  }
}

/* Star rating buttons - mobile optimized */
.star-btn {
  touch-action: manipulation;
  min-height: 48px;
  min-width: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
}

@media (hover: none) and (pointer: coarse) {
  .star-btn:active {
    transform: scale(0.9);
  }
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
  color: #6c757d;
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
  color: #6c757d;
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
  
  /* Mobile modal improvements */
  .modal-content {
    margin: 16px;
    max-height: calc(100vh - 32px);
    overflow-y: auto;
  }
  
  /* Better mobile button spacing */
  .overlay-actions {
    gap: 12px;
  }
  
  .action-btn {
    padding: 12px 16px;
    font-size: 18px;
  }
}
</style> 