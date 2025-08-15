<template>
  <div class="mobile-debug-panel bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-lg font-semibold text-blue-800">📱 Mobile Debug Panel</h3>
      <button 
        @click="toggleExpanded" 
        class="text-blue-600 hover:text-blue-800 text-sm"
      >
        {{ isExpanded ? 'Collapse' : 'Expand' }}
      </button>
    </div>
    
    <!-- Device Info Summary -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
      <div class="bg-white p-2 rounded border">
        <div class="text-xs text-gray-500">Device</div>
        <div class="font-medium text-sm">
          {{ deviceStatus.isIOS ? 'iOS' : 'Android' }}
        </div>
      </div>
      <div class="bg-white p-2 rounded border">
        <div class="text-xs text-gray-500">Browser</div>
        <div class="font-medium text-sm">
          {{ deviceStatus.isSafari ? 'Safari' : 'Other' }}
        </div>
      </div>
      <div class="bg-white p-2 rounded border">
        <div class="text-xs text-gray-500">Screen</div>
        <div class="font-medium text-sm">
          {{ deviceInfo.screenWidth }}x{{ deviceInfo.screenHeight }}
        </div>
      </div>
      <div class="bg-white p-2 rounded border">
        <div class="text-xs text-gray-500">Viewport</div>
        <div class="font-medium text-sm">
          {{ deviceInfo.viewportWidth }}x{{ deviceInfo.viewportHeight }}
        </div>
      </div>
    </div>

    <!-- Expanded Details -->
    <div v-if="isExpanded" class="space-y-4">
      <!-- Connection Info -->
      <div class="bg-white p-3 rounded border">
        <h4 class="font-medium text-blue-700 mb-2">🌐 Network Connection</h4>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div><span class="text-gray-600">Type:</span> {{ connectionInfo.effectiveType || 'Unknown' }}</div>
          <div><span class="text-gray-600">Speed:</span> {{ connectionInfo.downlink || 'Unknown' }} Mbps</div>
          <div><span class="text-gray-600">Latency:</span> {{ connectionInfo.rtt || 'Unknown' }}ms</div>
          <div><span class="text-gray-600">Data Saver:</span> {{ connectionInfo.saveData ? 'Yes' : 'No' }}</div>
        </div>
      </div>

      <!-- Device Capabilities -->
      <div class="bg-white p-3 rounded border">
        <h4 class="font-medium text-blue-700 mb-2">⚡ Device Capabilities</h4>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div><span class="text-gray-600">Touch:</span> {{ deviceInfo.maxTouchPoints }} points</div>
          <div><span class="text-gray-600">Memory:</span> {{ deviceInfo.deviceMemory || 'Unknown' }}GB</div>
          <div><span class="text-gray-600">CPU Cores:</span> {{ deviceInfo.hardwareConcurrency || 'Unknown' }}</div>
          <div><span class="text-gray-600">Cookies:</span> {{ deviceInfo.cookieEnabled ? 'Enabled' : 'Disabled' }}</div>
        </div>
      </div>

      <!-- Performance Metrics -->
      <div class="bg-white p-3 rounded border">
        <h4 class="font-medium text-blue-700 mb-2">📊 Performance</h4>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div><span class="text-gray-600">Page Load:</span> {{ performanceMetrics.pageLoadTime || 'Loading...' }}ms</div>
          <div><span class="text-gray-600">DOM Ready:</span> {{ performanceMetrics.domContentLoaded || 'Loading...' }}ms</div>
          <div><span class="text-gray-600">First Paint:</span> {{ performanceMetrics.firstPaint || 'Loading...' }}ms</div>
          <div><span class="text-gray-600">FCP:</span> {{ performanceMetrics.firstContentfulPaint || 'Loading...' }}ms</div>
        </div>
      </div>

      <!-- Recent Events -->
      <div class="bg-white p-3 rounded border">
        <h4 class="font-medium text-blue-700 mb-2">📝 Recent Events</h4>
        <div class="max-h-32 overflow-y-auto">
          <div 
            v-for="(event, index) in recentEvents.slice(-5)" 
            :key="index"
            class="text-xs p-1 border-b border-gray-100"
          >
            <span class="text-gray-500">{{ formatTime(event.timestamp) }}</span>
            <span class="font-medium ml-2">{{ event.action }}</span>
            <span class="text-gray-600 ml-2">{{ event.details || '' }}</span>
          </div>
        </div>
      </div>

      <!-- User Agent -->
      <div class="bg-white p-3 rounded border">
        <h4 class="font-medium text-blue-700 mb-2">🔍 User Agent</h4>
        <div class="text-xs font-mono bg-gray-100 p-2 rounded break-all">
          {{ deviceInfo.userAgent }}
        </div>
      </div>

      <!-- Test Actions -->
      <div class="bg-white p-3 rounded border">
        <h4 class="font-medium text-blue-700 mb-2">🧪 Test Actions</h4>
        <div class="flex flex-wrap gap-2">
          <button 
            @click="testFormInteraction"
            class="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm hover:bg-blue-200"
          >
            Test Form
          </button>
          <button 
            @click="testNetwork"
            class="px-3 py-1 bg-green-100 text-green-700 rounded text-sm hover:bg-green-200"
          >
            Test Network
          </button>
          <button 
            @click="testPerformance"
            class="px-3 py-1 bg-purple-100 text-purple-700 rounded text-sm hover:bg-purple-200"
          >
            Test Performance
          </button>
          <button 
            @click="clearEvents"
            class="px-3 py-1 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200"
          >
            Clear Events
          </button>
        </div>
      </div>
    </div>

    <!-- Status Indicator -->
    <div class="flex items-center justify-between text-sm">
      <div class="flex items-center space-x-2">
        <div 
          :class="[
            'w-2 h-2 rounded-full',
            deviceStatus.isProblematicDevice ? 'bg-red-500' : 'bg-green-500'
          ]"
        ></div>
        <span :class="deviceStatus.isProblematicDevice ? 'text-red-600' : 'text-green-600'">
          {{ deviceStatus.isProblematicDevice ? '⚠️ Problematic Device' : '✅ Normal Device' }}
        </span>
      </div>
      <div class="text-gray-500">
        {{ recentEvents.length }} events tracked
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { mobileAnalytics } from '@/utils/mobileAnalytics'

