import { createRouter, createWebHistory } from 'vue-router'
import Order from './views/Order.vue'
import Admin from './views/Admin.vue'
import Kitchen from './views/Kitchen.vue'
import Login from './views/Login.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: Login, name: 'login' },
    { path: '/order/:token?', component: Order, name: 'order' },
    { path: '/admin', component: Admin, name: 'admin', meta: { requiresAuth: true, adminOnly: true } },
    { path: '/kitchen', component: Kitchen, name: 'kitchen' },
  ],
})

// 路由守卫：检查登录状态
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = localStorage.getItem('user')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.adminOnly && user) {
    const isAdmin = JSON.parse(user).is_admin
    if (!isAdmin) {
      next('/order')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
