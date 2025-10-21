<template>
  <div class="login-page-wrapper">
    <!-- 左侧产品介绍面板 -->
    <div class="left-panel">
      <header class="logo-header">
        <CatLogo />
        <span class="platform-name">AiCat</span>
      </header>

      <main class="hero-content">
        <h1>灵活、易用的 Ai工具平台</h1>
        <img :src="heroImage" alt="AiCat Hero Image" class="hero-image" />
      </main>
    </div>

    <!-- 右侧登录表单面板 -->
    <div class="right-panel">
      <div class="login-form-wrapper">
        <h2 class="welcome-title">欢迎登录 <strong>AiCat</strong></h2>

        <div class="tabs-container">
          <button
            :class="{ active: activeTab === 'sms' }"
            @click="switchTab('sms')"
          >
            验证码登录
          </button>
          <button
            :class="{ active: activeTab === 'password' }"
            @click="switchTab('password')"
          >
            密码登录
          </button>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <!-- 验证码登录 -->
          <div v-if="activeTab === 'sms'">
            <div class="input-group">
              <label for="email">邮箱</label>
              <input 
                id="email" 
                type="tel" 
                v-model="emailForSms" 
                placeholder="请输入邮箱"
                :class="{ 'error-input': emailError }"
              >
              <p v-if="emailError" class="error-message">{{ emailError }}</p>
            </div>
            <div class="input-group">
              <label for="sms-code">验证码</label>
               <div class="input-with-button">
                <input 
                  id="sms-code" 
                  type="text" 
                  v-model="smsCode" 
                  placeholder="请输入验证码"
                  :class="{ 'error-input': smsCodeError }"
                >
                <button 
                  type="button" 
                  class="sms-button" 
                  :disabled="isSendingCode || countdown > 0" 
                  @click="handleGetCode"
                >
                  {{ getCodeButtonText }}
                </button>
             </div>
             <p v-if="smsCodeError" class="error-message">{{ smsCodeError }}</p>
            </div>
          </div>

          <!-- 密码登录 -->
          <div v-if="activeTab === 'password'" class="password-section">
            <div class="input-group">
              <label for="username">邮箱</label>
              <input 
                id="username" 
                type="text" 
                v-model="username" 
                placeholder="请输入邮箱"
                :class="{ 'error-input': usernameError }"
              >
              <p v-if="usernameError" class="error-message">{{ usernameError }}</p>
            </div>
            <div class="input-group">
                <label for="password">密码</label>
                <!-- 新增一个包装器用于定位图标 -->
                <div class="password-input-wrapper">
                    <input 
                      id="password" 
                      :type="isPasswordVisible ? 'text' : 'password'" 
                      v-model="password" 
                      placeholder="请输入密码"
                      :class="{ 'error-input': passwordError }"
                    >
                    <!-- 切换可见性的按钮 -->
                    <button type="button" @click="togglePasswordVisibility" class="password-toggle-btn">
                    <!-- 根据状态显示不同的SVG图标 -->
                      <EyeOpenIcon v-if="isPasswordVisible" />
                      <EyeClosedIcon v-else />
                    </button>
                </div>
                <p v-if="passwordError" class="error-message">{{ passwordError }}</p>
            </div>
             <button type="button" @click="showResetModal = true" class="forgot-password">忘记密码</button>
          </div>
          
          <div class="agreement">
            <!-- 使用 v-bind:id 或 :id 来动态绑定 id -->
            <input 
              type="checkbox" 
              :id="activeTab + '-agree'" 
              v-model="agreedToTerms"
            >
            <!-- label 的 for 属性也要相应地动态绑定 -->
            <label :for="activeTab + '-agree'">
                <span v-if="activeTab === 'sms'">
                同意<a href="#" target="_blank">服务协议</a>和<a href="#" target="_blank">隐私协议</a>，未注册的邮箱将自动创建账号
                </span>
                <span v-else>
                同意<a href="#" target="_blank">服务协议</a>和<a href="#" target="_blank">隐私协议</a>
                </span>
            </label>
          </div>

          <button 
            type="submit" 
            class="login-button" 
            :disabled="!agreedToTerms"
          >
            <span v-if="isLoading">登录中...</span>
            <span v-else>{{ activeTab === 'sms' ? '登录 / 注册' : '登录' }}</span>
          </button>
        </form>
      </div>
    </div>
    <ResetPassword v-if="showResetModal" @close="showResetModal = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import request from '@/api/request'; 
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus'; 
import CatLogo from './CatLogo.vue';
import heroImage from '@/assets/Cat.jpg';
import ResetPassword from './ResetPassword.vue';
import EyeOpenIcon from './icons/EyeOpenIcon.vue';
import EyeClosedIcon from './icons/EyeClosedIcon.vue';

