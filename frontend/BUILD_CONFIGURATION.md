# 前端构建时环境变量配置指南

## 概述

本文档描述了前端应用的构建时环境变量注入系统，确保在不同部署环境中正确配置API连接。

## 环境变量配置

### 必需变量

- `VITE_API_BASE_URL`: API基础URL，必须是有效的HTTP/HTTPS URL
  - 示例: `https://backend.railway.app`
  - 示例: `http://localhost:8000`

### 可选变量

- `VITE_APP_TITLE`: 应用标题 (默认: "AI食谱推荐")
- `VITE_DEBUG`: 调试模式 (默认: "false")
- `VITE_BUILD_TIME`: 构建时间戳 (自动生成)

## 构建方法

### 1. 本地开发构建

```bash
# 设置环境变量并构建
VITE_API_BASE_URL=http://localhost:8000 npm run build

# 或者在Windows PowerShell中
$env:VITE_API_BASE_URL="http://localhost:8000"; npm run build
```

### 2. 生产环境构建

```bash
# 完整配置
VITE_API_BASE_URL=https://your-backend.railway.app \
VITE_APP_TITLE="生产环境应用" \
VITE_DEBUG=false \
npm run build
```

### 3. Docker构建

#### 标准Dockerfile
```bash
docker build \
  --build-arg VITE_API_BASE_URL=https://backend.railway.app \
  --build-arg VITE_APP_TITLE="Docker应用" \
  -t frontend-app .
```

#### Railway专用Dockerfile
```bash
# 使用Railway专用配置
docker build -f railway.dockerfile \
  --build-arg VITE_API_BASE_URL=https://backend.railway.app \
  -t frontend-railway .
```

## 验证工具

### 配置验证脚本

```bash
# 验证当前环境变量配置
npm run validate-config

# 查看帮助信息
npm run validate-config:help
```

### 构建时验证

构建过程会自动验证环境变量：

1. 检查必需变量是否存在
2. 验证URL格式是否正确
3. 设置默认值给可选变量
4. 生成验证报告

## 部署配置

### Railway平台

1. **环境变量设置**:
   - 在Railway项目设置中添加 `VITE_API_BASE_URL`
   - 值应该是后端服务的完整URL

2. **自动构建**:
   ```bash
   # Railway会自动运行
   npm run build
   ```

3. **Dockerfile配置**:
   - 使用 `railway.dockerfile` 获得更好的Railway集成
   - 支持自动域名推断

### 其他平台

1. **Vercel**:
   ```bash
   # 在vercel.json或环境变量中设置
   VITE_API_BASE_URL=https://your-api.vercel.app
   ```

2. **Netlify**:
   ```bash
   # 在netlify.toml或环境变量中设置
   VITE_API_BASE_URL=https://your-api.netlify.app
   ```

## 故障排除

### 常见问题

1. **构建失败: "VITE_API_BASE_URL 缺失"**
   ```bash
   # 解决方案: 设置环境变量
   export VITE_API_BASE_URL=https://your-backend-url.com
   npm run build
   ```

2. **构建失败: "URL格式无效"**
   ```bash
   # 确保URL包含协议
   ✗ 错误: backend.railway.app
   ✓ 正确: https://backend.railway.app
   ```

3. **运行时API连接失败**
   - 检查CORS配置
   - 验证后端服务是否运行
   - 使用前端配置状态组件进行诊断

### 调试工具

1. **配置状态组件**:
   - 在应用中显示当前配置状态
   - 提供API连接测试功能
   - 显示构建时验证结果

2. **构建报告**:
   - 查看 `dist/build-config-report.json`
   - 包含完整的验证结果和环境信息

3. **开发模式调试**:
   ```bash
   # 开发模式会自动打印配置状态
   npm run dev
   ```

## 最佳实践

1. **环境变量管理**:
   - 使用 `.env.local` 文件进行本地开发
   - 在CI/CD中设置生产环境变量
   - 不要在代码中硬编码URL

2. **构建验证**:
   - 始终在构建前验证配置
   - 使用 `npm run validate-config` 检查设置
   - 查看构建日志确认配置正确

3. **部署验证**:
   - 部署后测试API连接
   - 使用配置状态组件验证设置
   - 监控构建报告文件

## 文件结构

```
frontend/
├── scripts/
│   └── validate-build-config.js    # 构建验证脚本
├── src/
│   ├── envManager.ts               # 环境变量管理器
│   ├── utils/
│   │   └── connectionTest.ts       # 连接测试工具
│   └── components/
│       └── ConfigStatus.tsx        # 配置状态组件
├── Dockerfile                      # 标准Docker配置
├── railway.dockerfile              # Railway专用配置
├── vite.config.ts                  # Vite构建配置
└── BUILD_CONFIGURATION.md          # 本文档
```

## 相关文档

- [Vite环境变量文档](https://vitejs.dev/guide/env-and-mode.html)
- [Railway部署指南](https://docs.railway.app/)
- [Docker多阶段构建](https://docs.docker.com/develop/dev-best-practices/dockerfile_best-practices/)