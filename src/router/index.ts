// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import Login from '../components/Login.vue'; // 登录组件
import AiToolsHome from '../components/AiToolsHome.vue'; // AI工具主界面

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/', // 网站的根路径
    name: 'AiToolsHome',
    component: AiToolsHome,
    meta: { requiresAuth: true } // 添加一个元字段,表示这个路由需要登录才能访问
  },
  {
    path: '/tools/:toolId',
    name: 'ToolCreator',
    component: () => import('../components/ToolCreator.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../components/About.vue'),
  },
  {
    path: '/help',
    name: 'Help',
    component: () => import('../components/Help.vue'),
  },
  {
    path: '/pricing',
    name: 'Pricing',
    component: () => import('../components/Pricing.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(), // 使用 HTML5 History 模式
  routes, // 上面定义的路由规则
});

// --- 全局路由守卫 (非常重要！) ---
// 这个守卫会在每次路由跳转之前执行
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token'); // 检查本地是否有 token

  // 1. 如果目标路由需要登录，但用户未登录
  if (to.meta.requiresAuth && !isAuthenticated) {
    // 重定向到登录页
    next({ name: 'Login' });
  }
  // 2. 如果用户已登录,但试图访问登录页
  else if (to.name === 'Login' && isAuthenticated) {
    // 阻止他们,并让他们停留在当前页面或重定向到首页
    next({ name: 'AiToolsHome' });
  }
  // 3. 其他情况，正常放行
  else {
    next();
  }
});

export default router;