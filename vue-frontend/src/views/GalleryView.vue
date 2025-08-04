<template>
  <div class="min-h-screen bg-art-cream">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <div class="flex items-center">
            <router-link to="/" class="text-2xl font-serif font-bold text-gray-900">🎨 Art Explorer</router-link>
          </div>
          <nav class="flex items-center space-x-4">
            <router-link to="/" class="text-gray-600 hover:text-gray-900">
              Home
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
      <div class="mb-8">
        <h1 class="text-3xl font-serif font-bold text-gray-900 mb-2">Your Gallery</h1>
        <p class="text-gray-600">Your collection of liked artworks</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading your gallery...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="likedArtworks.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">🖼️</div>
        <h2 class="text-2xl font-serif font-bold mb-2">Your gallery is empty</h2>
        <p class="text-gray-600 mb-6">Start exploring artworks and like them to build your collection!</p>
        <router-link to="/" class="btn-primary">
          Start Exploring
        </router-link>
      </div>

      <!-- Gallery Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div
          v-for="artwork in likedArtworks"
          :key="artwork.id"
          class="artwork-card group"
        >
          <div class="relative">
            <img
              :src="artwork.image_url"
              :alt="artwork.title"
              class="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300"
            >
            <div class="absolute top-2 right-2">
              <span class="text-red-500 text-xl">❤️</span>
            </div>
          </div>
          <div class="p-4">
            <h3 class="font-serif font-bold text-lg mb-1 truncate">{{ artwork.title }}</h3>
            <p class="text-gray-600 text-sm mb-2">by {{ artwork.artist }}</p>
            <div class="text-xs text-gray-500 mb-2">
              📅 {{ artwork.date }} • 🌍 {{ artwork.origin }}
            </div>
            <div class="text-xs text-gray-400">{{ artwork.source }}</div>
          </div>
        </div>
      </div>
    </main>
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

const loading = ref(false)
const likedArtworks = computed(() => artworkStore.likedArtworks)

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const loadLikedArtworks = async () => {
  loading.value = true
  try {
    await artworkStore.loadLikedArtworks()
  } catch (error) {
    console.error('Error loading liked artworks:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadLikedArtworks()
})
</script> 