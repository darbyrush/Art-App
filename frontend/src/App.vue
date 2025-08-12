<template>
  <div id="app">
    <AppHeader>
      <!-- Dynamic title based on route -->
      <template #title>
        <h1 v-if="$route.name === 'Gallery'" class="text-lg sm:text-2xl font-serif font-bold text-gray-900">🖼️ Gallery</h1>
        <h1 v-else-if="$route.name === 'Boards'" class="text-lg sm:text-2xl font-serif font-bold text-gray-900">📋 Boards</h1>
        <h1 v-else-if="$route.name === 'BoardDetail'" class="text-lg sm:text-2xl font-serif font-bold text-gray-900">📋 Board</h1>
        <h1 v-else-if="$route.name === 'Profile'" class="text-lg sm:text-2xl font-serif font-bold text-gray-900">👤 Profile</h1>
        <h1 v-else-if="$route.name === 'Exhibit'" class="text-lg sm:text-2xl font-serif font-bold text-gray-900">🎨 Exhibit</h1>
      </template>
    </AppHeader>
    <ErrorBoundary>
      <main class="min-h-screen bg-gray-50">
        <router-view />
      </main>
    </ErrorBoundary>
    <Toast />
  </div>
</template>

<script setup>
import AppHeader from '@/components/AppHeader.vue'
import Toast from '@/components/Toast.vue'
import ErrorBoundary from '@/components/ErrorBoundary.vue'
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // Initialize auth state from localStorage
  authStore.initializeAuth()
})
</script>

<style scoped>
#app {
  font-family: 'Inter', sans-serif;
}
</style> 