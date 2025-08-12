import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  createBoard as apiCreateBoard,
  getUserBoards,
  getBoard,
  updateBoard as apiUpdateBoard,
  deleteBoard as apiDeleteBoard,
  addArtworkToBoard,
  removeArtworkFromBoard,
  getBoardArtworks
} from '@/utils/apiClient'

export const useBoardStore = defineStore('board', () => {
  const boards = ref([])
  const currentBoard = ref(null)
  const boardArtworks = ref([])
  const loading = ref(false)

  // Computed properties
  const boardsCount = computed(() => boards.value.length)
  const publicBoards = computed(() => boards.value.filter(board => board.is_public))
  const privateBoards = computed(() => boards.value.filter(board => !board.is_public))

  // Actions
  const createBoard = async (boardData) => {
    try {
      loading.value = true
      const newBoard = await apiCreateBoard(boardData)
      boards.value.push(newBoard)
      return newBoard
    } catch (error) {
      console.error('Error creating board:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const loadUserBoards = async () => {
    try {
      loading.value = true
      const userBoards = await getUserBoards()
      boards.value = userBoards
      return userBoards
    } catch (error) {
      console.error('Error loading user boards:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const loadBoard = async (boardId) => {
    try {
      loading.value = true
      const board = await getBoard(boardId)
      currentBoard.value = board
      return board
    } catch (error) {
      console.error('Error loading board:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateBoard = async (boardId, boardData) => {
    try {
      loading.value = true
      const updatedBoard = await apiUpdateBoard(boardId, boardData)
      
      // Update in boards list
      const index = boards.value.findIndex(board => board.id === boardId)
      if (index !== -1) {
        boards.value[index] = updatedBoard
      }
      
      // Update current board if it's the one being updated
      if (currentBoard.value && currentBoard.value.id === boardId) {
        currentBoard.value = updatedBoard
      }
      
      return updatedBoard
    } catch (error) {
      console.error('Error updating board:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteBoard = async (boardId) => {
    try {
      loading.value = true
      await apiDeleteBoard(boardId)
      
      // Remove from boards list
      boards.value = boards.value.filter(board => board.id !== boardId)
      
      // Clear current board if it's the one being deleted
      if (currentBoard.value && currentBoard.value.id === boardId) {
        currentBoard.value = null
        boardArtworks.value = []
      }
      
      return { success: true }
    } catch (error) {
      console.error('Error deleting board:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const addArtworkToBoard = async (boardId, artworkId) => {
    try {
      loading.value = true
      const result = await addArtworkToBoard(boardId, artworkId)
      
      // Reload board artworks if this is the current board
      if (currentBoard.value && currentBoard.value.id === boardId) {
        await loadBoardArtworks(boardId)
      }
      
      // Also reload user boards to update artwork counts
      await loadUserBoards()
      
      return result
    } catch (error) {
      console.error('Error adding artwork to board:', error)
      
      // Provide more specific error messages
      if (error.response?.status === 401) {
        throw new Error('You need to be logged in to add artworks to boards')
      } else if (error.response?.status === 404) {
        throw new Error('Board not found')
      } else if (error.response?.status === 409) {
        throw new Error('This artwork is already in the board')
      } else {
        throw new Error('Failed to add artwork to board. Please try again.')
      }
    } finally {
      loading.value = false
    }
  }

  const removeArtworkFromBoard = async (boardId, artworkId) => {
    try {
      loading.value = true
      const result = await removeArtworkFromBoard(boardId, artworkId)
      
      // Remove from board artworks if this is the current board
      if (currentBoard.value && currentBoard.value.id === boardId) {
        boardArtworks.value = boardArtworks.value.filter(artwork => artwork.id !== artworkId)
      }
      
      return result
    } catch (error) {
      console.error('Error removing artwork from board:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const loadBoardArtworks = async (boardId) => {
    try {
      loading.value = true
      const artworks = await getBoardArtworks(boardId)
      boardArtworks.value = artworks
      return artworks
    } catch (error) {
      console.error('Error loading board artworks:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const clearCurrentBoard = () => {
    currentBoard.value = null
    boardArtworks.value = []
  }

  const getBoardById = (boardId) => {
    return boards.value.find(board => board.id === boardId)
  }

  return {
    // State
    boards,
    currentBoard,
    boardArtworks,
    loading,
    
    // Computed
    boardsCount,
    publicBoards,
    privateBoards,
    
    // Actions
    createBoard,
    loadUserBoards,
    loadBoard,
    updateBoard,
    deleteBoard,
    addArtworkToBoard,
    removeArtworkFromBoard,
    loadBoardArtworks,
    clearCurrentBoard,
    getBoardById
  }
}) 