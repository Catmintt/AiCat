<script setup>
import { useRoute } from 'vue-router';
import { ref, onMounted, onUnmounted, computed } from 'vue';

import request from '@/api/request.js';
import workflowApiTemplate from './flux_kontext_dev_basic.json';

import defaultAvatar from '@/assets/default-avatar.png';
import defaultAvatarBlack from '@/assets/default-avatar_black.png';

const route = useRoute();
// PRODUCT_ID 暂时保留，以备将来重新启用计费
const PRODUCT_ID = route.meta.productId;

// --- DOM Refs for Layout Sync ---
const controlsPanelRef = ref(null);
const outputPanelRef = ref(null);
const historyPanelRef = ref(null);

// --- CONFIG ---
const comfyUIHttpUrl = ref('');
const comfyUIWsUrl = ref('');
const isConfigLoaded = ref(false);

// --- MAIN UI STATE ---
const prompt = ref('Change the color of cat to black');
const selectedFile = ref(null);
const imagePreview = ref(defaultAvatar);
const steps = ref(20);
const cfg = ref(2.5);
const numImages = ref(1);
const seed = ref(-1);
const lastUsedSeed = ref(null);

const isLoading = ref(false);
const statusText = ref('Idle');
const progress = ref(0);
const outputImages = ref([defaultAvatarBlack]);

// --- HISTORY & MODAL STATE ---
const history = ref([]);
const isModalOpen = ref(false);
const activeHistoryItem = ref(null);
const pendingHistoryJobs = ref({});


// --- 图片查看器状态 ---
const isImageViewerOpen = ref(false);
const imageToView = ref('');
const currentImageIndex = ref(0);
const currentImageBatch = ref([]);

// --- WEBSOCKET STATE ---
let ws = null;
const listeningPromptId = ref(null);
const clientId = `flux_user_${Date.now()}`;

// --- WORKFLOW NODE IDs ---
const LOAD_IMAGE_NODE_ID = "191", PROMPT_NODE_ID = "6", CFG_NODE_ID = "35",
      KSAMPLER_NODE_ID = "31", REPEAT_LATENT_NODE_ID = "194";

// --- COMPUTED PROPERTIES ---
const gridClass = computed(() => {
    const count = outputImages.value.length;
    if (count === 1) return 'grid-items-1';
    if (count === 2) return 'grid-items-2';
    if (count >= 3) return 'grid-items-4';
    return '';
});

// --- LIFECYCLE HOOKS ---
onMounted(async () => {
  await fetchAppConfig();
  if (isConfigLoaded.value) {
    connectWebSocket();
    window.addEventListener('keydown', handleKeyDown);
  }
});
onUnmounted(() => {
  if (ws) ws.close();
  window.removeEventListener('keydown', handleKeyDown);
});

// --- CORE FUNCTIONS ---
const finalizeWorkflow = () => {
  if (isLoading.value) {
    isLoading.value = false;
    statusText.value = 'Completed!';
    listeningPromptId.value = null;
  }
};

const runWorkflow = async () => {

  let fileToUpload = selectedFile.value;
  if (!fileToUpload) {
    try {
      const response = await fetch(imagePreview.value);
      const blob = await response.blob();
      fileToUpload = new File([blob], 'image.png', { type: blob.type });
    } catch (error) {
      alert('Failed to load image for processing. Please upload an image manually.');
      return;
    }
  }
  isLoading.value = true;
  progress.value = 0;
  statusText.value = 'Uploading...';

  let currentSeedToUse;
  if (seed.value === -1 || seed.value === null || seed.value === '') {
    currentSeedToUse = Math.floor(Math.random() * 1000000000000000);
  } else {
    currentSeedToUse = seed.value;
  }
  lastUsedSeed.value = currentSeedToUse;
  seed.value = currentSeedToUse;

  const historyEntrySnapshot = {
      id: Date.now(),
      prompt: prompt.value,
      steps: steps.value,
      cfg: cfg.value,
      numImages: numImages.value,
      seed: currentSeedToUse,
      inputImage: imagePreview.value,
      images: [],
      previewImage: ''
  };

  try {
    const filename = await uploadImage(fileToUpload);
    statusText.value = 'Queueing...';
    const promptId = await queuePrompt(filename, currentSeedToUse);

    listeningPromptId.value = promptId;
    pendingHistoryJobs.value[promptId] = historyEntrySnapshot;

  } catch (error) {
    console.error('Workflow execution failed:', error);
    alert('An error occurred. Please check the console (F12) for details.');
    finalizeWorkflow();
  }
};

