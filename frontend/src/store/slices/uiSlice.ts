import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  persistent?: boolean;
  actions?: Array<{
    label: string;
    action: string;
    style?: 'primary' | 'secondary' | 'danger';
  }>;
  createdAt: string;
  read: boolean;
}

interface Modal {
  id: string;
  type: 'confirm' | 'alert' | 'custom';
  title: string;
  content: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm?: string;
  onCancel?: string;
  persistent?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

interface Breadcrumb {
  label: string;
  href?: string;
  active?: boolean;
}

interface UIState {
  // 主题设置
  theme: 'light' | 'dark' | 'auto';
  language: 'en' | 'fr' | 'zh';
  
  // 布局状态
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  mobileMenuOpen: boolean;
  
  // 加载状态
  globalLoading: boolean;
  pageLoading: boolean;
  
  // 通知系统
  notifications: Notification[];
  unreadNotifications: number;
  
  // 模态框
  modals: Modal[];
  
  // 面包屑导航
  breadcrumbs: Breadcrumb[];
  
  // 页面状态
  currentPage: string;
  pageTitle: string;
  
  // 网络状态
  isOnline: boolean;
  connectionQuality: 'good' | 'poor' | 'offline';
  
  // 设备信息
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  
  // 用户偏好
  preferences: {
    soundEnabled: boolean;
    animationsEnabled: boolean;
    autoRefresh: boolean;
    compactMode: boolean;
    showTips: boolean;
  };
  
  // 错误状态
  globalError: string | null;
  
  // 搜索状态
  searchQuery: string;
  searchResults: any[];
  searchLoading: boolean;
}

const initialState: UIState = {
  theme: 'light',
  language: 'en',
  
  sidebarOpen: false,
  sidebarCollapsed: false,
  mobileMenuOpen: false,
  
  globalLoading: false,
  pageLoading: false,
  
  notifications: [],
  unreadNotifications: 0,
  
  modals: [],
  
  breadcrumbs: [],
  
  currentPage: '',
  pageTitle: '',
  
  isOnline: navigator.onLine,
  connectionQuality: 'good',
  
  isMobile: window.innerWidth < 768,
  isTablet: window.innerWidth >= 768 && window.innerWidth < 1024,
  isDesktop: window.innerWidth >= 1024,
  
  preferences: {
    soundEnabled: true,
    animationsEnabled: true,
    autoRefresh: true,
    compactMode: false,
    showTips: true,
  },
  
  globalError: null,
  
  searchQuery: '',
  searchResults: [],
  searchLoading: false,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // 主题和语言
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'auto'>) => {
      state.theme = action.payload;
    },
    setLanguage: (state, action: PayloadAction<'en' | 'fr' | 'zh'>) => {
      state.language = action.payload;
    },
    
