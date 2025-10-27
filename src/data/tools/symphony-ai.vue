<!-- src/apps/SynthesizerPage.vue -->
<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white font-sans p-4 sm:p-6 lg:p-8">
    <div class="max-w-5xl mx-auto">
      
      <!-- 标题区域 -->
      <header class="text-center mb-12">
        <h1 class="text-4xl sm:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">
          AI 让你的声音栩栩如"声"
        </h1>
        <p class="mt-3 text-lg text-gray-300 max-w-2xl mx-auto">
          上传视频自动提取文本，或直接输入文本开始创作
        </p>
      </header>

      <!-- 工作流程指示器 -->
      <div class="flex justify-between items-center mb-8 px-4">
        <div class="flex flex-col items-center">
          <div class="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">1</div>
          <span class="mt-2 text-sm text-gray-300">上传视频</span>
        </div>
        <div class="flex-1 h-1 bg-gray-700 mx-2">
          <div class="h-full bg-blue-500" :style="{width: transcribedText ? '100%' : '0%', transition: 'width 0.5s'}"></div>
        </div>
        <div class="flex flex-col items-center">
          <div class="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center text-white font-bold" :class="{'bg-purple-500': translatedText}">2</div>
          <span class="mt-2 text-sm text-gray-300">翻译合成</span>
        </div>
        <div class="flex-1 h-1 bg-gray-700 mx-2">
          <div class="h-full bg-purple-500" :style="{width: audioUrl ? '100%' : '0%', transition: 'width 0.5s'}"></div>
        </div>
        <div class="flex flex-col items-center">
          <div class="w-10 h-10 rounded-full bg-gray-700 flex items-center justify-center text-white font-bold" :class="{'bg-pink-500': serverVideoPath}">3</div>
          <span class="mt-2 text-sm text-gray-300">生成视频</span>
        </div>
      </div>

      <!-- 主工作区 -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <!-- 左侧：上传和输入区域 -->
        <div class="lg:col-span-7 space-y-6">
          <!-- 步骤 1: 上传视频 -->
          <div class="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 shadow-lg transition-all hover:shadow-blue-900/20">
            <h2 class="text-xl font-semibold flex items-center text-blue-400">
              <span class="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center mr-2 text-blue-400">1</span>
              上传或拍摄视频
            </h2>
            
            <!-- 选项卡切换 -->
            <div class="flex border-b border-gray-700 mt-4">
              <button 
                @click="activeTab = 'upload'" 
                class="py-2 px-4 font-medium text-sm transition-all border-b-2 mr-4"
                :class="activeTab === 'upload' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-gray-300'"
              >
                上传视频
              </button>
              <button 
                @click="activeTab = 'record'" 
                class="py-2 px-4 font-medium text-sm transition-all border-b-2"
                :class="activeTab === 'record' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-gray-300'"
              >
                拍摄视频
              </button>
            </div>
            
            <!-- 上传视频选项 -->
            <div v-if="activeTab === 'upload'" class="mt-4">
              <label for="video-upload" class="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-600 p-8 text-center transition hover:border-blue-500/50 hover:bg-gray-700/30">
                <div class="flex flex-col items-center justify-center">
                  <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                  <span class="mt-2 block text-sm font-medium text-gray-300">{{ videoFile ? videoFile.name : '点击选择视频文件' }}</span>
                  <span class="mt-1 text-xs text-gray-500">支持 MP4, MOV, AVI 等常见格式</span>
                </div>
              </label>
              <input id="video-upload" type="file" @change="handleFileUpload" class="sr-only" accept="video/*" />
            </div>
            
            <!-- 拍摄视频选项 -->
            <div v-else class="mt-4">
              <div class="rounded-lg overflow-hidden bg-gray-900 border border-gray-700">
                <!-- 视频预览区域 -->
                <video 
                  ref="videoPreview" 
                  class="w-full h-64 object-cover" 
                  :class="{'hidden': !isRecording && recordedVideo}"
                ></video>
                
                <!-- 录制的视频回放 -->
                <video 
                  v-if="recordedVideo && !isRecording" 
                  ref="recordedVideoPreview" 
                  class="w-full h-64 object-cover" 
                  controls
                  :src="recordedVideo"
                ></video>
                
                <!-- 录制控制按钮 -->
                <div class="p-4 flex justify-center space-x-4">
                  <button 
                    v-if="!isRecording && !recordedVideo"
                    @click="startRecording" 
                    class="flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                      <circle cx="10" cy="10" r="8" />
                    </svg>
                    开始录制
                  </button>
                  
                  <button 
                    v-if="isRecording"
                    @click="stopRecording" 
                    class="flex items-center px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-all"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                      <rect x="6" y="6" width="8" height="8" />
                    </svg>
                    停止录制
                  </button>
                  
                  <button 
                    v-if="recordedVideo && !isRecording"
                    @click="retakeVideo" 
                    class="flex items-center px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-all"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    重新录制
                  </button>
                  
                  <button 
                    v-if="recordedVideo && !isRecording"
                    @click="useRecordedVideo" 
                    class="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    使用此视频
                  </button>
                </div>
                
                <!-- 录制状态指示器 -->
                <div v-if="isRecording" class="px-4 pb-4 flex items-center">
                  <div class="w-3 h-3 rounded-full bg-red-500 animate-pulse mr-2"></div>
                  <span class="text-red-400 text-sm">正在录制... {{ formatRecordingTime(recordingTime) }}</span>
                </div>
              </div>
              
              <p class="mt-2 text-xs text-gray-500 text-center">
                请确保您的浏览器有权限访问摄像头。
              </p>
            </div>
            
            <!-- 处理按钮 -->
            <button 
              @click="uploadAndTranscribe" 
              :disabled="(!videoFile && !recordedVideoBlob) || isLoading.transcribe" 
              class="mt-4 w-full py-3 px-4 rounded-lg font-medium transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-blue-500
                     bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div class="flex items-center justify-center">
                <Spinner v-if="isLoading.transcribe" class="mr-2" />
                <span>识别语音并填充至第二步</span>
              </div>
            </button>
          </div>

          <!-- 步骤 2: 翻译与语音合成 -->
          <div class="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 shadow-lg transition-all hover:shadow-purple-900/20">
            <h2 class="text-xl font-semibold flex items-center text-purple-400">
              <span class="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center mr-2 text-purple-400">2</span>
              翻译与语音合成
            </h2>
            
            <!-- 源文本输入 -->
            <div class="mt-4">
              <label for="transcribed-text" class="block text-sm font-medium text-gray-300 mb-1">源文本</label>
              <textarea 
                id="transcribed-text" 
                v-model="transcribedText" 
                rows="4" 
                placeholder="在此输入或粘贴文本，或从上一步自动填充"
                class="w-full rounded-lg bg-gray-700/50 border border-gray-600 text-white placeholder-gray-500 p-3 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              ></textarea>
            </div>
            
            <!-- 翻译选项 -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div class="md:col-span-2">
                <label for="language" class="block text-sm font-medium text-gray-300 mb-1">目标语言</label>
                <select 
                  id="language" 
                  v-model="selectedLanguage" 
                  class="w-full rounded-lg bg-gray-700/50 border border-gray-600 text-white p-3 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                >
                  <option disabled value="">请选择语言</option>
                  <option v-for="lang in config.languages" :key="lang" :value="lang">{{ lang }}</option>
                </select>
              </div>
              <div class="flex items-end">
                <button 
                  @click="handleTranslation" 
                  :disabled="!transcribedText || isLoading.translate" 
                  class="w-full py-3 px-4 rounded-lg font-medium transition-all focus:outline-none
                         bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div class="flex items-center justify-center">
                    <Spinner v-if="isLoading.translate" class="mr-2" />
                    <span>翻 译</span>
                  </div>
                </button>
              </div>
            </div>
            
            <!-- 翻译结果 -->
            <div class="mt-4">
              <label for="translated-text" class="block text-sm font-medium text-gray-300 mb-1">翻译结果 (可编辑)</label>
              <textarea 
                id="translated-text" 
                v-model="translatedText" 
                rows="4" 
                placeholder="点击翻译后结果将显示在此，您也可以手动修改"
                class="w-full rounded-lg bg-gray-700/50 border border-gray-600 text-white placeholder-gray-500 p-3 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              ></textarea>
            </div>
            
            <!-- 语音合成选项 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div>
                <label for="voice" class="block text-sm font-medium text-gray-300 mb-1">音色选择</label>
                <select 
                  id="voice" 
                  v-model="selectedVoice" 
                  class="w-full rounded-lg bg-gray-700/50 border border-gray-600 text-white p-3 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                >
                  <option disabled value="">请选择音色</option>
                  <option v-for="(value, key) in config.voices" :key="value" :value="key">{{ key }}</option>
                </select>
              </div>
              <div>
                <label for="speech-speed" class="block text-sm font-medium text-gray-300 mb-1">语速: {{ speechSpeed }}</label>
                <input 
                  id="speech-speed" 
                  type="range" 
                  min="0.5" 
                  max="2.0" 
                  step="0.1" 
                  v-model="speechSpeed" 
                  class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
                >
                <div class="flex justify-between text-xs text-gray-500 mt-1">
                  <span>慢</span>
                  <span>正常</span>
                  <span>快</span>
                </div>
              </div>
            </div>
            
            <!-- 生成按钮 -->
            <button 
              @click="handleSynthesis" 
              :disabled="!translatedText || isLoading.synthesize" 
              class="mt-6 w-full py-3 px-4 rounded-lg font-medium transition-all focus:outline-none
                     bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div class="flex items-center justify-center">
                <Spinner v-if="isLoading.synthesize" class="mr-2" />
                <span>生成目标语言音频</span>
              </div>
            </button>
          </div>
        </div>
        
        <!-- 右侧：结果预览区域 -->
        <div class="lg:col-span-5 space-y-6">
          <!-- 音频预览 -->
          <div v-if="audioUrl" class="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 shadow-lg">
            <h2 class="text-xl font-semibold text-pink-400 mb-4">音频预览</h2>
            <div class="bg-gray-700/50 rounded-lg p-4 flex flex-col items-center">
              <div class="w-full h-24 flex items-center justify-center mb-4">
                <div class="w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                  </svg>
                </div>
              </div>
              <audio :src="apiBaseUrl + audioUrl" controls class="w-full rounded-lg"></audio>
              <div class="mt-4 text-center">
                <p class="text-sm text-gray-400">音频已生成，可以试听或下载</p>
                <a :href="apiBaseUrl + audioUrl" download class="inline-flex items-center mt-2 text-sm text-purple-400 hover:text-purple-300">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  下载音频
                </a>
              </div>
            </div>
          </div>
          
          <!-- 步骤 3: 口型同步 -->
          <div :class="['bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 shadow-lg transition-all', serverVideoPath ? 'hover:shadow-pink-900/20' : 'opacity-70']">
            <h2 class="text-xl font-semibold flex items-center" :class="serverVideoPath ? 'text-pink-400' : 'text-gray-500'">
              <span class="w-8 h-8 rounded-full flex items-center justify-center mr-2" :class="serverVideoPath ? 'bg-pink-500/20 text-pink-400' : 'bg-gray-700 text-gray-500'">3</span>
              生成最终视频
            </h2>
            
            <div class="mt-4">
              <p class="text-sm" :class="serverVideoPath ? 'text-gray-300' : 'text-gray-500'">
                <span v-if="serverVideoPath">已生成目标语言音频，现在可以进行口型同步。</span>
                <span v-else>请先完成前两步，上传视频并生成音频。</span>
              </p>
              
              <button 
                @click="handleLipSync" 
                :disabled="!serverVideoPath || isLoading.lipSync" 
                class="mt-6 w-full py-3 px-4 rounded-lg font-medium transition-all focus:outline-none
                       bg-gradient-to-r from-pink-600 to-pink-700 hover:from-pink-500 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div class="flex items-center justify-center">
                  <Spinner v-if="isLoading.lipSync" class="mr-2" />
                  <span>生成口型同步视频</span>
                </div>
              </button>
            </div>
            
            <!-- 视频预览 -->
            <div v-if="finalVideoUrl" class="mt-6 bg-gray-700/50 rounded-lg p-4">
              <h3 class="text-lg font-medium text-pink-400 mb-2">最终视频</h3>
              <video :src="apiBaseUrl + finalVideoUrl" controls class="w-full rounded-lg"></video>
              <div class="mt-4 text-center">
                <a :href="apiBaseUrl + finalVideoUrl" download class="inline-flex items-center text-sm text-pink-400 hover:text-pink-300">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  下载视频
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import request from '@/api/request';
import Spinner from '@/data/tools/ui/Spinner/Spinner.vue';

