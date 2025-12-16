// API base URL
const BASE_URL = 'https://human-connection.onrender.com'

// HTTP request helper
const request = (url, method = 'GET', data = null) => {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(res.data)
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

// Room APIs
export const createRoom = (hostNickname, hostId) => {
  return request('/api/rooms', 'POST', {
    host_nickname: hostNickname,
    host_id: hostId
  })
}

export const getRoom = (roomCode) => {
  return request(`/api/rooms/${roomCode}`)
}

export const checkRoomExists = (roomCode) => {
  return request(`/api/rooms/${roomCode}/exists`)
}

export const joinRoom = (roomCode, nickname, playerId) => {
  return request(`/api/rooms/${roomCode}/join`, 'POST', {
    nickname,
    player_id: playerId
  })
}

export const leaveRoom = (roomCode, playerId) => {
  return request(`/api/rooms/${roomCode}/leave/${playerId}`, 'DELETE')
}

// Question APIs
export const getSystemQuestions = () => {
  return request('/api/questions')
}

export const getRoomQuestions = (roomCode) => {
  return request(`/api/questions/room/${roomCode}`)
}

export const getCustomQuestions = (roomCode) => {
  return request(`/api/questions/custom/${roomCode}`)
}

export const addQuestion = (content, roomCode) => {
  return request('/api/questions', 'POST', {
    content,
    created_by: roomCode
  })
}

export const deleteQuestion = (questionId, roomCode) => {
  return request(`/api/questions/${questionId}?room_code=${roomCode}`, 'DELETE')
}

export { BASE_URL }
