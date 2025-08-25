# 非洲彩票博彩平台 - 后端API

基于 Django + Django REST Framework 构建的高性能彩票博彩平台后端API，提供完整的用户管理、游戏系统、财务管理、奖励系统等功能。

## 🚀 技术栈

- **核心框架**: Django 4.2 + Django REST Framework 3.14
- **数据库**: PostgreSQL 14+ (主数据库) + Redis 7+ (缓存/会话)
- **任务队列**: Celery 5.3 + Redis (消息代理)
- **认证系统**: JWT + 双因子认证 (TOTP)
- **API文档**: drf-spectacular (OpenAPI 3.0)
- **监控工具**: Django Silk (性能分析)
- **安全防护**: django-ratelimit + 自定义安全中间件
- **文件存储**: 本地存储 + 云存储支持
- **实时通信**: Django Channels + WebSocket
- **数据验证**: Django Validators + 自定义验证器
- **日志系统**: Python logging + 结构化日志
- **测试框架**: pytest + factory_boy

## 🛠️ 快速开始

### 环境要求

- **Python**: >= 3.9
- **PostgreSQL**: >= 14.0
- **Redis**: >= 7.0
- **系统**: Linux/macOS (推荐) 或 Windows

### 安装依赖

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 环境配置

复制并配置环境变量：

```bash
cp .env.example .env
```

配置 `.env` 文件：

```env
# Django配置
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/lottery_db
REDIS_URL=redis://localhost:6379/0

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 邮件配置
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# 短信配置
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# 支付配置
PAYSTACK_PUBLIC_KEY=pk_test_xxx
PAYSTACK_SECRET_KEY=sk_test_xxx
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST-xxx
FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST-xxx

# 文件存储配置
USE_S3=False
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# 安全配置
JWT_SECRET_KEY=your-jwt-secret
ENCRYPTION_KEY=your-encryption-key
RATE_LIMIT_ENABLE=True

# 监控配置
SENTRY_DSN=https://your-sentry-dsn
ENABLE_SILK=True
```

### 数据库设置

```bash
# 创建数据库迁移
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 初始化系统数据
python manage.py init_system --admin-user=admin --admin-password=admin123

# 创建超级用户 (可选)
python manage.py createsuperuser
```

### 启动服务

```bash
# 启动Django开发服务器
python manage.py runserver

# 启动Celery Worker (新终端)
celery -A lottery_platform worker -l info

# 启动Celery Beat (新终端)
celery -A lottery_platform beat -l info

# 启动Celery Flower监控 (可选)
celery -A lottery_platform flower
```

访问：
- API文档: http://localhost:8000/api/docs/
- 管理后台: http://localhost:8000/admin/
- Flower监控: http://localhost:5555/

## 🎮 主要功能模块

### 🔐 用户管理系统 (`apps/users/`)

#### 核心功能
- **用户注册/登录**: 手机号、邮箱多种方式
- **身份验证**: JWT Token + 刷新机制
- **双因子认证**: TOTP (Google Authenticator)
- **KYC实名认证**: 身份证、护照等文档验证
- **用户资料管理**: 个人信息、偏好设置
- **安全功能**: 登录日志、设备管理、风险控制

#### API端点
```
POST   /api/v1/auth/register/           # 用户注册
POST   /api/v1/auth/login/              # 用户登录
POST   /api/v1/auth/logout/             # 用户登出
POST   /api/v1/auth/refresh/            # 刷新Token
POST   /api/v1/auth/forgot-password/    # 忘记密码
POST   /api/v1/auth/reset-password/     # 重置密码

GET    /api/v1/users/profile/           # 获取用户资料
PATCH  /api/v1/users/profile/           # 更新用户资料
POST   /api/v1/users/change-password/   # 修改密码
POST   /api/v1/users/2fa/enable/        # 启用双因子认证
POST   /api/v1/users/2fa/disable/       # 禁用双因子认证

POST   /api/v1/users/kyc/submit/        # 提交KYC申请
GET    /api/v1/users/kyc/status/        # 查询KYC状态
GET    /api/v1/users/login-logs/        # 登录日志
```

### 💰 财务管理系统 (`apps/finance/`)

#### 核心功能
- **余额管理**: 主余额、奖金余额分离管理
- **充值系统**: 支持Paystack、Flutterwave等支付网关
- **提现系统**: 银行卡提现、实时到账
- **交易记录**: 完整的资金流水记录
- **银行卡管理**: 绑定、验证、管理银行卡
- **风控系统**: 反洗钱、异常交易检测

#### API端点
```
GET    /api/v1/finance/balance/         # 获取余额信息
POST   /api/v1/finance/deposit/         # 发起充值
POST   /api/v1/finance/withdraw/        # 发起提现
GET    /api/v1/finance/transactions/    # 交易记录
GET    /api/v1/finance/transaction/{id}/ # 交易详情

GET    /api/v1/finance/bank-accounts/   # 银行卡列表
POST   /api/v1/finance/bank-accounts/   # 添加银行卡
DELETE /api/v1/finance/bank-accounts/{id}/ # 删除银行卡
POST   /api/v1/finance/verify-bank/     # 验证银行卡

GET    /api/v1/finance/payment-methods/ # 支付方式列表
POST   /api/v1/finance/payment-callback/ # 支付回调
```

