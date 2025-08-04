<template>
  <div id="app" class="min-h-screen bg-art-cream">
    <router-view />
  </div>
</template>

<script setup>
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