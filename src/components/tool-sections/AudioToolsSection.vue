<template>
  <section class="tool-category-section" id="audio-tools" v-show="filteredTools.length > 0">
    <header class="section-header">
      <h2 class="section-title">🎵 AI音频工具</h2>
      <a href="#" class="view-more-link">查看更多 >></a>
    </header>
    <div class="tools-grid">
      <div v-for="tool in filteredTools" :key="tool.id" class="tool-card" @click="handleToolClick(tool)">
        <div class="tool-thumbnail"><img :src="tool.thumbnail" :alt="tool.name" loading="lazy" /></div>
        <div class="tool-info">
          <h3 class="tool-name">{{ tool.name }}</h3>
          <p class="tool-description">{{ tool.description }}</p>
          <span v-if="tool.price" class="price-tag">{{ tool.price }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import type { Tool } from '@/data/tools';
import { audioTools } from '@/data/audioTools';

const props = defineProps<{ searchKeyword: string }>();
const router = useRouter();

const filteredTools = computed(() => {
  if (!props.searchKeyword.trim()) return audioTools;
  const keyword = props.searchKeyword.toLowerCase();
  return audioTools.filter(tool => 
    tool.name.toLowerCase().includes(keyword) ||
    tool.description.toLowerCase().includes(keyword) ||
    tool.tags.some(tag => tag.toLowerCase().includes(keyword))
  );
});

const handleToolClick = (tool: Tool) => router.push(tool.routePath);
</script>

<style scoped>
/* Common styles can be moved to a global CSS file */
.tool-category-section{margin-bottom:48px}.section-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}.section-title{font-size:22px;font-weight:600;color:#111827}.view-more-link{font-size:14px;color:#6b7280;text-decoration:none;transition:color .2s}.view-more-link:hover{color:#8b5cf6}.tools-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:24px}.tool-card{background-color:#fff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;cursor:pointer;transition:all .3s;display:flex;flex-direction:column}.tool-card:hover{transform:translateY(-4px);box-shadow:0 10px 25px rgba(0,0,0,.08)}.tool-thumbnail{width:100%;padding-top:60%;position:relative;background-color:#f3f4f6}.tool-thumbnail img{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover}.tool-info{padding:16px;flex-grow:1}.tool-name{font-size:16px;font-weight:600;color:#111827;margin:0 0 8px}.tool-description{font-size:14px;color:#6b7280;line-height:1.5;height:42px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:12px}.price-tag{font-size:13px;font-weight:500;color:#ef4444}
</style>