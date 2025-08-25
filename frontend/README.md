# 非洲彩票博彩平台 - 前端应用

基于 React + TypeScript + Vite 构建的现代化移动端彩票平台前端应用，提供完整的彩票游戏、钱包管理、奖励系统等功能。

## 🚀 技术栈

- **核心框架**: React 18 + TypeScript 4.9
- **构建工具**: Vite 4.x (快速构建和热更新)
- **状态管理**: Redux Toolkit + RTK Query (数据获取和缓存)
- **UI框架**: Tailwind CSS 3.x (原子化CSS)
- **路由管理**: React Router v6 (声明式路由)
- **国际化**: react-i18next (多语言支持)
- **图标库**: Lucide React (现代化图标)
- **HTTP客户端**: Axios (请求拦截和错误处理)
- **表单处理**: React Hook Form (高性能表单)
- **日期处理**: date-fns (轻量级日期库)
- **工具库**: lodash (实用工具函数)
- **WebSocket**: 原生WebSocket + 重连机制
- **PWA**: Service Worker + 离线支持

## 📁 项目结构

```
frontend/
├── public/                     # 静态资源
│   ├── icons/                 # 应用图标
│   ├── images/                # 图片资源
│   ├── sw.js                  # Service Worker
│   └── offline.html           # 离线页面
├── src/
│   ├── components/            # 可复用组件
│   │   ├── ui/               # 基础UI组件库
│   │   │   ├── Button.tsx    # 按钮组件
│   │   │   ├── Input.tsx     # 输入框组件
│   │   │   ├── Card.tsx      # 卡片组件
│   │   │   ├── Modal.tsx     # 模态框组件
│   │   │   ├── Table.tsx     # 表格组件
│   │   │   ├── Chart.tsx     # 图表组件
│   │   │   └── index.ts      # 组件导出
│   │   ├── layout/           # 布局组件
│   │   │   └── Layout.tsx    # 主布局
│   │   ├── navigation/       # 导航组件
│   │   │   ├── TopNavbar.tsx # 顶部导航
│   │   │   ├── Sidebar.tsx   # 侧边栏
│   │   │   ├── BottomNavigation.tsx # 底部导航
│   │   │   └── Breadcrumb.tsx # 面包屑
│   │   ├── games/            # 游戏相关组件
│   │   │   ├── GameStats.tsx # 游戏统计
│   │   │   └── GameEnhancer.tsx # 游戏增强
│   │   └── common/           # 通用组件
│   │       ├── LazyImage.tsx # 懒加载图片
│   │       ├── VirtualList.tsx # 虚拟列表
│   │       ├── PullToRefresh.tsx # 下拉刷新
│   │       ├── WebSocketProvider.tsx # WebSocket提供者
│   │       ├── RealtimeNotifications.tsx # 实时通知
│   │       ├── PerformanceMonitor.tsx # 性能监控
│   │       └── LanguageSwitcher.tsx # 语言切换
│   ├── pages/                # 页面组件
│   │   ├── auth/             # 认证页面
│   │   │   ├── LoginPage.tsx # 登录页
│   │   │   ├── RegisterPage.tsx # 注册页
│   │   │   ├── KYCPage.tsx   # KYC验证页
│   │   │   └── ForgotPasswordPage.tsx # 忘记密码
│   │   ├── home/             # 首页
│   │   │   └── HomePage.tsx  # 主页
│   │   ├── games/            # 游戏页面
│   │   │   ├── GamesPage.tsx # 游戏大厅
│   │   │   ├── Lottery11x5Page.tsx # 11选5
│   │   │   ├── SuperLottoPage.tsx # 大乐透
│   │   │   ├── ScratchCardPage.tsx # 刮刮乐
│   │   │   └── SportsPage.tsx # 体育博彩
│   │   ├── wallet/           # 钱包页面
│   │   │   ├── WalletPage.tsx # 钱包首页
│   │   │   ├── DepositPage.tsx # 充值页
│   │   │   ├── WithdrawPage.tsx # 提现页
│   │   │   └── TransactionHistoryPage.tsx # 交易记录
│   │   ├── rewards/          # 奖励页面
│   │   │   ├── RewardsPage.tsx # 奖励中心
│   │   │   ├── VipPage.tsx   # VIP页面
│   │   │   ├── ReferralPage.tsx # 推荐页面
│   │   │   ├── RewardsStatsPage.tsx # 奖励统计
│   │   │   └── RebateQueryPage.tsx # 返水查询
│   │   └── profile/          # 个人中心
│   │       └── ProfilePage.tsx # 个人资料
│   ├── store/                # Redux状态管理
│   │   ├── index.ts          # Store配置
│   │   ├── api/              # API切片
│   │   │   └── apiSlice.ts   # 基础API配置
│   │   └── slices/           # 状态切片
│   │       ├── authSlice.ts  # 认证状态
│   │       ├── userSlice.ts  # 用户状态
│   │       ├── gameSlice.ts  # 游戏状态
│   │       ├── financeSlice.ts # 财务状态
│   │       ├── rewardsSlice.ts # 奖励状态
│   │       └── uiSlice.ts    # UI状态
│   ├── services/             # API服务
│   │   ├── websocket.ts      # WebSocket服务
│   │   └── pushNotifications.ts # 推送通知
│   ├── hooks/                # 自定义Hooks
│   │   ├── useWebSocket.ts   # WebSocket Hook
│   │   └── useSwipeGesture.ts # 滑动手势Hook
│   ├── utils/                # 工具函数
│   │   ├── format.ts         # 格式化工具
│   │   ├── validation.ts     # 验证工具
│   │   ├── performance.ts    # 性能工具
│   │   ├── cache.ts          # 缓存工具
│   │   ├── preloader.ts      # 预加载工具
│   │   └── serviceWorker.ts  # Service Worker工具
│   ├── router/               # 路由配置
│   │   └── lazyRoutes.tsx    # 懒加载路由
│   ├── types/                # TypeScript类型定义
│   │   ├── index.ts          # 通用类型
│   │   └── global.d.ts       # 全局类型声明
│   ├── locales/              # 国际化文件
│   │   ├── en.json           # 英文
│   │   ├── zh.json           # 中文
│   │   └── fr.json           # 法文
│   ├── i18n/                 # 国际化配置
│   │   └── index.ts          # i18n配置
│   ├── __tests__/            # 测试文件
│   │   └── performance/      # 性能测试
│   ├── App.tsx               # 根组件
│   ├── main.tsx              # 应用入口
│   └── index.css             # 全局样式
├── .env                      # 环境变量
├── package.json              # 项目配置
├── vite.config.ts            # Vite配置
├── tailwind.config.js        # Tailwind配置
├── tsconfig.json             # TypeScript配置
├── PERFORMANCE_OPTIMIZATION.md # 性能优化文档
└── README.md                 # 项目文档
```

