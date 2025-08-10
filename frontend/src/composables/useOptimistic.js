import { ref } from 'vue'

export function useOptimistic() {
  const isOptimistic = ref(false)
  
  const withOptimistic = async (optimisticUpdate, apiCall, rollbackOnError = true) => {
    try {
      // Apply optimistic update immediately
      isOptimistic.value = true
      const rollback = optimisticUpdate()
      
      // Make the actual API call
      const result = await apiCall()
      
      // Success - keep the optimistic update
      isOptimistic.value = false
      return result
      
    } catch (error) {
      // Error - rollback if requested
      if (rollbackOnError && typeof rollback === 'function') {
        rollback()
      }
      isOptimistic.value = false
      throw error
    }
  }
  
  return {
    isOptimistic,
    withOptimistic
  }
}