// --- 配置 ---
const apiBaseUrl = 'http://localhost:8000/api'; 
const synthesizerApiPrefix = '/synthesizer';

// --- 响应式状态 ---
const isLoading = ref({
  transcribe: false,
  translate: false,
  synthesize: false,
  lipSync: false,
  config: true,
});
const error = ref<string | null>(null);

// --- 数据流 ---
const videoFile = ref<File | null>(null);
const config = ref<{ voices: Record<string, string>; languages: string[] }>({ voices: {}, languages: [] });
const transcribedText = ref('');
const translatedText = ref('');
const serverVideoPath = ref(''); // 【关键状态】用于判断是否执行了步骤1
const selectedLanguage = ref('');
const selectedVoice = ref('');
const audioUrl = ref('');
const serverAudioPath = ref('');
const finalVideoUrl = ref('');
const speechSpeed = ref(1.0);

// --- 口型同步参数 ---
const guidanceScale = ref(1.5);
const inferenceSteps = ref(20);
const seed = ref(1247);

// --- 视频录制相关状态 ---
const activeTab = ref('upload'); // 'upload' 或 'record'
const videoPreview = ref<HTMLVideoElement | null>(null);
const recordedVideoPreview = ref<HTMLVideoElement | null>(null);
const mediaRecorder = ref<MediaRecorder | null>(null);
const recordedChunks = ref<Blob[]>([]);
const recordedVideo = ref<string | null>(null);
const recordedVideoBlob = ref<Blob | null>(null);
const isRecording = ref(false);
const recordingTime = ref(0);
const recordingTimer = ref<number | null>(null);
let stream: MediaStream | null = null;

