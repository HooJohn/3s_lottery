import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface User {
  id: string;
  username: string;
  email: string;
  phone: string;
  fullName: string;
  avatar?: string;
  vipLevel: number;
  kycStatus: 'pending' | 'approved' | 'rejected' | 'not_submitted';
  twoFactorEnabled: boolean;
  country: string;
  referralCode: string;
  isActive: boolean;
  lastLogin?: string;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  loading: boolean;
  error: string | null;
  loginAttempts: number;
  isBlocked: boolean;
  blockExpiry: string | null;
}

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  accessToken: localStorage.getItem('accessToken'),
  refreshToken: localStorage.getItem('refreshToken'),
  loading: false,
  error: null,
  loginAttempts: 0,
  isBlocked: false,
  blockExpiry: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    loginSuccess: (state, action: PayloadAction<{ user: User; accessToken: string; refreshToken: string }>) => {
      state.loading = false;
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.error = null;
      state.loginAttempts = 0;
      state.isBlocked = false;
      state.blockExpiry = null;
      
      // 存储到localStorage
      localStorage.setItem('accessToken', action.payload.accessToken);
      localStorage.setItem('refreshToken', action.payload.refreshToken);
    },
    loginFailure: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
      state.loginAttempts += 1;
      
      // 5次失败后锁定30分钟
      if (state.loginAttempts >= 5) {
        state.isBlocked = true;
        state.blockExpiry = new Date(Date.now() + 30 * 60 * 1000).toISOString();
      }
    },
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.error = null;
      state.loginAttempts = 0;
      state.isBlocked = false;
      state.blockExpiry = null;
      
      // 清除localStorage
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
    updateTokens: (state, action: PayloadAction<{ accessToken: string; refreshToken?: string }>) => {
      state.accessToken = action.payload.accessToken;
      if (action.payload.refreshToken) {
        state.refreshToken = action.payload.refreshToken;
      }
      
      localStorage.setItem('accessToken', action.payload.accessToken);
      if (action.payload.refreshToken) {
        localStorage.setItem('refreshToken', action.payload.refreshToken);
      }
    },
    clearError: (state) => {
      state.error = null;
    },
    unblockUser: (state) => {
      state.isBlocked = false;
      state.blockExpiry = null;
      state.loginAttempts = 0;
    },
  },
});

export const {
  loginStart,
  loginSuccess,
  loginFailure,
  logout,
  updateUser,
  updateTokens,
  clearError,
  unblockUser,
} = authSlice.actions;

export default authSlice.reducer;