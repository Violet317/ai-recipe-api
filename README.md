# AI食谱推荐系统

一个基于FastAPI和React的全栈AI食谱推荐应用，支持根据用户输入的食材智能推荐相关食谱。

## 🚀 快速开始

### 本地开发

1. **后端启动**:
   ```bash
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **前端启动**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### 部署到Railway

详细部署指南请参考: [DEPLOYMENT.md](DEPLOYMENT.md)

## 📚 文档

- [📖 部署指南](DEPLOYMENT.md) - 完整的Railway部署指南
- [📁 文档目录](docs/README.md) - 所有项目文档的索引
- [⚙️ 环境配置](docs/ENV_CONFIGURATION_GUIDE.md) - 环境变量配置详解
- [🔧 故障排除](docs/TROUBLESHOOTING.md) - 常见问题解决方案
- [🧪 测试报告](docs/testing/) - 测试状态和报告

## 🏗️ 项目结构

```
├── backend/                 # 后端API (FastAPI)
│   ├── main.py             # 主应用文件
│   ├── models.py           # 数据模型
│   ├── auth.py             # 认证逻辑
│   ├── env_manager.py      # 环境变量管理
│   └── validate_config.py  # 配置验证工具
├── frontend/               # 前端应用 (React + Vite)
│   ├── src/               # 源代码
│   ├── Dockerfile         # Docker配置
│   └── scripts/           # 构建脚本
├── docs/                  # 项目文档
│   ├── testing/           # 测试相关文档
│   └── *.md              # 各种指南和说明
├── tests/                 # 测试文件
├── scripts/               # 部署和验证脚本
└── data/                  # 数据文件
```

## ✨ 功能特性

- 🍳 **智能食谱推荐**: 根据输入食材推荐相关食谱
- 🏷️ **标签过滤**: 支持按标签筛选食谱（如低脂、快手等）
- 👤 **用户认证**: 完整的用户注册和登录系统
- 📊 **匹配度显示**: 显示食谱与输入食材的匹配程度
- 🔧 **环境管理**: 完善的环境变量管理和验证系统
- 🚀 **一键部署**: 支持Railway平台一键部署

## 🧪 测试状态

- ✅ 业务功能测试: 6/6 通过
- ✅ 属性测试: 6/6 通过
- ✅ 配置验证: 正常工作
- ✅ 部署验证: 功能完整

详细测试报告: [测试文档](docs/testing/)

## 🛠️ 技术栈

### 后端
- **FastAPI** - 现代Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **SQLite** - 轻量级数据库
- **JWT** - 用户认证

### 前端
- **React 18** - 用户界面框架
- **TypeScript** - 类型安全的JavaScript
- **Vite** - 快速构建工具
- **Axios** - HTTP客户端

### 部署
- **Railway** - 云平台部署
- **Docker** - 容器化部署
- **Nginx** - 前端服务器

## 📝 开发指南

### 环境变量配置

参考 [环境变量配置指南](docs/ENV_CONFIGURATION_GUIDE.md) 了解详细配置方法。

### 添加新功能

1. 后端API: 在 `main.py` 中添加新的路由
2. 前端组件: 在 `frontend/src/components/` 中创建新组件
3. 数据模型: 在 `models.py` 中定义新的数据结构
4. 测试: 在 `tests/` 中添加相应测试

### 部署流程

1. 配置环境变量
2. 推送代码到GitHub
3. 在Railway中创建服务
4. 运行部署验证脚本

详细步骤请参考 [部署指南](DEPLOYMENT.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License