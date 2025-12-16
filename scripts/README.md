# 部署验证脚本

这个目录包含用于验证前后端应用部署的自动化脚本。

## 文件说明

- `validate_deployment.py` - 主要的部署验证脚本（Python）
- `validate_deployment.sh` - Shell包装脚本，简化使用
- `deployment_config.example.json` - 配置文件示例
- `README.md` - 本文档

## 快速开始

### 1. 基本用法

```bash
# 验证后端部署
python scripts/validate_deployment.py --backend-url https://your-backend.railway.app

# 验证前后端部署
python scripts/validate_deployment.py \
  --backend-url https://your-backend.railway.app \
  --frontend-url https://your-frontend.railway.app

# 使用配置文件
python scripts/validate_deployment.py --config-file deployment_config.json
```

### 2. 使用Shell包装脚本

```bash
# 给脚本添加执行权限（Linux/Mac）
chmod +x scripts/validate_deployment.sh

# 运行验证
./scripts/validate_deployment.sh --backend-url https://your-backend.railway.app
```

### 3. 配置文件方式

1. 复制配置文件模板：
```bash
cp scripts/deployment_config.example.json scripts/deployment_config.json
```

2. 编辑配置文件，设置你的URL：
```json
{
  "backend_url": "https://your-backend-service.railway.app",
  "frontend_url": "https://your-frontend-service.railway.app",
  "timeout": 30
}
```

3. 运行验证：
```bash
python scripts/validate_deployment.py --config-file scripts/deployment_config.json
```

## 验证项目

脚本会自动测试以下项目：

### 后端验证
- ✅ **健康检查** - 测试 `/health` 端点
- ✅ **根端点** - 测试 `/` 端点响应
- ✅ **食谱推荐API** - 测试 `/recommend` 端点功能
- ✅ **用户注册API** - 测试 `/register` 端点
- ✅ **用户登录API** - 测试 `/login` 端点
- ✅ **CORS配置** - 验证跨域请求配置
- ✅ **配置端点** - 测试 `/config/status` 等配置相关端点

### 前端验证（可选）
- ✅ **前端可访问性** - 测试前端服务是否可访问
- ✅ **HTML内容** - 验证返回的是HTML内容

## 命令行选项

```
--backend-url URL      后端服务URL（必需）
--frontend-url URL     前端服务URL（可选）
--timeout SECONDS      请求超时时间（默认30秒）
--verbose, -v          详细输出模式
--output FILE, -o      保存报告到JSON文件
--config-file FILE     从配置文件加载设置
--help, -h             显示帮助信息
```

## 输出示例

### 成功的验证
```
🚀 Starting Deployment Validation
============================================================
Backend URL: https://your-backend.railway.app
Frontend URL: https://your-frontend.railway.app
============================================================
🔍 Running: Backend Health Check
  ✅ Backend health check passed (245ms)
🔍 Running: Backend Root Endpoint
  ✅ Root endpoint working correctly (123ms)
🔍 Running: Recipe Recommendation API
  ✅ Recipe API working, returned 3 recipes (456ms)
🔍 Running: User Registration API
  ✅ User registration API working (234ms)
🔍 Running: User Login API
  ✅ User login API working (345ms)
🔍 Running: CORS Configuration
  ✅ CORS headers present (89ms)
🔍 Running: Configuration Endpoints
  ✅ Configuration endpoints working (156ms)
🔍 Running: Frontend Accessibility
  ✅ Frontend accessible and serving HTML (234ms)

============================================================
📋 DEPLOYMENT VALIDATION REPORT
============================================================
Timestamp: 2025-01-16 10:30:45 UTC
Backend URL: https://your-backend.railway.app
Frontend URL: https://your-frontend.railway.app
Overall Status: ✅ SUCCESS
Tests: 8/8 passed

💡 Recommendations:
--------------------------------------------
  🎉 所有测试都通过了！部署看起来很健康。

============================================================
```

### 失败的验证
```
🚀 Starting Deployment Validation
============================================================
Backend URL: https://broken-backend.railway.app
============================================================
🔍 Running: Backend Health Check
  ❌ Health check request failed: Connection timeout (30000ms)
🔍 Running: Backend Root Endpoint
  ❌ Root endpoint request failed: Connection timeout (30000ms)

============================================================
📋 DEPLOYMENT VALIDATION REPORT
============================================================
Timestamp: 2025-01-16 10:35:22 UTC
Backend URL: https://broken-backend.railway.app
Overall Status: ❌ FAILURE
Tests: 0/8 passed

💡 Recommendations:
--------------------------------------------
  ❌ 后端健康检查失败 - 检查服务是否正在运行
  ❌ 后端根端点失败 - 检查API服务配置
  ⚠️  多个测试失败，建议检查整体部署配置
  💡 查看详细的测试结果以获取更多诊断信息

============================================================
```

## 集成到CI/CD

### GitHub Actions示例

```yaml
name: Deployment Validation
on:
  deployment_status:
    types: [success]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install requests
      - name: Validate Deployment
        run: |
          python scripts/validate_deployment.py \
            --backend-url ${{ secrets.BACKEND_URL }} \
            --frontend-url ${{ secrets.FRONTEND_URL }} \
            --output validation_report.json
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: validation-report
          path: validation_report.json
```

### Railway部署后钩子

在Railway项目中，你可以在部署完成后自动运行验证：

```bash
# 在Railway的部署脚本中添加
python scripts/validate_deployment.py \
  --backend-url $RAILWAY_STATIC_URL \
  --timeout 60
```

## 故障排除

### 常见问题

1. **连接超时**
   - 检查URL是否正确
   - 增加超时时间：`--timeout 60`
   - 确认服务已完全启动

2. **CORS错误**
   - 检查后端的CORS_ORIGINS环境变量
   - 确认前端URL在CORS允许列表中

3. **API测试失败**
   - 检查数据库连接
   - 验证环境变量配置
   - 查看后端日志

4. **前端访问失败**
   - 确认前端服务已部署
   - 检查前端构建是否成功
   - 验证Nginx配置

### 调试模式

使用 `--verbose` 选项获取详细的调试信息：

```bash
python scripts/validate_deployment.py \
  --backend-url https://your-backend.railway.app \
  --verbose \
  --output debug_report.json
```

## 扩展脚本

你可以通过修改 `validate_deployment.py` 来添加自定义测试：

```python
def test_custom_endpoint(self) -> tuple[bool, str, Dict[str, Any]]:
    """自定义端点测试"""
    try:
        response = self.session.get(f"{self.backend_url}/custom")
        if response.status_code == 200:
            return True, "Custom endpoint working", {"status": response.status_code}
        else:
            return False, f"Custom endpoint failed: {response.status_code}", {}
    except Exception as e:
        return False, f"Custom endpoint error: {str(e)}", {"error": str(e)}

# 在run_all_tests方法中添加测试
tests = [
    # ... 现有测试 ...
    ("Custom Endpoint", self.test_custom_endpoint),
]
```

## 支持

如果遇到问题或需要帮助，请：

1. 检查本文档的故障排除部分
2. 使用 `--verbose` 模式获取详细信息
3. 查看生成的JSON报告文件
4. 检查后端和前端的部署日志