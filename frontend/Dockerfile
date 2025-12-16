# Railway前端部署专用Dockerfile
# 使用官方Node.js镜像作为基础镜像
FROM node:18-alpine AS build

# 设置工作目录
WORKDIR /app

# 复制前端项目文件
COPY package*.json ./
RUN npm ci

# 复制前端源代码
COPY . ./

# 接收构建时环境变量
ARG VITE_API_BASE_URL="https://placeholder-backend.railway.app"
ARG VITE_APP_TITLE="AI食谱推荐"
ARG VITE_DEBUG="false"

# 设置环境变量供Vite构建时使用
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_TITLE=$VITE_APP_TITLE
ENV VITE_DEBUG=$VITE_DEBUG

# 打印构建配置信息（用于调试）
RUN echo "构建配置信息:" && \
    echo "  API_BASE_URL: $VITE_API_BASE_URL" && \
    echo "  APP_TITLE: $VITE_APP_TITLE" && \
    echo "  DEBUG: $VITE_DEBUG"

# 构建生产版本
RUN npm run build

# 使用Nginx作为服务器
FROM nginx:alpine

# 复制构建结果到Nginx的html目录
COPY --from=build /app/dist /usr/share/nginx/html

# 复制Nginx配置文件
COPY --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf

# 暴露80端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]