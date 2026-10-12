import { ref, onMounted, onUnmounted } from 'vue'
import { ElNotification } from 'element-plus'

let ws: WebSocket | null = null
let reconnectTimer: any = null
let heartbeatTimer: any = null

// 全局连接状态
export const wsConnected = ref(false)
export const wsMessage = ref<any>(null)

// 消息回调列表
const messageCallbacks: Array<(data: any) => void> = []

/**
 * 初始化 WebSocket 连接
 */
export function initWebSocket() {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  ws = new WebSocket(`${protocol}//${window.location.host}/ws`)

  ws.onopen = () => {
    wsConnected.value = true
    console.log('WebSocket 已连接')
    
    // 启动心跳
    startHeartbeat()
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      wsMessage.value = data
      
      // 通知所有回调
      messageCallbacks.forEach(callback => {
        try {
          callback(data)
        } catch (e) {
          console.error('回调执行失败:', e)
        }
      })
    } catch (e) {
      console.error('解析消息失败:', e)
    }
  }

  ws.onclose = () => {
    wsConnected.value = false
    console.log('WebSocket 已断开，尝试重连...')
    
    // 停止心跳
    stopHeartbeat()
    
    // 自动重连
    scheduleReconnect()
  }

  ws.onerror = (error) => {
    console.error('WebSocket 错误:', error)
  }
}

/**
 * 添加消息回调
 */
export function onMessage(callback: (data: any) => void) {
  messageCallbacks.push(callback)
  return () => {
    const index = messageCallbacks.indexOf(callback)
    if (index > -1) {
      messageCallbacks.splice(index, 1)
    }
  }
}

/**
 * 调度重连
 */
function scheduleReconnect() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
  }
  reconnectTimer = setTimeout(() => {
    initWebSocket()
  }, 3000)
}

/**
 * 启动心跳
 */
function startHeartbeat() {
  stopHeartbeat()
  heartbeatTimer = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send('ping')
    }
  }, 25000)
}

/**
 * 停止心跳
 */
function stopHeartbeat() {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
}

/**
 * 在组件中使用 WebSocket
 */
export function useWebSocket() {
  let cleanup: (() => void) | null = null

  onMounted(() => {
    initWebSocket()
  })

  onUnmounted(() => {
    if (cleanup) {
      cleanup()
    }
  })

  return {
    wsConnected,
    wsMessage,
    onMessage
  }
}

/**
 * 显示通知
 */
export function showNotification(title: string, message: string, type: 'success' | 'warning' | 'info' | 'error' = 'info') {
  ElNotification({
    title,
    message,
    type,
    duration: 5000,
  })
}
