<template>
  <div class="order-page">
    <div class="header">
      <div class="header-left">
        <h1>{{ tableName }} · 点餐</h1>
        <span class="mode-tag" :class="currentMode">
          {{ currentMode === 'cook' ? '👨‍🍳 做餐模式' : '🍽️ 订餐模式' }}
        </span>
      </div>
      <div class="header-right">
        <el-button 
          v-if="user?.is_cooker || user?.is_admin"
          :type="currentMode === 'cook' ? 'success' : 'default'"
          @click="toggleMode"
        >
          {{ currentMode === 'cook' ? '切换到订餐' : '切换到做餐' }}
        </el-button>
        <el-button type="primary" @click="submitOrder" :disabled="cart.length === 0">
          提交预订 ({{ cart.length }} 项)
        </el-button>
        <el-button text @click="logout">退出</el-button>
      </div>
    </div>

    <!-- 做餐模式：待确认订单 -->
    <div v-if="currentMode === 'cook'" class="cook-section">
      <h2>📋 待确认订单</h2>
      <div v-if="pendingOrders.length === 0" class="empty-tip">
        <p>暂无待确认订单</p>
      </div>
      <div v-else class="order-list">
        <el-card v-for="order in pendingOrders" :key="order.id" class="pending-order-card">
          <div class="order-header">
            <span class="order-id">#{{ order.id }}</span>
            <el-tag type="warning">待确认</el-tag>
            <span class="order-time">{{ formatDate(order.created_at) }}</span>
          </div>
          <div class="order-items">
            <div v-for="(item, index) in order.items" :key="index">
              <span>{{ item.name }} × {{ item.quantity }}</span>
            </div>
          </div>
          <div class="order-note" v-if="order.note">
            <el-tag type="info">备注: {{ order.note }}</el-tag>
          </div>
          <div class="order-actions">
            <el-button type="success" @click="confirmOrder(order.id)">
              确认订单（开始制作）
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 餐段选择 -->
    <div class="meal-selector">
      <span class="label">选择餐段：</span>
      <el-radio-group v-model="selectedMealType" @change="loadMenus">
        <el-radio-button label="早餐">🌅 早餐</el-radio-button>
        <el-radio-button label="午餐">☀️ 午餐</el-radio-button>
        <el-radio-button label="晚餐">🌙 晚餐</el-radio-button>
        <el-radio-button label="夜宵">🌃 夜宵</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 菜单列表 -->
    <div class="menu-grid">
      <el-card
        v-for="menu in menus"
        :key="menu.id"
        class="menu-card"
        shadow="hover"
      >
        <div class="menu-image">
          <img :src="menu.image_url || defaultImage" :alt="menu.name" />
        </div>
        <div class="menu-info">
          <h3>{{ menu.name }}</h3>
          <p class="category">{{ menu.category }}</p>
        </div>
        <el-button
          type="success"
          circle
          @click="addToCart(menu)"
        >
          +
        </el-button>
      </el-card>
    </div>

    <!-- 购物车弹窗 -->
    <el-drawer v-model="cartVisible" title="购物车" direction="rtl">
      <div v-if="cart.length === 0" class="empty-cart">
        <p>购物车是空的</p>
      </div>
      <div v-else class="cart-list">
        <div v-for="(item, index) in cart" :key="index" class="cart-item">
          <span>{{ item.name }} × {{ item.quantity }}</span>
          <el-button type="danger" circle size="small" @click="removeFromCart(index)">
            ×
          </el-button>
        </div>
      </div>
      <div class="cart-footer">
        <el-input v-model="note" placeholder="备注（如：少辣、不要香菜等）" />
        <el-button type="primary" @click="submitOrder">
          提交预订
        </el-button>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { menuApi, tableApi, orderApi, authApi } from '../api'

const route = useRoute()
const router = useRouter()
const tableToken = ref(route.params.token as string || '')
const tableName = ref('未知餐桌')
const menus = ref<any[]>([])
const cart = ref<any[]>([])
const note = ref('')
const cartVisible = ref(false)
const selectedMealType = ref('早餐')
const pendingOrders = ref<any[]>([])
const currentMode = ref<'order' | 'cook'>('order')  // 当前模式：订餐或做餐
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const defaultImage = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150"><rect fill="%23e0e0e0" width="200" height="150"/><text x="100" y="80" font-size="14" fill="%23999" text-anchor="middle">暂无图片</text></svg>'

