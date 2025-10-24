// 定义统一的工具接口
export interface Tool {
  id: string;
  name: string;
  description: string;
  thumbnail: string; // 产品封面图片链接
  routePath: string; // 点击后跳转的路径
  tags: string[];
  price?: string; // 例如: '¥0.05/次'
  modelName?: string;
}