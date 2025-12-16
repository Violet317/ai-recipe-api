import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // 环境变量配置
  envPrefix: 'VITE_',
  
  // 构建配置
  build: {
    // 生成source map用于调试
    sourcemap: true,
    
    // 输出目录
    outDir: 'dist',
    
    // 清空输出目录
    emptyOutDir: true,
    
    // 资源内联阈值
    assetsInlineLimit: 4096,
    
    // Rollup配置
    rollupOptions: {
      output: {
        // 手动分块
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          http: ['axios']
        }
      }
    }
  },
  
  // 开发服务器配置
  server: {
    port: 3000,
    host: true, // 允许外部访问
    
    // 代理配置（开发时使用）
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  
  // 预览服务器配置
  preview: {
    port: 3000,
    host: true
  },
  
  // 定义全局常量
  define: {
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    __VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0')
  }
})