    // 布局控制
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    toggleSidebarCollapsed: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload;
    },
    toggleMobileMenu: (state) => {
      state.mobileMenuOpen = !state.mobileMenuOpen;
    },
    setMobileMenuOpen: (state, action: PayloadAction<boolean>) => {
      state.mobileMenuOpen = action.payload;
    },
    
    // 加载状态
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.globalLoading = action.payload;
    },
    setPageLoading: (state, action: PayloadAction<boolean>) => {
      state.pageLoading = action.payload;
    },
    
    // 通知系统
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id' | 'createdAt' | 'read'>>) => {
      const notification: Notification = {
        ...action.payload,
        id: Date.now().toString(),
        createdAt: new Date().toISOString(),
        read: false,
      };
      state.notifications.unshift(notification);
      state.unreadNotifications += 1;
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification && !notification.read) {
        state.unreadNotifications -= 1;
      }
      state.notifications = state.notifications.filter(n => n.id !== action.payload);
    },
    markNotificationRead: (state, action: PayloadAction<string>) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification && !notification.read) {
        notification.read = true;
        state.unreadNotifications -= 1;
      }
    },
    markAllNotificationsRead: (state) => {
      state.notifications.forEach(n => n.read = true);
      state.unreadNotifications = 0;
    },
    clearNotifications: (state) => {
      state.notifications = [];
      state.unreadNotifications = 0;
    },
    
    // 模态框
    showModal: (state, action: PayloadAction<Omit<Modal, 'id'>>) => {
      const modal: Modal = {
        ...action.payload,
        id: Date.now().toString(),
      };
      state.modals.push(modal);
    },
    hideModal: (state, action: PayloadAction<string>) => {
      state.modals = state.modals.filter(m => m.id !== action.payload);
    },
    hideAllModals: (state) => {
      state.modals = [];
    },
    
    // 面包屑导航
    setBreadcrumbs: (state, action: PayloadAction<Breadcrumb[]>) => {
      state.breadcrumbs = action.payload;
    },
    addBreadcrumb: (state, action: PayloadAction<Breadcrumb>) => {
      state.breadcrumbs.push(action.payload);
    },
    
    // 页面状态
    setCurrentPage: (state, action: PayloadAction<string>) => {
      state.currentPage = action.payload;
    },
    setPageTitle: (state, action: PayloadAction<string>) => {
      state.pageTitle = action.payload;
      document.title = action.payload;
    },
    
    // 网络状态
    setOnlineStatus: (state, action: PayloadAction<boolean>) => {
      state.isOnline = action.payload;
    },
    setConnectionQuality: (state, action: PayloadAction<'good' | 'poor' | 'offline'>) => {
      state.connectionQuality = action.payload;
    },
    
    // 设备信息
    updateDeviceInfo: (state, action: PayloadAction<{ width: number; height: number }>) => {
      const { width } = action.payload;
      state.isMobile = width < 768;
      state.isTablet = width >= 768 && width < 1024;
      state.isDesktop = width >= 1024;
    },
    
    // 用户偏好
    updatePreferences: (state, action: PayloadAction<Partial<UIState['preferences']>>) => {
      state.preferences = { ...state.preferences, ...action.payload };
    },
    toggleSound: (state) => {
      state.preferences.soundEnabled = !state.preferences.soundEnabled;
    },
    toggleAnimations: (state) => {
      state.preferences.animationsEnabled = !state.preferences.animationsEnabled;
    },
    toggleAutoRefresh: (state) => {
      state.preferences.autoRefresh = !state.preferences.autoRefresh;
    },
    toggleCompactMode: (state) => {
      state.preferences.compactMode = !state.preferences.compactMode;
    },
    toggleTips: (state) => {
      state.preferences.showTips = !state.preferences.showTips;
    },
    
    // 错误处理
    setGlobalError: (state, action: PayloadAction<string | null>) => {
      state.globalError = action.payload;
    },
    clearGlobalError: (state) => {
      state.globalError = null;
    },
    
    // 搜索
    setSearchQuery: (state, action: PayloadAction<string>) => {
      state.searchQuery = action.payload;
    },
    setSearchResults: (state, action: PayloadAction<any[]>) => {
      state.searchResults = action.payload;
    },
    setSearchLoading: (state, action: PayloadAction<boolean>) => {
      state.searchLoading = action.payload;
    },
    clearSearch: (state) => {
      state.searchQuery = '';
      state.searchResults = [];
      state.searchLoading = false;
    },
    
    // 重置状态
    resetUIState: (state) => {
      return { ...initialState, preferences: state.preferences };
    },
  },
});

export const {
  // 主题和语言
  setTheme,
  setLanguage,
  
  // 布局控制
  toggleSidebar,
  setSidebarOpen,
  toggleSidebarCollapsed,
  setSidebarCollapsed,
  toggleMobileMenu,
  setMobileMenuOpen,
  
  // 加载状态
  setGlobalLoading,
  setPageLoading,
  
  // 通知系统
  addNotification,
  removeNotification,
  markNotificationRead,
  markAllNotificationsRead,
  clearNotifications,
  
  // 模态框
  showModal,
  hideModal,
  hideAllModals,
  
  // 面包屑导航
  setBreadcrumbs,
  addBreadcrumb,
  
  // 页面状态
  setCurrentPage,
  setPageTitle,
  
  // 网络状态
  setOnlineStatus,
  setConnectionQuality,
  
  // 设备信息
  updateDeviceInfo,
  
  // 用户偏好
  updatePreferences,
  toggleSound,
  toggleAnimations,
  toggleAutoRefresh,
  toggleCompactMode,
  toggleTips,
  
  // 错误处理
  setGlobalError,
  clearGlobalError,
  
  // 搜索
  setSearchQuery,
  setSearchResults,
  setSearchLoading,
  clearSearch,
  
  // 重置状态
  resetUIState,
} = uiSlice.actions;

export default uiSlice.reducer;