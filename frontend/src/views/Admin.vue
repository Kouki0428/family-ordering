<template>
  <div class="admin-page">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>家庭点餐 · 管理后台</h1>
          <div class="user-info">
            <span>👤 {{ user?.username }}</span>
            <el-button size="small" @click="logout">退出</el-button>
          </div>
        </div>
      </el-header>
      <el-main>
        <el-tabs v-model="activeTab">
          <!-- 菜单管理 -->
          <el-tab-pane label="菜单管理" name="menus">
            <el-button type="primary" @click="openMenuDialog()">+ 新增菜单</el-button>
            <el-table :data="menus" style="width: 100%; margin-top: 20px">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="name" label="菜品名称" />
              <el-table-column prop="category" label="分类" width="120" />
              <el-table-column prop="meal_type" label="餐段" width="100">
                <template #default="{ row }">
                  <el-tag size="small">{{ getMealTypeIcon(row.meal_type) }} {{ row.meal_type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="is_available" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_available ? 'success' : 'info'">
                    {{ row.is_available ? '可售' : '下架' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button size="small" @click="openMenuDialog(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteMenu(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <!-- 订单管理 -->
          <el-tab-pane label="订单管理" name="orders">
            <el-table :data="orders" style="width: 100%">
              <el-table-column prop="id" label="订单号" width="80" />
              <el-table-column prop="status" label="状态" width="120">
                <template #default="{ row }">
                  <el-tag :type="row.status === '预订' ? 'warning' : 'primary'">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="items" label="菜品" min-width="250">
                <template #default="{ row }">
                  <span v-for="(item, i) in row.items" :key="i">
                    {{ item.name }}×{{ item.quantity }}{{ i < row.items.length - 1 ? '、' : '' }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="note" label="备注" min-width="150">
                <template #default="{ row }">
                  <el-tag v-if="row.note" type="warning" size="small">{{ row.note }}</el-tag>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="下单时间" width="180">
                <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button
                    v-if="row.status === '预订'"
                    type="primary"
                    size="small"
                    @click="updateOrderStatus(row.id, '待确认')"
                  >
                    确认订单
                  </el-button>
                  <el-button
                    v-if="row.status === '待确认'"
                    type="success"
                    size="small"
                    @click="updateOrderStatus(row.id, '预订')"
                  >
                    退回
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <!-- 用户管理 -->
          <el-tab-pane label="用户管理" name="users" v-if="user?.is_admin">
            <el-table :data="users" style="width: 100%">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="username" label="用户名" />
              <el-table-column label="角色" width="150">
                <template #default="{ row }">
                  <el-tag v-if="row.is_admin" type="danger">管理员</el-tag>
                  <el-tag v-else type="info">普通用户</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="300">
                <template #default="{ row }">
                  <el-checkbox 
                    v-model="row.is_admin" 
                    @change="updateUserRole(row.id, 'is_admin', row.is_admin)"
                    style="margin-right: 15px"
                  >
                    管理员
                  </el-checkbox>
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="deleteUser(row.id)"
                    :disabled="row.id === user.id"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-main>
    </el-container>

    <!-- 菜单编辑弹窗 -->
    <el-dialog v-model="menuDialogVisible" :title="editingMenu ? '编辑菜单' : '新增菜单'">
      <el-form :model="menuForm" label-width="80px">
        <el-form-item label="菜品名称">
          <el-input v-model="menuForm.name" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="menuForm.category">
            <el-option label="热菜" value="热菜" />
            <el-option label="凉菜" value="凉菜" />
            <el-option label="汤品" value="汤品" />
            <el-option label="主食" value="主食" />
            <el-option label="饮品" value="饮品" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="餐段">
          <el-select v-model="menuForm.meal_type">
            <el-option label="🌅 早餐" value="早餐" />
            <el-option label="☀️ 午餐" value="午餐" />
            <el-option label="🌙 晚餐" value="晚餐" />
            <el-option label="🌃 夜宵" value="夜宵" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="menuForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="图片URL">
          <el-input v-model="menuForm.image_url" placeholder="https://..." />
        </el-form-item>
        <el-form-item label="是否可售">
          <el-switch v-model="menuForm.is_available" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="menuDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMenu">保存</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { menuApi, orderApi, authApi, usersApi } from '../api'

const router = useRouter()
const activeTab = ref('menus')
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const menus = ref<any[]>([])
const orders = ref<any[]>([])
const users = ref<any[]>([])
const menuDialogVisible = ref(false)
const editingMenu = ref<any>(null)
const menuForm = ref({
  name: '',
  category: '热菜',
  meal_type: '早餐',
  description: '',
  image_url: '',
  is_available: true,
})

const loadMenus = async () => {
  try {
    menus.value = await menuApi.list()
  } catch (e) {
    ElMessage.error('加载菜单失败')
  }
}

const loadOrders = async () => {
  try {
    orders.value = await orderApi.listAll()
  } catch (e) {
    ElMessage.error('加载订单失败')
  }
}

const loadUsers = async () => {
  try {
    users.value = await usersApi.list()
  } catch (e) {
    ElMessage.error('加载用户失败')
  }
}

const openMenuDialog = (menu?: any) => {
  if (menu) {
    editingMenu.value = menu
    menuForm.value = { ...menu, is_available: !!menu.is_available }
  } else {
    editingMenu.value = null
    menuForm.value = {
      name: '',
      category: '热菜',
      meal_type: '早餐',
      description: '',
      image_url: '',
      is_available: true,
    }
  }
  menuDialogVisible.value = true
}

const saveMenu = async () => {
  try {
    if (editingMenu.value) {
      await menuApi.update(editingMenu.value.id, menuForm.value)
    } else {
      await menuApi.create(menuForm.value)
    }
    ElMessage.success('保存成功')
    menuDialogVisible.value = false
    loadMenus()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const deleteMenu = async (id: number) => {
  await ElMessageBox.confirm('确定删除？', '提示')
  try {
    await menuApi.delete(id)
    ElMessage.success('已删除')
    loadMenus()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const updateOrderStatus = async (id: number, status: string) => {
  try {
    await orderApi.updateStatus(id, status)
    ElMessage.success('状态已更新')
    loadOrders()
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

const getMealTypeIcon = (mealType: string) => {
  const icons: Record<string, string> = {
    '早餐': '🌅',
    '午餐': '☀️',
    '晚餐': '🌙',
    '夜宵': '🌃',
  }
  return icons[mealType] || ''
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const updateUserRole = async (userId: number, role: 'is_admin' | 'is_cooker', value: boolean) => {
  try {
    await usersApi.update(userId, { [role]: value })
    ElMessage.success('权限已更新')
    loadUsers()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '更新失败')
    // 回滚
    loadUsers()
  }
}

const deleteUser = async (id: number) => {
  await ElMessageBox.confirm('确定删除该用户？', '提示')
  try {
    await usersApi.delete(id)
    ElMessage.success('已删除')
    loadUsers()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}

onMounted(() => {
  loadMenus()
  loadOrders()
  loadUsers()
})
</script>

<style scoped>
.admin-page {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.tip {
  color: #666;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
  margin-bottom: 10px;
}
</style>