// --- 方法 ---

const fetchConfig = async () => {
  isLoading.value.config = true;
  try {
    const response = await request.get(`${apiBaseUrl}${synthesizerApiPrefix}/config/`); // <-- 修改点
    config.value = response.data;
    selectedLanguage.value = config.value.languages.includes('英语') ? '英语' : (config.value.languages[0] || '');
    selectedVoice.value = Object.keys(config.value.voices)[0] || '';
  } catch (err) {
    error.value = '无法从后端加载配置。请确保后端服务正在运行。';
  } finally {
    isLoading.value.config = false;
  }
};

onMounted(() => {
  fetchConfig();
  
  // 监听标签页切换，初始化摄像头
  watch(activeTab, (newValue) => {
    if (newValue === 'record') {
      initCamera();
    } else {
      stopCamera();
    }
  });
});

onUnmounted(() => {
  stopCamera();
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value);
  }
});

// 初始化摄像头
const initCamera = async () => {
  try {
    // 停止任何现有的流
    stopCamera();
    
    // 获取新的媒体流
    stream = await navigator.mediaDevices.getUserMedia({ 
      video: { 
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: "user" 
      }, 
      audio: true 
    });
    
    // 将流连接到视频元素
    if (videoPreview.value) {
      videoPreview.value.srcObject = stream;
      videoPreview.value.play();
    }
  } catch (err) {
    console.error('无法访问摄像头:', err);
    error.value = '无法访问摄像头，请确保您已授予浏览器访问权限。';
  }
};

