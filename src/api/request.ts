import axios from 'axios';
import type { AxiosResponse } from 'axios';

// 创建一个 Axios 实例
const service = axios.create({
    // baseURL 是 API 的基础路径,只需要写后面的路径
    // 重要：这里的地址要和后端运行的地址一致
    baseURL: 'http://127.0.0.1:8000/api/', 
    timeout: 10000, // 请求超时时间（毫秒）
});

// --- 请求拦截器 ---
// 在每次请求发送前，执行一些操作
service.interceptors.request.use(
    config => {
        // 例如，从 localStorage 获取 token
        const token = localStorage.getItem('access_token');
        if (token) {
            // 如果 token 存在，则添加到请求头中
            // 'Authorization' 是后端验证 token 的标准请求头字段
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        // 处理请求错误
        console.error('请求错误:', error);
        return Promise.reject(error);
    }
);

// --- 响应拦截器 ---
// 通过为 response 参数添加类型注解，可以获得更好的智能提示
service.interceptors.response.use(
    (response: AxiosResponse) => {
        // 后端成功响应 (状态码 2xx)
        // 我们只关心 data 部分
        return response.data;
    },
    error => {
        // 处理 HTTP 错误 (状态码非 2xx)
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    console.error('认证失败，请重新登录');
                    // 在实际项目中，这里可能会清除 token 并跳转到登录页
                    // localStorage.removeItem('access_token');
                    // window.location.href = '/login'; 
                    break;
                case 404:
                    console.error('请求的资源未找到');
                    break;
                // 你可以根据后端返回的错误结构，在这里统一处理错误提示
                // 例如: const message = error.response.data.detail || '请求失败';
                // ElMessage.error(message);
                default:
                    console.error(`请求错误，状态码：${error.response.status}`);
            }
        } else if (error.request) {
            // 请求已发出，但没有收到响应
            console.error('网络错误或服务器无响应');
        } else {
            // 设置请求时触发了错误
            console.error('请求设置错误:', error.message);
        }
        // 返回一个被拒绝的 Promise，并将错误对象传递下去，以便在业务代码的 .catch 中处理
        return Promise.reject(error);
    }
);

// 导出这个配置好的 Axios 实例
export default service;