## 🛠️ 快速开始

### 环境要求

- **Node.js**: >= 16.0.0
- **npm**: >= 8.0.0 或 **yarn**: >= 1.22.0
- **现代浏览器**: Chrome 90+, Firefox 88+, Safari 14+

### 安装依赖

```bash
cd frontend
npm install
# 或
yarn install
```

### 环境配置

复制并配置环境变量：

```bash
cp .env.example .env
```

配置 `.env` 文件：

```env
# API配置
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws

# 应用配置
VITE_APP_NAME=非洲彩票平台
VITE_APP_VERSION=1.0.0
VITE_APP_DESCRIPTION=专业的彩票博彩平台

# 功能开关
VITE_ENABLE_PWA=true
VITE_ENABLE_PERFORMANCE_MONITOR=true
VITE_ENABLE_WEBSOCKET=true

# 第三方服务
VITE_GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID
VITE_SENTRY_DSN=SENTRY_DSN_URL
```

### 启动开发服务器

```bash
npm run dev
# 或
yarn dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
# 或
yarn build
```

### 预览生产构建

```bash
npm run preview
# 或
yarn preview
```

## 🎮 主要功能

### 🔐 用户认证系统
- **多种登录方式**: 手机号、邮箱登录
- **安全验证**: 短信验证码、双因子认证
- **身份验证**: KYC实名认证，支持身份证、护照等
- **密码安全**: 密码强度检测、找回密码
- **会话管理**: 自动登录、会话过期处理

