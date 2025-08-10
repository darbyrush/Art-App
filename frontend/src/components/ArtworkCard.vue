<template>
  <div 
    class="card overflow-hidden hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 cursor-pointer group"
    @click="handleCardClick"
  >
    <!-- Image Container with Optimized Loading -->
    <div class="relative aspect-[4/3] bg-gray-100 overflow-hidden">
      <OptimizedImage
        :src="artwork.image_url"
        :alt="artwork.title || 'Artwork'"
        aspect-ratio="4/3"
        :lazy="true"
        :priority="showFavoriteButton ? 'high' : 'normal'"
        :show-progress="false"
        @click="handleCardClick"
      />
      
      <!-- Favorite Button -->
      <button
        v-if="showFavoriteButton"
        @click.stop="toggleFavorite"
        class="absolute top-2 right-2 p-2 bg-white/80 backdrop-blur-sm rounded-full shadow-md hover:bg-white transition-all duration-200 z-10"
        :class="{ 'bg-red-100': isFavorited }"
      >
        <svg 
          class="w-4 h-4 transition-colors duration-200" 
          :class="isFavorited ? 'text-red-500 fill-current' : 'text-gray-600'"
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path 
            v-if="isFavorited"
            fill-rule="evenodd" 
            d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" 
            clip-rule="evenodd" 
          />
          <path 
            v-else
            d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" 
          />
        </svg>
      </button>
    </div>

    <!-- Content -->
    <div class="p-4">
      <!-- Title -->
      <h3 class="font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
        {{ artwork.title || 'Untitled' }}
      </h3>
      
      <!-- Artist -->
      <p v-if="artwork.artist" class="text-sm text-gray-600 mb-2 line-clamp-1">
        by {{ artwork.artist }}
      </p>
      
      <!-- Museum/Collection -->
      <p v-if="artwork.museum" class="text-xs text-gray-500 mb-2 line-clamp-1">
        {{ artwork.museum }}
      </p>
      
      <!-- Year -->
      <p v-if="artwork.year" class="text-xs text-gray-500">
        {{ artwork.year }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useArtworkStore } from '@/stores/artwork'
import OptimizedImage from './OptimizedImage.vue'

const props = defineProps({
  artwork: {
    type: Object,
    required: true
  },
  showFavoriteButton: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click', 'favorite-toggle'])

const router = useRouter()
const artworkStore = useArtworkStore()

// Computed properties
const isFavorited = computed(() => {
  return artworkStore.isFavorited(props.artwork.id)
})

// Methods
const handleCardClick = () => {
  emit('click', props.artwork)
  // Navigate to artwork detail if available
  if (props.artwork.id) {
    router.push(`/artwork/${props.artwork.id}`)
  }
}

const toggleFavorite = async (event) => {
  event.stopPropagation()
  
  try {
    if (isFavorited.value) {
      await artworkStore.removeFavorite(props.artwork.id)
    } else {
      await artworkStore.addFavorite(props.artwork.id)
    }
    emit('favorite-toggle', props.artwork, !isFavorited.value)
  } catch (error) {
    console.error('Error toggling favorite:', error)
  }
}
</script>

<style scoped>
/* Line clamping utilities */
.line-clamp-1 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
}

.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

/* Smooth transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

.transition-colors {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.transition-transform {
  transition-property: transform;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}
</style> 