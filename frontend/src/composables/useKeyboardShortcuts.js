import { onMounted, onBeforeUnmount } from 'vue'

export function useKeyboardShortcuts(shortcuts) {
  const handleKeydown = (event) => {
    // Don't trigger shortcuts when typing in input fields
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
      return
    }
    
    const key = event.key.toLowerCase()
    const ctrl = event.ctrlKey
    const shift = event.shiftKey
    const alt = event.altKey
    
    // Check each shortcut
    for (const [keyCombo, handler] of Object.entries(shortcuts)) {
      const [keyChar, modifiers = {}] = keyCombo.split('+')
      
      if (key === keyChar.toLowerCase() &&
          modifiers.ctrl === ctrl &&
          modifiers.shift === shift &&
          modifiers.alt === alt) {
        
        event.preventDefault()
        handler(event)
        break
      }
    }
  }
  
  onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
  })
  
  onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleKeydown)
  })
}
