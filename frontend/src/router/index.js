import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/gallery'
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: () => import('@/views/GalleryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/boards',
    name: 'Boards',
    component: () => import('@/views/BoardsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/boards/:id',
    name: 'BoardDetail',
    component: () => import('@/views/BoardDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/exhibit',
    name: 'Exhibit',
    component: () => import('@/views/ExhibitView.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router 