#!/bin/bash

# 非洲彩票平台 - 项目初始化脚本

echo "🚀 开始初始化非洲彩票平台项目..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建Docker网络
echo "📡 创建Docker网络..."
docker network create lottery-network 2>/dev/null || echo "网络已存在"

# 启动数据库服务
echo "🗄️ 启动数据库服务..."
cd database
docker-compose up -d
cd ..

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 10

# 安装后端依赖
echo "🐍 安装后端Python依赖..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# 安装前端依赖
echo "⚛️ 安装前端Node.js依赖..."
cd frontend
npm install
cd ..

# 安装管理后台依赖
echo "🔧 安装管理后台依赖..."
cd admin
npm install
cd ..

# 运行数据库迁移
echo "📊 运行数据库迁移..."
cd backend
source venv/bin/activate
python manage.py migrate
cd ..

echo "✅ 项目初始化完成！"
echo ""
echo "🎯 接下来的步骤："
echo "1. 启动开发服务器: ./scripts/dev.sh"
echo "2. 访问前端: http://localhost:3000"
echo "3. 访问管理后台: http://localhost:3001"
echo "4. 访问API文档: http://localhost:8000/api/docs/"