<template>
  <div class="tool-creator">
    <div class="creator-header">
      <button class="back-btn" @click="goBack">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        返回
      </button>
      <h1>{{ toolName }}</h1>
    </div>
    <div class="creator-content">
      <p>工具创作界面 - 工具ID: {{ toolId }}</p>
      <p>这里将显示具体的AI工具创作界面</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const toolId = ref('');
const toolName = ref('AI工具');

const goBack = () => {
  const query = route.query;
  if (query.category) {
    router.push({ path: '/', query: { category: query.category as string } });
  } else {
    router.push('/');
  }
};

onMounted(() => {
  toolId.value = route.params.toolId as string;
  toolName.value = `${toolId.value} - AI创作工具`;
});
</script>

<style scoped>
.tool-creator {
  min-height: 100vh;
  background-color: #f9fafb;
}

.creator-header {
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  color: #374151;
  font-size: 14px;
  transition: all 0.2s;
}

.back-btn:hover {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.creator-header h1 {
  font-size: 24px;
  color: #111827;
  margin: 0;
}

.creator-content {
  padding: 40px 24px;
  text-align: center;
}

.creator-content p {
  font-size: 16px;
  color: #6b7280;
  margin: 8px 0;
}
</style>
