import request from './request';

// 工具分类接口
export interface Category {
  id: string;
  name: string;
  icon: string;
  order: number;
  toolCount?: number;
}

// 工具信息接口
export interface Tool {
  id: string;
  name: string;
  description: string;
  category: string;
  thumbnail: string;
  tags: string[];
  modelName?: string;
  routePath: string;
  popularity?: number;
}

// API响应接口
export interface ApiResponse<T> {
  code: number;
  data: T;
  message?: string;
}

export interface ToolsListResponse {
  list: Tool[];
  total: number;
  hasMore: boolean;
}

/**
 * 获取工具分类列表
 */
export const getCategoriesApi = (): Promise<ApiResponse<Category[]>> => {
  return request({
    url: '/tools/categories',
    method: 'GET',
  });
};

/**
 * 获取工具列表
 * @param params 查询参数
 */
export const getToolsApi = (params: {
  category?: string;
  keyword?: string;
  page?: number;
  pageSize?: number;
  sortBy?: 'popularity' | 'newest';
}): Promise<ApiResponse<ToolsListResponse>> => {
  return request({
    url: '/tools',
    method: 'GET',
    params,
  });
};

/**
 * 获取工具详情
 * @param toolId 工具ID
 */
export const getToolDetailApi = (toolId: string): Promise<ApiResponse<Tool>> => {
  return request({
    url: `/tools/${toolId}`,
    method: 'GET',
  });
};

/**
 * 搜索工具
 * @param keyword 搜索关键词
 */
export const searchToolsApi = (keyword: string): Promise<ApiResponse<ToolsListResponse>> => {
  return request({
    url: '/tools',
    method: 'GET',
    params: { keyword, pageSize: 50 },
  });
};
