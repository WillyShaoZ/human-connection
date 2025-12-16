<template>
  <view class="card-wrapper" @click="handleClick">
    <view class="card" :class="{ flipped: isFlipped, 'no-card': !card }">
      <!-- Front of card (question) -->
      <view class="card-face card-front">
        <view class="card-content">
          <text class="card-text">{{ card?.content || 'Draw a card to begin!' }}</text>
        </view>
        <view v-if="card && !card.is_system" class="card-badge">Custom</view>
      </view>

      <!-- Back of card -->
      <view class="card-face card-back">
        <view class="card-back-design">
          <text class="card-icon">?</text>
          <text class="card-label">Tap to reveal</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  card: {
    type: Object,
    default: null
  },
  autoFlip: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click'])

const isFlipped = ref(false)

// Watch for card changes to animate flip
watch(() => props.card, (newCard, oldCard) => {
  if (newCard && newCard !== oldCard) {
    // Flip to back first
    isFlipped.value = true
    // Then flip to front after delay
    setTimeout(() => {
      isFlipped.value = false
    }, 300)
  }
}, { immediate: false })

const handleClick = () => {
  emit('click')
}
</script>

<style lang="scss" scoped>
.card-wrapper {
  perspective: 2000rpx;
  width: 100%;
  max-width: 600rpx;
  margin: 0 auto;
}

.card {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  transform-style: preserve-3d;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.card.flipped {
  transform: rotateY(180deg);
}

.card-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 32rpx;
  overflow: hidden;
  box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.25);
}

.card-front {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48rpx;
}

.card-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-text {
  font-size: 36rpx;
  font-weight: 600;
  color: #ffffff;
  text-align: center;
  line-height: 1.6;
  text-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.2);
}

.card-badge {
  position: absolute;
  bottom: 24rpx;
  right: 24rpx;
  background: rgba(255, 255, 255, 0.3);
  color: #ffffff;
  font-size: 22rpx;
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  font-weight: 500;
}

.card-back {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: rotateY(180deg);
}

.card-back-design {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 20rpx,
    rgba(255, 255, 255, 0.05) 20rpx,
    rgba(255, 255, 255, 0.05) 40rpx
  );
}

.card-icon {
  font-size: 120rpx;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 24rpx;
}

.card-label {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.7);
}

.no-card .card-front {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
}

.no-card .card-text {
  opacity: 0.8;
}
</style>
