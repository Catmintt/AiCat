<template>
  <div class="ai-tools-home">
    <!-- 左侧快速导航栏 -->
    <aside 
      class="sidebar" 
      :class="{ 'collapsed': isNavCollapsed }"
    >
      <!-- Logo区域 -->
      <div class="logo-section">
        <CatLogo class="logo-icon" />
        <span v-show="!isNavCollapsed" class="logo-text">AiCat</span>
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
            placeholder="搜索AI工具..."
            @keyup.enter="handleSearch"
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
      <div class="tools-display" ref="toolsDisplay">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>

        <!-- 工具列表 -->
        <div v-else-if="toolsList.length > 0" class="tools-grid">
          <div
            v-for="tool in toolsList"
            :key="tool.id"
            class="tool-card"
            @click="handleToolClick(tool)"
          >
            <!-- 缩略图区域 -->
            <div class="tool-thumbnail">
              <img :src="tool.thumbnail" :alt="tool.name" />
              <span v-if="tool.popularity" class="popularity-badge">🔥 {{ formatPopularity(tool.popularity) }}</span>
            </div>

            <!-- 信息区域 -->
            <div class="tool-info">
              <h3 class="tool-name">{{ tool.name }}</h3>
              <p class="tool-description">{{ tool.description }}</p>
              <span v-if="tool.modelName" class="model-tag">{{ tool.modelName }}</span>
            </div>

            <!-- 底部操作区 -->
            <div class="tool-footer">
              <div class="tool-tags">
                <span
                  v-for="(tag, index) in tool.tags.slice(0, 3)"
                  :key="index"
                  class="tag"
                >
                  {{ tag }}
                </span>
                <span v-if="tool.tags.length > 3" class="tag">+{{ tool.tags.length - 3 }}</span>
              </div>
              <button class="use-btn" @click.stop="handleToolClick(tool)">开始使用</button>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <svg class="empty-icon" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <p class="empty-text">{{ emptyMessage }}</p>
        </div>

        <!-- 加载更多触发器 -->
        <div v-if="hasMore && !isLoading" ref="loadMoreTrigger" class="load-more-trigger"></div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import CatLogo from './CatLogo.vue';

// 定义类型
interface Category {
  id: string;
  name: string;
  icon: string;
  order: number;
  toolCount?: number;
}

interface Tool {
  id: string;
  name: string;
  description: string;
  category: string;
  thumbnail: string;
  tags: string[];
  modelName?: string;
  routePath: string;
  popularity?: number;
}

// 路由
const router = useRouter();

// 状态管理
const isNavCollapsed = ref(false);
const currentCategory = ref('image-tools');
const toolsList = ref<Tool[]>([]);
const searchKeyword = ref('');
const isLoading = ref(false);
const userInfo = ref<any>(null);
const hasMore = ref(true);
const currentPage = ref(1);
const toolsDisplay = ref<HTMLElement | null>(null);
const loadMoreTrigger = ref<HTMLElement | null>(null);

// 分类数据
const categories = ref<Category[]>([
  { id: 'image-tools', name: 'AI图像工具', icon: '🎨', order: 1 },
  { id: 'audio-tools', name: 'AI音频工具', icon: '🎵', order: 2 },
  { id: 'video-tools', name: 'AI视频工具', icon: '🎬', order: 3 },
  { id: 'text-tools', name: 'AI文本工具', icon: '📝', order: 4 },
  { id: 'code-tools', name: 'AI代码工具', icon: '💻', order: 5 },
]);

// 计算属性
const emptyMessage = computed(() => {
  if (searchKeyword.value) {
    return '未找到相关工具,试试其他关键词';
  }
  return '该分类暂无工具';
});

// 方法
const toggleSidebar = () => {
  isNavCollapsed.value = !isNavCollapsed.value;
  // 保存用户偏好
  localStorage.setItem('sidebarCollapsed', String(isNavCollapsed.value));
};

const handleCategoryChange = (categoryId: string) => {
  currentCategory.value = categoryId;
  currentPage.value = 1;
  searchKeyword.value = '';
  loadTools(categoryId);
};

const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    return;
  }
  currentCategory.value = '';
  currentPage.value = 1;
  loadTools('', searchKeyword.value);
};

const clearSearch = () => {
  searchKeyword.value = '';
  currentCategory.value = 'image-tools';
  currentPage.value = 1;
  loadTools(currentCategory.value);
};

const handleToolClick = (tool: Tool) => {
  const query: any = {};
  if (currentCategory.value) {
    query.category = currentCategory.value;
  }
  if (searchKeyword.value) {
    query.keyword = searchKeyword.value;
  }
  router.push({ path: tool.routePath, query });
};

const handleLogout = () => {
  localStorage.removeItem('access_token');
  userInfo.value = null;
  router.push('/login');
};

const formatPopularity = (num: number): string => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k';
  }
  return String(num);
};

const loadTools = async (category: string = '', keyword: string = '') => {
  isLoading.value = true;
  try {
    // 模拟数据加载
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 模拟工具数据
    const mockTools: Tool[] = [
      {
        id: 'flux-creator',
        name: 'Flux图像创作工具',
        description: '基于Flux模型的AI图像生成工具,支持多种艺术风格',
        category: 'image-tools',
        thumbnail: 'https://via.placeholder.com/400x240/8B5CF6/FFFFFF?text=Flux+Creator',
        tags: ['图像生成', '艺术创作', 'AI绘画'],
        modelName: 'Flux-1',
        routePath: '/tools/flux-creator',
        popularity: 8520,
      },
      {
        id: 'audio-gen',
        name: 'AI音频生成器',
        description: '智能语音合成与音频处理工具',
        category: 'audio-tools',
        thumbnail: 'https://via.placeholder.com/400x240/10B981/FFFFFF?text=Audio+Gen',
        tags: ['语音合成', '音频处理'],
        modelName: 'AudioGen-Pro',
        routePath: '/tools/audio-gen',
        popularity: 5200,
      },
      {
        id: 'video-editor',
        name: 'AI视频编辑助手',
        description: '智能视频剪辑与特效制作工具',
        category: 'video-tools',
        thumbnail: 'https://via.placeholder.com/400x240/F59E0B/FFFFFF?text=Video+Editor',
        tags: ['视频剪辑', '特效制作', 'AI编辑'],
        modelName: 'VideoAI-v2',
        routePath: '/tools/video-editor',
        popularity: 6800,
      },
    ];

    // 根据分类或关键词过滤
    let filtered = mockTools;
    if (category) {
      filtered = mockTools.filter(tool => tool.category === category);
    }
    if (keyword) {
      filtered = mockTools.filter(tool => 
        tool.name.includes(keyword) || tool.description.includes(keyword)
      );
    }

    toolsList.value = filtered;
    hasMore.value = false;
  } catch (error) {
    console.error('加载工具失败:', error);
    toolsList.value = [];
  } finally {
    isLoading.value = false;
  }
};

// 初始化
onMounted(() => {
  // 加载用户信息
  const token = localStorage.getItem('access_token');
  if (token) {
    userInfo.value = { username: '用户', email: 'user@aicat.com' };
  }

  // 加载导航栏折叠状态
  const savedCollapsed = localStorage.getItem('sidebarCollapsed');
  if (savedCollapsed) {
    isNavCollapsed.value = savedCollapsed === 'true';
  }

  // 加载默认分类工具
  loadTools(currentCategory.value);
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

.logo-icon {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.logo-text {
  margin-left: 12px;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
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
  padding: 24px;
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
</style>
