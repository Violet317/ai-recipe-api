# 前后端连接优化部署指南

## 概述

本指南详细说明如何在Railway平台上部署前后端分离的AI食谱推荐应用，包括环境变量配置、连接优化和部署验证。

## 目录

1. [快速开始](#快速开始)
2. [服务架构](#服务架构)
3. [环境变量配置](#环境变量配置)
4. [部署步骤](#部署步骤)
5. [部署验证](#部署验证)
6. [故障排除](#故障排除)
7. [最佳实践](#最佳实践)

## 快速开始

### 前置条件
- GitHub仓库包含完整的前后端代码
- Railway账户
- 基本的Docker和环境变量知识

### 快速部署
1. 在Railway创建两个服务
2. 配置环境变量
3. 部署并验证
4. 运行部署验证脚本

## 服务架构

### 服务划分
```
Repository Root
├── backend/           # 后端服务 (FastAPI)
│   ├── main.py
│   ├── Procfile
│   └── requirements.txt
└── frontend/          # 前端服务 (React + Vite)
    ├── Dockerfile
    ├── package.json
    └── src/
```

### 网络架构
```
[用户] → [前端服务] → [后端服务] → [数据库]
         (Railway)     (Railway)     (SQLite)
```

## 环境变量配置

### 后端环境变量

#### 必需变量
| 变量名 | 描述 | 示例值 | 验证规则 |
|--------|------|--------|----------|
| `SECRET_KEY` | JWT密钥 | `your-secret-key-32-chars-min` | 至少32个字符 |
| `CORS_ORIGINS` | CORS允许源 | `https://frontend.railway.app` | 有效的URL列表 |

#### 可选变量
| 变量名 | 描述 | 默认值 | 示例值 |
|--------|------|--------|--------|
| `DATABASE_URL` | 数据库连接 | `sqlite:///./recipes.db` | `sqlite:///./recipes.db` |
| `RAILWAY_STATIC_URL` | Railway静态URL | 自动设置 | `https://backend.railway.app` |

### 前端环境变量

#### 构建时变量
| 变量名 | 描述 | 示例值 | 必需 |
|--------|------|--------|------|
| `VITE_API_BASE_URL` | 后端API地址 | `https://backend.railway.app` | ✅ |
| `VITE_APP_TITLE` | 应用标题 | `AI食谱推荐` | ❌ |
| `VITE_DEBUG` | 调试模式 | `false` | ❌ |

### 环境变量设置示例

#### Railway后端服务环境变量
```bash
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
CORS_ORIGINS=https://your-frontend.railway.app,http://localhost:5173
DATABASE_URL=sqlite:///./recipes.db
```

#### Railway前端服务环境变量
```bash
VITE_API_BASE_URL=https://your-backend.railway.app
VITE_APP_TITLE=AI食谱推荐系统
VITE_DEBUG=false
```

## 部署步骤

### 1. 创建Railway服务

#### 后端服务
1. 在Railway创建新服务
2. 连接GitHub仓库
3. 设置 Root Directory 为 `/`（根目录）
4. Railway会自动检测到 `Procfile`

#### 前端服务
1. 在Railway创建新服务
2. 连接同一个GitHub仓库
3. 设置 Root Directory 为 `frontend/`
4. Railway会自动检测到 `Dockerfile`

### 2. 配置环境变量

#### 后端配置
```bash
# 在Railway后端服务的Variables页面添加
SECRET_KEY=<生成一个32字符以上的随机字符串>
CORS_ORIGINS=<前端服务的域名>
```

#### 前端配置
```bash
# 在Railway前端服务的Variables页面添加
VITE_API_BASE_URL=<后端服务的域名>
```

### 3. 部署触发
1. 推送代码到GitHub仓库
2. Railway会自动触发部署
3. 在Deployments页面查看部署日志

### 4. 获取服务域名
1. 后端服务：在Domains页面查看分配的域名
2. 前端服务：在Domains页面查看分配的域名
3. 更新环境变量中的URL引用

## 部署验证

### 自动验证脚本

使用提供的部署验证脚本：

```bash
# 基本验证
python scripts/validate_deployment.py \
  --backend-url https://your-backend.railway.app

# 完整验证
python scripts/validate_deployment.py \
  --backend-url https://your-backend.railway.app \
  --frontend-url https://your-frontend.railway.app \
  --verbose

# 使用配置文件
python scripts/validate_deployment.py \
  --config-file scripts/deployment_config.json
```

### 手动验证步骤

#### 后端验证
1. **健康检查**: `GET https://your-backend.railway.app/health`
2. **根端点**: `GET https://your-backend.railway.app/`
3. **API功能**: `POST https://your-backend.railway.app/recommend`
4. **配置状态**: `GET https://your-backend.railway.app/config/status`

#### 前端验证
1. **页面访问**: 打开前端URL
2. **功能测试**: 输入食材，测试推荐功能
3. **用户认证**: 测试注册和登录功能

#### 连接验证
1. **CORS测试**: 前端能否成功调用后端API
2. **错误处理**: 网络错误时的用户体验
3. **配置显示**: 开发模式下的配置状态

## 故障排除

### 常见问题及解决方案

#### 1. 前端无法连接后端

**症状**: 前端页面显示网络错误或API调用失败

**可能原因**:
- CORS配置错误
- API URL配置错误
- 后端服务未启动

**解决步骤**:
```bash
# 1. 检查后端健康状态
curl https://your-backend.railway.app/health

# 2. 验证CORS配置
python validate_config.py --check-cors https://your-backend.railway.app

# 3. 检查环境变量
python validate_config.py --json
```

#### 2. 构建失败

**前端构建失败**:
```bash
# 检查构建时环境变量
docker build --build-arg VITE_API_BASE_URL=https://your-backend.railway.app frontend/

# 验证构建配置
node frontend/scripts/validate-build-config.js
```

**后端启动失败**:
```bash
# 检查依赖
pip install -r requirements.txt

# 验证配置
python validate_config.py
```

#### 3. 数据库问题

**症状**: API返回数据库错误

**解决步骤**:
```bash
# 检查数据库连接
python -c "from models import SessionLocal; db = SessionLocal(); print('DB OK'); db.close()"

# 初始化数据
python tests/init_db.py
```

#### 4. 认证问题

**症状**: 用户注册或登录失败

**解决步骤**:
```bash
# 测试认证逻辑
python tests/test_business_functionality.py

# 检查JWT配置
python -c "from auth import create_access_token; print('JWT OK')"
```

### 调试工具

#### 1. 配置验证
```bash
# 完整配置检查
python validate_config.py

# JSON格式输出
python validate_config.py --json

# 修复常见问题
python validate_config.py --fix
```

#### 2. 部署验证
```bash
# 详细验证报告
python scripts/validate_deployment.py \
  --backend-url https://your-backend.railway.app \
  --verbose \
  --output validation_report.json
```

#### 3. 业务功能测试
```bash
# 测试所有业务逻辑
python tests/test_business_functionality.py
```

## 最佳实践

### 1. 环境变量管理

#### 开发环境
```bash
# .env.local (不要提交到Git)
SECRET_KEY=dev-secret-key-for-local-development
CORS_ORIGINS=http://localhost:5173
VITE_API_BASE_URL=http://localhost:8000
```

#### 生产环境
- 使用Railway的Variables功能
- 确保SECRET_KEY足够复杂
- 定期轮换密钥

### 2. 部署流程

#### 自动化部署
```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway
on:
  push:
    branches: [main]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Deployment
        run: |
          python scripts/validate_deployment.py \
            --backend-url ${{ secrets.BACKEND_URL }} \
            --frontend-url ${{ secrets.FRONTEND_URL }}
```

#### 部署检查清单
- [ ] 环境变量已正确设置
- [ ] 前后端服务都已部署
- [ ] 域名已正确配置
- [ ] CORS设置包含前端域名
- [ ] 部署验证脚本通过
- [ ] 手动功能测试通过

### 3. 监控和维护

#### 健康检查
```bash
# 定期运行健康检查
*/5 * * * * python scripts/validate_deployment.py --backend-url https://your-backend.railway.app
```

#### 日志监控
- 监控Railway部署日志
- 设置错误告警
- 定期检查性能指标

### 4. 安全考虑

#### 环境变量安全
- 不要在代码中硬编码敏感信息
- 使用强随机密钥
- 定期轮换SECRET_KEY

#### CORS安全
- 只允许必要的域名
- 避免使用通配符 `*`
- 定期审查CORS配置

## 附录

### A. 环境变量模板

#### 后端 (.env.example)
```bash
# JWT密钥 - 生产环境必须更改
SECRET_KEY=your-secret-key-here-minimum-32-characters

# CORS允许的源 - 设置为前端域名
CORS_ORIGINS=https://your-frontend.railway.app

# 数据库URL - 可选，默认使用SQLite
DATABASE_URL=sqlite:///./recipes.db

# Railway静态URL - 自动设置
# RAILWAY_STATIC_URL=https://your-backend.railway.app
```

#### 前端 (.env.example)
```bash
# API基础URL - 必须设置为后端域名
VITE_API_BASE_URL=https://your-backend.railway.app

# 应用标题 - 可选
VITE_APP_TITLE=AI食谱推荐系统

# 调试模式 - 生产环境设为false
VITE_DEBUG=false
```

### B. 有用的命令

#### 本地开发
```bash
# 启动后端
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动前端
cd frontend && npm run dev

# 运行测试
python tests/test_business_functionality.py
```

#### 部署相关
```bash
# 验证配置
python validate_config.py

# 验证部署
python scripts/validate_deployment.py --backend-url <URL>

# 生成配置报告
python validate_config.py --json > config_report.json
```

### C. 支持资源

- [Railway文档](https://docs.railway.app/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Vite文档](https://vitejs.dev/)
- [环境变量配置指南](docs/ENV_CONFIGURATION_GUIDE.md)
- [故障排除指南](docs/TROUBLESHOOTING.md)
- [项目GitHub仓库](https://github.com/your-username/your-repo)
