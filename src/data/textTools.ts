import type { Tool } from './tools';
import { getThumbnail } from '@/utils/thumbnailLoader';


export const textTools: Tool[] = [
  {
    id: 'write-wise',
    name: 'WriteWise',
    description: 'AI写作助手，提供语法纠错、风格润色和内容建议。',
    thumbnail: getThumbnail('write-wise'),
    routePath: '/tools/write-wise',
    tags: ['写作辅助', '内容创作'],
  },
  {
    id: 'summary-bot',
    name: 'SummaryBot',
    description: '快速总结长篇文章、报告和文档，提取核心要点。',
    thumbnail: getThumbnail('summary-bot'),
    routePath: '/tools/summary-bot',
    tags: ['文本摘要', '效率'],
    price: '¥0.01/千字',
  },
  {
    id: 'lingo-link',
    name: 'LingoLink',
    description: '基于神经网络的精准翻译工具，支持超过50种语言。',
    thumbnail: getThumbnail('lingo-link'),
    routePath: '/tools/lingo-link',
    tags: ['翻译', '多语言'],
  },
];