// --- 类型定义 ---
type Tab = 'sms' | 'password';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

// --- 响应式状态管理 ---
const activeTab = ref<Tab>('sms');
const router = useRouter();

// --- 表单数据 ---
const emailForSms = ref('');
const smsCode = ref('');
const username = ref(''); // 用于密码登录的邮箱
const password = ref('');
const agreedToTerms = ref(false);

// 表单验证错误
const emailError = ref('');
const smsCodeError = ref('');
const usernameError = ref('');
const passwordError = ref('');

// --- UI 状态 ---
const isPasswordVisible = ref(false);
const showResetModal = ref(false);
const isSendingCode = ref(false); // 专门用于"获取验证码"按钮的加载状态
const countdown = ref(0);
const isLoading = ref(false); // 用于"登录"主按钮的全局加载状态

watch(emailForSms, (newValue) => {
  if (newValue && emailError.value) {
    emailError.value = ''; // 如果用户开始输入，清除邮箱错误
  }
});

watch(smsCode, (newValue) => {
  if (newValue && smsCodeError.value) {
    smsCodeError.value = ''; // 如果用户开始输入，清除验证码错误
  }
});

watch(username, (newValue) => {
  if (newValue && usernameError.value) usernameError.value = '';
});

watch(password, (newValue) => {
  if (newValue && passwordError.value) passwordError.value = '';
});

// 用于动态显示按钮文本 ---
const getCodeButtonText = computed(() => {
  if (countdown.value > 0) {
    return `重新发送(${countdown.value}s)`;
  }
  if (isSendingCode.value) {
    return '发送中...';
  }
  return '获取验证码';
});

// --- Methods ---
const switchTab = (tab: Tab) => {
  activeTab.value = tab;
  emailError.value = '';
  smsCodeError.value = '';
  usernameError.value = '';
  passwordError.value = '';
};

const togglePasswordVisibility = () => {
  isPasswordVisible.value = !isPasswordVisible.value;
};