### 🎯 游戏模块
- **11选5彩票**: 
  - 多种玩法（任选、前三、后三等）
  - 实时开奖动画
  - 走势图分析
  - 号码推荐
- **大乐透**: 
  - 传统彩票玩法
  - 胆拖投注
  - 奖池累积显示
- **666刮刮乐**: 
  - 即开即中游戏
  - 刮奖动画效果
  - 自动连刮功能
- **体育博彩**: 
  - 实时赛事数据
  - 多种投注类型
  - 赔率变化提醒

### 💰 钱包系统
- **余额管理**: 主余额、奖金余额分离管理
- **充值功能**: 支持银行卡、第三方支付
- **提现功能**: 快速提现、银行卡绑定
- **交易记录**: 详细的资金流水记录
- **安全保障**: 交易密码、短信验证

### 🎁 奖励系统
- **VIP等级**: 8级VIP体系，专享特权
- **返水奖励**: 根据流水自动返水
- **推荐奖励**: 7级推荐佣金体系
- **活动奖励**: 签到、任务等多种奖励
- **奖励统计**: 详细的奖励数据分析

### 👤 个人中心
- **个人信息**: 头像、昵称、基本信息管理
- **安全设置**: 密码修改、双因子认证
- **通知设置**: 推送通知、邮件通知配置
- **语言切换**: 支持中文、英文、法文
- **主题设置**: 明暗主题切换

## � 开发指南

### 代码规范

项目使用严格的代码规范：

```bash
# 代码检查
npm run lint

# 代码格式化
npm run format

# 类型检查
npm run type-check
```

### 组件开发规范

#### 基础UI组件开发

```typescript
// src/components/ui/Button.tsx
import React from 'react';
import { cn } from '@/utils/cn';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  className,
  children,
  disabled,
  ...props
}) => {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded-md font-medium transition-colors',
        {
          'bg-primary text-white hover:bg-primary/90': variant === 'primary',
          'bg-secondary text-secondary-foreground hover:bg-secondary/80': variant === 'secondary',
          'border border-input hover:bg-accent': variant === 'outline',
        },
        {
          'h-8 px-3 text-sm': size === 'sm',
          'h-10 px-4': size === 'md',
          'h-12 px-6 text-lg': size === 'lg',
        },
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <LoadingSpinner className="mr-2 h-4 w-4" />}
      {children}
    </button>
  );
};
```

#### 页面组件开发

```typescript
// src/pages/games/GamesPage.tsx
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, Button } from '@/components/ui';
import { Layout } from '@/components/layout';

export const GamesPage: React.FC = () => {
  const { t } = useTranslation();

  return (
    <Layout title={t('games.title')}>
      <div className="grid grid-cols-2 gap-4 p-4">
        <Card className="p-4">
          <h3 className="text-lg font-semibold">{t('games.lottery11x5')}</h3>
          <Button className="mt-2 w-full">
            {t('games.playNow')}
          </Button>
        </Card>
        {/* 更多游戏卡片 */}
      </div>
    </Layout>
  );
};
```

### 状态管理

#### Redux Toolkit 使用

```typescript
// src/store/slices/authSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
}

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  loading: false,
};

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart: (state) => {
      state.loading = true;
    },
    loginSuccess: (state, action: PayloadAction<{ user: User; token: string }>) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.isAuthenticated = true;
      state.loading = false;
    },
    loginFailure: (state) => {
      state.loading = false;
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
    },
  },
});
```

