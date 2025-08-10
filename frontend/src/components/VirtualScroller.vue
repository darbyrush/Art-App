<template>
  <div 
    ref="containerRef" 
    class="virtual-scroller"
    @scroll="handleScroll"
    :style="{ height: containerHeight + 'px' }"
  >
    <div 
      class="virtual-scroller-content"
      :style="{ height: totalHeight + 'px', transform: `translateY(${offsetY}px)` }"
    >
      <div 
        v-for="item in visibleItems" 
        :key="item.id || item.key || item.index"
        :style="{ height: itemHeight + 'px' }"
        class="virtual-scroller-item"
      >
        <slot 
          :item="item" 
          :index="item.actualIndex"
          :isVisible="true"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { rafThrottle } from '@/utils/performance'

const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  itemHeight: {
    type: Number,
    required: true
  },
  containerHeight: {
    type: Number,
    required: true
  },
  overscan: {
    type: Number,
    default: 5
  },
  scrollToIndex: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['scroll', 'visible-range-change'])

const containerRef = ref(null)
const scrollTop = ref(0)

// Computed properties for virtual scrolling
const totalHeight = computed(() => props.items.length * props.itemHeight)

const visibleRange = computed(() => {
  const startIndex = Math.max(0, Math.floor(scrollTop.value / props.itemHeight) - props.overscan)
  const endIndex = Math.min(
    props.items.length - 1,
    Math.ceil((scrollTop.value + props.containerHeight) / props.itemHeight) + props.overscan
  )
  
  return { startIndex, endIndex }
})

const visibleItems = computed(() => {
  const { startIndex, endIndex } = visibleRange.value
  const items = []
  
  for (let i = startIndex; i <= endIndex; i++) {
    if (props.items[i]) {
      items.push({
        ...props.items[i],
        actualIndex: i,
        key: props.items[i].id || i
      })
    }
  }
  
  return items
})

const offsetY = computed(() => visibleRange.value.startIndex * props.itemHeight)

// Scroll handling with throttling
const handleScroll = rafThrottle((event) => {
  scrollTop.value = event.target.scrollTop
  emit('scroll', { scrollTop: scrollTop.value, visibleRange: visibleRange.value })
})

// Scroll to specific index
const scrollToItem = (index) => {
  if (!containerRef.value || index < 0 || index >= props.items.length) return
  
  const targetScrollTop = index * props.itemHeight
  containerRef.value.scrollTop = targetScrollTop
}

// Watch for scrollToIndex changes
watch(() => props.scrollToIndex, (newIndex) => {
  if (newIndex !== null && newIndex >= 0) {
    nextTick(() => scrollToItem(newIndex))
  }
})

// Emit visible range changes
watch(visibleRange, (newRange) => {
  emit('visible-range-change', newRange)
}, { deep: true })

// Expose methods
defineExpose({
  scrollToItem,
  scrollTop: computed(() => scrollTop.value),
  visibleRange: computed(() => visibleRange.value)
})

onMounted(() => {
  // Initial scroll position if needed
  if (props.scrollToIndex !== null && props.scrollToIndex >= 0) {
    nextTick(() => scrollToItem(props.scrollToIndex))
  }
})
</script>

<style scoped>
.virtual-scroller {
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}

.virtual-scroller-content {
  position: relative;
  will-change: transform;
}

.virtual-scroller-item {
  position: relative;
  width: 100%;
}
</style>
