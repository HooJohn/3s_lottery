import React from 'react';
import { useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { ChevronRight, Home } from 'lucide-react';
import { RootState } from '@/store';
import { cn } from '@/utils/cn';

interface BreadcrumbItem {
  label: string;
  href?: string;
  active?: boolean;
}

interface BreadcrumbProps {
  items?: BreadcrumbItem[];
  className?: string;
  showHome?: boolean;
  separator?: React.ReactNode;
}

const Breadcrumb: React.FC<BreadcrumbProps> = ({ 
  items: propItems, 
  className,
  showHome = true,
  separator = <ChevronRight className="w-4 h-4 text-gray-400" />
}) => {
  const { t } = useTranslation();
  const { breadcrumbs } = useSelector((state: RootState) => state.ui);
  
  // 使用传入的items或从Redux store获取
  const items = propItems || breadcrumbs;
  
  // 如果没有面包屑项目，不渲染组件
  if (!items || items.length === 0) {
    return null;
  }

  // 构建完整的面包屑路径
  const fullBreadcrumbs: BreadcrumbItem[] = [];
  
  // 添加首页链接
  if (showHome) {
    fullBreadcrumbs.push({
      label: t('navigation.home'),
      href: '/dashboard',
      active: false
    });
  }
  
  // 添加其他面包屑项目
  fullBreadcrumbs.push(...items);

  return (
    <nav 
      className={cn(
        'flex items-center space-x-2 text-sm',
        'py-2 px-4 lg:px-6',
        'bg-gray-50 border-b border-gray-200',
        className
      )}
      aria-label="面包屑导航"
    >
      <ol className="flex items-center space-x-2">
        {fullBreadcrumbs.map((item, index) => {
          const isLast = index === fullBreadcrumbs.length - 1;
          const isFirst = index === 0 && showHome;
          
          return (
            <li key={index} className="flex items-center">
              {/* 分隔符 */}
              {index > 0 && (
                <span className="mx-2 flex-shrink-0">
                  {separator}
                </span>
              )}
              
              {/* 面包屑项目 */}
              <div className="flex items-center">
                {isFirst && (
                  <Home className="w-4 h-4 mr-1 text-gray-500" />
                )}
                
                {item.href && !isLast ? (
                  <a
                    href={item.href}
                    className={cn(
                      'font-medium transition-colors duration-200',
                      'hover:text-primary-600 focus:text-primary-600',
                      'focus:outline-none focus:underline',
                      item.active || isLast
                        ? 'text-gray-900 cursor-default'
                        : 'text-gray-500'
                    )}
                    aria-current={isLast ? 'page' : undefined}
                  >
                    {item.label}
                  </a>
                ) : (
                  <span
                    className={cn(
                      'font-medium',
                      item.active || isLast
                        ? 'text-gray-900'
                        : 'text-gray-500'
                    )}
                    aria-current={isLast ? 'page' : undefined}
                  >
                    {item.label}
                  </span>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

// 预设的面包屑配置
export const createBreadcrumbs = {
  // 游戏相关
  games: (): BreadcrumbItem[] => [
    { label: '游戏中心', href: '/games' }
  ],
  lottery11x5: (): BreadcrumbItem[] => [
    { label: '游戏中心', href: '/games' },
    { label: '11选5彩票', active: true }
  ],
  scratch: (): BreadcrumbItem[] => [
    { label: '游戏中心', href: '/games' },
    { label: '刮刮乐', active: true }
  ],
  superlotto: (): BreadcrumbItem[] => [
    { label: '游戏中心', href: '/games' },
    { label: '大乐透', active: true }
  ],
  sports: (): BreadcrumbItem[] => [
    { label: '游戏中心', href: '/games' },
    { label: '体育博彩', active: true }
  ],
  
  // 钱包相关
  wallet: (): BreadcrumbItem[] => [
    { label: '我的钱包', active: true }
  ],
  deposit: (): BreadcrumbItem[] => [
    { label: '我的钱包', href: '/wallet' },
    { label: '存款', active: true }
  ],
  withdraw: (): BreadcrumbItem[] => [
    { label: '我的钱包', href: '/wallet' },
    { label: '提款', active: true }
  ],
  transactions: (): BreadcrumbItem[] => [
    { label: '我的钱包', href: '/wallet' },
    { label: '交易记录', active: true }
  ],
  
  // 奖励相关
  rewards: (): BreadcrumbItem[] => [
    { label: '奖励中心', active: true }
  ],
  vip: (): BreadcrumbItem[] => [
    { label: '奖励中心', href: '/rewards' },
    { label: 'VIP等级', active: true }
  ],
  referral: (): BreadcrumbItem[] => [
    { label: '奖励中心', href: '/rewards' },
    { label: '推荐奖励', active: true }
  ],
  rebate: (): BreadcrumbItem[] => [
    { label: '奖励中心', href: '/rewards' },
    { label: '返水查询', active: true }
  ],
  
  // 个人中心
  profile: (): BreadcrumbItem[] => [
    { label: '个人中心', active: true }
  ],
  settings: (): BreadcrumbItem[] => [
    { label: '个人中心', href: '/profile' },
    { label: '设置', active: true }
  ],
  
  // 认证相关
  kyc: (): BreadcrumbItem[] => [
    { label: '个人中心', href: '/profile' },
    { label: '身份验证', active: true }
  ],
};

export default Breadcrumb;