// 停止摄像头
const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
  
  if (videoPreview.value) {
    videoPreview.value.srcObject = null;
  }
};

// 开始录制
const startRecording = () => {
  if (!stream) return;
  
  recordedChunks.value = [];
  recordedVideo.value = null;
  recordedVideoBlob.value = null;
  isRecording.value = true;
  recordingTime.value = 0;
  
  // 创建MediaRecorder实例
  mediaRecorder.value = new MediaRecorder(stream, { mimeType: 'video/webm' });
  
  // 设置数据处理器
  mediaRecorder.value.ondataavailable = (event) => {
    if (event.data.size > 0) {
      recordedChunks.value.push(event.data);
    }
  };
  
  // 录制完成时的处理
  mediaRecorder.value.onstop = () => {
    const blob = new Blob(recordedChunks.value, { type: 'video/webm' });
    recordedVideoBlob.value = blob;
    recordedVideo.value = URL.createObjectURL(blob);
    
    // 将录制的视频显示在预览中
    if (recordedVideoPreview.value) {
      recordedVideoPreview.value.src = recordedVideo.value;
    }
    
    isRecording.value = false;
  };
  
  // 开始录制，每10秒保存一次数据块
  mediaRecorder.value.start(10000);
  
  // 设置录制时间计时器
  recordingTimer.value = window.setInterval(() => {
    recordingTime.value++;
  }, 1000);
};

// 停止录制
const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop();
    isRecording.value = false;
    
    if (recordingTimer.value) {
      clearInterval(recordingTimer.value);
      recordingTimer.value = null;
    }
  }
};

// 重新录制
const retakeVideo = () => {
  recordedVideo.value = null;
  recordedVideoBlob.value = null;
  recordedChunks.value = [];
  
  // 重新初始化摄像头
  initCamera();
};

