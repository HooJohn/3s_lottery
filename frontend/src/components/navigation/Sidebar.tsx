import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Home, 
  Gamepad2, 
  Wallet, 
  Gift, 
  User,
  ChevronLeft,
  ChevronRight,
  Settings,
  HelpCircle,
  Bell,
  Globe
} from 'lucide-react';
import { RootState } from '@/store';
import { setSidebarCollapsed, setSidebarOpen } from '@/store/slices/uiSlice';
import { cn } from '@/utils/cn';

interface SidebarProps {
  className?: string;
}

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<any>;
  badge?: number;
  children?: NavigationItem[];
}

const Sidebar: React.FC<SidebarProps> = ({ className }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const location = useLocation();
  const { sidebarOpen, sidebarCollapsed, isMobile } = useSelector((state: RootState) => state.ui);

  // 模拟用户数据
  const user = {
    name: 'John Doe',
    avatar: null,
    vipLevel: 2,
    balance: 15420.50,
  };

  // 导航菜单项
  const navigationItems: NavigationItem[] = [
    { 
      name: t('navigation.home'), 
      href: '/dashboard', 
      icon: Home 
    },
    { 
      name: t('navigation.games'), 
      href: '/games', 
      icon: Gamepad2,
      children: [
        { name: t('navigation.lottery11x5'), href: '/games/lottery11x5', icon: Gamepad2 },
        { name: t('navigation.scratch'), href: '/games/scratch', icon: Gamepad2 },
        { name: t('navigation.superlotto'), href: '/games/superlotto', icon: Gamepad2 },
        { name: t('navigation.sports'), href: '/games/sports', icon: Gamepad2 },
      ]
    },
    { 
      name: t('navigation.wallet'), 
      href: '/wallet', 
      icon: Wallet,
      children: [
        { name: t('navigation.deposit'), href: '/wallet/deposit', icon: Wallet },
        { name: t('navigation.withdraw'), href: '/wallet/withdraw', icon: Wallet },
        { name: t('navigation.transactions'), href: '/wallet/transactions', icon: Wallet },
      ]
    },
    { 
      name: t('navigation.rewards'), 
      href: '/rewards', 
      icon: Gift,
      badge: 3,
      children: [
        { name: t('navigation.vip'), href: '/rewards/vip', icon: Gift },
        { name: t('navigation.referral'), href: '/rewards/referral', icon: Gift },
      ]
    },
    { 
      name: t('navigation.profile'), 
      href: '/profile', 
      icon: User 
    },
  ];

  const [expandedItems, setExpandedItems] = React.useState<string[]>([]);

  const isItemActive = (href: string) => {
    return location.pathname === href || location.pathname.startsWith(href + '/');
  };

  const isItemExpanded = (name: string) => {
    return expandedItems.includes(name);
  };

  const toggleItemExpansion = (name: string) => {
    setExpandedItems(prev => 
      prev.includes(name) 
        ? prev.filter(item => item !== name)
        : [...prev, name]
    );
  };

  const handleCollapse = () => {
    dispatch(setSidebarCollapsed(!sidebarCollapsed));
  };

  const handleClose = () => {
    dispatch(setSidebarOpen(false));
  };

  const renderNavigationItem = (item: NavigationItem, level = 0) => {
    const isActive = isItemActive(item.href);
    const isExpanded = isItemExpanded(item.name);
    const hasChildren = item.children && item.children.length > 0;
    const Icon = item.icon;

    return (
      <div key={item.name}>
        <div
          className={cn(
            'group flex items-center justify-between px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200',
            level > 0 && 'ml-6 pl-6 border-l-2 border-gray-200',
            isActive
              ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
            sidebarCollapsed && level === 0 && 'justify-center px-2'
          )}
        >
          {hasChildren ? (
            <button
              onClick={() => toggleItemExpansion(item.name)}
              className="flex items-center flex-1 text-left"
            >
              <Icon
                className={cn(
                  'flex-shrink-0 h-5 w-5',
                  isActive
                    ? 'text-primary-500'
                    : 'text-gray-400 group-hover:text-gray-500',
                  !sidebarCollapsed && 'mr-3'
                )}
              />
              {!sidebarCollapsed && (
                <>
                  <span className="flex-1">{item.name}</span>
                  {item.badge && (
                    <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                      {item.badge}
                    </span>
                  )}
                  <ChevronRight
                    className={cn(
                      'ml-2 h-4 w-4 transition-transform duration-200',
                      isExpanded && 'rotate-90'
                    )}
                  />
                </>
              )}
            </button>
          ) : (
            <a
              href={item.href}
              onClick={isMobile ? handleClose : undefined}
              className="flex items-center flex-1"
            >
              <Icon
                className={cn(
                  'flex-shrink-0 h-5 w-5',
                  isActive
                    ? 'text-primary-500'
                    : 'text-gray-400 group-hover:text-gray-500',
                  !sidebarCollapsed && 'mr-3'
                )}
              />
              {!sidebarCollapsed && (
                <>
                  <span className="flex-1">{item.name}</span>
                  {item.badge && (
                    <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </a>
          )}
        </div>

        {/* 子菜单 */}
        <AnimatePresence>
          {hasChildren && isExpanded && !sidebarCollapsed && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="mt-1 space-y-1">
                {item.children!.map(child => renderNavigationItem(child, level + 1))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  };

  return (
    <div className={cn(
      'flex flex-col bg-white border-r border-gray-200 shadow-sm',
      'transition-all duration-300 ease-in-out',
      sidebarCollapsed ? 'w-16' : 'w-64',
      className
    )}>
      {/* Logo区域 */}
      <div className={cn(
        'flex items-center border-b border-gray-200',
        sidebarCollapsed ? 'justify-center px-2 py-4' : 'px-6 py-4'
      )}>
        {sidebarCollapsed ? (
          <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center">
            <span className="text-white font-bold text-lg">L</span>
          </div>
        ) : (
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">L</span>
            </div>
            <div>
              <h1 className="font-bold text-gray-900">非洲彩票</h1>
              <p className="text-xs text-gray-500">Africa Lottery</p>
            </div>
          </div>
        )}
      </div>

      {/* 用户信息卡片 */}
      {!sidebarCollapsed && (
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-primary rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-lg">
                {user.name.charAt(0)}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-gray-900 truncate">
                {user.name}
              </p>
              <div className="flex items-center space-x-2">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-secondary-100 text-secondary-800">
                  VIP{user.vipLevel}
                </span>
              </div>
            </div>
          </div>
          <div className="mt-3 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">账户余额</span>
              <span className="font-bold text-gray-900">
                ₦{user.balance.toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* 导航菜单 */}
      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
        {navigationItems.map(item => renderNavigationItem(item))}
      </nav>

      {/* 底部功能区 */}
      <div className={cn(
        'border-t border-gray-200',
        sidebarCollapsed ? 'px-2 py-4' : 'px-4 py-4'
      )}>
        {!sidebarCollapsed && (
          <div className="space-y-1 mb-4">
            <button className="w-full flex items-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
              <Settings className="w-4 h-4 mr-3" />
              {t('navigation.settings')}
            </button>
            <button className="w-full flex items-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
              <HelpCircle className="w-4 h-4 mr-3" />
              {t('navigation.support')}
            </button>
          </div>
        )}

        {/* 折叠按钮 */}
        <div className="flex items-center justify-between">
          <button
            onClick={handleCollapse}
            className={cn(
              'p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors',
              sidebarCollapsed && 'mx-auto'
            )}
            aria-label={sidebarCollapsed ? '展开侧边栏' : '折叠侧边栏'}
          >
            {sidebarCollapsed ? (
              <ChevronRight className="w-5 h-5" />
            ) : (
              <ChevronLeft className="w-5 h-5" />
            )}
          </button>

          {!sidebarCollapsed && (
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>© 2024 非洲彩票</span>
              <span>v1.0.0</span>
            </div>
          )}
        </div>
      </div>

      {/* Tooltip for collapsed items */}
      {sidebarCollapsed && (
        <style>{`
          .sidebar-tooltip:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            left: 100%;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 0.5rem;
            border-radius: 0.375rem;
            font-size: 0.875rem;
            white-space: nowrap;
            z-index: 50;
            margin-left: 0.5rem;
          }
        `}</style>
      )}
    </div>
  );
};

export default Sidebar;