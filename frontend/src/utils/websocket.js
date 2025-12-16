// WebSocket manager for real-time game communication
// Change to your IP for network play
const WS_BASE_URL = 'ws://192.168.4.26:8000'

class GameWebSocket {
  constructor() {
    this.socket = null
    this.roomCode = null
    this.playerId = null
    this.listeners = {}
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 2000
  }

  connect(roomCode, playerId) {
    return new Promise((resolve, reject) => {
      this.roomCode = roomCode
      this.playerId = playerId

      const url = `${WS_BASE_URL}/ws/${roomCode}/${playerId}`

      // #ifdef H5
      this.socket = new WebSocket(url)

      this.socket.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        resolve()
      }

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        this.handleMessage(data)
      }

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error)
        reject(error)
      }

      this.socket.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        this.emit('disconnected', { code: event.code, reason: event.reason })
        this.attemptReconnect()
      }
      // #endif

      // #ifndef H5
      this.socket = uni.connectSocket({
        url,
        complete: () => {}
      })

      uni.onSocketOpen(() => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        resolve()
      })

      uni.onSocketMessage((res) => {
        const data = JSON.parse(res.data)
        this.handleMessage(data)
      })

      uni.onSocketError((error) => {
        console.error('WebSocket error:', error)
        reject(error)
      })

      uni.onSocketClose((event) => {
        console.log('WebSocket closed')
        this.emit('disconnected', event)
        this.attemptReconnect()
      })
      // #endif
    })
  }

  handleMessage(data) {
    const { type } = data
    this.emit(type, data)
    this.emit('message', data)
  }

  send(type, data = {}) {
    const message = JSON.stringify({ type, ...data })

    // #ifdef H5
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(message)
    }
    // #endif

    // #ifndef H5
    uni.sendSocketMessage({ data: message })
    // #endif
  }

  // Event emitter methods
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = []
    }
    this.listeners[event].push(callback)
  }

  off(event, callback) {
    if (!this.listeners[event]) return
    this.listeners[event] = this.listeners[event].filter(cb => cb !== callback)
  }

  emit(event, data) {
    if (!this.listeners[event]) return
    this.listeners[event].forEach(callback => callback(data))
  }

  // Game actions
  startGame() {
    this.send('start_game')
  }

  drawCard() {
    this.send('draw_card')
  }

  switchCard() {
    this.send('switch_card')
  }

  endGame() {
    this.send('end_game')
  }

  restartGame() {
    this.send('restart_game')
  }

  // Reconnection logic
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnect attempts reached')
      this.emit('reconnect_failed', {})
      return
    }

    this.reconnectAttempts++
    console.log(`Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts}`)

    setTimeout(() => {
      if (this.roomCode && this.playerId) {
        this.connect(this.roomCode, this.playerId)
          .then(() => {
            this.emit('reconnected', {})
          })
          .catch(() => {
            this.attemptReconnect()
          })
      }
    }, this.reconnectDelay)
  }

  disconnect() {
    this.reconnectAttempts = this.maxReconnectAttempts // Prevent reconnection

    // #ifdef H5
    if (this.socket) {
      this.socket.close()
    }
    // #endif

    // #ifndef H5
    uni.closeSocket()
    // #endif

    this.socket = null
    this.roomCode = null
    this.playerId = null
    this.listeners = {}
  }
}

// Export singleton instance
export const gameSocket = new GameWebSocket()
