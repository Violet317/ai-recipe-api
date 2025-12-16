import { describe, it, expect, beforeEach, vi } from 'vitest'
import { frontendEnvManager, ConfigStatus } from '../envManager'

// Mock import.meta.env
const mockImportMeta = {
  env: {} as any
}

// Mock window.location
const mockLocation = {
  origin: 'https://frontend-production-abc123.up.railway.app'
}

describe('Environment Manager Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    
    // Reset mock environment
    mockImportMeta.env = {
      DEV: false,
      PROD: true,
      MODE: 'test'
    }
    
    // Mock import.meta
    vi.stubGlobal('import', {
      meta: mockImportMeta
    })
    
    // Mock window.location
    Object.defineProperty(window, 'location', {
      value: mockLocation,
      writable: true
    })
  })

  describe('API Configuration Dynamic Loading', () => {
    it('should return configured API URL when VITE_API_BASE_URL is set and valid', () => {
      mockImportMeta.env.VITE_API_BASE_URL = 'https://api.example.com'
      
      const apiUrl = frontendEnvManager.getApiBaseUrl()
      expect(apiUrl).toBe('https://api.example.com')
    })

    it('should auto-detect Railway backend URL in production', () => {
      mockImportMeta.env.PROD = true
      mockImportMeta.env.VITE_API_BASE_URL = undefined
      mockLocation.origin = 'https://frontend-production-abc123.up.railway.app'
      
      const apiUrl = frontendEnvManager.getApiBaseUrl()
      expect(apiUrl).toBe('https://backend-production-abc123.up.railway.app')
    })

    it('should handle different Railway domain patterns', () => {
      mockImportMeta.env.PROD = true
      mockImportMeta.env.VITE_API_BASE_URL = undefined
      
      // Test frontend- to backend- replacement
      mockLocation.origin = 'https://frontend-myapp.railway.app'
      expect(frontendEnvManager.getApiBaseUrl()).toBe('https://backend-myapp.railway.app')
      
      // Test frontend. to backend. replacement
      mockLocation.origin = 'https://frontend.myapp.railway.app'
      expect(frontendEnvManager.getApiBaseUrl()).toBe('https://backend.myapp.railway.app')
    })

    it('should return development default when in development mode', () => {
      mockImportMeta.env.DEV = true
      mockImportMeta.env.PROD = false
      mockImportMeta.env.VITE_API_BASE_URL = undefined
      
      const apiUrl = frontendEnvManager.getApiBaseUrl()
      expect(apiUrl).toBe('http://localhost:8000')
    })

    it('should validate URL format correctly', () => {
      // Test valid URLs
      mockImportMeta.env.VITE_API_BASE_URL = 'https://api.example.com'
      expect(frontendEnvManager.getApiBaseUrl()).toBe('https://api.example.com')
      
      mockImportMeta.env.VITE_API_BASE_URL = 'http://localhost:8000'
      expect(frontendEnvManager.getApiBaseUrl()).toBe('http://localhost:8000')
      
      // Test invalid URL - should fall back to auto-detection
      mockImportMeta.env.VITE_API_BASE_URL = 'invalid-url'
      mockImportMeta.env.PROD = true
      mockLocation.origin = 'https://frontend-test.railway.app'
      expect(frontendEnvManager.getApiBaseUrl()).toBe('https://backend-test.railway.app')
    })
  })

  describe('Environment Variable Validation', () => {
    it('should validate all required environment variables', () => {
      mockImportMeta.env.VITE_API_BASE_URL = 'https://api.example.com'
      mockImportMeta.env.VITE_APP_TITLE = 'Test App'
      mockImportMeta.env.VITE_DEBUG = 'false'
      
      const report = frontendEnvManager.validateEnvironmentVariables()
      
      expect(report.overallStatus).toBe(ConfigStatus.VALID)
      expect(report.items.find(item => item.name === 'VITE_API_BASE_URL')?.status).toBe(ConfigStatus.VALID)
    })

    it('should report missing required variables', () => {
      mockImportMeta.env.VITE_API_BASE_URL = undefined
      
      const report = frontendEnvManager.validateEnvironmentVariables()
      
      expect(report.overallStatus).toBe(ConfigStatus.INVALID)
      expect(report.items.find(item => item.name === 'VITE_API_BASE_URL')?.status).toBe(ConfigStatus.MISSING)
    })

    it('should use default values for optional variables', () => {
      mockImportMeta.env.VITE_API_BASE_URL = 'https://api.example.com'
      mockImportMeta.env.VITE_APP_TITLE = undefined
      mockImportMeta.env.VITE_DEBUG = undefined
      
      const report = frontendEnvManager.validateEnvironmentVariables()
      
      expect(report.overallStatus).toBe(ConfigStatus.WARNING)
      
      const appTitleItem = report.items.find(item => item.name === 'VITE_APP_TITLE')
      expect(appTitleItem?.status).toBe(ConfigStatus.WARNING)
      expect(appTitleItem?.value).toBe('AI食谱推荐')
      
      const debugItem = report.items.find(item => item.name === 'VITE_DEBUG')
      expect(debugItem?.status).toBe(ConfigStatus.WARNING)
      expect(debugItem?.value).toBe('false')
    })

    it('should validate invalid variable formats', () => {
      mockImportMeta.env.VITE_API_BASE_URL = 'invalid-url'
      mockImportMeta.env.VITE_DEBUG = 'maybe'
      
      const report = frontendEnvManager.validateEnvironmentVariables()
      
      expect(report.overallStatus).toBe(ConfigStatus.INVALID)
      expect(report.items.find(item => item.name === 'VITE_API_BASE_URL')?.status).toBe(ConfigStatus.INVALID)
      expect(report.items.find(item => item.name === 'VITE_DEBUG')?.status).toBe(ConfigStatus.INVALID)
    })
  })

  describe('Build Configuration Validation', () => {
    it('should validate complete build configuration', () => {
      mockImportMeta.env.VITE_API_BASE_URL = 'https://api.example.com'
      mockImportMeta.env.VITE_BUILD_TIME = '2024-01-01T00:00:00Z'
      mockImportMeta.env.VITE_APP_TITLE = 'Test App'
      
      const validation = frontendEnvManager.validateBuildConfiguration()
      
      expect(validation.isValid).toBe(true)
      expect(validation.errors).toHaveLength(0)
    })

    it('should report missing API URL in build configuration', () => {
      mockImportMeta.env.VITE_API_BASE_URL = undefined
      
      const validation = frontendEnvManager.validateBuildConfiguration()
      
      expect(validation.isValid).toBe(false)
      expect(validation.errors).toContain('VITE_API_BASE_URL 未在构建时设置')
    })

    it('should report invalid API URL format in build configuration', () => {
      mockImportMeta.env.VITE_API_BASE_URL = 'not-a-url'
      
      const validation = frontendEnvManager.validateBuildConfiguration()
      
      expect(validation.isValid).toBe(false)
      expect(validation.errors).toContain('VITE_API_BASE_URL 格式无效: not-a-url')
    })

    it('should warn about missing optional build variables', () => {
      mockImportMeta.env.VITE_API_BASE_URL = 'https://api.example.com'
      mockImportMeta.env.VITE_BUILD_TIME = undefined
      mockImportMeta.env.VITE_APP_TITLE = undefined
      
      const validation = frontendEnvManager.validateBuildConfiguration()
      
      expect(validation.isValid).toBe(true)
      expect(validation.warnings).toContain('VITE_BUILD_TIME 未设置，可能影响缓存管理')
      expect(validation.warnings).toContain('VITE_APP_TITLE 未设置，将使用默认标题')
    })
  })

  describe('Environment Configuration', () => {
    it('should return correct environment configuration', () => {
      mockImportMeta.env.VITE_API_BASE_URL = 'https://api.example.com'
      mockImportMeta.env.VITE_BUILD_TIME = '2024-01-01T00:00:00Z'
      mockImportMeta.env.PROD = true
      
      const config = frontendEnvManager.getEnvironmentConfig()
      
      expect(config.apiBaseUrl).toBe('https://api.example.com')
      expect(config.isProduction).toBe(true)
      expect(config.buildTime).toBe('2024-01-01T00:00:00Z')
    })

    it('should handle missing build time gracefully', () => {
      mockImportMeta.env.VITE_API_BASE_URL = 'https://api.example.com'
      mockImportMeta.env.VITE_BUILD_TIME = undefined
      
      const config = frontendEnvManager.getEnvironmentConfig()
      
      expect(config.apiBaseUrl).toBe('https://api.example.com')
      expect(config.buildTime).toBeDefined()
      expect(new Date(config.buildTime)).toBeInstanceOf(Date)
    })
  })

  describe('Configuration Status Checking', () => {
    it('should report configuration as ready when valid', () => {
      mockImportMeta.env.VITE_API_BASE_URL = 'https://api.example.com'
      
      const isReady = frontendEnvManager.isConfigurationReady()
      expect(isReady).toBe(true)
    })

    it('should report configuration as not ready when invalid', () => {
      mockImportMeta.env.VITE_API_BASE_URL = undefined
      
      const isReady = frontendEnvManager.isConfigurationReady()
      expect(isReady).toBe(false)
    })

    it('should report configuration as ready with warnings', () => {
      mockImportMeta.env.VITE_API_BASE_URL = 'https://api.example.com'
      mockImportMeta.env.VITE_APP_TITLE = undefined // This will cause a warning
      
      const isReady = frontendEnvManager.isConfigurationReady()
      expect(isReady).toBe(true) // Should still be ready despite warnings
    })
  })

  describe('Build Info', () => {
    it('should return build information', () => {
      mockImportMeta.env.VITE_BUILD_TIME = '2024-01-01T00:00:00Z'
      mockImportMeta.env.MODE = 'production'
      
      const buildInfo = frontendEnvManager.getBuildInfo()
      
      expect(buildInfo.buildTime).toBe('2024-01-01T00:00:00Z')
      expect(buildInfo.environment).toBe('production')
      expect(buildInfo.version).toBeDefined()
    })

    it('should handle missing build time', () => {
      mockImportMeta.env.VITE_BUILD_TIME = undefined
      
      const buildInfo = frontendEnvManager.getBuildInfo()
      
      expect(buildInfo.buildTime).toBe('unknown')
    })
  })
})