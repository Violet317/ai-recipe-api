import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

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