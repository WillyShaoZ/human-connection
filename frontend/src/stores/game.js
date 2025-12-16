import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useGameStore = defineStore('game', () => {
  // State
  const playerId = ref('')
  const playerNickname = ref('')
  const roomCode = ref('')
  const isHost = ref(false)
  const gameStatus = ref('waiting') // waiting, playing, ended
  const currentCard = ref(null)
  const players = ref([])

  // Computed
  const playerCount = computed(() => players.value.length)

  const isPlaying = computed(() => gameStatus.value === 'playing')

  const isWaiting = computed(() => gameStatus.value === 'waiting')

  const isEnded = computed(() => gameStatus.value === 'ended')

  // Actions
  function initPlayer() {
    // Generate or retrieve player ID
    let storedId = uni.getStorageSync('player_id')
    if (!storedId) {
      storedId = 'player_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
      uni.setStorageSync('player_id', storedId)
    }
    playerId.value = storedId

    // Retrieve stored nickname if any
    const storedNickname = uni.getStorageSync('player_nickname')
    if (storedNickname) {
      playerNickname.value = storedNickname
    }
  }

  function setNickname(nickname) {
    playerNickname.value = nickname
    uni.setStorageSync('player_nickname', nickname)
  }

  function setRoom(code, host = false) {
    roomCode.value = code
    isHost.value = host
    uni.setStorageSync('current_room', code)
  }

  function updateGameState(state) {
    if (state.status !== undefined) {
      gameStatus.value = state.status
    }
    if (state.current_card !== undefined) {
      currentCard.value = state.current_card
    }
    if (state.players !== undefined) {
      players.value = state.players
      // Check if we're still host
      const me = state.players.find(p => p.player_id === playerId.value)
      if (me) {
        isHost.value = me.is_host
      }
    }
  }

  function setCurrentCard(card) {
    currentCard.value = card
  }

  function addPlayer(player) {
    const exists = players.value.find(p => p.player_id === player.player_id)
    if (!exists) {
      players.value.push(player)
    }
  }

  function removePlayer(playerId) {
    players.value = players.value.filter(p => p.player_id !== playerId)
  }

  function setGameStatus(status) {
    gameStatus.value = status
  }

  function reset() {
    roomCode.value = ''
    isHost.value = false
    gameStatus.value = 'waiting'
    currentCard.value = null
    players.value = []
    uni.removeStorageSync('current_room')
  }

  return {
    // State
    playerId,
    playerNickname,
    roomCode,
    isHost,
    gameStatus,
    currentCard,
    players,
    // Computed
    playerCount,
    isPlaying,
    isWaiting,
    isEnded,
    // Actions
    initPlayer,
    setNickname,
    setRoom,
    updateGameState,
    setCurrentCard,
    addPlayer,
    removePlayer,
    setGameStatus,
    reset
  }
})
