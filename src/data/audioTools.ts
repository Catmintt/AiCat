import type { Tool } from './tools';
import { getThumbnail } from '@/utils/thumbnailLoader';

export const audioTools: Tool[] = [
  {
    id: 'symphony-ai',
    name: 'Symphony AI',
    description: '根据文本描述生成高质量的背景音乐和音效。',
    thumbnail: getThumbnail('symphony-ai'),
    routePath: '/tools/symphony-ai',
    tags: ['音乐生成', '音效'],
    price: '¥0.2/分钟',
  },
  {
    id: 'voice-weaver',
    name: 'VoiceWeaver',
    description: '先进的文本转语音（TTS）工具，声音自然流畅。',
    thumbnail: getThumbnail('voice-weaver'),    
    routePath: '/tools/voice-weaver',
    tags: ['TTS', '语音合成'],
  },
  {
    id: 'clarity-sound',
    name: 'ClaritySound',
    description: '一键去除音频中的背景噪音和回声，提升音质。',
    thumbnail: getThumbnail('clarity-sound'),    
    routePath: '/tools/clarity-sound',
    tags: ['降噪', '音频修复'],
    price: '¥0.1/分钟',
  },
];