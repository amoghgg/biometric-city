// WebSocket client with auto-reconnect and ping-keepalive

export class CitySocket {
  constructor(city, onSnapshot) {
    this.city = city
    this.onSnapshot = onSnapshot
    this.ws = null
    this.pingInterval = null
    this.reconnectTimeout = null
    this.closed = false
    this._connect()
  }

  _connect() {
    if (this.closed) return
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
    const url = `${protocol}://${location.host}/ws/${this.city}`

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log(`[ws] connected to ${this.city}`)
      this.pingInterval = setInterval(() => {
        if (this.ws.readyState === WebSocket.OPEN) {
          this.ws.send('ping')
        }
      }, 25000)
    }

    this.ws.onmessage = (evt) => {
      if (evt.data === 'pong') return
      try {
        const snapshot = JSON.parse(evt.data)
        this.onSnapshot(snapshot)
      } catch (e) {
        console.warn('[ws] parse error', e)
      }
    }

    this.ws.onerror = () => console.warn(`[ws] error on ${this.city}`)

    this.ws.onclose = () => {
      clearInterval(this.pingInterval)
      if (!this.closed) {
        console.log(`[ws] disconnected from ${this.city}, reconnecting in 3s...`)
        this.reconnectTimeout = setTimeout(() => this._connect(), 3000)
      }
    }
  }

  destroy() {
    this.closed = true
    clearInterval(this.pingInterval)
    clearTimeout(this.reconnectTimeout)
    if (this.ws) this.ws.close()
  }
}
