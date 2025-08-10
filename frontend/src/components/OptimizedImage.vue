<template>
  <div 
    ref="imageContainer" 
    class="optimized-image-container"
    :class="{ 
      'loading': !imageLoaded && !imageError,
      'loaded': imageLoaded,
      'error': imageError 
    }"
  >
    <!-- Loading Skeleton -->
    <div 
      v-if="!imageLoaded && !imageError" 
      class="image-skeleton"
      :style="{ aspectRatio: aspectRatio }"
    >
      <div class="skeleton-content">
        <div class="skeleton-shimmer"></div>
      </div>
    </div>
    
    <!-- Low Quality Placeholder -->
    <img
      v-if="showLowQuality && lowQualityUrl"
      :src="lowQualityUrl"
      :alt="alt"
      class="low-quality-placeholder"
      :style="{ aspectRatio: aspectRatio }"
    >
    
    <!-- High Quality Image -->
    <img
      v-if="!imageError"
      ref="imageRef"
      :src="imageUrl"
      :alt="alt"
      :class="imageClasses"
      :style="{ aspectRatio: aspectRatio }"
      @load="handleImageLoad"
      @error="handleImageError"
      @click="$emit('click', $event)"
    >
    
    <!-- Error Fallback -->
    <div 
      v-if="imageError" 
      class="image-error"
      :style="{ aspectRatio: aspectRatio }"
    >
      <div class="error-content">
        <svg class="error-icon" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
        </svg>
        <span class="error-text">{{ errorText }}</span>
        <button 
          v-if="retryable"
          @click="retryLoad"
          class="retry-button"
        >
          Retry
        </button>
      </div>
    </div>
    
    <!-- Loading Progress -->
    <div 
      v-if="showProgress && !imageLoaded && !imageError" 
      class="loading-progress"
    >
      <div class="progress-bar">
        <div 
          class="progress-fill"
          :style="{ width: loadingProgress + '%' }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { createIntersectionObserver } from '@/utils/performance'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: 'Image'
  },
  aspectRatio: {
    type: String,
    default: '16/9'
  },
  lazy: {
    type: Boolean,
    default: true
  },
  priority: {
    type: String,
    default: 'normal', // 'high', 'normal', 'low'
    validator: (value) => ['high', 'normal', 'low'].includes(value)
  },
  showProgress: {
    type: Boolean,
    default: false
  },
  retryable: {
    type: Boolean,
    default: true
  },
  errorText: {
    type: String,
    default: 'Failed to load image'
  }
})

const emit = defineEmits(['load', 'error', 'click'])

// Reactive state
const imageContainer = ref(null)
const imageRef = ref(null)
const imageLoaded = ref(false)
const imageError = ref(false)
const isInViewport = ref(false)
const loadingProgress = ref(0)
const showLowQuality = ref(false)

// Intersection observer for lazy loading
let intersectionObserver = null

