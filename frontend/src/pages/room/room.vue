<template>
  <view class="page">
    <!-- Back button -->
    <view class="nav-bar">
      <view class="back-btn" @click="handleBack">
        <text class="back-icon">←</text>
      </view>
      <text class="nav-title">Game Room</text>
      <view class="nav-right"></view>
    </view>

    <!-- Main Ticket Container -->
    <view class="ticket">
      <!-- Ticket Header (Yellow) -->
      <view class="ticket-header">
        <view class="ticket-badge">{{ statusText }}</view>
        <text class="ticket-title">Card Game</text>
        <view class="room-code-row">
          <text class="room-code">Room: {{ roomCode }}</text>
          <view class="copy-btn" @click="copyRoomCode">
            <text class="copy-icon">📋</text>
          </view>
        </view>
      </view>

      <!-- Side Notches -->
      <view class="notch-row">
        <view class="notch notch-left"></view>
        <view class="notch-line"></view>
        <view class="notch notch-right"></view>
      </view>

      <!-- Ticket Body (White) -->
      <view class="ticket-body">
        <!-- Players Section -->
        <view class="section">
          <text class="section-label">👥 Players ({{ players.length }})</text>
          <view class="tags-wrap">
            <view
              v-for="(player, index) in players"
              :key="player.player_id"
              class="tag"
              :style="{ background: getTagColor(index) }"
            >
              <text class="tag-text">{{ player.nickname }}</text>
              <text v-if="player.is_host" class="tag-icon">👑</text>
            </view>
          </view>
        </view>

        <!-- Game Status -->
        <view class="section">
          <text class="section-label">🎴 Status</text>
          <view class="status-card">
            <view class="status-dot" :class="gameStatus"></view>
            <text class="status-text">{{ gameStatusDisplay }}</text>
          </view>
        </view>

        <!-- Card Display - Flip Card -->
        <view v-if="gameStatus === 'playing'" class="section">
          <text class="section-label">❓ Current Card</text>
          <view class="flip-card-container">
            <view class="flip-card" :class="{ flipped: isCardFlipped }">
              <!-- Card Back -->
              <view class="flip-card-back">
                <view class="card-back-design">
                  <text class="card-logo">🎴</text>
                  <text class="card-brand">CARD GAME</text>
                </view>
              </view>
              <!-- Card Front -->
              <view class="flip-card-front">
                <view class="card-front-content">
                  <view v-if="currentCard && !currentCard.is_system" class="card-type-badge">Custom</view>
                  <text class="card-question">{{ currentCard?.content || 'Tap Draw Card!' }}</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- Quick Actions -->
        <view class="section">
          <text class="section-label">⚡ Quick Actions</text>
          <view class="quick-actions">
            <view class="action-item" @click="goToQuestions">
              <text class="action-icon">➕</text>
              <text class="action-text">Add Questions</text>
            </view>
            <view class="action-item" @click="copyRoomCode">
              <text class="action-icon">📤</text>
              <text class="action-text">Share</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Ticket Footer (Actions) -->
      <view class="ticket-footer">
        <!-- Waiting state -->
        <template v-if="gameStatus === 'waiting'">
          <view v-if="gameStore.isHost" class="footer-content">
            <view class="main-btn-wrap">
              <view class="float-avatar">
                <text>{{ gameStore.playerNickname?.charAt(0)?.toUpperCase() || 'P' }}</text>
              </view>
              <button class="main-btn pink" :class="{ disabled: players.length < 2 }" @click="startGame">
                <text class="btn-check">✓</text>
                <text class="btn-label">Start Game</text>
              </button>
            </view>
            <text class="hint">{{ players.length < 2 ? 'Waiting for more players...' : 'Ready to start!' }}</text>
          </view>
          <view v-else class="footer-content">
            <text class="waiting-msg">Waiting for host to start...</text>
          </view>
        </template>

        <!-- Playing state -->
        <template v-if="gameStatus === 'playing'">
          <view class="footer-content">
            <view class="main-btn-wrap">
              <view class="float-avatar">
                <text>{{ gameStore.playerNickname?.charAt(0)?.toUpperCase() || 'P' }}</text>
              </view>
              <button class="main-btn pink" @click="handleDrawCard">
                <text class="btn-check">🎴</text>
                <text class="btn-label">Draw Card</text>
              </button>
            </view>
            <view class="btn-row">
              <button class="sec-btn outline" @click="handleSwitchCard">Switch</button>
              <button class="sec-btn yellow" @click="copyRoomCode">Share Code</button>
              <button v-if="gameStore.isHost" class="sec-btn green square" @click="endGame">→</button>
            </view>
          </view>
        </template>

        <!-- Ended state -->
        <template v-if="gameStatus === 'ended'">
          <view class="footer-content">
            <text class="ended-title">Game Over! 🎉</text>
            <view class="main-btn-wrap" v-if="gameStore.isHost">
              <view class="float-avatar green">
                <text>{{ gameStore.playerNickname?.charAt(0)?.toUpperCase() || 'P' }}</text>
              </view>
              <button class="main-btn green" @click="restartGame">
                <text class="btn-check">🔄</text>
                <text class="btn-label">Play Again</text>
              </button>
            </view>
            <button class="sec-btn outline full" @click="handleBack">Leave Room</button>
          </view>
        </template>
      </view>
    </view>

  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useGameStore } from '@/stores/game'
