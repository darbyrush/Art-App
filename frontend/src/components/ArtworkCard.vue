<template>
  <div class="artwork-card bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
    <!-- Image Container -->
    <div class="relative aspect-square overflow-hidden">
      <!-- Loading State -->
      <div v-if="imageState.state === 'loading'" class="absolute inset-0 flex items-center justify-center bg-gray-100">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      
      <!-- Error State -->
      <div v-else-if="imageState.state === 'error'" class="absolute inset-0 flex items-center justify-center bg-gray-100">
        <div class="text-center">
          <div class="text-4xl mb-2">🖼️</div>
          <p class="text-sm text-gray-500">Image unavailable</p>
        </div>
      </div>
      
      <!-- Image -->
      <img
        v-show="imageState.state === 'loaded' || imageState.state === 'fallback'"
        :src="imageState.url"
        :alt="artwork.title"
        class="w-full h-full object-cover transition-opacity duration-300"
        :class="{ 'opacity-0': imageState.state === 'loading' }"
        @load="handleImageLoad"
        @error="handleImageError"
        @click="$emit('click', artwork)"
      >
      
      <!-- Optimization Badge -->
      <div v-if="imageState.optimized && imageState.state === 'loaded'" 
           class="absolute top-2 left-2 px-2 py-1 bg-green-500 text-white text-xs rounded-full opacity-75">
        ⚡
      </div>
      
      <!-- Fallback Badge -->
      <div v-if="imageState.state === 'fallback'" 
           class="absolute top-2 left-2 px-2 py-1 bg-yellow-500 text-white text-xs rounded-full opacity-75">
        🖼️
      </div>
      
      <!-- Like Button Overlay -->
      <button
        v-if="showLikeButton"
        @click.stop="toggleLike"
        class="absolute top-2 right-2 p-2 bg-white bg-opacity-80 rounded-full hover:bg-opacity-100 transition-all duration-200"
        :class="{ 'text-red-500': isLiked }"
      >
        <span class="text-lg">{{ isLiked ? '❤️' : '🤍' }}</span>
      </button>
    </div>
    
    <!-- Artwork Info -->
    <div class="p-4">
      <h3 class="font-serif font-bold text-lg mb-1 line-clamp-2">{{ artwork.title }}</h3>
      <p class="text-gray-600 text-sm mb-2 line-clamp-1">by {{ artwork.artist }}</p>
      <div class="text-xs text-gray-500 mb-3">
        📅 {{ artwork.date }} • 🌍 {{ artwork.origin }}
      </div>
      
      <!-- Source Badge -->
      <div class="flex items-center justify-between">
        <span class="inline-block px-2 py-1 text-xs bg-primary-100 text-primary-800 rounded-full">
          {{ getSourceDisplayName(artwork.source) }}
        </span>
        
        <!-- Rating Display -->
        <div v-if="artwork.rating" class="flex items-center">
          <span class="text-yellow-400 text-sm">⭐</span>
          <span class="text-xs text-gray-600 ml-1">{{ artwork.rating }}/5</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { 
  getOptimizedImageUrl, 
  getFallbackImageUrl, 
  loadImageWithFallback,
  IMAGE_STATES 
} from '@/utils/imageUtils'

const props = defineProps({
  artwork: {
    type: Object,
    required: true
  },
  showLikeButton: {
    type: Boolean,
    default: true
  },
  isLiked: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click', 'like', 'unlike'])

const imageState = ref({
  state: IMAGE_STATES.LOADING,
  url: null,
  error: null,
  optimized: false
})

const handleImageLoad = () => {
  imageState.value.state = IMAGE_STATES.LOADED
}

const handleImageError = async () => {
  // Try progressive loading with fallback
  try {
    const result = await loadImageWithFallback(
      props.artwork.image_url, 
      props.artwork.source, 
      'gallery'
    )
    
    imageState.value = result
    
    if (result.state === IMAGE_STATES.ERROR) {
      console.warn('All image loading strategies failed for:', props.artwork.title)
    }
  } catch (error) {
    console.error('Error in progressive image loading:', error)
    imageState.value.state = IMAGE_STATES.ERROR
    imageState.value.error = error.message
  }
}

const toggleLike = () => {
  if (props.isLiked) {
    emit('unlike', props.artwork.id)
  } else {
    emit('like', props.artwork.id)
  }
}

const getSourceDisplayName = (source) => {
  const displayNames = {
    'cleveland': 'Cleveland',
    'met': 'Met',
    'chicago': 'Chicago',
    'walters': 'Walters',
    'national_gallery': 'NGA',
    'smithsonian': 'Smithsonian',
    'harvard': 'Harvard'
  }
  return displayNames[source] || source
}

// Initialize image loading
const initializeImage = async () => {
  if (!props.artwork.image_url) {
    imageState.value = {
      state: IMAGE_STATES.FALLBACK,
      url: getFallbackImageUrl(props.artwork.source),
      error: null,
      optimized: false
    }
    return
  }
  
  // Start with optimized URL
  imageState.value = {
    state: IMAGE_STATES.LOADING,
    url: getOptimizedImageUrl(props.artwork.image_url, 'gallery'),
    error: null,
    optimized: true
  }
}

// Watch for artwork changes
watch(() => props.artwork, initializeImage, { immediate: true })

// Lifecycle
onMounted(() => {
  initializeImage()
})
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.artwork-card {
  cursor: pointer;
}

.artwork-card:hover {
  transform: translateY(-2px);
}
</style> 