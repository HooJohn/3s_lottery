# 非洲在线彩票博彩平台

## 项目结构

```
africa-lottery-platform/
├── backend/                 # Django后端API服务
│   ├── lottery_platform/    # Django项目主目录
│   ├── apps/                # 应用模块
│   ├── config/              # 配置文件
│   ├── requirements.txt     # Python依赖
│   └── manage.py           # Django管理脚本
├── frontend/               # React前端应用
│   ├── src/                # 源代码
│   ├── public/             # 静态资源
│   ├── package.json        # Node.js依赖
│   └── vite.config.ts      # Vite配置
├── admin/                  # 管理后台
│   ├── src/                # 管理后台源码
│   └── package.json        # 依赖配置
├── database/               # 数据库相关
│   ├── migrations/         # 数据库迁移文件
│   ├── seeds/              # 初始数据
│   └── docker-compose.yml  # 数据库容器配置
├── docker/                 # Docker配置
│   ├── backend/            # 后端Docker配置
│   ├── frontend/           # 前端Docker配置
│   └── nginx/              # Nginx配置
├── docs/                   # 项目文档
└── scripts/                # 部署和工具脚本
```

## 技术栈

### 后端 (Django)
- Django 4.2+ / Django REST Framework
- PostgreSQL (主从读写分离)
- Redis (缓存/会话/队列)
- Celery (异步任务)

### 前端 (React)
- React 18 + TypeScript
- Redux Toolkit + RTK Query
- Ant Design + Tailwind CSS
- Vite

### 基础设施
- Docker + Kubernetes
- Nginx (负载均衡)
- CloudFlare (CDN)


# 现在你可以正常使用Django管理命令了。比如：

python manage.py runserver - 启动开发服务器
python manage.py makemigrations - 创建数据库迁移
python manage.py migrate - 应用数据库迁移
python manage.py createsuperuser - 创建超级用户
记住在backend目录下运行这些命令时，确保已经激活了py310 conda环境。
