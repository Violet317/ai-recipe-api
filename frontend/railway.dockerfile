# Railway专用Dockerfile - 优化的构建时环境变量处理
FROM node:18-alpine AS build

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制项目文件
COPY . .

# 接收Railway环境变量作为构建参数
# Railway会自动提供这些变量
ARG VITE_API_BASE_URL
ARG VITE_APP_TITLE="AI食谱推荐"
ARG VITE_DEBUG="false"

# 如果没有提供API URL，尝试从Railway变量构建
# Railway提供RAILWAY_STATIC_URL用于当前服务的URL
ARG RAILWAY_STATIC_URL
RUN if [ -z "$VITE_API_BASE_URL" ] && [ -n "$RAILWAY_STATIC_URL" ]; then \
      # 尝试从前端URL推断后端URL
      BACKEND_URL=$(echo "$RAILWAY_STATIC_URL" | sed 's/frontend/backend/g'); \
      export VITE_API_BASE_URL="$BACKEND_URL"; \
      echo "自动推断的后端URL: $VITE_API_BASE_URL"; \
    fi

# 设置环境变量供Vite构建时使用
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_TITLE=$VITE_APP_TITLE
ENV VITE_DEBUG=$VITE_DEBUG
ENV VITE_BUILD_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Railway特定的环境变量
ENV RAILWAY_ENVIRONMENT=production
ENV NODE_ENV=production

# 验证构建配置
RUN node scripts/validate-build-config.js

# 构建生产版本
RUN npm run build:no-validation

# 使用Nginx作为服务器
FROM nginx:alpine

# 复制构建结果到Nginx的html目录
COPY --from=build /app/dist /usr/share/nginx/html

# 复制Nginx配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 复制构建报告（用于调试）
COPY --from=build /app/dist/build-config-report.json /usr/share/nginx/html/build-config-report.json

# 暴露80端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]