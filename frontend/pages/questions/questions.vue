<template>
  <view class="container">
    <!-- Header -->
    <view class="header">
      <view class="header-left" @click="handleBack">
        <text class="back-icon">←</text>
      </view>
      <view class="header-center">
        <text class="title">My Questions</text>
        <text v-if="roomCode" class="subtitle">Room: {{ roomCode }}</text>
      </view>
      <view class="header-right"></view>
    </view>

    <!-- Add question form -->
    <view class="add-section">
      <view class="input-wrapper">
        <textarea
          v-model="newQuestion"
          class="input"
          placeholder="Type your question here..."
          :maxlength="200"
          :auto-height="true"
        />
        <text class="char-count">{{ newQuestion.length }}/200</text>
      </view>
      <button class="btn btn-primary" @click="handleAddQuestion" :disabled="!newQuestion.trim() || adding">
        {{ adding ? 'Adding...' : 'Add Question' }}
      </button>
    </view>

    <!-- Questions list -->
    <view class="questions-section">
      <view class="section-header">
        <text class="section-title">Your Custom Questions ({{ questions.length }})</text>
      </view>

      <view v-if="loading" class="loading">
        <text>Loading...</text>
      </view>

      <view v-else-if="questions.length === 0" class="empty">
        <text class="empty-icon">📝</text>
        <text class="empty-text">No custom questions yet</text>
        <text class="empty-hint">Add your own questions to make the game more personal!</text>
      </view>

      <scroll-view v-else class="questions-list" scroll-y>
        <view
          v-for="question in questions"
          :key="question.id"
          class="question-item"
        >
          <text class="question-text">{{ question.content }}</text>
          <view class="question-actions">
            <view class="delete-btn" @click="handleDeleteQuestion(question)">
              <text class="delete-icon">🗑️</text>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- Info section -->
    <view class="info-section">
      <text class="info-text">
        💡 Custom questions are only visible in games created with the same room code.
      </text>
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

onMounted(async () => {
  // Get room code from URL params or generate from player ID
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  roomCode.value = currentPage.options?.room || gameStore.roomCode || generateRoomCode()

  await loadQuestions()
})

const generateRoomCode = () => {
  // Use player ID to generate consistent "room code" for private questions
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
    uni.showToast({ title: 'Failed to load questions', icon: 'none' })
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
    uni.showToast({ title: 'Question added!', icon: 'success' })
  } catch (error) {
    console.error('Failed to add question:', error)
    uni.showToast({ title: 'Failed to add question', icon: 'none' })
  } finally {
    adding.value = false
  }
}

const handleDeleteQuestion = (question) => {
  uni.showModal({
    title: 'Delete Question',
    content: 'Are you sure you want to delete this question?',
    success: async (res) => {
      if (res.confirm) {
        try {
          await deleteQuestion(question.id, roomCode.value)
          questions.value = questions.value.filter(q => q.id !== question.id)
          uni.showToast({ title: 'Question deleted', icon: 'success' })
        } catch (error) {
          console.error('Failed to delete question:', error)
          uni.showToast({ title: 'Failed to delete', icon: 'none' })
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
  margin-bottom: 32rpx;
}

.header-left,
.header-right {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-left {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}

.back-icon {
  font-size: 36rpx;
  color: #ffffff;
}

.header-center {
  flex: 1;
  text-align: center;
}

.title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #ffffff;
}

.subtitle {
  display: block;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 8rpx;
}

.add-section {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
}

.input-wrapper {
  position: relative;
  margin-bottom: 24rpx;
}

.input {
  width: 100%;
  min-height: 120rpx;
  background: #f3f4f6;
  border: 2rpx solid #e5e7eb;
  border-radius: 16rpx;
  padding: 24rpx;
  font-size: 30rpx;
  color: #1f2937;
  line-height: 1.5;
}

.input:focus {
  border-color: #667eea;
  background: #ffffff;
}

.char-count {
  position: absolute;
  right: 16rpx;
  bottom: 16rpx;
  font-size: 22rpx;
  color: #9ca3af;
}

.btn {
  width: 100%;
  height: 88rpx;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  box-shadow: 0 8rpx 24rpx rgba(102, 126, 234, 0.4);
}

.btn:active {
  transform: scale(0.98);
  opacity: 0.9;
}

.btn[disabled] {
  opacity: 0.5;
}

.questions-section {
  flex: 1;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  max-height: 60vh;
}

.section-header {
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1f2937;
}

.loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

.empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48rpx;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 24rpx;
}

.empty-text {
  font-size: 30rpx;
  color: #1f2937;
  font-weight: 600;
  margin-bottom: 12rpx;
}

.empty-hint {
  font-size: 26rpx;
  color: #6b7280;
  text-align: center;
}

.questions-list {
  flex: 1;
}

.question-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: #f9fafb;
  border-radius: 16rpx;
  margin-bottom: 16rpx;
}

.question-text {
  flex: 1;
  font-size: 28rpx;
  color: #1f2937;
  line-height: 1.5;
}

.question-actions {
  margin-left: 16rpx;
}

.delete-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fee2e2;
  border-radius: 12rpx;
}

.delete-icon {
  font-size: 28rpx;
}

.info-section {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16rpx;
  padding: 24rpx;
}

.info-text {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
}
</style>
