<template>
  <view class="page">
    <!-- Navigation -->
    <view class="nav-bar">
      <view class="nav-left"></view>
      <text class="nav-title">Card Game</text>
      <view class="nav-right"></view>
    </view>

    <!-- Main Ticket Container -->
    <view class="ticket">
      <!-- Ticket Header (Yellow) -->
      <view class="ticket-header">
        <view class="ticket-badge">🎴 Ready to Play</view>
        <text class="ticket-title">Get to Know Each Other Better</text>
        <text class="ticket-subtitle">Draw cards, answer questions, make connections</text>
      </view>

      <!-- Side Notches -->
      <view class="notch-row">
        <view class="notch notch-left"></view>
        <view class="notch-line"></view>
        <view class="notch notch-right"></view>
      </view>

      <!-- Ticket Body (White) -->
      <view class="ticket-body">
        <!-- Nickname Section -->
        <view class="section">
          <text class="section-label">👤 Your Nickname</text>
          <input
            v-model="nickname"
            class="input"
            placeholder="Enter your nickname"
            maxlength="20"
          />
        </view>

        <!-- Tab Selection -->
        <view class="section">
          <text class="section-label">🎮 Choose Action</text>
          <view class="tabs">
            <view
              class="tab"
              :class="{ active: activeTab === 'create' }"
              @click="activeTab = 'create'"
            >
              <text class="tab-icon">➕</text>
              <text class="tab-text">Create</text>
            </view>
            <view
              class="tab"
              :class="{ active: activeTab === 'join' }"
              @click="activeTab = 'join'"
            >
              <text class="tab-icon">🚪</text>
              <text class="tab-text">Join</text>
            </view>
          </view>
        </view>

        <!-- Create Room Panel -->
        <view v-if="activeTab === 'create'" class="section">
          <view class="info-card">
            <text class="info-icon">✨</text>
            <text class="info-text">Create a room and share the code with friends to play together!</text>
          </view>
        </view>

        <!-- Join Room Panel -->
        <view v-if="activeTab === 'join'" class="section">
          <text class="section-label">🔢 Room Code</text>
          <view class="code-input-row">
            <input
              v-model="roomCodeInput"
              class="input input-code"
              placeholder="XXXXXX"
              maxlength="6"
              @input="roomCodeInput = roomCodeInput.toUpperCase()"
            />
            <view class="paste-btn" @click="pasteCode">
              <text class="paste-icon">📋</text>
            </view>
          </view>
        </view>

        <!-- Quick Actions -->
        <view class="section">
          <text class="section-label">⚡ Quick Actions</text>
          <view class="quick-actions">
            <view class="action-item" @click="goToQuestions">
              <text class="action-icon">✏️</text>
              <text class="action-text">My Questions</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Ticket Footer (Action Button) -->
      <view class="ticket-footer">
        <view class="main-btn-wrap">
          <view class="float-avatar">
            <text>{{ nickname?.charAt(0)?.toUpperCase() || '?' }}</text>
          </view>
          <button
            class="main-btn pink"
            :class="{ disabled: loading }"
            @click="activeTab === 'create' ? handleCreateRoom() : handleJoinRoom()"
          >
            <text class="btn-check">✓</text>
            <text class="btn-label">{{ activeTab === 'create' ? 'Create Room' : 'Join Room' }}</text>
          </button>
        </view>
        <text class="hint">{{ activeTab === 'create' ? 'You will be the host' : 'Enter 6-digit code above' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useGameStore } from '@/stores/game'
import { createRoom, joinRoom } from '@/utils/api'

const gameStore = useGameStore()

const nickname = ref('')
const roomCodeInput = ref('')
const activeTab = ref('create')
const loading = ref(false)

onMounted(() => {
  gameStore.initPlayer()
  if (gameStore.playerNickname) {
    nickname.value = gameStore.playerNickname
  }
})

const pasteCode = async () => {
  try {
    const res = await uni.getClipboardData()
    if (res.data && res.data.length === 6) {
      roomCodeInput.value = res.data.toUpperCase()
      uni.showToast({ title: 'Pasted!', icon: 'success' })
    }
  } catch (e) {
    console.log('Paste failed')
  }
}

const handleCreateRoom = async () => {
  if (!nickname.value.trim()) {
    uni.showToast({ title: 'Please enter a nickname', icon: 'none' })
    return
  }

  loading.value = true
  try {
    gameStore.setNickname(nickname.value.trim())
    const room = await createRoom(nickname.value.trim(), gameStore.playerId)
    gameStore.setRoom(room.room_code, true)

    uni.navigateTo({
      url: `/pages/room/room?code=${room.room_code}`
    })
  } catch (error) {
    console.error('Create room error:', error)
    uni.showToast({ title: 'Failed to create room', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const handleJoinRoom = async () => {
  if (!nickname.value.trim()) {
    uni.showToast({ title: 'Please enter a nickname', icon: 'none' })
    return
  }

  if (!roomCodeInput.value.trim() || roomCodeInput.value.length !== 6) {
    uni.showToast({ title: 'Please enter a valid 6-digit room code', icon: 'none' })
    return
  }

  loading.value = true
  try {
    gameStore.setNickname(nickname.value.trim())
    const room = await joinRoom(
      roomCodeInput.value.toUpperCase(),
      nickname.value.trim(),
      gameStore.playerId
    )

    const isHost = room.players.some(p => p.player_id === gameStore.playerId && p.is_host)
    gameStore.setRoom(room.room_code, isHost)

    uni.navigateTo({
      url: `/pages/room/room?code=${room.room_code}`
    })
  } catch (error) {
    console.error('Join room error:', error)
    const message = error.detail || 'Failed to join room'
    uni.showToast({ title: message, icon: 'none' })
  } finally {
    loading.value = false
  }
}

const goToQuestions = () => {
  if (!nickname.value.trim()) {
    uni.showToast({ title: 'Please enter a nickname first', icon: 'none' })
    return
  }
  gameStore.setNickname(nickname.value.trim())
  uni.navigateTo({
    url: '/pages/questions/questions'
  })
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

.nav-left, .nav-right {
  width: 72rpx;
}

.nav-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1a1a1a;
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
  font-size: 36rpx;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.4;
  margin-bottom: 8rpx;
  padding-right: 140rpx;
}

.ticket-subtitle {
  display: block;
  font-size: 24rpx;
  color: rgba(0,0,0,0.6);
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

/* Input */
.input {
  width: 100%;
  height: 88rpx;
  background: #f9f9f9;
  border: none;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 30rpx;
  color: #1a1a1a;
}

.input-code {
  text-align: center;
  font-size: 36rpx;
  font-weight: 600;
  letter-spacing: 8rpx;
  text-transform: uppercase;
  flex: 1;
}

.code-input-row {
  display: flex;
  gap: 12rpx;
}

.paste-btn {
  width: 88rpx;
  height: 88rpx;
  background: #f9f9f9;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.paste-icon {
  font-size: 32rpx;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 12rpx;
}

.tab {
  flex: 1;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  background: #f9f9f9;
  border-radius: 16rpx;
  transition: all 0.3s;
}

.tab.active {
  background: #1a1a1a;
}

.tab.active .tab-icon,
.tab.active .tab-text {
  color: #fff;
}

.tab-icon {
  font-size: 24rpx;
}

.tab-text {
  font-size: 26rpx;
  font-weight: 500;
  color: #1a1a1a;
}

/* Info Card */
.info-card {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
  background: #f9f9f9;
  padding: 20rpx;
  border-radius: 16rpx;
}

.info-icon {
  font-size: 28rpx;
}

.info-text {
  flex: 1;
  font-size: 24rpx;
  color: #666;
  line-height: 1.5;
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
  text-align: center;
  background: #fff;
  border-radius: 0 0 32rpx 32rpx;
}

/* Main Button */
.main-btn-wrap {
  position: relative;
  padding-top: 32rpx;
  margin-bottom: 12rpx;
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
}
</style>