#### RTK Query API定义

```typescript
// src/store/api/apiSlice.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_API_BASE_URL,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['User', 'Game', 'Transaction', 'Reward'],
  endpoints: (builder) => ({
    getUser: builder.query<User, void>({
      query: () => '/users/profile',
      providesTags: ['User'],
    }),
    updateUser: builder.mutation<User, Partial<User>>({
      query: (userData) => ({
        url: '/users/profile',
        method: 'PATCH',
        body: userData,
      }),
      invalidatesTags: ['User'],
    }),
  }),
});
```

### 国际化

#### 多语言配置

```typescript
// src/i18n/index.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from '@/locales/en.json';
import zh from '@/locales/zh.json';
import fr from '@/locales/fr.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      zh: { translation: zh },
      fr: { translation: fr },
    },
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
```

#### 使用翻译

```typescript
// 在组件中使用
import { useTranslation } from 'react-i18next';

const { t, i18n } = useTranslation();

// 基础翻译
<h1>{t('welcome')}</h1>

// 带参数翻译
<p>{t('greeting', { name: 'John' })}</p>

// 切换语言
i18n.changeLanguage('zh');
```

### 样式系统

#### Tailwind CSS 使用

```jsx
// 响应式设计
<div className="w-full md:w-1/2 lg:w-1/3 xl:w-1/4">
  <Card className="p-4 shadow-lg hover:shadow-xl transition-shadow">
    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
      {title}
    </h3>
    <Button 
      className="mt-4 w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
      size="lg"
    >
      {t('submit')}
    </Button>
  </Card>
</div>
```

#### 自定义主题

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        secondary: {
          50: '#f8fafc',
          500: '#64748b',
          900: '#0f172a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
```

## 🚀 性能优化

### 代码分割和懒加载

```typescript
// src/router/lazyRoutes.tsx
import { lazy } from 'react';

// 路由懒加载
export const HomePage = lazy(() => import('@/pages/home/HomePage'));
export const GamesPage = lazy(() => import('@/pages/games/GamesPage'));
export const WalletPage = lazy(() => import('@/pages/wallet/WalletPage'));

// 组件懒加载
const LazyChart = lazy(() => import('@/components/ui/Chart'));

// 使用Suspense包装
<Suspense fallback={<Loading />}>
  <LazyChart data={chartData} />
</Suspense>
```

### 图片优化

```typescript
// src/components/common/LazyImage.tsx
import React, { useState, useRef, useEffect } from 'react';

interface LazyImageProps {
  src: string;
  alt: string;
  className?: string;
  placeholder?: string;
}

export const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  className,
  placeholder = '/images/placeholder.jpg',
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <img
      ref={imgRef}
      src={isInView ? src : placeholder}
      alt={alt}
      className={`transition-opacity duration-300 ${
        isLoaded ? 'opacity-100' : 'opacity-50'
      } ${className}`}
      onLoad={() => setIsLoaded(true)}
    />
  );
};
```

### 缓存策略

```typescript
// src/utils/cache.ts
class CacheManager {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();

