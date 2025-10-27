<template>
  <div class="tool-creator-layout">
    <!-- 1. 这是我们的通用顶部导航栏 -->
    <header class="creator-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 24 24"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
          返回
        </button>
        <h1>{{ toolName }}</h1>
      </div>
      <div class="header-right">
        <div class="user-menu">
          <button class="user-btn">👤 用户</button>
          <div class="dropdown-content">
            <a href="/profile">个人空间</a>
            <a href="#" @click.prevent="handleLogout">退出登录</a>
          </div>
        </div>
      </div>
    </header>

    <!-- 2. 主内容区域 -->
    <main class="creator-content">
      <!-- 子组件将会在这里被渲染 -->
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
// 假设你有一个方法可以根据ID找到工具信息
// 为了简单，我们先写死名字，后面可以优化
const router = useRouter();
const route = useRoute();

const toolName = ref('AI 工具');

// 监听路由变化，以便在组件内部导航时更新标题
watch(
  () => route.meta.toolName, // 直接监听我们在路由中设置的 meta.toolName
  (newName) => {
    if (newName) {
      toolName.value = `${newName as string} 创作工具`;
    } else {
      toolName.value = 'AI 工具'; // 如果没有名字，显示默认值
    }
  },
  { immediate: true } // 立即执行，以便页面加载时就设置好标题
);

const goBack = () => router.push('/');

const handleLogout = () => {
  localStorage.removeItem('access_token');
  router.push('/login');
};
</script>

<style scoped>
.tool-creator-layout {
  display: flex;
  flex-direction: column;
  height: 100vh; 
  background-color: #f9fafb;
}

.creator-header {
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  /* 样式与之前类似 */
  display: flex; align-items: center; gap: 8px; padding: 8px 16px;
  background: transparent; border: 1px solid #d1d5db; border-radius: 8px;
  cursor: pointer; color: #374151; font-size: 14px; transition: all 0.2s;
}
.back-btn:hover { background-color: #f3f4f6; }
.back-btn svg { stroke: currentColor; stroke-width: 2; fill: none; }

.creator-header h1 {
  font-size: 20px;
  color: #111827;
  margin: 0;
}

.header-right .user-menu {
  position: relative;
  display: inline-block;
}

.user-btn {
  padding: 8px 16px;
  background-color: #f3f4f6;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.user-menu .dropdown-content {
  display: none;
  position: absolute;
  right: 0;
  background-color: white;
  min-width: 120px;
  box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.1);
  z-index: 1;
  border-radius: 8px;
  overflow: hidden;
}

.user-menu:hover .dropdown-content {
  display: block;
}

.dropdown-content a {
  color: black;
  padding: 12px 16px;
  text-decoration: none;
  display: block;
  font-size: 14px;
}

.dropdown-content a:hover {
  background-color: #f1f1f1;
}

.creator-content {
  flex-grow: 1;
  overflow-y: auto;
  width: 100%;
}
</style>