const processOutputs = (output, historyEntrySnapshot) => {
    if (output?.images) {
        const urls = output.images.map(img =>
            `${comfyUIHttpUrl.value}/view?filename=${encodeURIComponent(img.filename)}&subfolder=${encodeURIComponent(img.subfolder)}&type=${img.type}`
        );
        outputImages.value = urls;
        historyEntrySnapshot.images = urls;
        historyEntrySnapshot.previewImage = urls[0];
        history.value.unshift(historyEntrySnapshot);
        if (history.value.length > 5) history.value.pop();
    }
};

// --- HELPER & EVENT HANDLER FUNCTIONS ---
const handleImageUpload = async (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
    imagePreview.value = URL.createObjectURL(file);
    if (outputImages.value.length > 0) outputImages.value = [];
  }
};

const randomizeSeed = () => {
    seed.value = Math.floor(Math.random() * 1000000000000000);
}

const openHistoryModal = (item) => {
  activeHistoryItem.value = item; isModalOpen.value = true;
};
const closeModal = () => {
  isModalOpen.value = false; activeHistoryItem.value = null;
};

const applyHistory = () => {
  if (!activeHistoryItem.value || isLoading.value) return;
  const item = activeHistoryItem.value;
  prompt.value = item.prompt; steps.value = item.steps; cfg.value = item.cfg;
  numImages.value = item.numImages; seed.value = item.seed; lastUsedSeed.value = item.seed;
  imagePreview.value = item.inputImage; outputImages.value = item.images;
  selectedFile.value = null; closeModal();
};