const loadMenus = async () => {
  try {
    menus.value = await menuApi.list(selectedMealType.value)
  } catch (e) {
    ElMessage.error('加载菜单失败')
  }
}

const loadTable = async () => {
  if (tableToken.value) {
    try {
      const table = await tableApi.getByToken(tableToken.value)
      tableName.value = table.name
    } catch (e) {
      ElMessage.error('餐桌不存在')
    }
  }
}

const loadPendingOrders = async () => {
  try {
    const allOrders = await orderApi.listAll()
    pendingOrders.value = allOrders.filter(o => o.status === '待确认')
  } catch (e) {
    console.error('加载订单失败')
  }
}

const addToCart = (menu: any) => {
  const existing = cart.value.find(item => item.menu_id === menu.id)
  if (existing) {
    existing.quantity++
  } else {
    cart.value.push({
      menu_id: menu.id,
      name: menu.name,
      quantity: 1,
    })
  }
  cartVisible.value = true
  ElMessage.success(`已加入：${menu.name}`)
}

const removeFromCart = (index: number) => {
  cart.value.splice(index, 1)
}

const submitOrder = async () => {
  if (cart.value.length === 0) return
  try {
    await orderApi.create({
      table_token: tableToken.value,
      items: cart.value,
      note: note.value,
    })
    ElMessage.success('预订已提交，等待确认')
    cart.value = []
    note.value = ''
    cartVisible.value = false
  } catch (e) {
    ElMessage.error('下单失败')
  }
}

const confirmOrder = async (orderId: number) => {
  try {
    await orderApi.updateStatus(orderId, '预订')
    ElMessage.success('订单已确认，开始制作')
    loadPendingOrders()
  } catch (e) {
    ElMessage.error('确认失败')
  }
}

const toggleMode = () => {
  currentMode.value = currentMode.value === 'cook' ? 'order' : 'cook'
  if (currentMode.value === 'cook') {
    loadPendingOrders()
  }
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN', { 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}

// 监听路由参数变化
watch(() => route.params.token, (newToken) => {
  tableToken.value = newToken as string || ''
  loadTable()
})

onMounted(() => {
  // 检查用户是否有做餐权限
  if (user.value.is_cooker || user.value.is_admin) {
    // 默认进入订餐模式，但可以切换
    currentMode.value = 'order'
  }
  loadMenus()
  loadTable()
})

// 定期刷新待确认订单（做餐模式）
setInterval(() => {
  if (currentMode.value === 'cook') {
    loadPendingOrders()
  }
}, 30000)
</script>

<style scoped>
.order-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mode-tag {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 14px;
}

.mode-tag.cook {
  background: #67c23a;
  color: white;
}

.mode-tag.order {
  background: #409eff;
  color: white;
}

.cook-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.cook-section h2 {
  margin: 0 0 15px 0;
  color: #333;
}

.empty-tip {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.order-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.pending-order-card {
  background: #fff;
  border: 2px solid #e6a23c;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.order-id {
  font-weight: bold;
  color: #e6a23c;
}

.order-time {
  font-size: 12px;
  color: #999;
}

.order-items {
  margin-bottom: 10px;
}

.order-note {
  margin-bottom: 10px;
}

.order-actions {
  display: flex;
  justify-content: flex-end;
}

.meal-selector {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.meal-selector .label {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.menu-card {
  position: relative;
  cursor: pointer;
}

.menu-image {
  width: 100%;
  height: 150px;
  overflow: hidden;
  border-radius: 8px;
  margin-bottom: 10px;
}

.menu-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.menu-info h3 {
  margin: 0 0 5px 0;
}

.category {
  color: #666;
  font-size: 14px;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.cart-footer {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.empty-cart {
  text-align: center;
  color: #999;
  padding: 40px 0;
}
</style>
