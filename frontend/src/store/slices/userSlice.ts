import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UserProfile {
  id: string;
  username: string;
  email: string;
  phone: string;
  fullName: string;
  avatar?: string;
  birthDate?: string;
  gender?: 'male' | 'female' | 'other';
  address?: string;
  city?: string;
  state?: string;
  country: string;
  timezone: string;
  language: 'en' | 'fr' | 'zh';
  currency: string;
  referralCode: string;
  referredBy?: string;
  registrationDate: string;
  lastLogin?: string;
  isActive: boolean;
  emailVerified: boolean;
  phoneVerified: boolean;
}

interface UserPreferences {
  language: 'en' | 'fr' | 'zh';
  timezone: string;
  currency: string;
  theme: 'light' | 'dark' | 'auto';
  notifications: {
    email: boolean;
    sms: boolean;
    push: boolean;
    marketing: boolean;
    gameResults: boolean;
    promotions: boolean;
  };
  privacy: {
    showOnline: boolean;
    showStats: boolean;
    allowMessages: boolean;
  };
}

interface UserSecurity {
  twoFactorEnabled: boolean;
  trustedDevices: Array<{
    id: string;
    name: string;
    lastUsed: string;
    location: string;
  }>;
  loginHistory: Array<{
    id: string;
    timestamp: string;
    ip: string;
    location: string;
    device: string;
    success: boolean;
  }>;
  passwordLastChanged: string;
  securityQuestions: boolean;
}

interface UserState {
  profile: UserProfile | null;
  preferences: UserPreferences;
  security: UserSecurity | null;
  loading: boolean;
  error: string | null;
  updateLoading: boolean;
}

const initialState: UserState = {
  profile: null,
  preferences: {
    language: 'en',
    timezone: 'Africa/Lagos',
    currency: 'NGN',
    theme: 'light',
    notifications: {
      email: true,
      sms: true,
      push: true,
      marketing: false,
      gameResults: true,
      promotions: true,
    },
    privacy: {
      showOnline: true,
      showStats: false,
      allowMessages: true,
    },
  },
  security: null,
  loading: false,
  error: null,
  updateLoading: false,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    fetchUserStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchUserSuccess: (state, action: PayloadAction<UserProfile>) => {
      state.loading = false;
      state.profile = action.payload;
      state.error = null;
    },
    fetchUserFailure: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
    },
    updateProfileStart: (state) => {
      state.updateLoading = true;
      state.error = null;
    },
    updateProfileSuccess: (state, action: PayloadAction<Partial<UserProfile>>) => {
      state.updateLoading = false;
      if (state.profile) {
        state.profile = { ...state.profile, ...action.payload };
      }
      state.error = null;
    },
    updateProfileFailure: (state, action: PayloadAction<string>) => {
      state.updateLoading = false;
      state.error = action.payload;
    },
    updatePreferences: (state, action: PayloadAction<Partial<UserPreferences>>) => {
      state.preferences = { ...state.preferences, ...action.payload };
    },
    updateNotificationSettings: (state, action: PayloadAction<Partial<UserPreferences['notifications']>>) => {
      state.preferences.notifications = { ...state.preferences.notifications, ...action.payload };
    },
    updatePrivacySettings: (state, action: PayloadAction<Partial<UserPreferences['privacy']>>) => {
      state.preferences.privacy = { ...state.preferences.privacy, ...action.payload };
    },
    setUserSecurity: (state, action: PayloadAction<UserSecurity>) => {
      state.security = action.payload;
    },
    addTrustedDevice: (state, action: PayloadAction<UserSecurity['trustedDevices'][0]>) => {
      if (state.security) {
        state.security.trustedDevices.push(action.payload);
      }
    },
    removeTrustedDevice: (state, action: PayloadAction<string>) => {
      if (state.security) {
        state.security.trustedDevices = state.security.trustedDevices.filter(
          device => device.id !== action.payload
        );
      }
    },
    addLoginHistory: (state, action: PayloadAction<UserSecurity['loginHistory'][0]>) => {
      if (state.security) {
        state.security.loginHistory.unshift(action.payload);
        // 只保留最近50条记录
        if (state.security.loginHistory.length > 50) {
          state.security.loginHistory = state.security.loginHistory.slice(0, 50);
        }
      }
    },
    clearError: (state) => {
      state.error = null;
    },
    resetUser: (state) => {
      state.profile = null;
      state.security = null;
      state.loading = false;
      state.error = null;
      state.updateLoading = false;
    },
  },
});

export const {
  fetchUserStart,
  fetchUserSuccess,
  fetchUserFailure,
  updateProfileStart,
  updateProfileSuccess,
  updateProfileFailure,
  updatePreferences,
  updateNotificationSettings,
  updatePrivacySettings,
  setUserSecurity,
  addTrustedDevice,
  removeTrustedDevice,
  addLoginHistory,
  clearError,
  resetUser,
} = userSlice.actions;

export default userSlice.reducer;