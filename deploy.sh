#!/bin/bash

echo "开始部署..."

# 进入前端目录
cd /home/ubuntu/Cei-Noise/frontend

# 重新构建
echo "构建前端..."
npm run build

# 重启后端（如果有后端代码修改）
echo "重启后端服务..."
sudo systemctl restart drone-api

# 重启 Nginx（通常不需要，除非改了配置）
# sudo systemctl restart nginx

echo "部署完成！"
