import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useTranslation } from 'react-i18next';
import { 
  Menu, 
  Bell, 
  User, 
  ChevronDown,
  Search,
  Settings,
  LogOut
} from 'lucide-react';
import { RootState } from '@/store';
import { toggleSidebar, toggleMobileMenu, addNotification } from '@/store/slices/uiSlice';
import LanguageSwitcher from '@/components/common/LanguageSwitcher';
import WebSocketStatus from '@/components/common/WebSocketStatus';
import { cn } from '@/utils/cn';

interface TopNavbarProps {
  className?: string;
}

const TopNavbar: React.FC<TopNavbarProps> = ({ className }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { sidebarOpen, unreadNotifications, isMobile } = useSelector((state: RootState) => state.ui);
  
  const [userMenuOpen, setUserMenuOpen] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [searchFocused, setSearchFocused] = React.useState(false);

  // 模拟用户数据
  const user = {
    name: 'John Doe',
    avatar: null,
    vipLevel: 2,
    balance: 15420.50,
  };

  const handleMenuToggle = () => {
    if (isMobile) {
      dispatch(toggleMobileMenu());
    } else {
      dispatch(toggleSidebar());
    }
  };

  const handleNotificationClick = () => {
    dispatch(addNotification({
      type: 'info',
      title: '通知中心',
      message: '您有新的消息',
    }));
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      console.log('搜索:', searchQuery);
      // 这里可以实现搜索功能
    }
  };

  const handleLogout = () => {
    // 实现登出逻辑
    console.log('用户登出');
  };

  return (
    <header className={cn(
      'bg-white border-b border-gray-200 shadow-sm',
      'sticky top-0 z-40',
      className
    )}>
      <div className="flex items-center justify-between h-16 px-4 lg:px-6">
        {/* 左侧：菜单按钮和Logo */}
        <div className="flex items-center space-x-4">
          {/* 菜单按钮 */}
          <button
            onClick={handleMenuToggle}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors lg:hidden"
            aria-label="打开菜单"
          >
            <Menu className="w-6 h-6" />
          </button>

          {/* Logo - 桌面端 */}
          <div className="hidden lg:flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">L</span>
            </div>
            <div>
              <h1 className="font-bold text-gray-900">非洲彩票</h1>
              <p className="text-xs text-gray-500">Africa Lottery</p>
            </div>
          </div>

          {/* Logo - 移动端 */}
          <div className="lg:hidden flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">L</span>
            </div>
            <span className="font-bold text-gray-900">彩票平台</span>
          </div>
        </div>

        {/* 中间：搜索框 - 仅桌面端显示 */}
        <div className="hidden lg:flex flex-1 max-w-lg mx-8">
          <form onSubmit={handleSearch} className="w-full">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setSearchFocused(true)}
                onBlur={() => setSearchFocused(false)}
                placeholder={t('common.search')}
                className={cn(
                  'w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg',
                  'focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                  'transition-colors',
                  searchFocused && 'ring-2 ring-primary-500 border-primary-500'
                )}
              />
            </div>
          </form>
        </div>

        {/* 右侧：功能按钮和用户信息 */}
        <div className="flex items-center space-x-2 lg:space-x-4">
          {/* 搜索按钮 - 仅移动端显示 */}
          <button className="lg:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
            <Search className="w-5 h-5" />
          </button>

          {/* 通知按钮 */}
          <button
            onClick={handleNotificationClick}
            className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="通知"
          >
            <Bell className="w-5 h-5" />
            {unreadNotifications > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-danger-500 text-white text-xs rounded-full flex items-center justify-center">
                {unreadNotifications > 99 ? '99+' : unreadNotifications}
              </span>
            )}
          </button>

          {/* WebSocket状态 */}
          <WebSocketStatus size="sm" />

          {/* 语言切换 */}
          <LanguageSwitcher size="sm" variant="button" />

          {/* 用户菜单 */}
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center space-x-2 p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="用户菜单"
            >
              <div className="w-8 h-8 bg-gradient-primary rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-sm">
                  {user.name.charAt(0)}
                </span>
              </div>
              <div className="hidden lg:block text-left">
                <p className="text-sm font-medium text-gray-900 truncate max-w-24">
                  {user.name}
                </p>
                <p className="text-xs text-gray-500">
                  VIP{user.vipLevel}
                </p>
              </div>
              <ChevronDown className="w-4 h-4" />
            </button>

            {/* 用户下拉菜单 */}
            {userMenuOpen && (
              <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                {/* 用户信息 */}
                <div className="px-4 py-3 border-b border-gray-200">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gradient-primary rounded-full flex items-center justify-center">
                      <span className="text-white font-bold text-lg">
                        {user.name.charAt(0)}
                      </span>
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{user.name}</p>
                      <p className="text-sm text-gray-500">VIP{user.vipLevel}</p>
                    </div>
                  </div>
                  <div className="mt-3 p-2 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">账户余额</span>
                      <span className="font-bold text-gray-900">
                        ₦{user.balance.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* 菜单项 */}
                <div className="py-2">
                  <a
                    href="/profile"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <User className="w-4 h-4 mr-3" />
                    {t('navigation.profile')}
                  </a>
                  <a
                    href="/profile/settings"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <Settings className="w-4 h-4 mr-3" />
                    {t('navigation.settings')}
                  </a>
                  <div className="border-t border-gray-200 my-2"></div>
                  <button
                    onClick={() => {
                      setUserMenuOpen(false);
                      handleLogout();
                    }}
                    className="w-full flex items-center px-4 py-2 text-sm text-danger-600 hover:bg-danger-50 transition-colors"
                  >
                    <LogOut className="w-4 h-4 mr-3" />
                    {t('common.logout')}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 点击外部关闭用户菜单 */}
      {userMenuOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setUserMenuOpen(false)}
        />
      )}
    </header>
  );
};

export default TopNavbar;