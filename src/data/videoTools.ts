import type { Tool } from './tools';
import { getThumbnail } from '@/utils/thumbnailLoader';


export const videoTools: Tool[] = [
  {
    id: 'sora-gen',
    name: 'SoraGen',
    description: '革命性的文生视频模型，将想象变为高清视频。',
    thumbnail: getThumbnail('sora-gen'),
    routePath: '/tools/sora-gen',
    tags: ['文生视频', '高质量'],
  },
  {
    id: 'clip-crafter',
    name: 'ClipCrafter',
    description: '智能视频剪辑与特效制作工具，自动化处理繁琐任务。',
    thumbnail: getThumbnail('clip-crafter'),
    routePath: '/tools/clip-crafter',
    tags: ['视频剪辑', 'AI编辑'],
    price: '¥0.5/项目',
  },
  {
    id: 'avatar-me',
    name: 'AvatarMe',
    description: '根据照片或文本生成逼真的数字人视频。',
    thumbnail: getThumbnail('avatar-me'),
    routePath: '/tools/avatar-me',
    tags: ['数字人', '虚拟形象'],
  },
];