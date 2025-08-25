#!/bin/bash

# 非洲彩票平台 - 开发环境启动脚本

echo "🚀 启动开发环境..."

# 启动所有服务
docker-compose -f docker/docker-compose.yml up -d

echo "✅ 开发环境启动完成！"
echo ""
echo "🌐 服务访问地址："
echo "- 前端应用: http://localhost:3000"
echo "- 管理后台: http://localhost:3001"
echo "- 后端API: http://localhost:8000"
echo "- API文档: http://localhost:8000/api/docs/"
echo ""
echo "📊 数据库连接："
echo "- PostgreSQL主库: localhost:5432"
echo "- PostgreSQL从库: localhost:5433"
echo "- Redis: localhost:6379"
echo ""
echo "🔧 常用命令："
echo "- 查看日志: docker-compose -f docker/docker-compose.yml logs -f"
echo "- 停止服务: docker-compose -f docker/docker-compose.yml down"
echo "- 重启服务: docker-compose -f docker/docker-compose.yml restart"