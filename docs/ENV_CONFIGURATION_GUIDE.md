# 环境变量配置指南

## 概述

本指南详细说明了前后端连接优化项目中所有环境变量的配置方法、验证规则和最佳实践。

## 目录

1. [环境变量概览](#环境变量概览)
2. [后端环境变量](#后端环境变量)
3. [前端环境变量](#前端环境变量)
4. [环境特定配置](#环境特定配置)
5. [验证和测试](#验证和测试)
6. [故障排除](#故障排除)
7. [最佳实践](#最佳实践)

## 环境变量概览

### 变量分类

| 类型 | 用途 | 设置时机 | 示例 |
|------|------|----------|------|
| 后端运行时 | 服务器运行配置 | 部署时 | `SECRET_KEY` |
| 前端构建时 | 打包时注入 | 构建时 | `VITE_API_BASE_URL` |
| 开发环境 | 本地开发 | 开发时 | `DEBUG=true` |
| 生产环境 | 生产部署 | 部署时 | `NODE_ENV=production` |

### 优先级顺序

1. **Railway环境变量** (最高优先级)
2. **系统环境变量**
3. **`.env`文件**
4. **代码默认值** (最低优先级)

## 后端环境变量

### 必需变量

#### SECRET_KEY
- **用途**: JWT令牌签名密钥
- **类型**: 字符串
- **要求**: 至少32个字符
- **示例**: `09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7`
- **生成方法**:
  ```bash
  # Python生成
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  
  # OpenSSL生成
  openssl rand -hex 32
  ```
- **验证规则**:
  ```python
  len(secret_key) >= 32
  ```

#### CORS_ORIGINS
- **用途**: 跨域资源共享允许的源
- **类型**: 逗号分隔的URL列表
- **格式**: `https://domain1.com,https://domain2.com`
- **示例**: `https://frontend.railway.app,http://localhost:5173`
- **验证规则**:
  ```python
  # 每个源必须是有效的URL或通配符
  for origin in origins.split(','):
      assert origin == '*' or origin.startswith(('http://', 'https://'))
  ```

### 可选变量

#### DATABASE_URL
- **用途**: 数据库连接字符串
- **默认值**: `sqlite:///./recipes.db`
- **支持格式**:
  - SQLite: `sqlite:///./database.db`
  - PostgreSQL: `postgresql://user:pass@host:port/db`
  - MySQL: `mysql://user:pass@host:port/db`
- **验证规则**:
  ```python
  url.startswith(('sqlite://', 'postgresql://', 'mysql://'))
  ```

#### RAILWAY_STATIC_URL
- **用途**: Railway平台自动分配的服务URL
- **设置**: Railway自动设置
- **格式**: `https://service-name.railway.app`
- **用途**: 用于自动配置API基础URL

### 后端环境变量配置示例

#### 开发环境 (.env.development)
```bash
# 开发环境配置
SECRET_KEY=dev-secret-key-for-local-development-32chars
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
DATABASE_URL=sqlite:///./dev_recipes.db
DEBUG=true
```

#### 生产环境 (Railway Variables)
```bash
# 生产环境配置
SECRET_KEY=prod-secret-key-generated-securely-32chars-minimum
CORS_ORIGINS=https://your-frontend.railway.app
DATABASE_URL=sqlite:///./recipes.db
```

## 前端环境变量

### 构建时变量

#### VITE_API_BASE_URL (必需)
- **用途**: 后端API的基础URL
- **类型**: URL字符串
- **示例**: `https://backend.railway.app`
- **注意**: Vite只会注入以`VITE_`开头的变量
- **验证规则**:
  ```javascript
  new URL(apiBaseUrl) // 必须是有效URL
  ```

#### VITE_APP_TITLE (可选)
- **用途**: 应用标题
- **默认值**: `AI食谱推荐`
- **类型**: 字符串
- **示例**: `AI食谱推荐系统`

#### VITE_DEBUG (可选)
- **用途**: 前端调试模式
- **默认值**: `false`
- **类型**: 布尔字符串
- **有效值**: `true`, `false`

#### VITE_BUILD_TIME (自动生成)
- **用途**: 构建时间戳
- **设置**: 构建时自动生成
- **格式**: ISO 8601时间戳
- **示例**: `2025-01-16T10:30:45Z`

### 前端环境变量配置示例

#### 开发环境 (.env.development)
```bash
# 前端开发环境
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=AI食谱推荐 (开发版)
VITE_DEBUG=true
```

#### 生产环境 (Railway Variables)
```bash
# 前端生产环境
VITE_API_BASE_URL=https://your-backend.railway.app
VITE_APP_TITLE=AI食谱推荐系统
VITE_DEBUG=false
```

## 环境特定配置

### 本地开发环境

#### 后端配置文件 (.env.local)
```bash
# 后端本地开发配置
SECRET_KEY=local-dev-secret-key-32-characters-minimum
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
DATABASE_URL=sqlite:///./dev_recipes.db
DEBUG=true
LOG_LEVEL=DEBUG
```

#### 前端配置文件 (frontend/.env.local)
```bash
# 前端本地开发配置
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=AI食谱推荐 (本地开发)
VITE_DEBUG=true
```

### Railway部署环境

#### 后端服务变量
```bash
# Railway后端服务 Variables 页面
SECRET_KEY=<生成的安全密钥>
CORS_ORIGINS=https://your-frontend-service.railway.app
```

#### 前端服务变量
```bash
# Railway前端服务 Variables 页面
VITE_API_BASE_URL=https://your-backend-service.railway.app
VITE_APP_TITLE=AI食谱推荐系统
VITE_DEBUG=false
```

### Docker构建环境

#### Dockerfile中的ARG和ENV
```dockerfile
# 前端Dockerfile
ARG VITE_API_BASE_URL
ARG VITE_APP_TITLE="AI食谱推荐"
ARG VITE_DEBUG="false"

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_TITLE=$VITE_APP_TITLE
ENV VITE_DEBUG=$VITE_DEBUG
```

## 验证和测试

### 自动验证工具

#### 后端配置验证
```bash
# 基本验证
python validate_config.py

# JSON格式输出
python validate_config.py --json

# 修复常见问题
python validate_config.py --fix

# 检查CORS配置
python validate_config.py --check-cors https://your-backend.railway.app
```

#### 前端构建验证
```bash
# 验证构建时配置
node frontend/scripts/validate-build-config.js

# Docker构建验证
docker build --build-arg VITE_API_BASE_URL=https://api.example.com frontend/
```

### 手动验证步骤

#### 1. 检查环境变量是否设置
```bash
# 后端
echo $SECRET_KEY
echo $CORS_ORIGINS

# 前端 (构建时)
echo $VITE_API_BASE_URL
echo $VITE_DEBUG
```

#### 2. 验证变量格式
```bash
# 验证SECRET_KEY长度
python -c "import os; key=os.getenv('SECRET_KEY'); print(f'Length: {len(key) if key else 0}')"

# 验证URL格式
python -c "from urllib.parse import urlparse; import os; url=os.getenv('VITE_API_BASE_URL'); print(urlparse(url) if url else 'Not set')"
```

#### 3. 测试配置效果
```bash
# 测试CORS配置
curl -H "Origin: https://example.com" -H "Access-Control-Request-Method: POST" -X OPTIONS https://your-backend.railway.app/recommend

# 测试API连接
curl https://your-backend.railway.app/health
```

## 故障排除

### 常见问题及解决方案

#### 1. SECRET_KEY相关问题

**问题**: `SECRET_KEY must be at least 32 characters`
```bash
# 解决方案：生成新的密钥
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

**问题**: JWT令牌验证失败
```bash
# 检查密钥是否一致
python -c "import os; print('Current SECRET_KEY length:', len(os.getenv('SECRET_KEY', '')))"
```

#### 2. CORS相关问题

**问题**: `CORS policy: No 'Access-Control-Allow-Origin' header`
```bash
# 检查CORS配置
python validate_config.py --check-cors https://your-backend.railway.app

# 更新CORS_ORIGINS
export CORS_ORIGINS="https://your-frontend.railway.app,http://localhost:5173"
```

**问题**: CORS配置格式错误
```bash
# 验证CORS格式
python -c "
import os
origins = os.getenv('CORS_ORIGINS', '').split(',')
for origin in origins:
    if origin and origin != '*' and not origin.startswith(('http://', 'https://')):
        print(f'Invalid origin: {origin}')
"
```

#### 3. 前端构建问题

**问题**: `VITE_API_BASE_URL is not defined`
```bash
# 检查构建时变量
docker build --build-arg VITE_API_BASE_URL=https://your-backend.railway.app frontend/

# 验证变量注入
node -e "console.log('VITE_API_BASE_URL:', process.env.VITE_API_BASE_URL)"
```

**问题**: API调用失败
```bash
# 检查前端配置
curl -s https://your-frontend.railway.app/build-config-report.json | jq .
```

#### 4. Railway部署问题

**问题**: 环境变量未生效
- 确认在正确的服务中设置变量
- 检查变量名拼写
- 重新部署服务

**问题**: 服务间无法通信
- 检查CORS_ORIGINS包含前端域名
- 验证VITE_API_BASE_URL指向正确的后端
- 确认两个服务都已成功部署

### 调试命令

#### 环境变量调试
```bash
# 显示所有环境变量
env | grep -E "(SECRET_KEY|CORS|VITE_)"

# 检查特定变量
python -c "import os; print({k:v for k,v in os.environ.items() if 'SECRET' in k or 'CORS' in k or 'VITE' in k})"
```

#### 配置状态调试
```bash
# 后端配置状态
curl https://your-backend.railway.app/config/status

# 前端配置状态 (开发模式)
curl https://your-frontend.railway.app/ | grep -o 'config.*status'
```

## 最佳实践

### 1. 安全性

#### 密钥管理
- 使用强随机密钥生成器
- 定期轮换SECRET_KEY
- 不要在代码中硬编码密钥
- 使用环境变量管理敏感信息

#### CORS安全
- 避免使用通配符 `*`
- 只允许必要的域名
- 定期审查CORS配置
- 使用HTTPS域名

### 2. 开发流程

#### 环境隔离
```bash
# 开发环境
.env.development

# 测试环境
.env.test

# 生产环境
Railway Variables
```

#### 配置验证
```bash
# 部署前验证
python validate_config.py
node frontend/scripts/validate-build-config.js

# 部署后验证
python scripts/validate_deployment.py --backend-url <URL>
```

### 3. 文档化

#### 环境变量文档
- 记录所有变量的用途
- 提供示例值
- 说明验证规则
- 更新配置指南

#### 配置模板
```bash
# 创建配置模板
cp .env.example .env.local
cp frontend/.env.example frontend/.env.local
```

### 4. 自动化

#### CI/CD集成
```yaml
# GitHub Actions示例
- name: Validate Configuration
  run: |
    python validate_config.py
    node frontend/scripts/validate-build-config.js
```

#### 部署脚本
```bash
#!/bin/bash
# deploy.sh
set -e

echo "Validating configuration..."
python validate_config.py

echo "Building frontend..."
cd frontend && npm run build

echo "Deploying to Railway..."
railway deploy

echo "Validating deployment..."
python scripts/validate_deployment.py --backend-url $BACKEND_URL
```

## 附录

### A. 环境变量检查清单

#### 部署前检查
- [ ] SECRET_KEY已设置且长度≥32字符
- [ ] CORS_ORIGINS包含所有必要的域名
- [ ] VITE_API_BASE_URL指向正确的后端
- [ ] 所有必需变量都已设置
- [ ] 配置验证脚本通过

#### 部署后检查
- [ ] 后端健康检查通过
- [ ] 前端可以访问
- [ ] API调用成功
- [ ] CORS配置正确
- [ ] 用户认证功能正常

### B. 常用命令参考

#### 配置生成
```bash
# 生成SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 生成配置文件
python -c "
import secrets
print(f'SECRET_KEY={secrets.token_urlsafe(32)}')
print('CORS_ORIGINS=http://localhost:5173')
print('DATABASE_URL=sqlite:///./recipes.db')
"
```

#### 配置验证
```bash
# 完整验证
python validate_config.py --json | jq .

# 特定检查
python validate_config.py --check-cors https://your-backend.railway.app
```

#### 部署验证
```bash
# 快速验证
python scripts/validate_deployment.py --backend-url https://your-backend.railway.app

# 详细报告
python scripts/validate_deployment.py \
  --backend-url https://your-backend.railway.app \
  --frontend-url https://your-frontend.railway.app \
  --verbose \
  --output deployment_report.json
```

### C. 相关资源

- [Railway环境变量文档](https://docs.railway.app/develop/variables)
- [Vite环境变量文档](https://vitejs.dev/guide/env-and-mode.html)
- [FastAPI配置文档](https://fastapi.tiangolo.com/advanced/settings/)
- [CORS配置指南](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)