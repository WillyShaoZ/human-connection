<template>
  <view class="container">
    <!-- Header -->
    <view class="header">
      <view class="header-left" @click="handleBack">
        <text class="back-icon">←</text>
      </view>
      <view class="header-center">
        <text class="room-code">Room: {{ roomCode }}</text>
        <text class="room-status" :class="gameStatus">{{ statusText }}</text>
      </view>
      <view class="header-right" @click="copyRoomCode">
        <text class="copy-icon">📋</text>
      </view>
    </view>

    <!-- Players -->
    <PlayerList :players="players" :current-player-id="gameStore.playerId" />

    <!-- Card area -->
    <view class="card-area">
      <Card :card="currentCard" @click="handleCardClick" />
    </view>

    <!-- Action buttons -->
    <view class="actions">
      <!-- Waiting state -->
      <template v-if="gameStatus === 'waiting'">
        <view v-if="gameStore.isHost" class="action-group">
          <button class="btn btn-primary" @click="startGame" :disabled="players.length < 1">
            Start Game
          </button>
          <text class="hint">{{ players.length < 2 ? 'Waiting for more players...' : 'Ready to start!' }}</text>
        </view>
        <view v-else class="action-group">
          <text class="waiting-text">Waiting for host to start the game...</text>
        </view>
      </template>

      <!-- Playing state -->
      <template v-if="gameStatus === 'playing'">
        <view class="action-row">
          <button class="btn btn-secondary" @click="switchCard">
            🔄 Switch
          </button>
          <button class="btn btn-primary" @click="drawCard">
            🎴 Draw Card
          </button>
        </view>
        <button v-if="gameStore.isHost" class="btn btn-outline" @click="endGame">
          End Game
        </button>
      </template>

      <!-- Ended state -->
      <template v-if="gameStatus === 'ended'">
        <view class="ended-message">
          <text class="ended-title">Game Over!</text>
          <text class="ended-subtitle">Thanks for playing!</text>
        </view>
        <view v-if="gameStore.isHost" class="action-group">
          <button class="btn btn-primary" @click="restartGame">
            Play Again
          </button>
        </view>
      </template>
    </view>

    <!-- Manage questions link -->
    <view class="footer-link" @click="goToQuestions">
      <text class="link">➕ Add Custom Questions</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useGameStore } from '@/stores/game'
import { gameSocket } from '@/utils/websocket'
import { getRoom } from '@/utils/api'
import Card from '@/components/Card.vue'
import PlayerList from '@/components/PlayerList.vue'

const gameStore = useGameStore()

const roomCode = ref('')
const gameStatus = ref('waiting')
const currentCard = ref(null)
const players = ref([])
const connected = ref(false)

const statusText = computed(() => {
  switch (gameStatus.value) {
    case 'waiting': return 'Waiting'
    case 'playing': return 'In Progress'
    case 'ended': return 'Ended'
    default: return ''
  }
})

onMounted(async () => {
  // Get room code from URL
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  roomCode.value = currentPage.options?.code || gameStore.roomCode

  if (!roomCode.value) {
    uni.showToast({ title: 'Invalid room', icon: 'none' })
    uni.navigateBack()
    return
  }

  // Initialize player if not done
  if (!gameStore.playerId) {
    gameStore.initPlayer()
  }

  // Fetch room info
  try {
    const room = await getRoom(roomCode.value)
    players.value = room.players
    gameStatus.value = room.status
    currentCard.value = room.current_card

    // Check if we're host
    const me = room.players.find(p => p.player_id === gameStore.playerId)
    if (me) {
      gameStore.setRoom(roomCode.value, me.is_host)
    }
  } catch (error) {
    uni.showToast({ title: 'Room not found', icon: 'none' })
    uni.navigateBack()
    return
  }

  // Connect WebSocket
  setupWebSocket()
})

onUnmounted(() => {
  gameSocket.disconnect()
})

