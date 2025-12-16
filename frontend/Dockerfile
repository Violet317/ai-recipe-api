# 使用官方Node.js镜像作为基础镜像
FROM node:18-alpine AS build

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制项目文件
COPY . .

# 【关键修改】接收并设置构建时环境变量
# 这些ARG必须添加在 RUN npm run build 之前
ARG VITE_API_BASE_URL
ARG VITE_APP_TITLE="AI食谱推荐"
ARG VITE_DEBUG="false"

# 设置环境变量供Vite构建时使用
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_TITLE=$VITE_APP_TITLE
ENV VITE_DEBUG=$VITE_DEBUG
ENV VITE_BUILD_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 验证必需的构建时变量
RUN if [ -z "$VITE_API_BASE_URL" ]; then \
      echo "错误: VITE_API_BASE_URL 构建参数是必需的"; \
      echo "请使用: docker build --build-arg VITE_API_BASE_URL=<your-api-url> ."; \
      exit 1; \
    fi

# 打印构建配置信息（用于调试）
RUN echo "构建配置信息:" && \
    echo "  API_BASE_URL: $VITE_API_BASE_URL" && \
    echo "  APP_TITLE: $VITE_APP_TITLE" && \
    echo "  DEBUG: $VITE_DEBUG" && \
    echo "  BUILD_TIME: $VITE_BUILD_TIME"

# 构建生产版本（此时Vite能读取到环境变量）
RUN npm run build

# 使用Nginx作为服务器
FROM nginx:alpine

# 复制构建结果到Nginx的html目录
COPY --from=build /app/dist /usr/share/nginx/html

# 复制Nginx配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露80端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
