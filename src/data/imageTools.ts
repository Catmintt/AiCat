import type { Tool } from './tools';
import { getThumbnail } from '@/utils/thumbnailLoader';

export const imageTools: Tool[] = [
  {
    id: 'midjourney',
    name: 'Midjourney',
    description: '业界领先的AI图像生成工具，创造惊艳的视觉艺术。',
    thumbnail: getThumbnail('midjourney'),
    routePath: '/tools/midjourney',
    tags: ['艺术创作', '高质量'],
    price: '¥0.1/次',
  },
  {
    id: 'stable-diffusion',
    name: 'Stable Diffusion',
    description: '强大且开源的文生图模型，拥有丰富的社区支持。',
    thumbnail: getThumbnail('stable-diffusion'),
    routePath: '/tools/stable-diffusion',
    tags: ['开源', '可定制'],
  },
  {
    id: 'dall-e-3',
    name: 'DALL-E 3',
    description: '来自OpenAI的创意图像生成器，与ChatGPT深度集成。',
    thumbnail: getThumbnail('dall-e-3'),
    routePath: '/tools/dall-e-3',
    tags: ['创意', '易用'],
    price: '¥0.08/次',
  },
  {
    id: 'dall-e-4',
    name: 'DALL-E 4',
    description: '来自OpenAI的创意图像生成器，与ChatGPT深度集成。',
    thumbnail: getThumbnail('dall-e-4'),
    routePath: '/tools/dall-e-4',
    tags: ['创意', '易用'],
    price: '¥0.08/次',
  },
  {
    id: 'dall-e-5',
    name: 'DALL-E 5',
    description: '来自OpenAI的创意图像生成器，与ChatGPT深度集成。',
    thumbnail: getThumbnail('dall-e-5'),
    routePath: '/tools/dall-e-5',
    tags: ['创意', '易用'],
    price: '¥0.08/次',
  },
];