### 🎯 游戏系统 (`apps/games/`)

#### 11选5彩票系统 (`apps/games/lottery11x5/`)

**核心功能**:
- 多种玩法支持 (任选、前三、后三等)
- 自动开奖引擎
- 走势分析
- 号码推荐
- 购物车功能

**API端点**:
```
GET    /api/v1/games/11x5/current/     # 当前期次信息
GET    /api/v1/games/11x5/draws/       # 开奖历史
POST   /api/v1/games/11x5/bet/         # 投注
GET    /api/v1/games/11x5/trends/      # 走势数据
GET    /api/v1/games/11x5/hot-cold/    # 冷热号码
POST   /api/v1/games/11x5/cart/add/    # 添加到购物车
POST   /api/v1/games/11x5/cart/submit/ # 提交购物车
```

#### 大乐透系统 (`apps/games/superlotto/`)

**核心功能**:
- 传统大乐透玩法
- 胆拖投注
- 奖池管理
- 自动派奖

**API端点**:
```
GET    /api/v1/games/superlotto/current/    # 当前期次
POST   /api/v1/games/superlotto/bet/        # 投注
GET    /api/v1/games/superlotto/results/    # 开奖结果
GET    /api/v1/games/superlotto/jackpot/    # 奖池信息
```

#### 666刮刮乐系统 (`apps/games/scratch666/`)

**核心功能**:
- 即开即中游戏
- 多种卡片类型
- 自动连刮功能
- 中奖概率控制

**API端点**:
```
POST   /api/v1/games/scratch666/buy/       # 购买刮刮乐
POST   /api/v1/games/scratch666/scratch/   # 刮奖
GET    /api/v1/games/scratch666/cards/     # 我的卡片
GET    /api/v1/games/scratch666/stats/     # 统计信息
```

#### 体育博彩系统 (`apps/games/sports/`)

**核心功能**:
- 体育赛事管理
- 实时赔率更新
- 多种投注类型
- 赛果结算

**API端点**:
```
GET    /api/v1/games/sports/events/       # 赛事列表
GET    /api/v1/games/sports/odds/         # 赔率信息
POST   /api/v1/games/sports/bet/          # 投注
GET    /api/v1/games/sports/results/      # 赛果
```

### 🎁 奖励系统 (`apps/rewards/`)

#### 核心功能
- **VIP等级系统**: 8级VIP体系，专享特权
- **返水奖励**: 根据流水自动计算返水
- **推荐奖励**: 7级推荐佣金体系
- **活动奖励**: 签到、任务等多种奖励
- **奖励统计**: 详细的奖励数据分析

#### API端点
```
GET    /api/v1/rewards/vip/status/       # VIP状态
GET    /api/v1/rewards/vip/benefits/     # VIP权益
GET    /api/v1/rewards/rebate/           # 返水记录
GET    /api/v1/rewards/referral/         # 推荐奖励
POST   /api/v1/rewards/referral/bind/    # 绑定推荐人
GET    /api/v1/rewards/statistics/       # 奖励统计
```

### 🛡️ 系统管理和监控 (`apps/core/`)

#### 核心功能
- **系统监控**: CPU、内存、数据库连接等指标监控
- **日志系统**: 结构化日志记录和分析
- **安全防护**: 异常检测、风险控制
- **性能优化**: 缓存管理、数据库优化
- **报表生成**: 业务数据分析和报表
- **管理后台**: 统一的系统管理界面

#### 管理命令
```bash
# 系统初始化
python manage.py init_system

# 生成报表
python manage.py generate_report --type daily
python manage.py generate_report --type weekly
python manage.py generate_report --type monthly --export

# 安全扫描
python manage.py security_scan --scan-type all
python manage.py security_scan --scan-type users --auto-fix

# 数据清理
python manage.py cleanup_old_data
python manage.py backup_system_data
```

## 🧪 测试

### 单元测试

```bash
# 运行所有测试
pytest

# 运行特定应用测试
pytest apps/users/tests/

# 运行测试并生成覆盖率报告
pytest --cov=apps --cov-report=html

# 运行性能测试
pytest apps/games/tests/test_performance.py -v
```

## 🚀 部署

### Docker部署

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "lottery_platform.wsgi:application"]
```

### Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: lottery_db
      POSTGRES_USER: lottery_user
      POSTGRES_PASSWORD: lottery_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://lottery_user:lottery_pass@db:5432/lottery_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./media:/app/media
      - ./logs:/app/logs

  celery:
    build: .
    command: celery -A lottery_platform worker -l info
    environment:
      - DATABASE_URL=postgresql://lottery_user:lottery_pass@db:5432/lottery_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./media:/app/media
      - ./logs:/app/logs

  celery-beat:
    build: .
    command: celery -A lottery_platform beat -l info
    environment:
      - DATABASE_URL=postgresql://lottery_user:lottery_pass@db:5432/lottery_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

## 📚 API文档

访问 http://localhost:8000/api/docs/ 查看完整的API文档，包括：

- **认证接口**: 注册、登录、密码重置等
- **用户接口**: 个人资料、KYC、安全设置等
- **财务接口**: 余额、充值、提现、交易记录等
- **游戏接口**: 各类游戏的投注、查询、统计等
- **奖励接口**: VIP、返水、推荐奖励等

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件