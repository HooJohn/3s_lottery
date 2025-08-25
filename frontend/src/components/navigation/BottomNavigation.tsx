import React from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { 
  Home, 
  Gamepad2, 
  Wallet, 
  Gift, 
  User
} from 'lucide-react';
import { cn } from '@/utils/cn';

interface BottomNavigationProps {
  className?: string;
}

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<any>;
  badge?: number;
}

const BottomNavigation: React.FC<BottomNavigationProps> = ({ className }) => {
  const { t } = useTranslation();
  const location = useLocation();

  // 5个主要功能入口
  const navigationItems: NavigationItem[] = [
    { 
      name: t('navigation.home'), 
      href: '/dashboard', 
      icon: Home 
    },
    { 
      name: t('navigation.games'), 
      href: '/games', 
      icon: Gamepad2 
    },
    { 
      name: t('navigation.wallet'), 
      href: '/wallet', 
      icon: Wallet 
    },
    { 
      name: t('navigation.rewards'), 
      href: '/rewards', 
      icon: Gift,
      badge: 3
    },
    { 
      name: t('navigation.profile'), 
      href: '/profile', 
      icon: User 
    },
  ];

  const isItemActive = (href: string) => {
    if (href === '/dashboard') {
      return location.pathname === '/' || location.pathname === '/dashboard';
    }
    return location.pathname === href || location.pathname.startsWith(href + '/');
  };

  return (
    <nav className={cn(
      'fixed bottom-0 left-0 right-0 z-30',
      'bg-white border-t border-gray-200 shadow-lg',
      'safe-bottom lg:hidden', // 只在移动端显示
      className
    )}>
      <div className="grid grid-cols-5">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = isItemActive(item.href);
          
          return (
            <a
              key={item.name}
              href={item.href}
              className={cn(
                'relative flex flex-col items-center justify-center py-2 px-1',
                'text-xs font-medium transition-colors duration-200',
                'min-h-[60px] touch-target', // 确保触摸目标足够大
                isActive
                  ? 'text-primary-600 bg-primary-50'
                  : 'text-gray-500 hover:text-gray-700 active:bg-gray-50'
              )}
              aria-label={item.name}
            >
              {/* 图标容器 */}
              <div className="relative">
                <Icon className={cn(
                  'w-6 h-6 mb-1 transition-transform duration-200',
                  isActive && 'scale-110'
                )} />
                
                {/* 徽章 */}
                {item.badge && (
                  <span className="absolute -top-2 -right-2 w-5 h-5 bg-danger-500 text-white text-xs rounded-full flex items-center justify-center">
                    {item.badge > 99 ? '99+' : item.badge}
                  </span>
                )}
              </div>
              
              {/* 文本标签 */}
              <span className={cn(
                'truncate max-w-full transition-all duration-200',
                isActive && 'font-semibold'
              )}>
                {item.name}
              </span>
              
              {/* 活跃指示器 */}
              {isActive && (
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-8 h-1 bg-primary-500 rounded-b-full" />
              )}
            </a>
          );
        })}
      </div>
      
      {/* 安全区域适配 */}
      <div className="h-safe-bottom bg-white" />
    </nav>
  );
};

export default BottomNavigation;