import { gameSocket } from '@/utils/websocket'
import { getRoom } from '@/utils/api'

const gameStore = useGameStore()

const roomCode = ref('')
const gameStatus = ref('waiting')
const currentCard = ref(null)
const players = ref([])
const connected = ref(false)

// Card flip state
const isCardFlipped = ref(false)

const statusText = computed(() => {
  switch (gameStatus.value) {
    case 'waiting': return '⏳ Waiting'
    case 'playing': return '🎮 Playing'
    case 'ended': return '🏁 Ended'
    default: return ''
  }
})

const gameStatusDisplay = computed(() => {
  switch (gameStatus.value) {
    case 'waiting': return 'Waiting for players to join'
    case 'playing': return 'Game in progress'
    case 'ended': return 'Game has ended'
    default: return ''
  }
})

const getTagColor = (index) => {
  const colors = ['#FFE135', '#7DD3FC', '#FDA4AF', '#86EFAC', '#FED7AA', '#C4B5FD', '#FCA5A5', '#A5F3FC']
  return colors[index % colors.length]
}

// Flip card animation
const flipCard = () => {
  isCardFlipped.value = false
  setTimeout(() => {
    isCardFlipped.value = true
  }, 100)
}

const handleDrawCard = () => {
  isCardFlipped.value = false
  gameSocket.drawCard()
}

const handleSwitchCard = () => {
  isCardFlipped.value = false
  setTimeout(() => {
    gameSocket.switchCard()
  }, 300)
}

onMounted(async () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  roomCode.value = currentPage.options?.code || gameStore.roomCode

  if (!roomCode.value) {
    uni.showToast({ title: 'Invalid room', icon: 'none' })
    uni.navigateBack()
    return
  }

  if (!gameStore.playerId) {
    gameStore.initPlayer()
  }

  try {
    const room = await getRoom(roomCode.value)
    players.value = room.players
    gameStatus.value = room.status
    currentCard.value = room.current_card

    const me = room.players.find(p => p.player_id === gameStore.playerId)
    if (me) {
      gameStore.setRoom(roomCode.value, me.is_host)
    }
  } catch (error) {
    uni.showToast({ title: 'Room not found', icon: 'none' })
    uni.navigateBack()
    return
  }

  setupWebSocket()
})

onUnmounted(() => {
  gameSocket.disconnect()
})

