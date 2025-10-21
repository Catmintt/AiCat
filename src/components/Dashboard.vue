<!-- src/views/Dashboard.vue -->
<template>
  <div class="dashboard-container">
    <h1>欢迎来到 AiCat 平台!</h1>
    <p>您已成功登录。</p>
    <button @click="handleLogout" class="logout-button">退出登录</button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus'; 


const router = useRouter();

const handleLogout = () => {
  // 1. 清除本地存储的 token
  localStorage.removeItem('access_token');
  
  // 2. 提示用户
  ElMessage.warning('您已成功退出登录。');
  
  // 3. 跳转回登录页面
  router.push('/login');
};
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
  background-color: #f9fafb;
}

h1 {
  font-size: 2.5rem;
  color: #333;
}

p {
  font-size: 1.2rem;
  color: #666;
  margin-top: 1rem;
}

.logout-button {
  margin-top: 2rem;
  padding: 10px 20px;
  font-size: 1rem;
  color: white;
  background-color: #ef4444; /* 红色 */
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.logout-button:hover {
  background-color: #dc2626; /* 深红色 */
}
</style>