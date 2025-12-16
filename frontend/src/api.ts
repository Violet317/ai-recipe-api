import axios from 'axios';
import { getApiBaseUrl, frontendEnvManager } from './envManager';

// 创建axios实例
const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 添加请求拦截器用于动态URL更新和调试
api.interceptors.request.use(
  (config) => {
    // 在开发模式下记录请求信息
    if (import.meta.env.DEV) {
      console.log(`🌐 API请求: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    }
    
    // 确保使用最新的API基础URL
    config.baseURL = getApiBaseUrl();
    
    return config;
  },
  (error) => {
    console.error('API请求配置错误:', error);
    return Promise.reject(error);
  }
);

// 添加响应拦截器用于错误处理和连接验证
api.interceptors.response.use(
  (response) => {
    // 在开发模式下记录响应信息
    if (import.meta.env.DEV) {
      console.log(`✅ API响应: ${response.status} ${response.config.url}`);
    }
    return response;
  },
  (error) => {
    // 详细的错误处理
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      console.error('🚫 网络连接错误 - 无法连接到后端服务');
      console.error('当前API基础URL:', getApiBaseUrl());
      console.error('请检查后端服务是否正在运行，或环境变量配置是否正确');
      
      // 在开发模式下提供更多调试信息
      if (import.meta.env.DEV) {
        console.group('🔧 调试信息');
        console.log('环境配置:', frontendEnvManager.getEnvironmentConfig());
        console.log('构建信息:', frontendEnvManager.getBuildInfo());
        frontendEnvManager.printConfigStatus();
        console.groupEnd();
      }
    } else if (error.response?.status === 404) {
      console.error('🔍 API端点未找到:', error.config?.url);
    } else if (error.response?.status >= 500) {
      console.error('🔥 服务器内部错误:', error.response.status);
    }
    
    return Promise.reject(error);
  }
);

// 接口类型定义
export interface Recipe {
  id: number;
  name: string;
  match_rate: number;
  missing_ingredients: string[];
  time: number;
  tags: string[];
}

export interface RecommendRequest {
  ingredients: string[];
  tags?: string[];
}

export interface RecommendResponse {
  user_ingredients: string[];
  filter_tags: string[];
  recommendations: Recipe[];
  total: number;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// API方法
export const recipeApi = {
  // 食谱推荐
  recommend: async (data: RecommendRequest): Promise<RecommendResponse> => {
    const response = await api.post('/recommend', data);
    return response.data;
  },
  // 用户注册
  register: async (data: UserCreate): Promise<any> => {
    const response = await api.post('/register', data);
    return response.data;
  },
  // 用户登录
  login: async (data: UserLogin): Promise<TokenResponse> => {
    const response = await api.post('/login', data);
    return response.data;
  },
};

export default api;