import { ref } from 'vue'

const toasts = ref([])
let nextId = 1

export function useToast() {
  const show = (message, type = 'info', duration = 4000) => {
    const id = nextId++
    const toast = {
      id,
      message,
      type,
      visible: true
    }
    
    toasts.value.push(toast)
    
    // Auto-remove after duration
    setTimeout(() => {
      remove(id)
    }, duration)
    
    return id
  }
  
  const remove = (id) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }
  
  const success = (message, duration) => show(message, 'success', duration)
  const error = (message, duration) => show(message, 'error', duration)
  const warning = (message, duration) => show(message, 'warning', duration)
  
  return {
    toasts,
    show,
    success,
    error,
    warning,
    remove
  }
}
