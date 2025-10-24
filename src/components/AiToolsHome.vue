<template>
  <div class="ai-tools-home">
    <!-- 左侧快速导航栏 -->
    <aside 
      class="sidebar" 
      :class="{ 'collapsed': isNavCollapsed }"
    >
      <!-- Logo区域 -->
      <div class="logo-section">
        <PlatformBrand />
      </div>

      <!-- 分类索引区域 -->
      <nav class="category-nav">
        <ul class="category-list">
          <li
            v-for="category in categories"
            :key="category.id"
            class="category-item"
            :class="{ 'active': currentCategory === category.id }"
            @click="handleCategoryChange(category.id)"
            :title="isNavCollapsed ? category.name : ''"
          >
            <span class="category-icon">{{ category.icon }}</span>
            <span v-show="!isNavCollapsed" class="category-name">{{ category.name }}</span>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- 右侧主体内容区 -->
    <main class="main-content">
      <!-- 顶部导航栏 -->
      <header class="top-navbar">
        <!-- 左侧折叠按钮 -->
        <div class="navbar-left">
          <button class="collapse-btn" @click="toggleSidebar" aria-label="折叠导航栏">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>
        </div>

        <!-- 中间平台链接区 -->
        <nav class="navbar-center">
          <a href="/about" class="nav-link">关于我们</a>
          <a href="/help" class="nav-link">帮助中心</a>
          <a href="/pricing" class="nav-link">定价方案</a>
        </nav>

        <!-- 右侧用户操作区 -->
        <div class="navbar-right">
          <div v-if="userInfo" class="user-section">
            <span class="user-name">{{ userInfo.username || userInfo.email }}</span>
            <button class="logout-btn" @click="handleLogout">退出</button>
          </div>
          <button v-else class="login-btn" @click="$router.push('/login')">登录</button>
        </div>
      </header>

      <!-- 搜索栏区域 -->
      <div class="search-section">
        <div class="search-bar">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <input
            v-model="searchKeyword"
            type="text"
            class="search-input"
            placeholder="在所有工具中搜索..."
            @input="handleSearch"
          />
          <button
            v-if="searchKeyword"
            class="clear-btn"
            @click="clearSearch"
            aria-label="清除搜索"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
          <button class="search-btn" @click="handleSearch">搜索</button>
        </div>
      </div>

      <!-- 工具展示区域 -->
      <div class="tools-display" ref="toolsDisplayRef">
        <!-- 动态渲染所有分类组件 -->
        <component 
          v-for="section in toolSections" 
          :is="section.component" 
          :key="section.id"
          :search-keyword="searchKeyword"
        />

        <!-- 如果搜索结果为空，显示提示 -->
        <div v-if="isSearchResultEmpty" class="empty-state">
          <svg class="empty-icon" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          <p class="empty-text">未找到与 "{{ searchKeyword }}" 相关的工具</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, shallowRef, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import PlatformBrand from './PlatformBrand.vue';
import ImageToolsSection from './tool-sections/ImageToolsSection.vue';
import AudioToolsSection from './tool-sections/AudioToolsSection.vue';
import VideoToolsSection from './tool-sections/VideoToolsSection.vue';
import TextToolsSection from './tool-sections/TextToolsSection.vue';
import CodeToolsSection from './tool-sections/CodeToolsSection.vue';

// 路由
const router = useRouter();

// 状态管理
const isNavCollapsed = ref(false);
const searchKeyword = ref('');
const userInfo = ref<any>(null);
const toolsDisplayRef = ref<HTMLElement | null>(null);
const currentCategory = ref('image-tools'); 
const isSearchResultEmpty = ref(false);

// 分类数据
const categories = ref([
  { id: 'image-tools', name: 'AI图像工具', icon: '🎨' },
  { id: 'audio-tools', name: 'AI音频工具', icon: '🎵' },
  { id: 'video-tools', name: 'AI视频工具', icon: '🎬' },
  { id: 'text-tools', name: 'AI文本工具', icon: '📝' },
  { id: 'code-tools', name: 'AI代码工具', icon: '💻' },
]);

const toolSections = shallowRef([
  { id: 'image-tools', component: ImageToolsSection },
  { id: 'audio-tools', component: AudioToolsSection },
  { id: 'video-tools', component: VideoToolsSection },
  { id: 'text-tools', component: TextToolsSection },
  { id: 'code-tools', component: CodeToolsSection },
]);


const toggleSidebar = () => {
  isNavCollapsed.value = !isNavCollapsed.value;
  localStorage.setItem('sidebarCollapsed', String(isNavCollapsed.value));
};

const handleCategoryChange = (categoryId: string) => {
  const targetElement = document.getElementById(categoryId);
  if (targetElement) {
    targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

const handleSearch = async () => {
  // 等待DOM更新，因为子组件的 v-show 会根据 searchKeyword 变化
  await nextTick();
  if (toolsDisplayRef.value) {
    // 找出所有显示的 section
    const visibleSections = Array.from(
      toolsDisplayRef.value.querySelectorAll<HTMLElement>('.tool-category-section')
    ).filter(section => section.style.display !== 'none');
    
    // 如果有搜索词但没有一个 section 是可见的，则显示“空状态”
    isSearchResultEmpty.value = searchKeyword.value.trim() !== '' && visibleSections.length === 0;
  }
};

const clearSearch = () => {
  searchKeyword.value = '';
  isSearchResultEmpty.value = false;
  toolsDisplayRef.value?.scrollTo({ top: 0, behavior: 'smooth' });
};

const handleLogout = () => {
  localStorage.removeItem('access_token');
  userInfo.value = null;
  router.push('/login');
};

let observer: IntersectionObserver | null = null;
onMounted(() => {
  const token = localStorage.getItem('access_token');
  if (token) { userInfo.value = { username: '用户', email: 'user@aicat.com' }; }
  isNavCollapsed.value = localStorage.getItem('sidebarCollapsed') === 'true';

  const options = {
    root: toolsDisplayRef.value,
    rootMargin: '0px 0px -60% 0px', // 当 section 滚动到视口顶部 40% 区域时触发
    threshold: 0,
  };
  
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        currentCategory.value = entry.target.id;
      }
    });
  }, options);

  // 确保在 DOM 渲染完成后再开始观察
  nextTick(() => {
    const sections = document.querySelectorAll('.tool-category-section');
    sections.forEach(section => {
      if(observer) {
        observer.observe(section)
      }
    });
  });
});

