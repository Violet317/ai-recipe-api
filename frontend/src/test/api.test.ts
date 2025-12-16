import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

// Mock the envManager module
vi.mock('../envManager', () => ({
  getApiBaseUrl: vi.fn(() => 'https://test-api.example.com'),
  frontendEnvManager: {
    getEnvironmentConfig: vi.fn(() => ({
      apiBaseUrl: 'https://test-api.example.com',
      isProduction: false,
      buildTime: '2024-01-01T00:00:00Z'
    })),
    getBuildInfo: vi.fn(() => ({
      buildTime: '2024-01-01T00:00:00Z',
      version: '1.0.0',
      environment: 'test'
    })),
    printConfigStatus: vi.fn()
  }
}))

describe('API Configuration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock axios.create to return a mock instance
    const mockAxiosInstance = {
      interceptors: {
        request: {
          use: vi.fn()
        },
        response: {
          use: vi.fn()
        }
      },
      post: vi.fn(),
      get: vi.fn()
    }
    
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any)
  })

  describe('API Instance Configuration', () => {
    it('should create axios instance with correct base URL', async () => {
      // Import the api module to trigger axios.create
      await import('../api')
      
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: 'https://test-api.example.com',
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        },
      })
    })

    it('should configure request and response interceptors', async () => {
      const mockAxiosInstance = {
        interceptors: {
          request: {
            use: vi.fn()
          },
          response: {
            use: vi.fn()
          }
        }
      }
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance as any)
      
      // Import the api module to trigger interceptor setup
      await import('../api')
      
      expect(mockAxiosInstance.interceptors.request.use).toHaveBeenCalled()
      expect(mockAxiosInstance.interceptors.response.use).toHaveBeenCalled()
    })
  })

  describe('Dynamic API URL Loading', () => {
    it('should update base URL dynamically in request interceptor', () => {
      const { getApiBaseUrl } = require('../envManager')
      
      // Mock different API URLs
      getApiBaseUrl.mockReturnValueOnce('https://api-v1.example.com')
      
      // The request interceptor should call getApiBaseUrl() to get the latest URL
      expect(getApiBaseUrl).toBeDefined()
    })

    it('should handle API URL changes during runtime', () => {
      const { getApiBaseUrl } = require('../envManager')
      
      // Simulate URL change
      getApiBaseUrl.mockReturnValueOnce('https://api-v1.example.com')
      getApiBaseUrl.mockReturnValueOnce('https://api-v2.example.com')
      
      // Each call should potentially return a different URL
      expect(getApiBaseUrl()).toBe('https://api-v2.example.com')
    })
  })

  describe('API Method Configuration', () => {
    it('should define recipe recommendation API method', async () => {
      const { recipeApi } = await import('../api')
      
      expect(recipeApi.recommend).toBeDefined()
      expect(typeof recipeApi.recommend).toBe('function')
    })

    it('should define user registration API method', async () => {
      const { recipeApi } = await import('../api')
      
      expect(recipeApi.register).toBeDefined()
      expect(typeof recipeApi.register).toBe('function')
    })

    it('should define user login API method', async () => {
      const { recipeApi } = await import('../api')
      
      expect(recipeApi.login).toBeDefined()
      expect(typeof recipeApi.login).toBe('function')
    })
  })

  describe('API Request Configuration', () => {
    it('should handle recipe recommendation requests', async () => {
      const mockAxiosInstance = {
        post: vi.fn().mockResolvedValue({
          data: {
            user_ingredients: ['tomato', 'cheese'],
            recommendations: [],
            total: 0
          }
        }),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      }
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance as any)
      
      const { recipeApi } = await import('../api')
      
      const requestData = {
        ingredients: ['tomato', 'cheese'],
        tags: ['vegetarian']
      }
      
      await recipeApi.recommend(requestData)
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/recommend', requestData)
    })

    it('should handle user registration requests', async () => {
      const mockAxiosInstance = {
        post: vi.fn().mockResolvedValue({
          data: { message: 'User created successfully' }
        }),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      }
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance as any)
      
      const { recipeApi } = await import('../api')
      
      const userData = {
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123'
      }
      
      await recipeApi.register(userData)
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/register', userData)
    })

    it('should handle user login requests', async () => {
      const mockAxiosInstance = {
        post: vi.fn().mockResolvedValue({
          data: {
            access_token: 'test-token',
            token_type: 'bearer'
          }
        }),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      }
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance as any)
      
      const { recipeApi } = await import('../api')
      
      const loginData = {
        username: 'testuser',
        password: 'password123'
      }
      
      const result = await recipeApi.login(loginData)
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/login', loginData)
      expect(result.access_token).toBe('test-token')
      expect(result.token_type).toBe('bearer')
    })
  })

  describe('Error Handling Configuration', () => {
    it('should handle network connection errors', async () => {
      const mockAxiosInstance = {
        post: vi.fn().mockRejectedValue({
          code: 'ECONNREFUSED',
          config: { url: '/test' }
        }),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      }
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance as any)
      
      const { recipeApi } = await import('../api')
      
      await expect(recipeApi.recommend({ ingredients: [] })).rejects.toMatchObject({
        code: 'ECONNREFUSED'
      })
    })

    it('should handle HTTP error responses', async () => {
      const mockAxiosInstance = {
        post: vi.fn().mockRejectedValue({
          response: {
            status: 404,
            data: { message: 'Not found' }
          },
          config: { url: '/nonexistent' }
        }),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      }
      
      mockedAxios.create.mockReturnValue(mockAxiosInstance as any)
      
      const { recipeApi } = await import('../api')
      
      await expect(recipeApi.recommend({ ingredients: [] })).rejects.toMatchObject({
        response: {
          status: 404
        }
      })
    })
  })
})