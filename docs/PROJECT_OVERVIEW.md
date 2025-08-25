# 非洲在线彩票博彩平台 - 项目概览

## 🎯 项目目标
构建一个支持10万+用户的合规在线彩票和博彩综合平台，专注于尼日利亚、喀麦隆等非洲英语区国家市场。

## 📁 项目结构

```
africa-lottery-platform/
├── 📋 .kiro/specs/                    # Kiro规范文档
│   └── africa-lottery-platform/
│       ├── requirements.md            # 需求文档
│       ├── design.md                  # 设计文档
│       ├── tasks.md                   # 任务文档
│       └── economic-model.md          # 经济模型
├── 🐍 backend/                        # Django后端服务
│   ├── lottery_platform/             # Django项目主目录
│   ├── apps/                          # 应用模块
│   ├── requirements.txt               # Python依赖
│   └── manage.py                      # Django管理脚本
├── ⚛️ frontend/                       # React前端应用
│   ├── src/                           # 源代码
│   ├── package.json                   # Node.js依赖
│   └── vite.config.ts                 # Vite配置
├── 🔧 admin/                          # 管理后台
│   ├── src/                           # 管理后台源码
│   └── package.json                   # 依赖配置
├── 🗄️ database/                       # 数据库相关
│   ├── docker-compose.yml             # 数据库容器配置
│   └── init-scripts/                  # 初始化脚本
├── 🐳 docker/                         # Docker配置
│   ├── backend/Dockerfile             # 后端Docker配置
│   ├── frontend/Dockerfile            # 前端Docker配置
│   ├── nginx/                         # Nginx配置
│   └── docker-compose.yml             # 完整服务编排
└── 📜 scripts/                        # 部署和工具脚本
    ├── setup.sh                       # 项目初始化
    └── dev.sh                         # 开发环境启动
```

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Django 4.2+ / Django REST Framework
- **数据库**: PostgreSQL (主从读写分离)
- **缓存**: Redis (多层缓存策略)
- **异步任务**: Celery + Redis
- **认证**: Django Auth + JWT + 双因子认证
- **支付**: Paystack, Flutterwave, 移动货币API

### 前端技术栈
- **框架**: React 18 + TypeScript
- **状态管理**: Redux Toolkit + RTK Query
- **UI组件**: Ant Design + Tailwind CSS
- **构建工具**: Vite
- **多语言**: react-i18next

### 基础设施
- **容器化**: Docker + Docker Compose
- **负载均衡**: Nginx
- **监控**: Django-silk + APM工具
- **部署**: Kubernetes (生产环境)

## 🎮 核心功能

### 游戏产品线
1. **11选5彩票** (核心产品) - 18%毛利率
   - 定位胆和任选玩法
   - 每日7期开奖
   - 实时走势分析

2. **"666"刮刮乐** - 30%毛利率
   - 即时游戏体验
   - 自动连刮功能
   - 简化中奖机制

3. **大乐透彩票** - 35%毛利率
   - 高奖池彩票游戏
   - 9个奖级设置
   - 浮动奖池机制

4. **体育博彩集成** - 10%毛利率
   - 第三方平台集成
   - 钱包转账功能
   - 投注记录聚合

### 奖励系统
- **VIP等级**: VIP0-VIP7 (8级精细化)
- **统一返水**: 0.38%-0.80% (行业领先)
- **推荐奖励**: 7级推荐，总计7.6%
- **总奖励率**: 最高8.4% (行业第一)

## 💰 经济模型

### 竞争优势
- **奖励率**: 8.4% vs 行业平均4% (高出110%)
- **返水比例**: 0.38%-0.80% vs 行业0.2%-0.5%
- **推荐层级**: 7级 vs 行业2-5级
- **手续费**: 0%-2% vs 行业1%-4%

### 盈利预测
- **月净利润率**: 12.24%
- **用户奖励成本**: 占总流水1.86%
- **LTV/CAC比率**: 29.38 (优秀水平)
- **3年增长**: 用户规模10倍增长

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装Docker和Docker Compose
# 克隆项目代码
git clone <repository-url>
cd africa-lottery-platform
```

### 2. 项目初始化
```bash
# 运行初始化脚本
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. 启动开发环境
```bash
# 启动所有服务
chmod +x scripts/dev.sh
./scripts/dev.sh
```

### 4. 访问应用
- 前端应用: http://localhost:3000
- 管理后台: http://localhost:3001
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/api/docs/

## 📅 开发里程碑

### 第1阶段 (1-4周): 基础架构 ✅
- [x] 项目结构搭建
- [x] Docker环境配置
- [ ] Django项目初始化
- [ ] 用户认证系统

### 第2阶段 (5-8周): 核心功能
- [ ] 财务管理系统
- [ ] 11选5彩票功能
- [ ] 基础前端界面

### 第3阶段 (9-12周): 功能扩展
- [ ] 刮刮乐系统
- [ ] 大乐透彩票
- [ ] 奖励系统

### 第4阶段 (13-16周): 系统完善
- [ ] 体育博彩集成
- [ ] 管理后台
- [ ] 实时通信

### 第5阶段 (17-20周): 上线准备
- [ ] 测试和优化
- [ ] 安全加固
- [ ] 生产部署

## 📞 联系信息

- **项目文档**: `.kiro/specs/africa-lottery-platform/`
- **技术支持**: 查看各模块README文件
- **问题反馈**: 通过Issue跟踪系统