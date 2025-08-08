import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import ExhibitView from '@/views/ExhibitView.vue'
import GalleryView from '@/views/GalleryView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import ProfileView from '@/views/ProfileView.vue'
import BoardsView from '@/views/BoardsView.vue'
import BoardDetailView from '@/views/BoardDetailView.vue'

const routes = [
  {
    path: '/',
    name: 'exhibit',
    component: ExhibitView,
    meta: { requiresAuth: true }
  },
  {
    path: '/gallery',
    name: 'gallery',
    component: GalleryView,
    meta: { requiresAuth: true }
  },
  {
    path: '/boards',
    name: 'boards',
    component: BoardsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/boards/:id',
    name: 'board-detail',
    component: BoardDetailView,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresGuest: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
    return
  }
  
  next()
})

export default router 