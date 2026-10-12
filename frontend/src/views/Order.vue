<template>
  <div class="order-page">
    <div class="header">
      <h1>{{ tableName }} · 点餐</h1>
      <el-button type="primary" @click="submitOrder" :disabled="cart.length === 0">
        提交预订 ({{ cart.length }} 项)
      </el-button>
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
import { ref, onMounted, watch } from 'vue'
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
    ElMessage.success('预订已提交')
    cart.value = []
    note.value = ''
    cartVisible.value = false
  } catch (e) {
    ElMessage.error('下单失败')
  }
}

// 监听路由参数变化
watch(() => route.params.token, (newToken) => {
  tableToken.value = newToken as string || ''
  loadTable()
})

onMounted(() => {
  loadMenus()
  loadTable()
})
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
