<template>
  <view class="container">
    <!-- Header -->
    <view class="header">
      <text class="title">Card Game</text>
      <text class="subtitle">Get to know each other better</text>
    </view>

    <!-- Main content -->
    <view class="content">
      <!-- Nickname input -->
      <view class="input-group">
        <text class="label">Your Nickname</text>
        <input
          v-model="nickname"
          class="input"
          placeholder="Enter your nickname"
          maxlength="20"
        />
      </view>

      <!-- Tab buttons -->
      <view class="tabs">
        <view
          class="tab"
          :class="{ active: activeTab === 'create' }"
          @click="activeTab = 'create'"
        >
          Create Room
        </view>
        <view
          class="tab"
          :class="{ active: activeTab === 'join' }"
          @click="activeTab = 'join'"
        >
          Join Room
        </view>
      </view>

      <!-- Create room panel -->
      <view v-if="activeTab === 'create'" class="panel">
        <text class="panel-text">Start a new game and invite your friends!</text>
        <button class="btn btn-primary" @click="handleCreateRoom" :disabled="loading">
          {{ loading ? 'Creating...' : 'Create Room' }}
        </button>
      </view>

      <!-- Join room panel -->
      <view v-if="activeTab === 'join'" class="panel">
        <view class="input-group">
          <text class="label">Room Code</text>
          <input
            v-model="roomCodeInput"
            class="input input-code"
            placeholder="Enter 6-digit code"
            maxlength="6"
            @input="roomCodeInput = roomCodeInput.toUpperCase()"
          />
        </view>
        <button class="btn btn-primary" @click="handleJoinRoom" :disabled="loading">
          {{ loading ? 'Joining...' : 'Join Room' }}
        </button>
      </view>
    </view>

    <!-- Footer link -->
    <view class="footer">
      <text class="link" @click="goToQuestions">Manage My Questions</text>
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

    // Check if we became host (e.g., only player)
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
.container {
  min-height: 100vh;
  padding: 60rpx 40rpx;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  margin-bottom: 80rpx;
}

.title {
  display: block;
  font-size: 64rpx;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 16rpx;
  text-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.2);
}

.subtitle {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.85);
}

.content {
  flex: 1;
  background: #ffffff;
  border-radius: 32rpx;
  padding: 48rpx;
  box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.15);
}

.input-group {
  margin-bottom: 32rpx;
}

.label {
  display: block;
  font-size: 26rpx;
  color: #6b7280;
  margin-bottom: 12rpx;
  font-weight: 500;
}

.input {
  width: 100%;
  height: 88rpx;
  background: #f3f4f6;
  border: 2rpx solid #e5e7eb;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 30rpx;
  color: #1f2937;
  transition: all 0.3s;
}

.input:focus {
  border-color: #667eea;
  background: #ffffff;
}

.input-code {
  text-align: center;
  font-size: 40rpx;
  font-weight: 600;
  letter-spacing: 8rpx;
  text-transform: uppercase;
}

.tabs {
  display: flex;
  background: #f3f4f6;
  border-radius: 16rpx;
  padding: 8rpx;
  margin-bottom: 32rpx;
}

.tab {
  flex: 1;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: #6b7280;
  border-radius: 12rpx;
  transition: all 0.3s;
}

.tab.active {
  background: #ffffff;
  color: #667eea;
  font-weight: 600;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}

.panel {
  padding: 24rpx 0;
}

.panel-text {
  display: block;
  text-align: center;
  font-size: 28rpx;
  color: #6b7280;
  margin-bottom: 32rpx;
}

.btn {
  width: 100%;
  height: 96rpx;
  border-radius: 16rpx;
  font-size: 32rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  box-shadow: 0 8rpx 24rpx rgba(102, 126, 234, 0.4);
}

.btn-primary:active {
  transform: scale(0.98);
  opacity: 0.9;
}

.btn[disabled] {
  opacity: 0.6;
}

.footer {
  text-align: center;
  padding: 40rpx 0;
}

.link {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: underline;
}
</style>
