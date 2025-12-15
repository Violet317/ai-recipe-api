# 部署指南（Railway，前后端同仓）

## 服务划分
- 后端服务：根目录 `/`
- 前端服务：子目录 `frontend/`

## 环境变量
- 后端
  - `SECRET_KEY`：JWT密钥（必须）
  - `CORS_ORIGINS`：允许的前端来源，多个用逗号分隔，如 `https://your-frontend.up.railway.app`
- 前端
  - `VITE_API_BASE_URL`：后端公开域名，如 `https://your-backend.up.railway.app`

## 后端
- 启动：由 `Procfile` 自动识别
- 端口：`$PORT`（Railway自动注入）
- 数据：启动事件自动按 `data/recipes.json` 导入新增菜谱（按ID去重）

## 前端
- 构建：使用 `frontend/Dockerfile`（Node构建 + Nginx托管）
- 预览域名：在服务的 Domains 页面查看

## Monorepo配置步骤
1. 在 Railway 创建两个服务，均选择当前GitHub仓库
2. 后端服务 Settings → Root Directory 设为 `/`
3. 前端服务 Settings → Root Directory 设为 `frontend/`
4. 分别在各自服务设置环境变量
5. 触发部署并在 Deployments 页查看日志

## 验证
- 后端健康：`GET /` 返回 `{"message":"AI食谱API服务正常"}`
- 推荐接口：`POST /recommend`，示例体 `{"ingredients":["番茄","鸡蛋"]}`
- 前端：打开前端域名，输入中文或英文逗号分隔的食材均可

## 常见问题
- 构建失败（找不到Dockerfile）：确认前端服务的 Root Directory 为 `frontend/`
- 端口错误：后端必须使用 `$PORT`（见 `Procfile`）
- 跨域失败：设置 `CORS_ORIGINS` 为前端域名；前端的 `VITE_API_BASE_URL` 指向后端域名