onUnmounted(() => {
  if (observer) observer.disconnect();
});
</script>

<style scoped>
.ai-tools-home {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background-color: #f9fafb;
}

/* 左侧导航栏 */
.sidebar {
  width: 240px;
  background-color: #ffffff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  flex-shrink: 0;
}

.sidebar.collapsed {
  width: 60px;
}

/* Logo区域 */
.logo-section {
  display: flex;
  align-items: center;
  padding: 20px 16px;
  border-bottom: 1px solid #e5e7eb;
  background-color: #fafafa;
}

/* 分类导航 */
.category-nav {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}

.category-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.category-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.category-item:hover {
  background-color: #f3f4f6;
}

.category-item.active {
  background-color: #e9e6ff;
  font-weight: 600;
}

.category-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: #8b5cf6;
}

.category-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.category-name {
  margin-left: 12px;
  color: #374151;
  white-space: nowrap;
}

.sidebar.collapsed .category-name {
  display: none;
}

/* 主体内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航栏 */
.top-navbar {
  height: 60px;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.navbar-left {
  width: 80px;
}

.collapse-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #6b7280;
  transition: all 0.2s;
}

.collapse-btn:hover {
  background-color: #f3f4f6;
  color: #111827;
}

.navbar-center {
  display: flex;
  gap: 24px;
}

.nav-link {
  font-size: 14px;
  color: #666666;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.2s;
}

.nav-link:hover {
  color: #333333;
  background-color: #f5f5f5;
}

.navbar-right {
  width: 200px;
  display: flex;
  justify-content: flex-end;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  font-size: 14px;
  color: #374151;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-btn {
  padding: 8px 16px;
  font-size: 14px;
  color: #dc2626;
  background: transparent;
  border: 1px solid #dc2626;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background-color: #dc2626;
  color: #ffffff;
}

.login-btn {
  padding: 10px 24px;
  font-size: 14px;
  color: #ffffff;
  background-color: #8b5cf6;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.login-btn:hover {
  background-color: #7c3aed;
}

/* 搜索栏 */
.search-section {
  padding: 20px 24px 30px;
  display: flex;
  justify-content: center;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

.search-bar {
  position: relative;
  max-width: 800px;
  width: 100%;
  height: 50px;
  display: flex;
  align-items: center;
  background-color: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  padding: 0 16px;
  transition: border-color 0.2s;
}

.search-bar:focus-within {
  border-color: #8b5cf6;
  background-color: #ffffff;
}

.search-icon {
  color: #9ca3af;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
  padding: 0 12px;
  color: #111827;
}

.search-input::placeholder {
  color: #9ca3af;
}

.clear-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  border-radius: 4px;
  transition: all 0.2s;
}

.clear-btn:hover {
  background-color: #e5e7eb;
  color: #374151;
}

.search-btn {
  margin-left: 8px;
  padding: 8px 20px;
  font-size: 14px;
  color: #ffffff;
  background-color: #8b5cf6;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-btn:hover {
  background-color: #7c3aed;
}

/* 工具展示区 */
.tools-display {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  scroll-behavior: smooth;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #6b7280;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #8b5cf6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 工具网格 */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

/* 工具卡片 */
.tool-card {
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.tool-thumbnail {
  position: relative;
  width: 100%;
  height: 180px;
  overflow: hidden;
  background-color: #f3f4f6;
}

.tool-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.popularity-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tool-info {
  padding: 16px;
}

.tool-name {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tool-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 12px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.model-tag {
  display: inline-block;
  padding: 4px 12px;
  font-size: 12px;
  color: #7c3aed;
  background-color: #ede9fe;
  border-radius: 6px;
}

.tool-footer {
  padding: 12px 16px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tool-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  flex: 1;
}

.tag {
  padding: 4px 10px;
  font-size: 12px;
  color: #4b5563;
  background-color: #f3f4f6;
  border-radius: 6px;
}

.use-btn {
  padding: 8px 16px;
  font-size: 14px;
  color: #8b5cf6;
  background: transparent;
  border: 1px solid #8b5cf6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.use-btn:hover {
  background-color: #8b5cf6;
  color: #ffffff;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.empty-icon {
  color: #d1d5db;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  color: #9ca3af;
}

/* 加载更多触发器 */
.load-more-trigger {
  height: 20px;
}

/* 响应式设计 */
@media (max-width: 1600px) {
  .tools-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 1200px) {
  .tools-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 1024px) {
  .navbar-center {
    display: none;
  }
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -240px;
    top: 0;
    bottom: 0;
    z-index: 1000;
    width: 240px;
  }

  .sidebar.collapsed {
    left: 0;
    width: 240px;
  }

  .tools-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .search-section {
    padding: 16px;
  }

  .tools-display {
    padding: 16px;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}
.empty-icon {
  color: #d1d5db;
  margin-bottom: 16px;
}
.empty-text {
  font-size: 16px;
  color: #9ca3af;
}
</style>
