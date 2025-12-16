# 故障排除指南

## 概述

本指南提供了前后端连接优化项目中常见问题的诊断和解决方案。

## 目录

1. [快速诊断](#快速诊断)
2. [连接问题](#连接问题)
3. [配置问题](#配置问题)
4. [部署问题](#部署问题)
5. [性能问题](#性能问题)
6. [安全问题](#安全问题)
7. [诊断工具](#诊断工具)

## 快速诊断

### 问题分类流程图

```
用户报告问题
    ↓
前端能访问吗？
    ├─ 否 → 前端部署问题
    └─ 是 → 前端能调用API吗？
              ├─ 否 → 连接/CORS问题
              └─ 是 → API返回正确吗？
                        ├─ 否 → 后端逻辑问题
                        └─ 是 → 用户体验问题
```

### 快速检查命令

```bash
# 1. 检查服务状态
curl -f https://your-backend.railway.app/health
curl -f https://your-frontend.railway.app/

# 2. 验证配置
python validate_config.py --json

# 3. 运行完整诊断
python scripts/validate_deployment.py \
  --backend-url https://your-backend.railway.app \
  --frontend-url https://your-frontend.railway.app
```

## 连接问题

### 1. 前端无法连接后端

#### 症状
- 前端显示"网络错误"
- 浏览器控制台显示CORS错误
- API调用超时或失败

#### 诊断步骤

**步骤1: 检查后端可访问性**
```bash
# 测试后端健康状态
curl https://your-backend.railway.app/health

# 预期响应
{
  "status": "healthy",
  "service": "AI食谱API",
  "configuration": {...}
}
```

**步骤2: 检查CORS配置**
```bash
# 测试CORS预检请求
curl -H "Origin: https://your-frontend.railway.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://your-backend.railway.app/recommend

# 检查响应头
# 应该包含: Access-Control-Allow-Origin
```

**步骤3: 验证API URL配置**
```bash
# 检查前端配置
curl -s https://your-frontend.railway.app/build-config-report.json | jq .

# 检查API基础URL是否正确
```

#### 解决方案

**CORS配置错误**
```bash
# 在Railway后端服务中设置
CORS_ORIGINS=https://your-frontend.railway.app,http://localhost:5173

# 验证配置
python validate_config.py --check-cors https://your-backend.railway.app
```

**API URL配置错误**
```bash
# 在Railway前端服务中设置
VITE_API_BASE_URL=https://your-backend.railway.app

# 重新部署前端服务
```

**网络连接问题**
```bash
# 检查服务是否运行
railway status

# 查看部署日志
railway logs
```

### 2. 间歇性连接失败

#### 症状
- 有时能连接，有时不能
- 请求超时
- 502/503错误

#### 诊断步骤

**检查服务健康状态**
```bash
# 持续监控
while true; do
  curl -w "%{http_code} %{time_total}s\n" -o /dev/null -s https://your-backend.railway.app/health
  sleep 5
done
```

**检查资源使用**
```bash
# 查看Railway服务指标
railway metrics

# 检查内存和CPU使用情况
```

#### 解决方案

**增加超时时间**
```javascript
// 前端API配置
const api = axios.create({
  timeout: 30000, // 增加到30秒
  retry: 3        // 添加重试机制
});
```

**优化后端性能**
```python
# 添加连接池配置
from sqlalchemy import create_engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30
)
```

## 配置问题

### 1. 环境变量未生效

#### 症状
- 配置验证失败
- 使用了默认值而不是设置的值
- 服务启动错误

#### 诊断步骤

**检查变量设置**
```bash
# Railway控制台
railway variables

# 本地环境
env | grep -E "(SECRET_KEY|CORS|VITE_)"
```

**验证变量格式**
```bash
# 运行配置验证
python validate_config.py --json

# 检查特定变量
python -c "import os; print('SECRET_KEY length:', len(os.getenv('SECRET_KEY', '')))"
```

#### 解决方案

**重新设置环境变量**
```bash
# Railway CLI
railway variables set SECRET_KEY=your-new-secret-key
railway variables set CORS_ORIGINS=https://your-frontend.railway.app

# 重新部署
railway redeploy
```

**修复格式错误**
```bash
# 生成正确的SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 验证CORS格式
python -c "
origins = 'https://frontend.railway.app,http://localhost:5173'
for origin in origins.split(','):
    print(f'Valid: {origin}' if origin.startswith(('http://', 'https://')) or origin == '*' else f'Invalid: {origin}')
"
```

### 2. 构建时变量问题

#### 症状
- 前端构建失败
- API URL未正确注入
- 构建配置验证失败

#### 诊断步骤

**检查构建日志**
```bash
# Railway部署日志
railway logs --deployment <deployment-id>

# 本地构建测试
cd frontend && npm run build
```

**验证构建时变量**
```bash
# 检查Dockerfile ARG
docker build --build-arg VITE_API_BASE_URL=https://test.com frontend/ --no-cache

# 运行构建验证
node frontend/scripts/validate-build-config.js
```

#### 解决方案

**修复Dockerfile配置**
```dockerfile
# 确保ARG在ENV之前
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# 验证变量存在
RUN if [ -z "$VITE_API_BASE_URL" ]; then echo "Error: VITE_API_BASE_URL not set"; exit 1; fi
```

**更新Railway构建配置**
```bash
# 在Railway前端服务Variables中设置
VITE_API_BASE_URL=https://your-backend.railway.app
VITE_DEBUG=false
```

## 部署问题

### 1. 服务启动失败

#### 症状
- 部署显示失败
- 服务无法访问
- 健康检查失败

#### 诊断步骤

**检查部署日志**
```bash
# Railway部署日志
railway logs --deployment latest

# 查找错误信息
railway logs | grep -i error
```

**检查服务配置**
```bash
# 验证Procfile
cat Procfile
# 应该是: web: uvicorn main:app --host 0.0.0.0 --port $PORT

# 检查依赖
pip check
```

#### 解决方案

**修复依赖问题**
```bash
# 更新requirements.txt
pip freeze > requirements.txt

# 检查版本冲突
pip-check
```

**修复启动配置**
```bash
# 确保Procfile正确
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 验证应用可以启动
python -c "from main import app; print('App imports successfully')"
```

### 2. 部署成功但功能异常

#### 症状
- 服务可访问但API返回错误
- 数据库连接失败
- 认证功能不工作

#### 诊断步骤

**运行业务功能测试**
```bash
# 测试核心功能
python tests/test_business_functionality.py

# 检查数据库状态
python -c "from models import SessionLocal; db = SessionLocal(); print('Recipes:', db.query(Recipe).count()); db.close()"
```

**检查API端点**
```bash
# 测试各个端点
curl https://your-backend.railway.app/
curl https://your-backend.railway.app/health
curl -X POST https://your-backend.railway.app/recommend -H "Content-Type: application/json" -d '{"ingredients":["番茄","鸡蛋"]}'
```

#### 解决方案

**初始化数据库**
```bash
# 运行数据初始化
python tests/init_db.py

# 验证数据
python tests/check_db.py
```

**修复配置问题**
```bash
# 重新验证所有配置
python validate_config.py --fix

# 重新部署
railway redeploy
```

## 性能问题

### 1. 响应时间慢

#### 症状
- API调用超时
- 页面加载缓慢
- 用户体验差

#### 诊断步骤

**测量响应时间**
```bash
# 测试API响应时间
curl -w "Time: %{time_total}s\n" -o /dev/null -s https://your-backend.railway.app/health

# 测试不同端点
for endpoint in "/" "/health" "/recommend"; do
  echo "Testing $endpoint"
  curl -w "Time: %{time_total}s\n" -o /dev/null -s "https://your-backend.railway.app$endpoint"
done
```

**分析性能瓶颈**
```bash
# 检查数据库查询
python -c "
import time
from models import SessionLocal
from recipe_service import recommend_recipes

start = time.time()
recipes = recommend_recipes(['番茄', '鸡蛋'])
print(f'Query time: {time.time() - start:.2f}s')
print(f'Results: {len(recipes)}')
"
```

#### 解决方案

**优化数据库查询**
```python
# 添加数据库索引
from sqlalchemy import Index
Index('idx_recipe_ingredients', Recipe.ingredients)

# 优化查询逻辑
def recommend_recipes_optimized(ingredients, tags=None):
    # 使用更高效的查询
    pass
```

**添加缓存**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_recommend_recipes(ingredients_tuple, tags_tuple=None):
    return recommend_recipes(list(ingredients_tuple), list(tags_tuple) if tags_tuple else None)
```

### 2. 内存使用过高

#### 症状
- 服务重启频繁
- 内存不足错误
- 性能下降

#### 诊断步骤

**监控内存使用**
```bash
# 检查Railway指标
railway metrics

# 本地内存分析
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

#### 解决方案

**优化内存使用**
```python
# 使用生成器而不是列表
def get_recipes_generator():
    for recipe in db.query(Recipe).yield_per(100):
        yield recipe

# 及时关闭数据库连接
try:
    db = SessionLocal()
    # 操作
finally:
    db.close()
```

## 安全问题

### 1. 认证失败

#### 症状
- 用户无法登录
- JWT令牌验证失败
- 权限错误

#### 诊断步骤

**测试认证流程**
```bash
# 测试用户注册
curl -X POST https://your-backend.railway.app/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'

# 测试用户登录
curl -X POST https://your-backend.railway.app/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

**验证JWT配置**
```bash
# 检查SECRET_KEY
python -c "
import os
key = os.getenv('SECRET_KEY')
print(f'SECRET_KEY set: {bool(key)}')
print(f'Length: {len(key) if key else 0}')
"
```

#### 解决方案

**重新生成SECRET_KEY**
```bash
# 生成新密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 在Railway中更新
railway variables set SECRET_KEY=<new-key>
railway redeploy
```

**修复认证逻辑**
```python
# 检查密码哈希
from auth import verify_password, get_password_hash
password = "test123"
hashed = get_password_hash(password)
print(f"Hash verification: {verify_password(password, hashed)}")
```

### 2. CORS安全问题

#### 症状
- 跨域请求被阻止
- 安全警告
- 未授权访问

#### 诊断步骤

**检查CORS配置**
```bash
# 验证CORS设置
python validate_config.py --check-cors https://your-backend.railway.app

# 测试不同源的请求
curl -H "Origin: https://malicious-site.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://your-backend.railway.app/recommend
```

#### 解决方案

**加强CORS安全**
```bash
# 只允许特定域名
CORS_ORIGINS=https://your-frontend.railway.app

# 避免使用通配符
# 错误: CORS_ORIGINS=*
# 正确: CORS_ORIGINS=https://specific-domain.com
```

## 诊断工具

### 1. 自动化诊断脚本

#### 完整系统诊断
```bash
#!/bin/bash
# diagnose.sh - 完整系统诊断

echo "=== 系统诊断开始 ==="

echo "1. 检查配置..."
python validate_config.py --json > config_report.json

echo "2. 测试部署..."
python scripts/validate_deployment.py \
  --backend-url https://your-backend.railway.app \
  --frontend-url https://your-frontend.railway.app \
  --output deployment_report.json

echo "3. 测试业务功能..."
python tests/test_business_functionality.py

echo "4. 检查性能..."
curl -w "Backend response time: %{time_total}s\n" -o /dev/null -s https://your-backend.railway.app/health
curl -w "Frontend response time: %{time_total}s\n" -o /dev/null -s https://your-frontend.railway.app/

echo "=== 诊断完成 ==="
```

#### 快速健康检查
```bash
#!/bin/bash
# health_check.sh - 快速健康检查

BACKEND_URL="https://your-backend.railway.app"
FRONTEND_URL="https://your-frontend.railway.app"

echo "Backend Health:"
curl -f $BACKEND_URL/health && echo " ✅" || echo " ❌"

echo "Frontend Access:"
curl -f $FRONTEND_URL && echo " ✅" || echo " ❌"

echo "API Functionality:"
curl -f -X POST $BACKEND_URL/recommend \
  -H "Content-Type: application/json" \
  -d '{"ingredients":["番茄","鸡蛋"]}' && echo " ✅" || echo " ❌"
```

### 2. 监控和告警

#### 持续监控脚本
```bash
#!/bin/bash
# monitor.sh - 持续监控

while true; do
  timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  
  # 检查后端
  if curl -f -s https://your-backend.railway.app/health > /dev/null; then
    echo "$timestamp Backend: OK"
  else
    echo "$timestamp Backend: FAIL" | tee -a alerts.log
  fi
  
  # 检查前端
  if curl -f -s https://your-frontend.railway.app > /dev/null; then
    echo "$timestamp Frontend: OK"
  else
    echo "$timestamp Frontend: FAIL" | tee -a alerts.log
  fi
  
  sleep 60
done
```

### 3. 日志分析工具

#### 错误日志分析
```bash
# 分析Railway日志中的错误
railway logs | grep -i error | tail -20

# 统计错误类型
railway logs | grep -i error | awk '{print $NF}' | sort | uniq -c | sort -nr

# 查找特定时间段的日志
railway logs --since 1h | grep -i error
```

## 联系支持

如果以上解决方案都无法解决问题，请收集以下信息并联系技术支持：

### 必需信息
1. **错误描述**: 详细描述问题症状
2. **复现步骤**: 如何重现问题
3. **环境信息**: 开发/生产环境
4. **时间信息**: 问题开始时间
5. **诊断报告**: 运行诊断脚本的输出

### 收集诊断信息
```bash
# 生成完整诊断报告
./diagnose.sh > diagnostic_report.txt 2>&1

# 收集配置信息
python validate_config.py --json > config_status.json

# 收集部署信息
python scripts/validate_deployment.py \
  --backend-url https://your-backend.railway.app \
  --verbose \
  --output deployment_status.json
```

### 支持渠道
- GitHub Issues: [项目仓库](https://github.com/your-repo)
- 文档: [部署指南](../DEPLOYMENT.md)
- 配置指南: [环境变量配置](ENV_CONFIGURATION_GUIDE.md)