// 使用录制的视频
const useRecordedVideo = () => {
  if (recordedVideoBlob.value) {
    // 创建一个File对象
    const fileName = `recorded_video_${new Date().getTime()}.webm`;
    videoFile.value = new File([recordedVideoBlob.value], fileName, { type: 'video/webm' });
    
    // 切换到上传标签页以显示文件名
    activeTab.value = 'upload';
  }
};

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    videoFile.value = target.files[0];
    
    // 如果有录制的视频，清除它
    recordedVideo.value = null;
    recordedVideoBlob.value = null;
  }
};

const uploadAndTranscribe = async () => {
  if (!videoFile.value) return;
  isLoading.value.transcribe = true;
  error.value = null;
  const formData = new FormData();
  formData.append('video_file', videoFile.value);
  try {
    const response = await request.post(`${apiBaseUrl}${synthesizerApiPrefix}/upload-and-transcribe/`, formData); // <-- 修改点
    transcribedText.value = response.data.transcribed_text;
    serverVideoPath.value = response.data.server_video_path;
  } catch (err: any) {
    error.value = err.response?.data?.detail || '语音识别失败。';
  } finally {
    isLoading.value.transcribe = false;
  }
};

const handleTranslation = async () => {
  if (!transcribedText.value) {
    error.value = "源文本为空，无法翻译。";
    return;
  }
  isLoading.value.translate = true;
  error.value = null;
  try {
    const response = await request.post(`${apiBaseUrl}${synthesizerApiPrefix}/translate/`, { // <-- 修改点
      text: transcribedText.value,
      target_language: selectedLanguage.value
    });
    translatedText.value = response.data.translated_text;
  } catch (err: any) {
    error.value = err.response?.data?.detail || '翻译失败。';
  } finally {
    isLoading.value.translate = false;
  }
};

const handleSynthesis = async () => {
  if (!translatedText.value) {
    error.value = "翻译结果为空，请先点击翻译按钮。";
    return;
  }
  isLoading.value.synthesize = true;
  error.value = null;
  try {
    const response = await request.post(`${apiBaseUrl}${synthesizerApiPrefix}/synthesize-audio/`, { // <-- 修改点
      text: translatedText.value,
      voice: selectedVoice.value,
      speed: Number(speechSpeed.value),
      language: selectedLanguage.value,
    });
    audioUrl.value = response.data.audio_url;
    serverAudioPath.value = response.data.server_audio_path;
  } catch (err: any) {
    error.value = err.response?.data?.detail || '语音合成失败。';
  } finally {
    isLoading.value.synthesize = false;
  }
};

const handleLipSync = async () => {
  if (!serverVideoPath.value || !serverAudioPath.value) {
    error.value = "请先上传视频并生成音频。";
    return;
  }
  isLoading.value.lipSync = true;
  error.value = null;
  try {
    const response = await request.post(`${apiBaseUrl}${synthesizerApiPrefix}/lipsync/`, { // <-- 修改点
      video_path: serverVideoPath.value,
      audio_path: serverAudioPath.value,
      guidance_scale: Number(guidanceScale.value),
      inference_steps: Number(inferenceSteps.value),
      seed: Number(seed.value),
    });
    finalVideoUrl.value = response.data.final_video_url;
  } catch (err: any) {
    error.value = err.response?.data?.detail || '口型同步失败。';
  } finally {
    isLoading.value.lipSync = false;
  }
};

const resetState = () => {
  videoFile.value = null;
  transcribedText.value = '';
  translatedText.value = '';
  serverVideoPath.value = ''; // 必须清空
  audioUrl.value = '';
  serverAudioPath.value = '';
  finalVideoUrl.value = '';
  error.value = null;
  speechSpeed.value = 1.0;
  
  // 清除录制相关状态
  recordedVideo.value = null;
  recordedVideoBlob.value = null;
  recordedChunks.value = [];
  isRecording.value = false;
  
  fetchConfig();
};

// 格式化录制时间为分:秒格式
const formatRecordingTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
};
</script>

<style scoped>
/* 自定义样式 */
.step-card {
  @apply bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 shadow-lg transition-all;
}

.action-button {
  @apply py-3 px-4 rounded-lg font-medium transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-blue-500
         bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed;
}

.input-field {
  @apply w-full rounded-lg bg-gray-700/50 border border-gray-600 text-white placeholder-gray-500 p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all;
}

.slider-field {
  @apply w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500;
}

.disabled-step {
  @apply opacity-70;
}
</style>
