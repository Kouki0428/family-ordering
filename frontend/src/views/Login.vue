<template>
  <div class="login-page">
    <div class="login-card">
      <h1>🏠 家庭点餐系统</h1>
      <p class="subtitle">请登录您的账号</p>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="登录" name="login">
          <el-form @submit.prevent="handleLogin">
            <el-form-item>
              <el-input 
                v-model="loginForm.username" 
                placeholder="用户名"
                prefix-icon="User"
                size="large"
              />
            </el-form-item>
            <el-form-item>
              <el-input 
                v-model="loginForm.password" 
                placeholder="密码"
                type="password"
                prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              style="width: 100%"
              :loading="loading"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="注册" name="register">
          <el-form @submit.prevent="handleRegister">
            <el-form-item>
              <el-input 
                v-model="registerForm.username" 
                placeholder="用户名"
                prefix-icon="User"
                size="large"
              />
            </el-form-item>
            <el-form-item>
              <el-input 
                v-model="registerForm.password" 
                placeholder="密码"
                type="password"
                prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="registerForm.is_admin">
                设为管理员（首次注册建议勾选）
              </el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="registerForm.is_cooker">
                设为做餐者（可以确认订单）
              </el-checkbox>
            </el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              style="width: 100%"
              :loading="loading"
              @click="handleRegister"
            >
              注册
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '../api'

const router = useRouter()
const activeTab = ref('login')
const loading = ref(false)

const loginForm = ref({
  username: '',
  password: '',
})

const registerForm = ref({
  username: '',
  password: '',
  is_admin: false,
  is_cooker: false,
})

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  
  loading.value = true
  try {
    const token = await authApi.login(loginForm.value.username, loginForm.value.password)
    localStorage.setItem('token', token.access_token)
    ElMessage.success('登录成功')
    
    // 获取用户信息
    const user = await authApi.me()
    localStorage.setItem('user', JSON.stringify(user))
    
    // 根据用户角色跳转
    if (user.is_admin) {
      router.push('/admin')
    } else {
      router.push('/order')
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  
  if (registerForm.value.password.length < 4) {
    ElMessage.warning('密码至少 4 位')
    return
  }
  
  loading.value = true
  try {
    await authApi.register(registerForm.value)
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.value.username = registerForm.value.username
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-card h1 {
  text-align: center;
  margin: 0 0 10px 0;
  color: #333;
}

.subtitle {
  text-align: center;
  color: #666;
  margin: 0 0 30px 0;
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}
</style>
