# 环境变量管理和验证系统

本文档描述了为前后端连接优化项目实现的环境变量管理和验证系统。

## 概述

环境变量管理系统提供了以下功能：
- 自动验证所有必需和可选的环境变量
- 提供详细的配置状态报告
- 支持环境变量格式验证和错误处理
- 集成到主应用中，提供健康检查和配置端点
- 支持Railway等云平台的自动配置

## 文件结构

```
├── env_manager.py              # 后端环境变量管理器
├── frontend/src/envManager.ts  # 前端环境变量管理器
├── frontend/src/components/ConfigStatus.tsx  # 配置状态显示组件
├── validate_config.py          # 独立配置验证脚本
├── test_env_manager.py         # 环境管理器单元测试
├── test_integration.py         # 集成测试
└── ENV_MANAGEMENT_README.md    # 本文档
```

## 后端环境变量管理

### 必需的环境变量

| 变量名 | 描述 | 验证规则 | 示例 |
|--------|------|----------|------|
| `SECRET_KEY` | JWT密钥 | 至少32个字符 | `your-secret-key-here-32-chars-min` |
| `CORS_ORIGINS` | CORS允许的源 | 逗号分隔的有效URL列表 | `http://localhost:5173,https://myapp.com` |

### 可选的环境变量

| 变量名 | 描述 | 默认值 | 示例 |
|--------|------|--------|------|
| `DATABASE_URL` | 数据库连接URL | `sqlite:///./recipes.db` | `postgresql://user:pass@host:port/db` |
| `RAILWAY_STATIC_URL` | Railway静态URL | 无 | `https://myapp.railway.app` |

### 使用方法

```python
from env_manager import env_manager, validate_environment

# 验证环境变量
report = validate_environment()
print(f"配置状态: {report.overall_status.value}")

# 获取配置值
api_url = env_manager.get_api_base_url()
cors_origins = env_manager.get_cors_origins()

# 设置默认值
env_manager.setup_environment_defaults()

# 打印配置状态
env_manager.print_config_status()
```

## 前端环境变量管理

### 必需的环境变量

| 变量名 | 描述 | 验证规则 | 示例 |
|--------|------|----------|------|
| `VITE_API_BASE_URL` | API基础URL | 有效的HTTP/HTTPS URL | `http://localhost:8000` |

### 可选的环境变量

| 变量名 | 描述 | 默认值 | 示例 |
|--------|------|--------|------|
| `VITE_APP_TITLE` | 应用标题 | `AI食谱推荐` | `My Recipe App` |
| `VITE_DEBUG` | 调试模式 | `false` | `true` |

### 使用方法

```typescript
import { frontendEnvManager, getApiBaseUrl } from './envManager';

// 验证环境变量
const report = frontendEnvManager.validateEnvironmentVariables();
console.log(`配置状态: ${report.overallStatus}`);

// 获取API基础URL
const apiUrl = getApiBaseUrl();

// 获取环境配置
const config = frontendEnvManager.getEnvironmentConfig();

// 检查配置是否就绪
const isReady = frontendEnvManager.isConfigurationReady();
```

## API端点

主应用提供了以下配置相关的API端点：

### GET /health
健康检查端点，返回服务状态和基本配置信息。

```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z",
  "service": "AI食谱API",
  "version": "1.0.0",
  "configuration": {
    "status": "valid",
    "summary": "所有配置项验证通过"
  },
  "api_base_url": "http://localhost:8000",
  "cors_origins": ["http://localhost:5173"]
}
```

### GET /config/status
获取详细的配置状态信息。

```json
{
  "items": [
    {
      "name": "SECRET_KEY",
      "value": "***",
      "status": "valid",
      "message": "✓ JWT密钥配置正确",
      "required": true
    }
  ],
  "overall_status": "valid",
  "summary": "所有配置项验证通过"
}
```

### GET /config/validate
验证配置并返回详细报告和建议。

```json
{
  "valid": true,
  "report": { /* 详细配置报告 */ },
  "recommendations": ["配置看起来不错！"]
}
```

## 命令行工具

### validate_config.py

独立的配置验证脚本，支持多种操作模式：

```bash
# 基本验证
python validate_config.py

# JSON格式输出
python validate_config.py --json

# 尝试修复常见问题
python validate_config.py --fix

# 检查CORS配置
python validate_config.py --check-cors http://localhost:8000

# 静默模式
python validate_config.py --quiet
```

## 配置状态

系统定义了四种配置状态：

- **VALID** ✅: 配置正确且完整
- **WARNING** ⚠️: 配置基本正确但有警告项
- **INVALID** ❌: 配置有错误，需要修复
- **MISSING** 🔍: 缺少必需的配置项

## Railway部署配置

在Railway平台部署时，系统会自动：

1. 检测Railway环境变量
2. 使用`RAILWAY_STATIC_URL`作为API基础URL
3. 自动配置CORS源以匹配前端域名
4. 提供Railway特定的配置建议

### Railway环境变量设置

在Railway项目设置中添加以下环境变量：

```bash
SECRET_KEY=your-secret-key-here-32-chars-minimum
CORS_ORIGINS=https://your-frontend.railway.app
RAILWAY_STATIC_URL=https://your-backend.railway.app
```

## 前端配置组件

`ConfigStatus`组件提供了可视化的配置状态显示：

```tsx
import ConfigStatus from './components/ConfigStatus';

// 基本使用
<ConfigStatus />

// 显示详细信息
<ConfigStatus showDetails={true} />

// 监听配置就绪状态
<ConfigStatus onConfigReady={(isReady) => console.log('Config ready:', isReady)} />
```

## 测试

### 运行单元测试

```bash
# 后端环境管理器测试
python test_env_manager.py

# 集成测试
python test_integration.py

# 手动测试
python test_env_manager.py --manual
python test_integration.py --manual
```

### 前端测试

```bash
cd frontend
npm run build  # 验证TypeScript编译
npm run dev    # 开发模式下会自动显示配置状态
```

## 故障排除

### 常见问题

1. **SECRET_KEY太短**
   ```bash
   python validate_config.py --fix
   # 会生成一个安全的密钥建议
   ```

2. **CORS配置错误**
   ```bash
   python validate_config.py --check-cors http://your-backend-url
   # 检查CORS配置是否正确
   ```

3. **前端无法连接后端**
   - 检查`VITE_API_BASE_URL`是否正确
   - 验证CORS配置是否包含前端域名
   - 使用配置状态组件查看详细信息

### 调试模式

在开发环境中：
- 前端会自动显示配置状态
- 后端启动时会打印配置警告
- 可以使用配置状态组件查看详细信息

## 最佳实践

1. **环境变量安全**
   - 使用强密钥（至少32个字符）
   - 不要在代码中硬编码敏感信息
   - 在生产环境中使用环境变量管理服务

2. **配置验证**
   - 在应用启动时验证配置
   - 定期检查配置状态
   - 使用健康检查端点监控配置

3. **部署流程**
   - 部署前运行配置验证
   - 使用`validate_config.py --json`进行自动化检查
   - 在CI/CD流程中集成配置验证

## 扩展

要添加新的环境变量：

1. 在`env_manager.py`中更新`REQUIRED_VARS`或`OPTIONAL_VARS`
2. 添加相应的验证函数
3. 更新文档和测试
4. 如果是前端变量，同时更新`envManager.ts`

示例：

```python
# 在env_manager.py中添加新变量
REQUIRED_VARS = {
    # ... 现有变量
    "NEW_VARIABLE": {
        "description": "新变量描述",
        "validator": lambda x: len(x) > 0,
        "error_msg": "NEW_VARIABLE不能为空"
    }
}
```