<template>
  <div class="artwork-card bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
    <!-- Image Container -->
    <div class="relative aspect-square overflow-hidden">
      <!-- Loading State -->
      <div v-if="imageState.loading" class="absolute inset-0 flex items-center justify-center bg-gray-100">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      
      <!-- Error State -->
      <div v-else-if="imageState.error" class="absolute inset-0 flex items-center justify-center bg-gray-100">
        <div class="text-center">
          <div class="text-4xl mb-2">🖼️</div>
          <p class="text-sm text-gray-500">Image unavailable</p>
        </div>
      </div>
      
      <!-- Image -->
      <img
        v-show="!imageState.loading && !imageState.error"
        :src="imageState.optimizedUrl"
        :alt="artwork.title"
        class="w-full h-full object-cover transition-opacity duration-300"
        :class="{ 'opacity-0': imageState.loading }"
        @load="handleImageLoad"
        @error="handleImageError"
        @click="$emit('click', artwork)"
      >
      
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
import { ref, computed, onMounted } from 'vue'
import { getOptimizedImageUrl, getFallbackImageUrl } from '@/utils/imageUtils'

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
  originalUrl: props.artwork.image_url,
  optimizedUrl: getOptimizedImageUrl(props.artwork.image_url, 'gallery'),
  fallbackUrl: getFallbackImageUrl(props.artwork.source),
  loading: true,
  error: false,
  loaded: false
})

const handleImageLoad = () => {
  imageState.value.loading = false
  imageState.value.loaded = true
}

const handleImageError = () => {
  imageState.value.loading = false
  imageState.value.error = true
  
  // Try fallback image
  if (imageState.value.optimizedUrl !== imageState.value.fallbackUrl) {
    imageState.value.optimizedUrl = imageState.value.fallbackUrl
    imageState.value.loading = true
    imageState.value.error = false
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

// Reset image state when artwork changes
onMounted(() => {
  imageState.value = {
    originalUrl: props.artwork.image_url,
    optimizedUrl: getOptimizedImageUrl(props.artwork.image_url, 'gallery'),
    fallbackUrl: getFallbackImageUrl(props.artwork.source),
    loading: true,
    error: false,
    loaded: false
  }
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