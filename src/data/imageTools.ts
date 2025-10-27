import type { Tool } from './tools';
import { getThumbnail } from '@/utils/thumbnailLoader';

export const imageTools: Tool[] = [
  {
    id: 'flux-basic',
    name: 'FluxKontextGenerator',
    description: '业界领先的AI图像生成工具，创造惊艳的视觉艺术。基于Flux模型，提供高度可定制的图像生成功能。',
    thumbnail: getThumbnail('flux-basic'),
    tags: ['艺术创作', '高质量'],
    price: '¥0.1/次',
  },
  {
    id: 'flux-mul',
    name: 'FluxKontextMultiImageGenerator',
    description: '基于Flux模型的多图片编辑二创，支持批量处理和自定义参数。',
    thumbnail: getThumbnail('flux-mul'),
    tags: ['艺术创作', '高质量', '多图片'],
    price: '¥0.5/次',
  },
  {
    id: 'dall-e-3',
    name: 'DALL-E 3',
    description: '来自OpenAI的创意图像生成器，与ChatGPT深度集成。',
    thumbnail: getThumbnail('dall-e-3'),
    tags: ['艺术创作', '高质量', '多图片'],
    price: '¥0.08/次',
  },
  {
    id: 'dall-e-4',
    name: 'DALL-E 4',
    description: '来自OpenAI的创意图像生成器，与ChatGPT深度集成。',
    thumbnail: getThumbnail('dall-e-4'),
    tags: ['创意', '易用'],
    price: '¥0.08/次',
  },
  {
    id: 'dall-e-5',
    name: 'DALL-E 5',
    description: '来自OpenAI的创意图像生成器，与ChatGPT深度集成。',
    thumbnail: getThumbnail('dall-e-5'),
    tags: ['创意', '易用'],
    price: '¥0.08/次',
  },
];