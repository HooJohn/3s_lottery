import React, { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { RootState } from '@/store';
import { TopNavbar, Sidebar, BottomNavigation, Breadcrumb } from '@/components/navigation';
import RealtimeNotifications from '@/components/common/RealtimeNotifications';
import { cn } from '@/utils/cn';

interface LayoutProps {
  children?: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { sidebarOpen, sidebarCollapsed, mobileMenuOpen, isMobile } = useSelector((state: RootState) => state.ui);
  const [showShortcuts, setShowShortcuts] = React.useState(false);

  // 桌面端键盘快捷键支持
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // 只在桌面端启用快捷键
      if (window.innerWidth < 1024) return;

      // Ctrl/Cmd + K 打开快捷键帮助
      if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        setShowShortcuts(!showShortcuts);
      }

      // Ctrl/Cmd + 1-5 快速导航
      if ((event.ctrlKey || event.metaKey) && event.key >= '1' && event.key <= '5') {
        event.preventDefault();
        const navigationItems = [
          '/dashboard',
          '/games', 
          '/wallet',
          '/rewards',
          '/profile'
        ];
        const index = parseInt(event.key) - 1;
        if (navigationItems[index]) {
          window.location.href = navigationItems[index];
        }
      }

      // ESC 关闭快捷键帮助
      if (event.key === 'Escape' && showShortcuts) {
        setShowShortcuts(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [showShortcuts]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <TopNavbar />

      <div className="flex">
        {/* 桌面端侧边栏 */}
        <div className={cn(
          'hidden lg:flex lg:flex-col lg:fixed lg:inset-y-0 lg:top-16',
          'transition-all duration-300 ease-in-out',
          sidebarCollapsed ? 'lg:w-16' : 'lg:w-64'
        )}>
          <Sidebar />
        </div>

        {/* 移动端侧边栏遮罩 */}
        {(sidebarOpen || mobileMenuOpen) && isMobile && (
          <div className="lg:hidden fixed inset-0 z-40 top-16">
            <div className="absolute inset-0 bg-black opacity-50" />
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ duration: 0.3 }}
              className="relative w-64 md:w-80 h-full"
            >
              <Sidebar />
            </motion.div>
          </div>
        )}

        {/* 主内容区域 */}
        <div className={cn(
          'flex-1 transition-all duration-300 ease-in-out',
          'pt-16', // 为顶部导航栏留出空间
          !isMobile && (sidebarCollapsed ? 'lg:ml-16' : 'lg:ml-64')
        )}>
          {/* 面包屑导航 */}
          <Breadcrumb />
          
          <main className="min-h-screen pb-20 lg:pb-0">
            {children || <Outlet />}
          </main>
        </div>
      </div>

      {/* 移动端底部导航栏 */}
      <BottomNavigation />

      {/* 实时通知组件 */}
      <RealtimeNotifications />

      {/* 桌面端快捷键帮助弹窗 */}
      {showShortcuts && (
        <div className="hidden lg:block fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-white rounded-xl shadow-2xl p-6 max-w-md w-full mx-4"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">键盘快捷键</h3>
              <button
                onClick={() => setShowShortcuts(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">打开快捷键帮助</span>
                <kbd className="px-2 py-1 bg-gray-100 rounded text-xs font-mono">Ctrl + K</kbd>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">快速导航到首页</span>
                <kbd className="px-2 py-1 bg-gray-100 rounded text-xs font-mono">Ctrl + 1</kbd>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">快速导航到游戏</span>
                <kbd className="px-2 py-1 bg-gray-100 rounded text-xs font-mono">Ctrl + 2</kbd>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">快速导航到钱包</span>
                <kbd className="px-2 py-1 bg-gray-100 rounded text-xs font-mono">Ctrl + 3</kbd>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">快速导航到奖励</span>
                <kbd className="px-2 py-1 bg-gray-100 rounded text-xs font-mono">Ctrl + 4</kbd>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">快速导航到个人</span>
                <kbd className="px-2 py-1 bg-gray-100 rounded text-xs font-mono">Ctrl + 5</kbd>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">关闭弹窗</span>
                <kbd className="px-2 py-1 bg-gray-100 rounded text-xs font-mono">ESC</kbd>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-500 text-center">
                在 Mac 上使用 Cmd 键替代 Ctrl 键
              </p>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Layout;