const setupWebSocket = async () => {
  try {
    await gameSocket.connect(roomCode.value, gameStore.playerId)
    connected.value = true

    // Listen for events
    gameSocket.on('game_state', (data) => {
      gameStatus.value = data.status
      currentCard.value = data.current_card
      players.value = data.players
    })

    gameSocket.on('player_joined', (data) => {
      uni.showToast({ title: `${data.player?.nickname || 'Someone'} joined!`, icon: 'none' })
    })

    gameSocket.on('player_connected', (data) => {
      // Refresh players list
      getRoom(roomCode.value).then(room => {
        players.value = room.players
      })
    })

    gameSocket.on('player_disconnected', (data) => {
      // Refresh players list
      getRoom(roomCode.value).then(room => {
        players.value = room.players
        // Check if we're now host
        const me = room.players.find(p => p.player_id === gameStore.playerId)
        if (me && me.is_host && !gameStore.isHost) {
          gameStore.setRoom(roomCode.value, true)
          uni.showToast({ title: 'You are now the host!', icon: 'none' })
        }
      })
    })

    gameSocket.on('game_started', (data) => {
      gameStatus.value = 'playing'
      uni.showToast({ title: 'Game started!', icon: 'none' })
    })

    gameSocket.on('card_drawn', (data) => {
      currentCard.value = data.card
    })

    gameSocket.on('card_switched', (data) => {
      currentCard.value = data.card
    })

    gameSocket.on('game_ended', (data) => {
      gameStatus.value = 'ended'
    })

    gameSocket.on('game_restarted', (data) => {
      gameStatus.value = 'waiting'
      currentCard.value = null
      uni.showToast({ title: 'Game restarted!', icon: 'none' })
    })

    gameSocket.on('error', (data) => {
      uni.showToast({ title: data.message, icon: 'none' })
    })

    gameSocket.on('disconnected', () => {
      connected.value = false
      uni.showToast({ title: 'Disconnected from server', icon: 'none' })
    })

    gameSocket.on('reconnected', () => {
      connected.value = true
      uni.showToast({ title: 'Reconnected!', icon: 'success' })
    })

  } catch (error) {
    console.error('WebSocket connection failed:', error)
    uni.showToast({ title: 'Failed to connect', icon: 'none' })
  }
}

const startGame = () => {
  gameSocket.startGame()
}

const drawCard = () => {
  gameSocket.drawCard()
}

const switchCard = () => {
  gameSocket.switchCard()
}

const endGame = () => {
  uni.showModal({
    title: 'End Game',
    content: 'Are you sure you want to end the game?',
    success: (res) => {
      if (res.confirm) {
        gameSocket.endGame()
      }
    }
  })
}

const restartGame = () => {
  gameSocket.restartGame()
}

const handleBack = () => {
  uni.showModal({
    title: 'Leave Room',
    content: 'Are you sure you want to leave?',
    success: (res) => {
      if (res.confirm) {
        gameSocket.disconnect()
        gameStore.reset()
        uni.navigateBack()
      }
    }
  })
}

const handleCardClick = () => {
  if (gameStatus.value === 'playing' && !currentCard.value) {
    drawCard()
  }
}

const copyRoomCode = () => {
  uni.setClipboardData({
    data: roomCode.value,
    success: () => {
      uni.showToast({ title: 'Code copied!', icon: 'success' })
    }
  })
}

const goToQuestions = () => {
  uni.navigateTo({
    url: `/pages/questions/questions?room=${roomCode.value}`
  })
}
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 0;
  margin-bottom: 24rpx;
}

.header-left,
.header-right {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}

.back-icon {
  font-size: 36rpx;
  color: #ffffff;
}

.copy-icon {
  font-size: 32rpx;
}

.header-center {
  flex: 1;
  text-align: center;
}

.room-code {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8rpx;
}

.room-status {
  display: inline-block;
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
  font-weight: 500;
}

.room-status.waiting {
  background: #fbbf24;
  color: #1f2937;
}

.room-status.playing {
  background: #4ade80;
  color: #1f2937;
}

.room-status.ended {
  background: #9ca3af;
  color: #ffffff;
}

.card-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32rpx 0;
}

.actions {
  padding: 32rpx 0;
}

.action-group {
  text-align: center;
}

.action-row {
  display: flex;
  gap: 24rpx;
  margin-bottom: 24rpx;
}

.btn {
  flex: 1;
  height: 96rpx;
  border-radius: 16rpx;
  font-size: 30rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #ffffff;
  box-shadow: 0 8rpx 24rpx rgba(240, 147, 251, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  border: 2rpx solid rgba(255, 255, 255, 0.3);
}

.btn-outline {
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  border: 2rpx solid rgba(255, 255, 255, 0.3);
  margin-top: 16rpx;
}

.btn:active {
  transform: scale(0.98);
  opacity: 0.9;
}

.btn[disabled] {
  opacity: 0.5;
}

.hint {
  display: block;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 16rpx;
}

.waiting-text {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
}

.ended-message {
  text-align: center;
  margin-bottom: 32rpx;
}

.ended-title {
  display: block;
  font-size: 48rpx;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8rpx;
}

.ended-subtitle {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
}

.footer-link {
  text-align: center;
  padding: 24rpx 0;
}

.link {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
}
</style>
