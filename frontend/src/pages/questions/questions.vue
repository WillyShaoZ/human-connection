<template>
  <view class="page">
    <!-- Navigation -->
    <view class="nav-bar">
      <view class="back-btn" @click="handleBack">
        <text class="back-icon">←</text>
      </view>
      <text class="nav-title">My Questions</text>
      <view class="nav-right"></view>
    </view>

    <!-- Main Ticket Container -->
    <view class="ticket">
      <!-- Ticket Header (Yellow) -->
      <view class="ticket-header">
        <view class="ticket-badge">✏️ Custom</view>
        <text class="ticket-title">Add Your Own Questions</text>
        <text class="ticket-subtitle">Make the game more personal and fun!</text>
      </view>

      <!-- Side Notches -->
      <view class="notch-row">
        <view class="notch notch-left"></view>
        <view class="notch-line"></view>
        <view class="notch notch-right"></view>
      </view>

      <!-- Ticket Body (White) -->
      <view class="ticket-body">
        <!-- Add Question Section -->
        <view class="section">
          <text class="section-label">➕ New Question</text>
          <textarea
            v-model="newQuestion"
            class="textarea"
            placeholder="Type your question here..."
            :maxlength="200"
          />
          <view class="input-footer">
            <text class="char-count">{{ newQuestion.length }}/200</text>
            <button class="add-btn" @click="handleAddQuestion" :disabled="!newQuestion.trim() || adding">
              {{ adding ? '...' : '+ Add' }}
            </button>
          </view>
        </view>

        <!-- Questions List -->
        <view class="section">
          <text class="section-label">📝 Your Questions ({{ questions.length }})</text>

          <view v-if="loading" class="loading-state">
            <text class="loading-text">Loading...</text>
          </view>

          <view v-else-if="questions.length === 0" class="empty-state">
            <text class="empty-icon">📝</text>
            <text class="empty-text">No custom questions yet</text>
            <text class="empty-hint">Add your own questions above!</text>
          </view>

          <scroll-view v-else class="questions-list" scroll-y>
            <view
              v-for="(question, index) in questions"
              :key="question.id"
              class="question-item"
              :style="{ background: getTagColor(index) }"
            >
              <text class="question-text">{{ question.content }}</text>
              <view class="delete-btn" @click="handleDeleteQuestion(question)">
                <text>×</text>
              </view>
            </view>
          </scroll-view>
        </view>
      </view>

      <!-- Ticket Footer (Info) -->
      <view class="ticket-footer">
        <view class="info-card">
          <text class="info-icon">💡</text>
          <text class="info-text">Custom questions are private to your games and will appear randomly when playing.</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useGameStore } from '@/stores/game'
import { getCustomQuestions, addQuestion, deleteQuestion } from '@/utils/api'

const gameStore = useGameStore()

const roomCode = ref('')
const newQuestion = ref('')
const questions = ref([])
const loading = ref(true)
const adding = ref(false)

const getTagColor = (index) => {
  const colors = ['#FEF3C7', '#DBEAFE', '#FCE7F3', '#D1FAE5', '#FED7AA', '#E9D5FF', '#FEE2E2', '#CFFAFE']
  return colors[index % colors.length]
}

onMounted(async () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  roomCode.value = currentPage.options?.room || gameStore.roomCode || generateRoomCode()
  await loadQuestions()
})

const generateRoomCode = () => {
  const playerId = gameStore.playerId || 'default'
  return 'P_' + playerId.substring(0, 10).toUpperCase()
}

const loadQuestions = async () => {
  loading.value = true
  try {
    const data = await getCustomQuestions(roomCode.value)
    questions.value = data
  } catch (error) {
    console.error('Failed to load questions:', error)
  } finally {
    loading.value = false
  }
}

const handleAddQuestion = async () => {
  if (!newQuestion.value.trim()) return
  adding.value = true
  try {
    const question = await addQuestion(newQuestion.value.trim(), roomCode.value)
    questions.value.unshift(question)
    newQuestion.value = ''
    uni.showToast({ title: 'Added!', icon: 'success' })
  } catch (error) {
    uni.showToast({ title: 'Failed to add', icon: 'none' })
  } finally {
    adding.value = false
  }
}

const handleDeleteQuestion = (question) => {
  uni.showModal({
    title: 'Delete',
    content: 'Delete this question?',
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteQuestion(question.id, roomCode.value)
          questions.value = questions.value.filter(q => q.id !== question.id)
          uni.showToast({ title: 'Deleted', icon: 'success' })
        } catch (error) {
          uni.showToast({ title: 'Failed', icon: 'none' })
        }
      }
    }
  })
}

const handleBack = () => {
  uni.navigateBack()
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
  margin-bottom: 8rpx;
  padding-right: 120rpx;
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

/* Textarea */
.textarea {
  width: 100%;
  min-height: 140rpx;
  background: #f9f9f9;
  border: none;
  border-radius: 16rpx;
  padding: 20rpx;
  font-size: 28rpx;
  color: #1a1a1a;
  line-height: 1.5;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12rpx;
}

.char-count {
  font-size: 22rpx;
  color: #999;
}

.add-btn {
  background: #1a1a1a;
  color: #fff;
  font-size: 26rpx;
  font-weight: 600;
  padding: 12rpx 28rpx;
  border-radius: 24rpx;
  border: none;
}

.add-btn[disabled] {
  opacity: 0.4;
}

/* Loading & Empty States */
.loading-state, .empty-state {
  padding: 48rpx;
  text-align: center;
}

.loading-text {
  font-size: 26rpx;
  color: #999;
}

.empty-icon {
  display: block;
  font-size: 64rpx;
  margin-bottom: 12rpx;
}

.empty-text {
  display: block;
  font-size: 28rpx;
  color: #1a1a1a;
  font-weight: 600;
  margin-bottom: 8rpx;
}

.empty-hint {
  display: block;
  font-size: 24rpx;
  color: #999;
}

/* Questions List */
.questions-list {
  max-height: 400rpx;
}

.question-item {
  display: flex;
  align-items: center;
  padding: 20rpx;
  border-radius: 16rpx;
  margin-bottom: 12rpx;
}

.question-text {
  flex: 1;
  font-size: 26rpx;
  color: #1a1a1a;
  line-height: 1.5;
}

.delete-btn {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.1);
  border-radius: 50%;
  margin-left: 12rpx;
  font-size: 32rpx;
  color: #666;
}

/* Ticket Footer */
.ticket-footer {
  padding: 24rpx 32rpx 32rpx;
  border-top: 1rpx solid #f0f0f0;
  background: #fff;
  border-radius: 0 0 32rpx 32rpx;
}

.info-card {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
  background: #f9f9f9;
  padding: 20rpx;
  border-radius: 16rpx;
}

.info-icon {
  font-size: 24rpx;
}

.info-text {
  flex: 1;
  font-size: 24rpx;
  color: #666;
  line-height: 1.5;
}
</style>
