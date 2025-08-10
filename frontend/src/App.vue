<template>
  <div id="app">
    <AppHeader />
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