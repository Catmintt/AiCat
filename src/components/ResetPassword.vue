<template>
  <!-- 模态框遮罩层 -->
  <div 
    class="modal-overlay" 
    @mousedown="handleOverlayMouseDown" 
    @mouseup="handleOverlayMouseUp"
  >
    <!-- 模态框内容 -->
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">重置密码</h3>
        <button class="close-button" @click="$emit('close')">&times;</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="handleReset">
          <!-- 邮箱 -->
          <div class="input-group">
            <label for="reset-email">邮箱</label>
            <input 
              id="reset-email" 
              type="tel" 
              v-model="email" 
              placeholder="请输入邮箱"
              :class="{ 'error-input': emailError }"
            >
            <p v-if="emailError" class="error-message">{{ emailError }}</p>
          </div>
          <!-- 验证码 -->
          <div class="input-group">
            <label for="reset-code">验证码</label>
            <div class="input-with-button">
              <input 
                id="reset-code" 
                type="text" 
                v-model="code" 
                placeholder="请输入验证码"
                :class="{ 'error-input': codeError }"
              >
              <button 
                type="button" 
                class="sms-button" 
                @click="handleGetCode"
                :disabled="isSendingCode || countdown > 0"
              >
                {{ getCodeButtonText }}
              </button>
            </div>
            <p v-if="codeError" class="error-message">{{ codeError }}</p>
          </div>
          <!-- 新密码 -->
          <div class="input-group">
            <label for="reset-new-password">新密码</label>
            <div class="password-input-wrapper">
              <input 
                id="reset-new-password" 
                :type="isNewPasswordVisible ? 'text' : 'password'" 
                v-model="newPassword" 
                placeholder="设置8-16位密码(含大小写字母和数字)" 
                :class="{ 'error-input': newPasswordError }"
              >
              <button type="button" @click="isNewPasswordVisible = !isNewPasswordVisible" class="password-toggle-btn">
                <EyeOpenIcon v-if="isNewPasswordVisible" />
                <EyeClosedIcon v-else />
              </button>
            </div>
            <p v-if="newPasswordError" class="error-message">{{ newPasswordError }}</p>
          </div>
          <!-- 确认新密码 -->
          <div class="input-group">
            <label for="reset-confirm-password">确认新密码</label>
             <div class="password-input-wrapper">
              <input 
                id="reset-confirm-password" 
                :type="isConfirmPasswordVisible ? 'text' : 'password'" 
                v-model="confirmPassword" 
                placeholder="再次输入新密码" 
                :class="{ 'error-input': confirmPasswordError }"
              >
              <button type="button" @click="isConfirmPasswordVisible = !isConfirmPasswordVisible" class="password-toggle-btn">
                <EyeOpenIcon v-if="isConfirmPasswordVisible" />
                <EyeClosedIcon v-else />
              </button>
            </div>
            <p v-if="confirmPasswordError" class="error-message">{{ confirmPasswordError }}</p>
          </div>
          <button type="submit" class="submit-button" :disabled="isSubmitting">
            {{ isSubmitting ? '重置中...' : '重置密码' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import EyeOpenIcon from './icons/EyeOpenIcon.vue';
import EyeClosedIcon from './icons/EyeClosedIcon.vue';
import { ElMessage } from 'element-plus';
import request from '@/api/request'; // 引入 axios 实例

// --- Emits ---
const emit = defineEmits(['close']);

const isMouseDownOnOverlay = ref(false);
const handleOverlayMouseDown = (event: MouseEvent) => {
  if (event.target === event.currentTarget) {
    isMouseDownOnOverlay.value = true;
  }
};

const handleOverlayMouseUp = (event: MouseEvent) => {
  if (isMouseDownOnOverlay.value && event.target === event.currentTarget) {
    emit('close');
  }
  isMouseDownOnOverlay.value = false;
};

// --- 表单数据 ---
const email = ref('');
const code = ref('');
const newPassword = ref('');
const confirmPassword = ref('');

// --- UI 状态 ---
const isNewPasswordVisible = ref(false);
const isConfirmPasswordVisible = ref(false);
const isSendingCode = ref(false);
const countdown = ref(0);
const isSubmitting = ref(false);

// --- 错误状态 ---
const emailError = ref('');
const codeError = ref('');
const newPasswordError = ref('');
const confirmPasswordError = ref('');

// --- Watchers ---
watch(email, (val) => val && (emailError.value = ''));
watch(code, (val) => val && (codeError.value = ''));
watch(newPassword, (val) => val && (newPasswordError.value = ''));
watch(confirmPassword, (val) => val && (confirmPasswordError.value = ''));

// --- Computed ---
const getCodeButtonText = computed(() => {
  if (countdown.value > 0) return `重新发送(${countdown.value}s)`;
  if (isSendingCode.value) return '发送中...';
  return '获取验证码';
});

// --- 验证函数 ---
const isValidEmail = (email: string): boolean => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

const isValidPassword = (password: string): boolean => {
  // 8-16位，包含大写字母、小写字母和数字
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,16}$/;
  return passwordRegex.test(password);
};

// --- 方法 ---
const handleGetCode = async () => {
  if (isSendingCode.value || countdown.value > 0) return;

  if (!email.value) {
    emailError.value = '请输入邮箱地址';
    return;
  }
  if (!isValidEmail(email.value)) {
    emailError.value = '请输入有效的邮箱地址';
    return;
  }

  isSendingCode.value = true;
  try {
    // 复用登录的发送验证码接口
    await request.post<void>('/users/send-code', { email: email.value });
    ElMessage.success('验证码已发送，请检查您的邮箱。');

    countdown.value = 30;
    const timer = setInterval(() => {
      countdown.value--;
      if (countdown.value <= 0) clearInterval(timer);
    }, 1000);
  } catch (error) {
    ElMessage.error('发送验证码失败，请稍后再试。');
  } finally {
    isSendingCode.value = false;
  }
};

const handleReset = async () => {
  // 1. 客户端表单验证
  emailError.value = '';
  codeError.value = '';
  newPasswordError.value = '';
  confirmPasswordError.value = '';

  let hasError = false;
  if (!email.value) {
    emailError.value = '请输入邮箱地址'; hasError = true;
  } else if (!isValidEmail(email.value)) {
    emailError.value = '请输入有效的邮箱地址'; hasError = true;
  }
  if (!code.value) {
    codeError.value = '请输入验证码'; hasError = true;
  }
  if (!newPassword.value) {
    newPasswordError.value = '请输入新密码'; hasError = true;
  } else if (!isValidPassword(newPassword.value)) {
    newPasswordError.value = '密码需为8-16位，含大小写字母和数字'; hasError = true;
  }
  if (!confirmPassword.value) {
    confirmPasswordError.value = '请再次输入新密码'; hasError = true;
  } else if (newPassword.value !== confirmPassword.value) {
    confirmPasswordError.value = '两次输入的密码不一致'; hasError = true;
  }

  if (hasError) return;

  // 2. 发送请求到后端
  isSubmitting.value = true;
  try {
    await request.post('/users/reset-password', {
      email: email.value,
      code: code.value,
      new_password: newPassword.value,
    });
    ElMessage.success('密码重置成功！');
    emit('close'); // 关闭模态框
  } catch (error: any) {
    const detail = error.response?.data?.detail || '操作失败，请稍后再试';
    // 根据后端返回的错误，精确地显示在对应输入框
    if (detail.includes('邮箱')) {
      emailError.value = detail;
    } else if (detail.includes('验证码')) {
      codeError.value = detail;
    } else {
      ElMessage.error(detail);
    }
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* ... (大部分样式保持不变) ... */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.3s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-content {
  background-color: white;
  padding: 24px 32px;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 420px;
  animation: slideIn 0.3s ease-out;
}
@keyframes slideIn { from { transform: translateY(30px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #111;
  margin: 0;
}
.close-button {
  background: none;
  border: none;
  font-size: 28px;
  font-weight: 300;
  color: #9CA3AF;
  cursor: pointer;
  line-height: 1;
}
.close-button:hover { color: #111; }

.input-group { margin-bottom: 20px; }
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
  border: none;
  border-radius: 8px;
  background-color: #F4F4F5;
  font-size: 15px;
  transition: box-shadow 0.2s;
  border: 1px solid transparent; /* 添加一个透明边框以防止应用错误类时布局抖动 */
}
.input-group input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
  background-color: #fff;
  border-color: #8B5CF6;
}

.password-input-wrapper, .input-with-button { position: relative; }

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
  color: #9CA3AF;
}

.sms-button {
  position: absolute;
  right: 16px;
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
  color: #A1A1AA;
  cursor: not-allowed;
}

.submit-button {
  width: 100%;
  padding: 12px;
  background-color: #8B5CF6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 8px;
  transition: background-color 0.2s;
}
.submit-button:hover { background-color: #7C3AED; }
.submit-button:disabled {
  background-color: #C4B5FD;
  cursor: not-allowed;
}

.error-input {
  border-color: #F56C6C !important;
  background-color: #fff !important;
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
</style>