// 检查邮箱是否合理
const isValidEmail = (email: string): boolean => {
  // 这是一个常用且足够好的正则表达式，用于检查基本的邮箱格式
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// 获取验证码
const handleGetCode = async () => {
  if (isSendingCode.value || countdown.value > 0) return;
  if (!emailForSms.value) {
    ElMessage.warning('请输入邮箱地址！');
    emailError.value = '请输入邮箱地址';
    return;
  }

  if (!isValidEmail(emailForSms.value)) {
    ElMessage.warning('请输入有效的邮箱地址！');
    emailError.value = '请输入有效的邮箱地址';
    return;
  }

  isSendingCode.value = true;
  try {
    // 后端接口 `/users/send-code` 没有返回有意义的数据，所以我们期望 void
    await request.post<void>('/users/send-code', { email: emailForSms.value });
    ElMessage.success('验证码已发送，请检查您的邮箱。');

    // 开始倒计时
    countdown.value = 30;
    const timer = setInterval(() => {
      countdown.value--;
      if (countdown.value <= 0) {
        clearInterval(timer);
        // 注意：倒计时结束后，isSendingCode 应该为 false
        // 但我们在 finally 块中处理，这里就不需要了
      }
    }, 1000);
  } catch (error) {
    console.error('发送验证码失败:', error);
    ElMessage.error('发送验证码失败，请稍后再试。');
  } finally {
    isSendingCode.value = false; // 无论成功失败，最终都结束发送状态
  }
};

/**
 * 处理登录成功后的通用逻辑
 * @param response 后端返回的响应数据
 */
const handleSuccessfulLogin = (response: LoginResponse) => {
  // 1. 将 token 保存到 localStorage
  localStorage.setItem('access_token', response.access_token);
  
  // 2. (可选) 保存用户信息到 Pinia store 或 localStorage
  
  // 3. 提示成功并跳转到主页或仪表盘
  ElMessage.success('登录成功！');
  router.push('/'); // 跳转到首页
};

// 密码登录处理函数
const handlePasswordLogin = async () => {
  usernameError.value = '';
  passwordError.value = '';

  if (!username.value || !password.value) {
    ElMessage.warning('请输入邮箱和密码！');
  }
  let hasError = false;
  if (!username.value) {
    usernameError.value = '请输入邮箱地址';
    hasError = true;
  } else if (!isValidEmail(username.value)) { // 可以增加邮箱格式校验
    usernameError.value = '请输入有效的邮箱地址';
    hasError = true;
  }

  if (!password.value) {
    passwordError.value = '请输入密码';
    hasError = true;
  }

  if (hasError) {
    return;
  }

  const formData = new FormData();
  formData.append('username', username.value);
  formData.append('password', password.value);
  
  const responseData = await request.post('/users/login', formData) as LoginResponse;
  handleSuccessfulLogin(responseData);
};


// 处理验证码登录
const handleCodeLogin = async () => {
  emailError.value = '';
  smsCodeError.value = '';

  let hasError = false;
  if (!emailForSms.value) {
    emailError.value = '请输入邮箱地址';
    hasError = true;
  }
  if (!smsCode.value) {
    smsCodeError.value = '请输入6位数字验证码';
    hasError = true;
  }

  if (!emailForSms.value || !smsCode.value) {
    ElMessage.warning('请输入邮箱和验证码！');
    return;
  }

  if (hasError) {
    return; // 如果有错误，则中断登录流程
  }
  
  // FIX: 同样使用泛型
  const responseData = await request.post('/users/login-code', {
    email: emailForSms.value,
    code: smsCode.value,
  }) as LoginResponse;
  handleSuccessfulLogin(responseData);
};

// 主登录函数
const handleLogin = async () => {
  if (!agreedToTerms.value) {
    ElMessage.warning('请先同意服务协议和隐私协议。');
    return;
  }
  
  isLoading.value = true;
  try {
    if (activeTab.value === 'password') {
      await handlePasswordLogin();
    } else {
      await handleCodeLogin();
    }
  } catch (error: any) {
    // 尝试从后端响应中获取详细错误信息
    const detail = error.response?.data?.detail || '登录失败，请检查您的输入是否有误或网络连接。';
    if (activeTab.value === 'password' && error.response?.status === 401) {
        passwordError.value = detail; // 将 "邮箱或密码错误" 显示在密码框下方
    } 
    // 如果是验证码登录，并且状态码是 400 (Bad Request)
    else if (activeTab.value === 'sms' && error.response?.status === 400) {
        smsCodeError.value = detail; // 将 "验证码错误或已过期" 显示在验证码输入框下方
    } else {
        ElMessage.error(detail);
    }
    console.error('登录失败:', error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* --- 全局布局 --- */
.login-page-wrapper {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
}

/* --- 左侧介绍面板 (全新样式) --- */
.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column; /* 垂直布局 */
  align-items: center; /* 水平居中 */
  justify-content: flex-start; /* 从顶部开始排列 */
  background: linear-gradient(160deg, #e9e6ff 0%, #dbeafe 100%); /* 淡雅的渐变背景 */
}

.logo-header {
  display: flex;
  align-items: center;
  width: 100%; /* 确保Logo在容器内左对齐 */
  margin-bottom: auto; /* 关键：将主要内容推向中心 */
}

.platform-name {
  font-size: 1.75rem;
  font-weight: 600;
  margin-left: 12px;
  color: #4338ca; /* 深紫色文字以保证可读性 */
}

.hero-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  width: 100%;
  margin-bottom: auto; /* 关键：将主要内容推向中心 */
}

.hero-content h1 {
  font-size: 3rem;
  font-weight: bold;
  color: #17171D; /* 更深的紫色 */
  line-height: 1.4;
  margin-bottom: 40px; /* 标题和图片之间的间距 */
}

.hero-image {
  max-width: 90%; /* 图片最大宽度为父容器的90% */
  height: auto; /* 高度自动，保持图片比例 */
  max-height: 50vh; /* 限制最大高度，防止图片过高 */
  object-fit: contain; /* 确保图片完整显示 */
  border-radius: 16px;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.1);
}


/* --- 右侧登录表单 (样式保持不变) --- */
.right-panel {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fff;
}

.login-form-wrapper {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.welcome-title {
  font-size: 28px;
  font-weight: 600;
  color: #111;
  margin-bottom: 8px;
}
.welcome-title strong { font-weight: 600; }

.highlight-orange { color: #F97316; font-weight: 500; }

.tabs-container {
  display: inline-flex;
  background-color: #F4F4F5;
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 24px;
}

.tabs-container button {
  border: none;
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  background-color: transparent;
  color: #555;
}

.tabs-container button.active {
  background-color: white;
  color: #111;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.input-group { margin-bottom: 24px; }
.input-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}
.input-group input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  background-color: #FFF;
  font-size: 15px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-group input:focus {
  outline: none;
  border-color: #8B5CF6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
}

.error-input {
  border-color: #F56C6C !important; /* 使用 !important 确保覆盖 :focus 样式 */
}

.error-input:focus {
  border-color: #F56C6C !important;
  box-shadow: 0 0 0 3px rgba(245, 108, 108, 0.2) !important;
}

.error-message {
  color: #F56C6C;
  font-size: 12px;
  margin-top: 6px; /* 与输入框的间距 */
  height: 14px; /* 给一个固定高度防止布局抖动 */
}

.error-input {
  border-color: #F56C6C !important;
}
.error-input:focus {
  border-color: #F56C6C !important;
  box-shadow: 0 0 0 3px rgba(245, 108, 108, 0.2) !important;
}
.error-message {
  color: #F56C6C;
  font-size: 12px;
  margin-top: 6px;
  height: 14px; 
}

.password-section {
  display: flex;
  flex-direction: column; /* 让内部元素垂直排列 */
}

.password-input-wrapper {
  position: relative;
}

.password-toggle-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9CA3AF; /* 图标的默认颜色 */
}
.password-toggle-btn:hover {
  color: #333; /* 鼠标悬停时图标颜色 */
}

.input-with-button { position: relative; }
.sms-button {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #8B5CF6;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}
.sms-button:disabled {
  color: #A1A1AA; /* 变暗的颜色 */
  cursor: not-allowed;
}

.forgot-password {
  background: none;
  border: none;
  padding: 0;
  font-family: inherit;

  align-self: flex-end;

  font-size: 14px;
  color: #9CA3AF;
  margin-top: -16px;
  margin-bottom: 24px;
  transition: color 0.2s;
  cursor: pointer;
}
.forgot-password:hover {
  color: #333;
}

.agreement {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  font-size: 12px;
  color: #666;
}
.agreement a {
  color: #8B5CF6; /* 蓝紫色 */
  text-decoration: none;
  margin: 0 4px; /* 增加一点左右间距 */
}

.agreement a:hover {
  text-decoration: underline;
}

.agreement input[type="checkbox"] {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  accent-color: #8B5CF6;
}

.login-button {
  width: 100%;
  padding: 12px;
  background-color: #8B5CF6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s, opacity 0.2s;
}
.login-button:hover { background-color: #7C3AED; }
.login-button:disabled {
  background-color: #C4B5FD;
  cursor: not-allowed;
  opacity: 0.8;
}

/* --- 响应式设计 --- */
@media (max-width: 900px) {
  .left-panel { display: none; }
  .right-panel { flex-basis: 100%; }
}
</style>