// 使用 import.meta.glob 导入指定目录下所有 .png, .jpg, .svg, .webp 文件
// 'eager: true' 意味着所有图片会被立即加载，而不是返回一个动态导入函数
const thumbnails = import.meta.glob('@/assets/tool-thumbnails/*.{png,jpg,svg,webp}', { eager: true });

// 创建一个Map来存储更干净的键值对 (例如: 'symphony-ai' -> '/src/assets/...')
const thumbnailMap = new Map<string, string>();

// 遍历 Vite 返回的对象，并格式化键名
for (const path in thumbnails) {
  const module = thumbnails[path] as { default: string };
  // 从路径中提取文件名 (例如: '/src/assets/tool-thumbnails/symphony-ai.png' -> 'symphony-ai')
  const fileName = path.split('/').pop()?.split('.')[0] ?? '';
  if (fileName) {
    thumbnailMap.set(fileName, module.default);
  }
}

// 导出一个函数，根据工具ID获取图片URL
export function getThumbnail(toolId: string): string {
  const imageUrl = thumbnailMap.get(toolId);
  if (!imageUrl) {
    // 如果找不到图片，可以返回一个默认的占位图，或者打印警告
    console.warn(`Thumbnail for tool "${toolId}" not found.`);
    return 'https://via.placeholder.com/320x192/CCCCCC/FFFFFF?text=Image+Not+Found';
  }
  return imageUrl;
}