const downloadImage = async (url) => {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = `flux-output-${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(blobUrl);
    } catch (error) {
        console.error('Download failed:', error);
        alert('Failed to download image.');
    }
};

const remixImage = async (imageUrl) => {
    try {
        const response = await fetch(imageUrl);
        const blob = await response.blob();
        const file = new File([blob], `remixed_${Date.now()}.png`, { type: blob.type });
        selectedFile.value = file;
        imagePreview.value = URL.createObjectURL(file);
        if (isModalOpen.value) closeModal();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
        console.error('Failed to prepare image for remix:', error);
        alert('Could not set this image for remixing.');
    }
};

const openImageViewer = (url, index, batch) => {
    imageToView.value = url;
    currentImageIndex.value = index;
    currentImageBatch.value = batch;
    isImageViewerOpen.value = true;
};
const closeImageViewer = () => { isImageViewerOpen.value = false; };
const navigateImage = (direction) => {
    if (!currentImageBatch.value || currentImageBatch.value.length === 0) return;
    let newIndex = currentImageIndex.value + direction;
    if (newIndex < 0) newIndex = currentImageBatch.value.length - 1;
    if (newIndex >= currentImageBatch.value.length) newIndex = 0;
    currentImageIndex.value = newIndex;
    imageToView.value = currentImageBatch.value[newIndex];
};
const handleKeyDown = (event) => {
    if (isImageViewerOpen.value) {
      if (event.key === 'ArrowLeft') navigateImage(-1);
      else if (event.key === 'ArrowRight') navigateImage(1);
      else if (event.key === 'Escape') closeImageViewer();
    } else if (isModalOpen.value) {
      if (event.key === 'Escape') closeModal();
    }
};

// --- API & WEBSOCKET FUNCTIONS ---
const fetchAppConfig = async () => {
  try {
    // 接口路径 /api/config 与后端 main.py 中 systems 路由配置一致
    const response = await request.get('/comfyui_sys/config');
    comfyUIHttpUrl.value = response.data.comfyUI.httpUrl;
    comfyUIWsUrl.value = response.data.comfyUI.wsUrl;
    isConfigLoaded.value = true;
  } catch (error) {
    console.error('❌ 加载应用配置失败:', error);
    alert('无法加载应用核心配置，功能不可用。');
  }
};

const uploadImage = async (file) => {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('overwrite', 'true');
    // 接口路径 /api/flux/upload-image 与后端 main.py 中 flux 路由配置一致
    const response = await request.post('/flux/upload-image', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data.name;
};

const queuePrompt = async (imageFilename, currentSeed) => {
  const promptData = JSON.parse(JSON.stringify(workflowApiTemplate));
  promptData[LOAD_IMAGE_NODE_ID].inputs.image = imageFilename;
  promptData[PROMPT_NODE_ID].inputs.text = prompt.value;
  promptData[CFG_NODE_ID].inputs.guidance = cfg.value;
  promptData[KSAMPLER_NODE_ID].inputs.steps = steps.value;
  promptData[KSAMPLER_NODE_ID].inputs.seed = currentSeed;
  promptData[REPEAT_LATENT_NODE_ID].inputs.amount = numImages.value;
  const payload = { prompt: promptData, client_id: clientId };
  
  // 接口路径 /api/flux/queue-prompt 与后端 main.py 中 flux 路由配置一致
  const response = await request.post('/flux/queue-prompt', payload);

  if (response?.prompt_id) return response.data.prompt_id;
  throw new Error("Invalid response from /queue-prompt endpoint.");
};

const connectWebSocket = () => {
  ws = new WebSocket(`${comfyUIWsUrl.value}?clientId=${clientId}`);
  ws.onmessage = (event) => {
    if (typeof event.data !== 'string') return;
    const message = JSON.parse(event.data);
    const { type, data } = message;

    if (type === 'status') return;

    const promptId = data?.prompt_id;
    if (promptId !== listeningPromptId.value) return;

    if (isLoading.value && statusText.value === 'Queueing...') {
        statusText.value = 'Generating...';
    }

    switch (type) {
      case 'execution_start':
        progress.value = 0;
        break;
      case 'progress':
        progress.value = (data.value / data.max) * 100;
        break;
      case 'executed':
        const pendingJob = pendingHistoryJobs.value[promptId];
        if (data.output?.images && pendingJob) {
            processOutputs(data.output, pendingJob);
            delete pendingHistoryJobs.value[promptId];
        }
        break;
      case 'executing':
        if (data.node === null) {
          finalizeWorkflow();
        }
        break;
    }
  };
};
</script>

<template>
  <div class="editor-container">
    <div class="editor-layout">
      <!-- Left Controls Panel -->
      <div class="controls-panel" ref="controlsPanelRef">
        <div class="controls-panel-content">
            <h2>FLUX Kontext Editor</h2>
            <div class="control-group"><label for="prompt-input">Prompt</label><textarea id="prompt-input" v-model="prompt" rows="4"></textarea></div>
            <div class="control-group"><label for="image-upload">Image</label><div class="image-upload-box"><input id="image-upload" type="file" @change="handleImageUpload" accept="image/png, image/jpeg, image/webp" /><div v-if="!imagePreview" class="upload-hint">Click or drag file</div><img v-if="imagePreview" :src="imagePreview" alt="Preview" class="image-preview" /></div></div>
            <div class="control-group"><label>Inference Steps: {{ steps }}</label><input type="range" v-model.number="steps" min="1" max="50" step="1" /></div>
            <div class="control-group"><label>Guidance Scale (CFG): {{ cfg }}</label><input type="range" v-model.number="cfg" min="0" max="10" step="0.1" /></div>
            <div class="control-group"><label>Number of Images: {{ numImages }}</label><input type="range" v-model.number="numImages" min="1" max="4" step="1" /></div>
            <div class="control-group">
                <label for="seed-input">Seed (last run: {{ lastUsedSeed || 'N/A' }})</label>
                <div class="input-with-button">
                    <input id="seed-input" type="number" v-model.number="seed" placeholder="-1 for random" />
                    <button class="icon-button" @click="randomizeSeed" title="Generate new random seed">🔄</button>
                </div>
            </div>
        </div>
        <button class="run-button" @click="runWorkflow" :disabled="isLoading || !isConfigLoaded">
            <span v-if="!isConfigLoaded">Connecting...</span>
            <span v-else-if="isLoading"><i class="loading-icon"></i> Generating...</span>
            <span v-else>Run</span>
        </button>
      </div>

      <!-- Center Output Panel -->
      <div class="output-panel" ref="outputPanelRef">
        <div class="output-header"><span>{{ statusText }}</span><div v-if="isLoading" class="progress-bar-container"><div class="progress-bar" :style="{ width: progress + '%' }"></div></div></div>
        <div class="results-grid-container">
            <div v-if="outputImages.length > 0" class="results-grid" :class="gridClass">
                <div v-for="(imgUrl, index) in outputImages" :key="index" class="grid-item">
                    <img :src="imgUrl" alt="Generated Image" />
                    <div class="actions-overlay">
                        <button class="action-btn" @click.stop="openImageViewer(imgUrl, index, outputImages)">View</button>
                        <button class="action-btn" @click.stop="remixImage(imgUrl)">Remix</button>
                        <button class="action-btn" @click.stop="downloadImage(imgUrl)">Save</button>
                    </div>
                </div>
            </div>
            <div v-else-if="isLoading" class="output-placeholder"><i class="loading-icon large"></i></div>
            <div v-else class="output-placeholder"><p>Your generated images will appear here.</p></div>
        </div>
      </div>

      <!-- Right History Panel -->
      <div class="history-panel" ref="historyPanelRef">
        <h3>History</h3>
        <div class="history-list">
            <div v-if="history.length === 0" class="history-placeholder">History will appear here.</div>
            <div v-for="item in history" :key="item.id" class="history-item" @click="openHistoryModal(item)">
                <img :src="item.previewImage" alt="History thumbnail" class="history-thumbnail"/><div class="history-info"><p class="history-prompt">{{ item.prompt }}</p><span class="history-seed">Seed: {{ item.seed }}</span></div>
            </div>
        </div>
      </div>
    </div>

    <!-- History Detail Modal -->
    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
            <div class="modal-header">
                <h3>History Details</h3>
                <button class="modal-close-button" @click="closeModal">×</button>
            </div>
            <div class="modal-layout">
                <div class="modal-params">
                    <h4>Parameters</h4>
                    <div class="param-item"><strong>Prompt:</strong> {{ activeHistoryItem.prompt }}</div>
                    <div class="param-item"><strong>Steps:</strong> {{ activeHistoryItem.steps }}</div>
                    <div class="param-item"><strong>CFG:</strong> {{ activeHistoryItem.cfg }}</div>
                    <div class="param-item"><strong>Seed:</strong> {{ activeHistoryItem.seed }}</div>
                    <div class="param-item"><strong>Output Images:</strong> {{ activeHistoryItem.numImages }}</div>
                    <div class="param-item">
                      <strong>Input Image:</strong>
                      <div class="history-input-images">
                        <img v-if="activeHistoryItem.inputImage" :src="activeHistoryItem.inputImage" class="history-input-thumb" alt="Input image thumbnail"/>
                      </div>
                    </div>
                    <button class="apply-button" @click="applyHistory" :disabled="isLoading">Apply Parameters</button>
                </div>
                <div
                  class="modal-images"
                  :class="{ 'single-image-container': activeHistoryItem.images.length === 1 }"
                >
                    <div
                        v-for="(imgUrl, index) in activeHistoryItem.images"
                        :key="'modal-flex-'+index"
                        class="image-wrapper"
                        :class="`image-count-${activeHistoryItem.images.length}`"
                    >
                        <img :src="imgUrl" alt="History Image" />
                        <div class="actions-overlay">
                            <button class="action-btn" @click.stop="openImageViewer(imgUrl, index, activeHistoryItem.images)">View</button>
                            <button class="action-btn" @click.stop="remixImage(imgUrl)">Remix</button>
                            <button class="action-btn" @click.stop="downloadImage(imgUrl)">Save</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Image Viewer Modal -->
    <div v-if="isImageViewerOpen" class="image-viewer-overlay" @click.self="closeImageViewer">
        <button class="nav-button prev" v-if="currentImageBatch.length > 1" @click.stop="navigateImage(-1)">❮</button>
        <div class="image-viewer-content">
            <img :src="imageToView" alt="Full screen image view" @click.stop />
        </div>
        <button class="nav-button next" v-if="currentImageBatch.length > 1" @click.stop="navigateImage(1)">❯</button>
        <button class="image-viewer-close-button" @click="closeImageViewer">×</button>
    </div>

  </div>
</template>


<style scoped>
.editor-container {
  display: flex;
  flex-direction: column; 
  background-color: #1A1B1E;
  color: #E9ECEF;
  padding: 2rem;
  font-family: sans-serif;
  box-sizing: border-box;
  width: 100%;
}

.editor-layout {
  display: flex;
  gap: 2rem;
  max-width: 1800px;
  margin: 0 auto;
  align-items: flex-start;
  width: 100%;
}

.controls-panel { width: 380px; flex-shrink: 0; }
.output-panel { flex-grow: 1; }
.history-panel { width: 280px; flex-shrink: 0; }

.controls-panel, .output-panel, .history-panel {
  background-color: #25262B;
  border-radius: 12px;
  border: 1px solid #373A40;
  display: flex;
  flex-direction: column;
}

.output-panel, .history-panel {
  min-height: 500px;
}

.controls-panel {
  padding: 0;
}
.controls-panel-content {
  padding: 1.5rem 2rem;
}
.run-button {
  margin-top: auto;
  flex-shrink: 0;
  border-radius: 0 0 11px 11px;
  width: 100%; padding: 0.9rem; font-size: 1.1rem; font-weight: bold; color: white;
  background-color: #228BE6; border: none; cursor: pointer; display: flex;
  align-items: center; justify-content: center;
}
.run-button:disabled { background: #555; cursor: not-allowed; }

h2, h3 { text-align: center; color: #E9ECEF; margin: 0 0 1.5rem; font-weight: 600; }
h2 { padding-top: 1.5rem; }
h3 { padding: 1.5rem 0 0; margin-bottom: 1rem; }

.control-group { margin-bottom: 1.25rem; }
.control-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; font-size: 0.9rem; color: #868E96; }
input[type="range"] { width: 100%; -webkit-appearance: none; appearance: none; height: 4px; background: #373A40; border-radius: 2px; cursor: pointer; }
input[type="range"]::-webkit-slider-thumb { -webkit-appearance: none; width: 16px; height: 16px; background: #228BE6; border-radius: 50%; border: 2px solid #25262B; }
textarea, .input-with-button input { width: 100%; padding: 0.75rem; background-color: #1A1B1E; border: 1px solid #373A40; border-radius: 6px; color: #E9ECEF; box-sizing: border-box; }
.input-with-button { display: flex; gap: 0.5rem; }
.icon-button { padding: 0 0.8rem; background-color: #373A40; border: none; color: #E9ECEF; cursor: pointer; border-radius: 6px; font-size: 1.2rem; }
.image-upload-box { position: relative; border: 2px dashed #373A40; border-radius: 8px; min-height: 100px; display: flex; align-items: center; justify-content: center; }
.image-upload-box input[type="file"] { position: absolute; width: 100%; height: 100%; opacity: 0; cursor: pointer; }
.upload-hint, .history-placeholder { color: #868E96; text-align: center; padding: 1rem; }
.image-preview { max-width: 100%; max-height: 150px; object-fit: contain; }

.output-header { padding: 1rem 1.5rem; border-bottom: 1px solid #373A40; display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; color: #868E96; flex-shrink: 0; }
.progress-bar-container { width: 150px; background-color: #373A40; border-radius: 4px; overflow: hidden; height: 6px; }
.progress-bar { height: 100%; background-color: #228BE6; }
.results-grid-container { flex-grow: 1; padding: 1.5rem; overflow-y: auto; }
.results-grid { display: grid; gap: 1rem; }
.grid-item { position: relative; border-radius: 8px; overflow: hidden; border: 1px solid #373A40; }
.grid-item img { width: 100%; height: 100%; object-fit: cover; display: block; }
.results-grid.grid-items-1 { grid-template-columns: 1fr; place-items: center; }
.results-grid.grid-items-1 .grid-item { width: auto; max-width: 100%; max-height: 100%; border: none; }
.results-grid.grid-items-1 .grid-item img { object-fit: contain; }
.results-grid.grid-items-2 { grid-template-columns: repeat(2, 1fr); align-content: start; }
.results-grid.grid-items-4 { grid-template-columns: repeat(2, 1fr); grid-template-rows: repeat(2, 1fr); align-content: start; }
.output-placeholder { display: flex; align-items: center; justify-content: center; height: 100%; min-height: 300px; color: #868E96; }

.actions-overlay {
  position: absolute; bottom: 0; left: 0; width: 100%;
  display: flex; justify-content: center; gap: 1px;
  opacity: 0; transition: opacity 0.3s ease;
  background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 100%);
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  overflow: hidden;
}
.grid-item:hover .actions-overlay,
.image-wrapper:hover .actions-overlay {
  opacity: 1;
}
.action-btn {
  flex-grow: 1; background-color: rgba(40, 40, 40, 0.8); color: white;
  border: none; padding: 10px 0; font-size: 0.9rem; font-weight: 500;
  cursor: pointer; transition: background-color 0.2s; border-top: 1px solid #444;
}
.action-btn:hover { background-color: #228BE6; }

.history-panel { padding: 0; }
.history-list { overflow-y: auto; padding: 0 1rem 1rem; flex-grow: 1; }
.history-item { display: flex; gap: 1rem; padding: 0.75rem; border-radius: 8px; cursor: pointer; transition: background-color 0.2s; }
.history-item:hover { background-color: #373A40; }
.history-thumbnail { width: 56px; height: 56px; object-fit: cover; border-radius: 6px; flex-shrink: 0; }
.history-info { overflow: hidden; }
.history-prompt { font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin: 0 0 0.25rem; }
.history-seed { font-size: 0.8rem; color: #868E96; }

.history-input-images {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}

.history-input-thumb {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #373A40;
}

.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content {
  background-color: #25262B;
  border-radius: 12px;
  width: 90%;
  max-width: 1200px;
  height: 80vh;
  padding: 0;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  border-bottom: 1px solid #373A40;
  flex-shrink: 0;
}
.modal-header h3 { margin: 0; padding: 0; font-size: 1.2rem; font-weight: 600; text-align: left; }
.modal-close-button { position: static; background: none; border: none; color: #868E96; font-size: 1.8rem; cursor: pointer; line-height: 1; padding: 0; }
.modal-close-button:hover { color: #fff; }

.modal-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 2rem;
  flex-grow: 1;
  overflow: hidden;
  padding: 2rem;
}
.modal-params { overflow-y: auto; padding-right: 1rem; }
.modal-params h4 { margin-top: 0; margin-bottom: 1.5rem; padding-top: 0; text-align: left; }
.param-item { margin-bottom: 1rem; font-size: 0.9rem; word-wrap: break-word; }
.param-item strong { color: #868E96; display: block; margin-bottom: 0.25rem; }
.apply-button { width: 100%; padding: 0.8rem; background-color: #228BE6; border: none; border-radius: 6px; color: white; font-weight: bold; cursor: pointer; margin-top: 2rem; }

.modal-images {
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  justify-content: center;
  gap: 1rem;
  height: 100%;
  width: 100%;
  overflow-y: auto;
  padding: 4px;
}

.modal-images:has(.image-wrapper.image-count-1) {
  align-content: center;
  overflow-y: hidden;
}

.image-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #373A40;
  flex-grow: 0;
  flex-shrink: 1;
}

.image-wrapper.image-count-2,
.image-wrapper.image-count-3,
.image-wrapper.image-count-4 {
  flex-basis: calc(50% - 0.5rem);
  max-width: calc(50% - 0.5rem);
}

.image-wrapper.image-count-1 {
  flex-basis: auto;
  width: auto;
  max-width: 95%;
  max-height: 95%;
  border: none;
}

.image-wrapper img {
  width: 100%;
  height: auto;
  display: block;
}

.history-list {
  overflow-y: auto;
  padding: 0 1rem 1rem;
  flex-grow: 1;
}

.modal-images,
.modal-params,
.history-list,
.results-grid-container {
  scrollbar-width: thin;
  scrollbar-color: #495057 #25262B;
}
.modal-images::-webkit-scrollbar,
.modal-params::-webkit-scrollbar,
.history-list::-webkit-scrollbar,
.results-grid-container::-webkit-scrollbar {
  width: 8px;
}
.modal-images::-webkit-scrollbar-track,
.modal-params::-webkit-scrollbar-track,
.history-list::-webkit-scrollbar-track,
.results-grid-container::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
}
.modal-images::-webkit-scrollbar-thumb,
.modal-params::-webkit-scrollbar-thumb,
.history-list::-webkit-scrollbar-thumb,
.results-grid-container::-webkit-scrollbar-thumb {
  background-color: #495057;
  border-radius: 4px;
  border: 2px solid #25262B;
}
.modal-images::-webkit-scrollbar-thumb:hover,
.modal-params::-webkit-scrollbar-thumb:hover,
.history-list::-webkit-scrollbar-thumb:hover,
.results-grid-container::-webkit-scrollbar-thumb:hover {
  background-color: #868E96;
}

.loading-icon { display: inline-block; width: 1em; height: 1em; border: 2px solid rgba(255, 255, 255, 0.3); border-radius: 50%; border-top-color: #fff; animation: spin 1s linear infinite; margin-right: 0.5em; }
.loading-icon.large { width: 48px; height: 48px; border-width: 4px; }
@keyframes spin { to { transform: rotate(360deg); } }
@media (max-width: 1200px) { .editor-layout { flex-direction: column; } .controls-panel, .output-panel, .history-panel { width: 100%; height: auto !important; min-height: auto; } }

.image-viewer-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex; align-items: center; justify-content: center; z-index: 1001;
}
.image-viewer-content {
  position: relative; width: 90vw; height: 90vh;
  display: flex; align-items: center; justify-content: center;
}
.image-viewer-content img {
  width: auto; height: auto; max-width: 100%; max-height: 100%;
  object-fit: contain; cursor: default; border-radius: 4px;
}
.image-viewer-close-button {
  position: absolute; top: 15px; right: 25px; background: none; border: none;
  color: rgba(255, 255, 255, 0.7); font-size: 3rem; font-weight: bold;
  cursor: pointer; line-height: 1; transition: color 0.2s, transform 0.2s;
}
.image-viewer-close-button:hover { color: white; transform: scale(1.1); }
.nav-button {
  position: absolute; top: 50%; transform: translateY(-50%);
  background-color: rgba(0, 0, 0, 0.3); color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2); font-size: 2.5rem; padding: 1rem 1.5rem;
  cursor: pointer; border-radius: 8px; transition: all 0.2s; user-select: none;
}
.nav-button:hover { background-color: rgba(0, 0, 0, 0.5); color: white; }
.nav-button.prev { left: 20px; }
.nav-button.next { right: 20px; }
</style>