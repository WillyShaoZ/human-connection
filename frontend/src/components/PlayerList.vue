<template>
  <view class="player-list">
    <view class="player-header">
      <text class="player-title">Players ({{ players.length }})</text>
    </view>
    <scroll-view class="player-scroll" scroll-x>
      <view class="player-items">
        <view
          v-for="player in players"
          :key="player.player_id"
          class="player-item"
          :class="{ 'is-me': player.player_id === currentPlayerId }"
        >
          <view class="player-avatar" :style="{ background: getAvatarColor(player.player_id) }">
            {{ player.nickname.charAt(0).toUpperCase() }}
          </view>
          <text class="player-name">{{ player.nickname }}</text>
          <view v-if="player.is_host" class="host-badge">Host</view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
defineProps({
  players: {
    type: Array,
    default: () => []
  },
  currentPlayerId: {
    type: String,
    default: ''
  }
})

// Generate consistent avatar color based on player ID
const getAvatarColor = (playerId) => {
  const colors = [
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
    'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)'
  ]
  const index = playerId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return colors[index % colors.length]
}
</script>

<style lang="scss" scoped>
.player-list {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 32rpx;
}

.player-header {
  margin-bottom: 16rpx;
}

.player-title {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.player-scroll {
  white-space: nowrap;
}

.player-items {
  display: inline-flex;
  gap: 24rpx;
}

.player-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16rpx;
  border-radius: 16rpx;
  min-width: 120rpx;
  position: relative;
}

.player-item.is-me {
  background: rgba(255, 255, 255, 0.1);
}

.player-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 12rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.2);
}

.player-name {
  font-size: 24rpx;
  color: #ffffff;
  max-width: 100rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.host-badge {
  position: absolute;
  top: 8rpx;
  right: 8rpx;
  background: #fbbf24;
  color: #1f2937;
  font-size: 18rpx;
  padding: 4rpx 8rpx;
  border-radius: 6rpx;
  font-weight: 600;
}
</style>