const isExpanded = ref(false)
const recentEvents = ref([])
const performanceMetrics = ref({})

// Computed properties
const deviceStatus = computed(() => mobileAnalytics.getDeviceStatus())
const deviceInfo = computed(() => deviceStatus.value.deviceInfo)
const connectionInfo = computed(() => deviceInfo.value.connection || {})

// Methods
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

const addEvent = (action, details = '') => {
  recentEvents.value.push({
    action,
    details,
    timestamp: new Date().toISOString()
  })
  
  // Keep only last 20 events
  if (recentEvents.value.length > 20) {
    recentEvents.value = recentEvents.value.slice(-20)
  }
}

const testFormInteraction = () => {
  addEvent('Form Test', 'Simulated form interaction')
  mobileAnalytics.trackMobileBehavior('debug_test', { testType: 'form_interaction' })
}

const testNetwork = () => {
  addEvent('Network Test', 'Simulated network test')
  mobileAnalytics.trackMobileBehavior('debug_test', { testType: 'network' })
}

const testPerformance = () => {
  addEvent('Performance Test', 'Simulated performance test')
  mobileAnalytics.trackMobileBehavior('debug_test', { testType: 'performance' })
}

const clearEvents = () => {
  recentEvents.value = []
}

const updatePerformanceMetrics = () => {
  if ('performance' in window) {
    const perf = performance.getEntriesByType('navigation')[0]
    if (perf) {
      performanceMetrics.value = {
        pageLoadTime: Math.round(perf.loadEventEnd - perf.loadEventStart),
        domContentLoaded: Math.round(perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart),
        firstPaint: Math.round(performance.getEntriesByName('first-paint')[0]?.startTime || 0),
        firstContentfulPaint: Math.round(performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0)
      }
    }
  }
}

// Lifecycle
onMounted(() => {
  updatePerformanceMetrics()
  
  // Update performance metrics periodically
  setInterval(updatePerformanceMetrics, 5000)
  
  // Add initial event
  addEvent('Debug Panel Mounted', 'Component loaded successfully')
  
  // Listen for mobile analytics events
  if (mobileAnalytics.isProblematicDevice()) {
    addEvent('Problematic Device Detected', 'Mobile Safari iOS - Enhanced tracking enabled')
  }
})
</script>

<style scoped>
.mobile-debug-panel {
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
}

.mobile-debug-panel::-webkit-scrollbar {
  width: 6px;
}

.mobile-debug-panel::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.mobile-debug-panel::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.mobile-debug-panel::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
