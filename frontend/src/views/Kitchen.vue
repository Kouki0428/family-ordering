<template>
  <div class="kitchen-page">
    <div class="header">
      <h1>🍳 后厨订单大屏</h1>
      <div class="connection-status">
        <el-tag :type="wsConnected ? 'success' : 'danger'" size="small">
          <span class="pulse-dot">{{ wsConnected ? '●' : '○' }}</span>
          {{ wsConnected ? '已连接' : '已断开' }}
        </el-tag>
        <el-tag size="small" type="warning">预订: {{ pendingCount }}</el-tag>
        <el-tag size="small" type="primary">待确认: {{ confirmedCount }}</el-tag>
      </div>
    </div>

    <!-- 订单列表 -->
    <div class="orders-grid">
      <el-card
        v-for="order in activeOrders"
        :key="order.id"
        class="order-card"
        :class="`status-${order.status}`"
        shadow="hover"
      >
        <div class="order-header">
          <span class="order-id">#{{ order.id }}</span>
          <el-tag :type="order.status === '预订' ? 'success' : 'warning'" size="small">
            {{ order.status }}
          </el-tag>
        </div>
        <div class="order-items">
          <div v-for="(item, index) in order.items" :key="index" class="order-item">
            <span class="item-name">{{ item.name }}</span>
            <span class="item-quantity">×{{ item.quantity }}</span>
          </div>
        </div>
        <div class="order-footer" v-if="order.note">
          <el-tag type="warning" size="small">备注: {{ order.note }}</el-tag>
        </div>
        <div class="order-actions">
          <el-button
            v-if="order.status === '待确认'"
            type="primary"
            size="small"
            @click="updateStatus(order.id, '预订')"
          >
            确认订单
          </el-button>
          <el-button
            v-if="order.status === '预订'"
            type="info"
            size="small"
            @click="updateStatus(order.id, '待确认')"
          >
            退回
          </el-button>
        </div>
      </el-card>

      <div v-if="activeOrders.length === 0" class="empty-state">
        <p>暂无待处理订单</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { orderApi } from '../api'
import { useWebSocket, showNotification } from '../composables/useWebSocket'

const { wsConnected, onMessage } = useWebSocket()

const orders = ref<any[]>([])
let removeCallback: (() => void) | null = null

const activeOrders = computed(() => {
  return orders.value.filter(o => o.status === '预订' || o.status === '待确认')
})

const pendingCount = computed(() => orders.value.filter(o => o.status === '预订').length)
const confirmedCount = computed(() => orders.value.filter(o => o.status === '待确认').length)

const loadOrders = async () => {
  try {
    const all = await orderApi.listAll()
    orders.value = all
  } catch (e) {
    ElMessage.error('加载订单失败')
  }
}

const updateStatus = async (orderId: number, status: string) => {
  try {
    await orderApi.updateStatus(orderId, status)
    ElMessage.success('状态已更新')
    loadOrders()
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

onMounted(() => {
  loadOrders()
  
  // 注册 WebSocket 消息回调
  removeCallback = onMessage((data) => {
    if (data.type === 'order_created' || data.type === 'order_status_changed') {
      // 自动刷新订单
      loadOrders()
      
      // 显示通知
      if (data.type === 'order_created') {
        showNotification(
          '新订单',
          `订单 #${data.data?.order?.id} 已提交`,
          'warning'
        )
      }
    }
  })
  
  // 定期刷新（兜底）
  setInterval(loadOrders, 30000)
})

onUnmounted(() => {
  if (removeCallback) {
    removeCallback()
  }
})
</script>

<style scoped>
.kitchen-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background: #1a1a2e;
  min-height: 100vh;
  color: #fff;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: #16213e;
  border-radius: 12px;
}

.header h1 {
  margin: 0;
  font-size: 28px;
}

.connection-status {
  display: flex;
  gap: 10px;
  align-items: center;
}

.orders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.order-card {
  background: #16213e;
  border: 2px solid #0f3460;
  color: #fff;
  border-radius: 12px;
}

.order-card.status-预订 {
  border-color: #67c23a;
}

.order-card.status-待确认 {
  border-color: #e6a23c;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #0f3460;
}

.order-id {
  font-size: 20px;
  font-weight: bold;
  color: #e6a23c;
}

.order-items {
  margin-bottom: 15px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  font-size: 16px;
}

.item-name {
  color: #e0e0e0;
}

.item-quantity {
  color: #e6a23c;
  font-weight: bold;
}

.order-footer {
  margin-bottom: 15px;
}

.order-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px;
  color: #666;
}

.empty-state p {
  font-size: 24px;
}

.pulse-dot {
  display: inline-block;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
