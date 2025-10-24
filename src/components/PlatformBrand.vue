<template>
  <div class="platform-brand">
    <CatLogo class="logo-icon" />
    <img :src="platformNameImage" alt="AiCat 平台" class="platform-name" />
  </div>
</template>

<script setup lang="ts">
import CatLogo from './CatLogo.vue';
import platformNameImage from '@/assets/AiCat.svg';
</script>

<style scoped>
.platform-brand {
  display: flex;
  align-items: center;
  gap: 12px; /* 控制 Logo 和文字的间距 */
  text-decoration: none; /* 如果被链接包裹，去除下划线 */
}

/* 
  默认尺寸，父组件可以通过 CSS 覆盖它们以适应不同场景
  例如：.some-container .logo-icon { width: 40px; height: 40px; }
*/
.logo-icon {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.platform-name {
  height: 38px; /* 保持一个和谐的高度比例 */
  width: auto;
}
</style>