  set(key: string, data: any, ttl: number = 300000) { // 5分钟默认TTL
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  get(key: string) {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  clear() {
    this.cache.clear();
  }
}

export const cacheManager = new CacheManager();
```

### 虚拟列表

```typescript
// src/components/common/VirtualList.tsx
import React, { useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';

interface VirtualListProps<T> {
  items: T[];
  height: number;
  itemHeight: number;
  renderItem: (item: T, index: number) => React.ReactNode;
}

export function VirtualList<T>({
  items,
  height,
  itemHeight,
  renderItem,
}: VirtualListProps<T>) {
  const Row = useMemo(
    () =>
      ({ index, style }: { index: number; style: React.CSSProperties }) => (
        <div style={style}>
          {renderItem(items[index], index)}
        </div>
      ),
    [items, renderItem]
  );

  return (
    <List
      height={height}
      itemCount={items.length}
      itemSize={itemHeight}
      width="100%"
    >
      {Row}
    </List>
  );
}
```

## 🧪 测试

### 单元测试

```bash
# 运行所有测试
npm run test

# 监听模式
npm run test:watch

# 测试覆盖率
npm run test:coverage
```

### 测试示例

```typescript
// src/components/ui/__tests__/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../Button';

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### E2E测试

```typescript
// cypress/e2e/auth.cy.ts
describe('Authentication', () => {
  it('should login successfully', () => {
    cy.visit('/login');
    cy.get('[data-testid=phone-input]').type('1234567890');
    cy.get('[data-testid=password-input]').type('password123');
    cy.get('[data-testid=login-button]').click();
    
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid=user-menu]').should('be.visible');
  });
});
```

## 📱 PWA支持

### Service Worker配置

```javascript
// public/sw.js
const CACHE_NAME = 'lottery-app-v1';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/offline.html',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
```

### 离线支持

```html
<!-- public/offline.html -->
<!DOCTYPE html>
<html>
<head>
  <title>离线模式 - 非洲彩票平台</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
  <div class="offline-container">
    <h1>您当前处于离线状态</h1>
    <p>请检查网络连接后重试</p>
    <button onclick="window.location.reload()">重新加载</button>
  </div>
</body>
</html>
```

## 🚀 部署

### Docker部署

```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx配置

```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # 缓存静态资源
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket代理
    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### CI/CD配置

```yaml
# .github/workflows/deploy.yml
name: Deploy Frontend

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm run test:ci
    
    - name: Build
      run: npm run build
      env:
        VITE_API_BASE_URL: ${{ secrets.API_BASE_URL }}
    
    - name: Deploy to S3
      run: aws s3 sync dist/ s3://${{ secrets.S3_BUCKET }} --delete
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## 🔧 故障排除

### 常见问题

1. **构建失败**
   ```bash
   # 清除缓存
   rm -rf node_modules package-lock.json
   npm install
   
   # 检查Node版本
   node --version
   npm --version
   ```

2. **API请求失败**
   ```bash
   # 检查环境变量
   echo $VITE_API_BASE_URL
   
   # 检查网络连接
   curl -I $VITE_API_BASE_URL/health
   ```

3. **样式问题**
   ```bash
   # 重新构建Tailwind
   npm run build:css
   
   # 检查Tailwind配置
   npx tailwindcss --help
   ```

4. **TypeScript错误**
   ```bash
   # 类型检查
   npm run type-check
   
   # 重新生成类型
   npm run generate-types
   ```

### 性能问题诊断

```typescript
// src/utils/performance.ts
export class PerformanceMonitor {
  static measureRender(componentName: string) {
    return (target: any, propertyName: string, descriptor: PropertyDescriptor) => {
      const method = descriptor.value;
      descriptor.value = function (...args: any[]) {
        const start = performance.now();
        const result = method.apply(this, args);
        const end = performance.now();
        
        console.log(`${componentName}.${propertyName} took ${end - start} milliseconds`);
        return result;
      };
    };
  }

  static trackUserInteraction(action: string, data?: any) {
    if (import.meta.env.PROD) {
      // 发送到分析服务
      gtag('event', action, data);
    } else {
      console.log('User interaction:', action, data);
    }
  }
}
```

## 📚 学习资源

- [React官方文档](https://react.dev/)
- [TypeScript手册](https://www.typescriptlang.org/docs/)
- [Vite指南](https://vitejs.dev/guide/)
- [Tailwind CSS文档](https://tailwindcss.com/docs)
- [Redux Toolkit文档](https://redux-toolkit.js.org/)

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 代码提交规范

```bash
# 功能开发
git commit -m "feat: add user authentication"

# 问题修复
git commit -m "fix: resolve login redirect issue"

# 文档更新
git commit -m "docs: update API documentation"

# 样式调整
git commit -m "style: improve button hover effects"

# 重构代码
git commit -m "refactor: optimize component structure"
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件