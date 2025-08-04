import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/utils/apiClient'

export const useArtworkStore = defineStore('artwork', () => {
  const currentArtwork = ref(null)
  const artworkHistory = ref([])
  const likedArtworks = ref([])
  const loading = ref(false)
  const selectedSources = ref(['all'])

  const availableSources = [
    'all',
    'Cleveland Museum of Art',
    'Metropolitan Museum of Art',
    'Art Institute of Chicago',
    'Walters Art Museum',
    'National Gallery of Art',
    'Smithsonian American Art Museum',
    'Harvard Art Museums'
  ]

  const getRandomArtwork = async () => {
    loading.value = true
    try {
      const artwork = await apiClient.getRandomArtwork(selectedSources.value)
      if (artwork) {
        currentArtwork.value = artwork
        artworkHistory.value.unshift(artwork)
        
        // Keep only last 10 artworks in history
        if (artworkHistory.value.length > 10) {
          artworkHistory.value = artworkHistory.value.slice(0, 10)
        }
      }
      return artwork
    } catch (error) {
      console.error('Error fetching artwork:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const likeArtwork = async (artworkId, liked = true) => {
    try {
      await apiClient.likeArtwork(artworkId, liked)
      
      // Update local state
      if (liked) {
        const artwork = artworkHistory.value.find(a => a.id === artworkId)
        if (artwork && !likedArtworks.value.find(a => a.id === artworkId)) {
          likedArtworks.value.push(artwork)
        }
      } else {
        likedArtworks.value = likedArtworks.value.filter(a => a.id !== artworkId)
      }
    } catch (error) {
      console.error('Error liking artwork:', error)
      throw error
    }
  }

  const rateArtwork = async (artworkId, rating) => {
    try {
      await apiClient.rateArtwork(artworkId, rating)
    } catch (error) {
      console.error('Error rating artwork:', error)
      throw error
    }
  }

  const addNote = async (artworkId, note) => {
    try {
      await apiClient.addNote(artworkId, note)
    } catch (error) {
      console.error('Error adding note:', error)
      throw error
    }
  }

  const loadLikedArtworks = async () => {
    try {
      const artworks = await apiClient.getLikedArtworks()
      likedArtworks.value = artworks
    } catch (error) {
      console.error('Error loading liked artworks:', error)
      throw error
    }
  }

  const getUserStats = async () => {
    try {
      return await apiClient.getUserStats()
    } catch (error) {
      console.error('Error loading user stats:', error)
      throw error
    }
  }

  return {
    currentArtwork,
    artworkHistory,
    likedArtworks,
    loading,
    selectedSources,
    availableSources,
    getRandomArtwork,
    likeArtwork,
    rateArtwork,
    addNote,
    loadLikedArtworks,
    getUserStats
  }
}) 