const setupWebSocket = async () => {
  try {
    await gameSocket.connect(roomCode.value, gameStore.playerId)
    connected.value = true

    gameSocket.on('game_state', (data) => {
      gameStatus.value = data.status
      currentCard.value = data.current_card
      players.value = data.players
    })

    gameSocket.on('player_connected', () => {
      getRoom(roomCode.value).then(room => { players.value = room.players })
    })

    gameSocket.on('player_disconnected', () => {
      getRoom(roomCode.value).then(room => {
        players.value = room.players
        const me = room.players.find(p => p.player_id === gameStore.playerId)
        if (me && me.is_host && !gameStore.isHost) {
          gameStore.setRoom(roomCode.value, true)
          uni.showToast({ title: 'You are now the host!', icon: 'none' })
        }
      })
    })

    gameSocket.on('game_started', () => {
      gameStatus.value = 'playing'
      uni.showToast({ title: 'Game started!', icon: 'none' })
    })

    gameSocket.on('card_drawn', (data) => {
      currentCard.value = data.card
      flipCard()
    })

    gameSocket.on('card_switched', (data) => {
      currentCard.value = data.card
      flipCard()
    })

    gameSocket.on('game_ended', () => { gameStatus.value = 'ended' })
    gameSocket.on('game_restarted', () => {
      gameStatus.value = 'waiting'
      currentCard.value = null
      uni.showToast({ title: 'Game restarted!', icon: 'none' })
    })
    gameSocket.on('error', (data) => { uni.showToast({ title: data.message, icon: 'none' }) })
  } catch (error) {
    console.error('WebSocket connection failed:', error)
    uni.showToast({ title: 'Failed to connect', icon: 'none' })
  }
}

const startGame = () => gameSocket.startGame()
const endGame = () => {
  uni.showModal({
    title: 'End Game',
    content: 'Are you sure?',
    success: (res) => { if (res.confirm) gameSocket.endGame() }
  })
}
const restartGame = () => gameSocket.restartGame()

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

const copyRoomCode = () => {
  uni.setClipboardData({
    data: roomCode.value,
    success: () => uni.showToast({ title: 'Copied!', icon: 'success' })
  })
}

const goToQuestions = () => {
  uni.navigateTo({ url: `/pages/questions/questions?room=${roomCode.value}` })
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 24rpx;
}

/* Navigation */
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 0;
  margin-bottom: 16rpx;
}

.back-btn {
  width: 72rpx;
  height: 72rpx;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 36rpx;
  color: #1a1a1a;
}

.nav-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1a1a1a;
}

.nav-right {
  width: 72rpx;
}

/* Ticket Container */
.ticket {
  background: #fff;
  border-radius: 32rpx;
  overflow: visible;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.08);
  position: relative;
}

/* Ticket Header */
.ticket-header {
  background: #FFE135;
  padding: 32rpx;
  border-radius: 32rpx 32rpx 0 0;
}

.ticket-badge {
  position: absolute;
  top: 24rpx;
  right: 0;
  background: #1a1a1a;
  color: #fff;
  padding: 8rpx 20rpx 8rpx 24rpx;
  border-radius: 20rpx 0 0 20rpx;
  font-size: 22rpx;
  z-index: 10;
}

.ticket-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.4;
  margin-bottom: 16rpx;
  padding-right: 120rpx;
}

.room-code-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.room-code {
  font-size: 26rpx;
  color: rgba(0,0,0,0.7);
}

.copy-btn {
  width: 48rpx;
  height: 48rpx;
  background: rgba(0,0,0,0.1);
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.copy-icon {
  font-size: 24rpx;
}

/* Notch Row - Side notches like a ticket */
.notch-row {
  display: flex;
  align-items: center;
  background: linear-gradient(to bottom, #FFE135 50%, #fff 50%);
  position: relative;
}

.notch {
  width: 40rpx;
  height: 40rpx;
  background: #f5f5f5;
  border-radius: 50%;
  flex-shrink: 0;
}

.notch-left {
  margin-left: -20rpx;
}

.notch-right {
  margin-right: -20rpx;
}

.notch-line {
  flex: 1;
  border-top: 2rpx dashed #e0e0e0;
}

/* Ticket Body */
.ticket-body {
  padding: 32rpx;
  background: #fff;
}

.section {
  margin-bottom: 24rpx;
}

.section:last-child {
  margin-bottom: 0;
}

.section-label {
  display: block;
  font-size: 24rpx;
  color: #999;
  margin-bottom: 12rpx;
}

/* Tags */
.tags-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 6rpx;
  padding: 12rpx 20rpx;
  border-radius: 24rpx;
}

.tag-text {
  font-size: 24rpx;
  font-weight: 600;
  color: #1a1a1a;
}

.tag-icon {
  font-size: 18rpx;
}

/* Status Card */
.status-card {
  display: flex;
  align-items: center;
  gap: 12rpx;
  background: #f9f9f9;
  padding: 16rpx 20rpx;
  border-radius: 16rpx;
}

.status-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #ccc;
}

