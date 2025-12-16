import '@testing-library/jest-dom'

// Mock import.meta.env for testing
Object.defineProperty(globalThis, 'import', {
  value: {
    meta: {
      env: {
        DEV: false,
        PROD: true,
        MODE: 'test',
        VITE_API_BASE_URL: 'https://test-api.example.com',
        VITE_APP_TITLE: 'Test App',
        VITE_DEBUG: 'false',
        VITE_BUILD_TIME: '2024-01-01T00:00:00Z'
      }
    }
  }
})