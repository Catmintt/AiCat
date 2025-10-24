import type { Tool } from './tools';
import { getThumbnail } from '@/utils/thumbnailLoader';

export const codeTools: Tool[] = [
  {
    id: 'code-pilot',
    name: 'CodePilot',
    description: '智能代码补全和生成工具，大幅提升编码效率。',
    thumbnail: getThumbnail('code-pilot'),
    routePath: '/tools/code-pilot',
    tags: ['代码补全', 'AI编程'],
  },
  {
    id: 'bug-buster',
    name: 'BugBuster AI',
    description: '自动分析和调试代码，快速定位并修复潜在错误。',
    thumbnail: getThumbnail('bug-buster'),
    routePath: '/tools/bug-buster',
    tags: ['调试', '代码审查'],
    price: '¥1.0/次扫描',
  },
  {
    id: 'dev-drafter',
    name: 'DevDrafter',
    description: '根据需求文档自动生成项目框架和样板代码。',
    thumbnail: getThumbnail('dev-drafter'),
    routePath: '/tools/dev-drafter',
    tags: ['项目启动', '脚手架'],
  },
];