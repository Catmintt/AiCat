<template>
  <section class="tool-category-section" id="image-tools" v-show="filteredTools.length > 0">
    <header class="section-header">
      <h2 class="section-title">🎨 AI图像工具</h2>
      <a href="#" class="view-more-link">查看更多 >></a>
    </header>
    <div class="tools-grid">
      <div
        v-for="tool in filteredTools"
        :key="tool.id"
        class="tool-card"
        @click="handleToolClick(tool)"
      >
        <div class="tool-thumbnail">
          <img :src="tool.thumbnail" :alt="tool.name" loading="lazy" />
        </div>
        <div class="tool-info">
          <h3 class="tool-name">{{ tool.name }}</h3>
          <p class="tool-description">{{ tool.description }}</p>
          <span v-if="tool.price" class="price-tag">{{ tool.price }}</span>
        </div>
        <!-- 可以保留或修改底部样式 -->
        <div class="tool-footer">
          <div class="tool-tags">
            <span v-for="(tag, index) in tool.tags.slice(0, 2)" :key="index" class="tag">
              {{ tag }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import type { Tool } from '@/data/tools';
import { imageTools } from '@/data/imageTools';

const props = defineProps<{
  searchKeyword: string;
}>();

const router = useRouter();

const filteredTools = computed(() => {
  if (!props.searchKeyword.trim()) {
    return imageTools;
  }
  const keyword = props.searchKeyword.toLowerCase();
  return imageTools.filter(tool => 
    tool.name.toLowerCase().includes(keyword) ||
    tool.description.toLowerCase().includes(keyword) ||
    tool.tags.some(tag => tag.toLowerCase().includes(keyword))
  );
});

const handleToolClick = (tool: Tool) => {
  router.push(tool.routePath);
};
</script>

<style scoped>
/* 样式可以从 AiToolsHome.vue 迁移和调整 */
.tool-category-section {
  margin-bottom: 48px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-size: 22px;
  font-weight: 600;
  color: #111827;
}

.view-more-link {
  font-size: 14px;
  color: #6b7280;
  text-decoration: none;
  transition: color 0.2s;
}

.view-more-link:hover {
  color: #8b5cf6;
}

/* 复用 AiToolsHome.vue 中的 .tools-grid 和 .tool-card 样式 */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.tool-card {
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
}

.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
}

.tool-thumbnail {
  width: 100%;
  padding-top: 60%; /* 宽高比 5:3 */
  position: relative;
  background-color: #f3f4f6;
}

.tool-thumbnail img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tool-info {
  padding: 16px;
  flex-grow: 1;
}

.tool-name {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 8px 0;
}

.tool-description {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
  height: 42px; /* 约2行高度 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 12px;
}

.price-tag {
  font-size: 13px;
  font-weight: 500;
  color: #ef4444;
}

.tool-footer {
  padding: 0 16px 16px;
  border-top: 1px solid #f3f4f6;
  margin-top: auto;
}

.tool-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  padding-top: 12px;
}

.tag {
  padding: 4px 10px;
  font-size: 12px;
  color: #4b5563;
  background-color: #f3f4f6;
  border-radius: 6px;
}
</style>