.status-dot.waiting { background: #f59e0b; }
.status-dot.playing { background: #10b981; }
.status-dot.ended { background: #6b7280; }

.status-text {
  font-size: 26rpx;
  color: #1a1a1a;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  gap: 16rpx;
}

.action-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  background: #f9f9f9;
  padding: 20rpx;
  border-radius: 16rpx;
}

.action-icon {
  font-size: 24rpx;
}

.action-text {
  font-size: 24rpx;
  color: #1a1a1a;
}

/* Ticket Footer */
.ticket-footer {
  padding: 24rpx 32rpx 32rpx;
  border-top: 1rpx solid #f0f0f0;
  background: #fff;
  border-radius: 0 0 32rpx 32rpx;
}

.footer-content {
  text-align: center;
}

/* Main Button */
.main-btn-wrap {
  position: relative;
  padding-top: 32rpx;
  margin-bottom: 16rpx;
}

.float-avatar {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 64rpx;
  height: 64rpx;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 700;
  color: #fff;
  border: 3rpx solid #fff;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.15);
  z-index: 10;
}

.float-avatar.green {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.main-btn {
  width: 100%;
  height: 100rpx;
  border-radius: 50rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  border: none;
}

.main-btn.pink {
  background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%);
}

.main-btn.green {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.main-btn.disabled {
  background: #d1d5db;
}

.btn-check {
  font-size: 28rpx;
  color: #fff;
}

.btn-label {
  font-size: 30rpx;
  font-weight: 700;
  color: #fff;
}

.hint {
  display: block;
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}

.waiting-msg {
  font-size: 28rpx;
  color: #999;
  padding: 32rpx 0;
}

.ended-title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 20rpx;
}

/* Secondary Buttons */
.btn-row {
  display: flex;
  gap: 12rpx;
}

.sec-btn {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 500;
  border: none;
}

.sec-btn.outline {
  background: #fff;
  border: 2rpx solid #1a1a1a;
  color: #1a1a1a;
}

.sec-btn.yellow {
  background: #FFE135;
  color: #1a1a1a;
}

.sec-btn.green {
  background: #10b981;
  color: #fff;
}

.sec-btn.square {
  flex: none;
  width: 80rpx;
  font-size: 28rpx;
}

.sec-btn.full {
  margin-top: 12rpx;
}

/* ===================== */
/* Embedded Flip Card */
/* ===================== */
.flip-card-container {
  perspective: 1000px;
  width: 100%;
}

.flip-card {
  width: 100%;
  height: 280rpx;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.6s ease;
}

.flip-card.flipped {
  transform: rotateY(180deg);
}

.flip-card-front,
.flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 24rpx;
  overflow: hidden;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);
}

/* Card Back */
.flip-card-back {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-back-design {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.card-back-design::before {
  content: '';
  position: absolute;
  top: 16rpx;
  left: 16rpx;
  right: 16rpx;
  bottom: 16rpx;
  border: 3rpx solid rgba(255,255,255,0.2);
  border-radius: 16rpx;
}

.card-logo {
  font-size: 64rpx;
  margin-bottom: 8rpx;
}

.card-brand {
  font-size: 22rpx;
  font-weight: 700;
  color: #fff;
  letter-spacing: 4rpx;
}

/* Card Front */
.flip-card-front {
  transform: rotateY(180deg);
  background: linear-gradient(135deg, #FFE135 0%, #FFC107 100%);
}

.card-front-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24rpx;
  position: relative;
}

.card-type-badge {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  background: rgba(0,0,0,0.12);
  padding: 6rpx 14rpx;
  border-radius: 14rpx;
  font-size: 20rpx;
  color: #1a1a1a;
}

.card-question {
  font-size: 28rpx;
  font-weight: 600;
  color: #1a1a1a;
  text-align: center;
  line-height: 1.5;
  max-height: 200rpx;
  overflow: hidden;
}
</style>
