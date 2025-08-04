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
            <router-link to="/gallery" class="text-gray-600 hover:text-gray-900">
              Gallery
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
      <div class="max-w-2xl mx-auto">
        <div class="mb-8">
          <h1 class="text-3xl font-serif font-bold text-gray-900 mb-2">Your Profile</h1>
          <p class="text-gray-600">Your art exploration journey</p>
        </div>

        <!-- User Info -->
        <div class="card p-6 mb-6">
          <h2 class="text-xl font-semibold mb-4">Account Information</h2>
          <div class="space-y-3">
            <div>
              <span class="text-sm font-medium text-gray-500">Username:</span>
              <span class="ml-2 text-gray-900">{{ user?.username }}</span>
            </div>
            <div v-if="user?.email">
              <span class="text-sm font-medium text-gray-500">Email:</span>
              <span class="ml-2 text-gray-900">{{ user.email }}</span>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-500">Member since:</span>
              <span class="ml-2 text-gray-900">{{ formatDate(user?.created_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Stats -->
        <div class="card p-6 mb-6">
          <h2 class="text-xl font-semibold mb-4">Your Stats</h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center">
              <div class="text-3xl font-bold text-primary-600">{{ stats.liked_artworks || 0 }}</div>
              <div class="text-sm text-gray-500">Liked Artworks</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-primary-600">{{ stats.unique_museums || 0 }}</div>
              <div class="text-sm text-gray-500">Museums Visited</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-primary-600">{{ stats.total_ratings || 0 }}</div>
              <div class="text-sm text-gray-500">Artworks Rated</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-primary-600">{{ stats.total_notes || 0 }}</div>
              <div class="text-sm text-gray-500">Notes Added</div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="card p-6">
          <h2 class="text-xl font-semibold mb-4">Quick Actions</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <router-link to="/" class="btn-primary text-center">
              🎲 Explore More Art
            </router-link>
            <router-link to="/gallery" class="btn-secondary text-center">
              🖼️ View Gallery
            </router-link>
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

const user = computed(() => authStore.user)
const stats = ref({})

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const loadStats = async () => {
  try {
    stats.value = await artworkStore.getUserStats()
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script> 