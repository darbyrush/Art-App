<template>
  <div class="animate-pulse">
    <div
      v-if="type === 'card'"
      class="bg-white rounded-lg shadow-md p-4"
    >
      <div class="bg-gray-300 rounded h-48 mb-4"></div>
      <div class="space-y-2">
        <div class="bg-gray-300 h-4 rounded w-3/4"></div>
        <div class="bg-gray-300 h-4 rounded w-1/2"></div>
      </div>
    </div>
    
    <div
      v-else-if="type === 'avatar'"
      class="bg-gray-300 rounded-full"
      :class="sizeClasses[size]"
    ></div>
    
    <div
      v-else-if="type === 'text'"
      class="space-y-2"
    >
      <div
        v-for="i in lines"
        :key="i"
        class="bg-gray-300 h-4 rounded"
        :class="lineWidths[i - 1] || 'w-full'"
      ></div>
    </div>
    
    <div
      v-else
      class="bg-gray-300 rounded"
      :class="[sizeClasses[size], 'animate-pulse']"
    ></div>
  </div>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['card', 'avatar', 'text', 'default'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  lines: {
    type: Number,
    default: 3
  }
})

const sizeClasses = {
  sm: 'w-8 h-8',
  md: 'w-12 h-12',
  lg: 'w-16 h-16',
  xl: 'w-24 h-24'
}

const lineWidths = ['w-full', 'w-3/4', 'w-1/2', 'w-2/3']
</script>