// Computed properties
const imageUrl = computed(() => {
  if (!props.src) return null
  
  // Handle both relative and absolute URLs
  if (props.src.startsWith('http')) {
    return props.src
  }
  
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${props.src}`
})

const lowQualityUrl = computed(() => {
  if (!props.src) return null
  
  // Generate low quality version for progressive loading
  const baseUrl = props.src.startsWith('http') ? props.src : `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${props.src}`
  return `${baseUrl}?quality=low&w=100`
})

const imageClasses = computed(() => {
  return [
    'optimized-image',
    {
      'image-loaded': imageLoaded,
      'image-loading': !imageLoaded && !imageError,
      'image-error': imageError,
      'high-priority': props.priority === 'high'
    }
  ]
})

// Methods
const handleImageLoad = () => {
  imageLoaded.value = true
  imageError.value = false
  loadingProgress.value = 100
  
  // Emit load event
  emit('load', {
    src: props.src,
    naturalWidth: imageRef.value?.naturalWidth,
    naturalHeight: imageRef.value?.naturalHeight
  })
  
  // Hide low quality placeholder after a short delay
  setTimeout(() => {
    showLowQuality.value = false
  }, 200)
}

const handleImageError = (event) => {
  imageError.value = true
  imageLoaded.value = false
  loadingProgress.value = 0
  
  emit('error', {
    src: props.src,
    error: event
  })
}

const retryLoad = () => {
  imageError.value = false
  imageLoaded.value = false
  loadingProgress.value = 0
  
  // Force reload by updating src
  if (imageRef.value) {
    const currentSrc = imageRef.value.src
    imageRef.value.src = ''
    nextTick(() => {
      imageRef.value.src = currentSrc
    })
  }
}

const startLoading = () => {
  if (props.lazy && !isInViewport.value) return
  
  // Show low quality placeholder for progressive loading
  if (lowQualityUrl.value) {
    showLowQuality.value = true
  }
  
  // Simulate loading progress for better UX
  if (props.showProgress) {
    const progressInterval = setInterval(() => {
      if (loadingProgress.value < 90) {
        loadingProgress.value += Math.random() * 10
      } else {
        clearInterval(progressInterval)
      }
    }, 100)
  }
}

// Intersection observer setup
const setupIntersectionObserver = () => {
  if (!props.lazy || !imageContainer.value) return
  
  intersectionObserver = createIntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          isInViewport.value = true
          startLoading()
          
          // Disconnect observer once image is in viewport
          if (intersectionObserver) {
            intersectionObserver.disconnect()
            intersectionObserver = null
          }
        }
      })
    },
    {
      rootMargin: '50px', // Start loading 50px before entering viewport
      threshold: 0.1
    }
  )
  
  if (intersectionObserver && imageContainer.value) {
    intersectionObserver.observe(imageContainer.value)
  }
}

// Lifecycle
onMounted(() => {
  // High priority images load immediately
  if (props.priority === 'high') {
    isInViewport.value = true
    startLoading()
  } else if (props.lazy) {
    setupIntersectionObserver()
  } else {
    // Non-lazy images load immediately
    isInViewport.value = true
    startLoading()
  }
})

onUnmounted(() => {
  if (intersectionObserver) {
    intersectionObserver.disconnect()
  }
})

// Watch for src changes
watch(() => props.src, () => {
  imageLoaded.value = false
  imageError.value = false
  loadingProgress.value = 0
  showLowQuality.value = false
  
  if (props.priority === 'high' || !props.lazy) {
    startLoading()
  }
})
</script>

<style scoped>
.optimized-image-container {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.optimized-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.image-loading {
  opacity: 0;
}

.image-loaded {
  opacity: 1;
}

.image-error {
  opacity: 0;
}

.high-priority {
  fetchpriority: high;
}

.image-skeleton {
  width: 100%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.skeleton-shimmer {
  width: 60%;
  height: 60%;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.low-quality-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: blur(2px);
  opacity: 0.7;
  z-index: 1;
}

.optimized-image {
  z-index: 2;
  position: relative;
}

.image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border: 2px dashed #dee2e6;
  color: #6c757d;
}

.error-content {
  text-align: center;
  padding: 1rem;
}

.error-icon {
  width: 3rem;
  height: 3rem;
  margin-bottom: 0.5rem;
  opacity: 0.5;
}

.error-text {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.retry-button {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s ease;
}

.retry-button:hover {
  background: #0056b3;
}

.loading-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(0, 0, 0, 0.1);
  z-index: 3;
}

.progress-bar {
  height: 100%;
  background: #007bff;
  transition: width 0.3s ease;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #007bff, #0056b3);
  transition: width 0.3s ease;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .error-content {
    padding: 0.5rem;
  }
  
  .error-icon {
    width: 2rem;
    height: 2rem;
  }
  
  .error-text {
    font-size: 0.75rem;
  }
}
</style>
