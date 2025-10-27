// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import Login from '../components/Login.vue'; // 登录组件
import AiToolsHome from '../components/AiToolsHome.vue'; // AI工具主界面
import ToolCreator from '../components/ToolCreator.vue';

import { imageTools } from '../data/imageTools';
import { audioTools } from '../data/audioTools';
import { videoTools } from '../data/videoTools';
import { textTools } from '../data/textTools';
import { codeTools } from '../data/codeTools';
const allTools = [
  ...imageTools,
  ...audioTools,
  ...videoTools,
  ...textTools,
  ...codeTools,
];

// 动态生成所有工具的子路由
const toolRoutes = allTools.map(tool => {
  // 我们直接使用 tool.id 来决定路由名称和组件文件名
  const componentFileName = tool.id; // 例如: 'symphony-ai'
  const routeName = tool.id;         // 路由的唯一名称，也使用 id

  return {
    // URL 路径就是 tool.id
    path: tool.id,
    // 路由的 name 也使用 tool.id，确保唯一性
    name: routeName,
    // 动态导入组件时，直接使用 id 拼接文件名
    // 例如，寻找 '../components/tools/symphony-ai.vue'
    component: () => import(`../data/tools/${componentFileName}.vue`),
    meta: {
      toolName: tool.name, // meta.toolName 仍然使用工具的显示名称，用于在页面顶部显示
      requiresAuth: true,
    }
  };
});

const routes = [
  {
    path: '/', // 网站的根路径
    name: 'AiToolsHome',
    component: AiToolsHome,
    // meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/tools',       // 父路由
    component: ToolCreator, // 使用 ToolCreator作为布局
    children: toolRoutes, // 将上面动态生成的路由作为子路由！
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