import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface VIPLevel {
  level: number;
  name: string;
  requiredTurnover: number;
  rebateRate: number;
  withdrawLimit: number;
  withdrawTimes: number;
  withdrawFee: number;
  benefits: string[];
  color: string;
}

interface VIPStatus {
  currentLevel: number;
  currentTurnover: number;
  nextLevel: number;
  nextLevelTurnover: number;
  progress: number;
  totalRebate: number;
  monthlyRebate: number;
  upgradeDate?: string;
}

interface RebateRecord {
  id: string;
  date: string;
  effectiveTurnover: number;
  rebateRate: number;
  rebateAmount: number;
  status: 'pending' | 'settled' | 'cancelled';
  settledAt?: string;
  vipLevel: number;
}

interface ReferralStats {
  totalMembers: number;
  activeMembers: number;
  totalCommission: number;
  monthlyCommission: number;
  todayCommission: number;
  referralCode: string;
  shareUrl: string;
  qrCodeUrl: string;
}

interface ReferralLevel {
  level: number;
  members: number;
  turnover: number;
  commission: number;
  commissionRate: number;
}

interface ReferralRecord {
  id: string;
  date: string;
  username: string;
  level: number;
  turnover: number;
  commissionRate: number;
  commissionAmount: number;
  status: 'pending' | 'settled';
}

interface Promotion {
  id: string;
  title: string;
  description: string;
  type: 'deposit_bonus' | 'cashback' | 'free_bet' | 'tournament' | 'special';
  image: string;
  startDate: string;
  endDate: string;
  isActive: boolean;
  requirements: string[];
  rewards: string[];
  participated: boolean;
  progress?: number;
  maxProgress?: number;
}

interface RewardsState {
  // VIP系统
  vipLevels: VIPLevel[];
  vipStatus: VIPStatus | null;
  rebateRecords: RebateRecord[];
  rebateLoading: boolean;
  rebateError: string | null;
  
  // 推荐系统
  referralStats: ReferralStats | null;
  referralLevels: ReferralLevel[];
  referralRecords: ReferralRecord[];
  referralLoading: boolean;
  referralError: string | null;
  
  // 促销活动
  promotions: Promotion[];
  promotionsLoading: boolean;
  promotionsError: string | null;
  
  // 通用状态
  loading: boolean;
  error: string | null;
}

const initialState: RewardsState = {
  vipLevels: [
    {
      level: 0,
      name: 'Bronze',
      requiredTurnover: 0,
      rebateRate: 0.1,
      withdrawLimit: 50000,
      withdrawTimes: 3,
      withdrawFee: 0.02,
      benefits: ['基础返水', '客服支持'],
      color: '#CD7F32',
    },
    {
      level: 1,
      name: 'Silver',
      requiredTurnover: 100000,
      rebateRate: 0.15,
      withdrawLimit: 100000,
      withdrawTimes: 5,
      withdrawFee: 0.015,
      benefits: ['提升返水', '优先客服', '生日礼金'],
      color: '#C0C0C0',
    },
    {
      level: 2,
      name: 'Gold',
      requiredTurnover: 500000,
      rebateRate: 0.2,
      withdrawLimit: 200000,
      withdrawTimes: 8,
      withdrawFee: 0.01,
      benefits: ['黄金返水', '专属客服', '月度奖金', '特殊活动'],
      color: '#FFD700',
    },
    {
      level: 3,
      name: 'Platinum',
      requiredTurnover: 1000000,
      rebateRate: 0.25,
      withdrawLimit: 500000,
      withdrawTimes: 10,
      withdrawFee: 0.008,
      benefits: ['白金返水', '专属经理', '定制服务', '高额奖金'],
      color: '#E5E4E2',
    },
    {
      level: 4,
      name: 'Diamond',
      requiredTurnover: 2000000,
      rebateRate: 0.3,
      withdrawLimit: 1000000,
      withdrawTimes: 15,
      withdrawFee: 0.005,
      benefits: ['钻石返水', '私人顾问', '豪华礼品', '独家活动'],
      color: '#B9F2FF',
    },
    {
      level: 5,
      name: 'Crown',
      requiredTurnover: 5000000,
      rebateRate: 0.35,
      withdrawLimit: 2000000,
      withdrawTimes: 20,
      withdrawFee: 0.003,
      benefits: ['皇冠返水', '顶级服务', '奢华体验', '无限特权'],
      color: '#FFD700',
    },
    {
      level: 6,
      name: 'Royal',
      requiredTurnover: 10000000,
      rebateRate: 0.4,
      withdrawLimit: 5000000,
      withdrawTimes: 30,
      withdrawFee: 0.001,
      benefits: ['皇家返水', '至尊服务', '专属活动', '终极特权'],
      color: '#800080',
    },
    {
      level: 7,
      name: 'Supreme',
      requiredTurnover: 20000000,
      rebateRate: 0.5,
      withdrawLimit: 10000000,
      withdrawTimes: 50,
      withdrawFee: 0,
      benefits: ['至尊返水', '无限服务', '定制体验', '传奇地位'],
      color: '#FF0000',
    },
  ],
  vipStatus: null,
  rebateRecords: [],
  rebateLoading: false,
  rebateError: null,
  
  referralStats: null,
  referralLevels: [],
  referralRecords: [],
  referralLoading: false,
  referralError: null,
  
  promotions: [],
  promotionsLoading: false,
  promotionsError: null,
  
  loading: false,
  error: null,
};

const rewardsSlice = createSlice({
  name: 'rewards',
  initialState,
  reducers: {
    // VIP系统
    setVIPStatus: (state, action: PayloadAction<VIPStatus>) => {
      state.vipStatus = action.payload;
    },
    updateVIPProgress: (state, action: PayloadAction<{ turnover: number }>) => {
      if (state.vipStatus) {
        state.vipStatus.currentTurnover = action.payload.turnover;
        
        // 计算升级进度
        const nextLevel = state.vipLevels.find(level => level.level === state.vipStatus!.nextLevel);
        if (nextLevel) {
          const currentLevel = state.vipLevels.find(level => level.level === state.vipStatus!.currentLevel);
          const currentRequired = currentLevel?.requiredTurnover || 0;
          const nextRequired = nextLevel.requiredTurnover;
          const progress = Math.min(
            ((action.payload.turnover - currentRequired) / (nextRequired - currentRequired)) * 100,
            100
          );
          state.vipStatus.progress = Math.max(progress, 0);
        }
      }
    },
    upgradeVIPLevel: (state, action: PayloadAction<{ newLevel: number; upgradeDate: string }>) => {
      if (state.vipStatus) {
        state.vipStatus.currentLevel = action.payload.newLevel;
        state.vipStatus.nextLevel = Math.min(action.payload.newLevel + 1, 7);
        state.vipStatus.upgradeDate = action.payload.upgradeDate;
        state.vipStatus.progress = 0;
      }
    },
    
    // 返水记录
    setRebateLoading: (state, action: PayloadAction<boolean>) => {
      state.rebateLoading = action.payload;
    },
    setRebateRecords: (state, action: PayloadAction<RebateRecord[]>) => {
      state.rebateRecords = action.payload;
      state.rebateError = null;
    },
    addRebateRecord: (state, action: PayloadAction<RebateRecord>) => {
      state.rebateRecords.unshift(action.payload);
    },
    updateRebateRecord: (state, action: PayloadAction<{ id: string; updates: Partial<RebateRecord> }>) => {
      const index = state.rebateRecords.findIndex(record => record.id === action.payload.id);
      if (index !== -1) {
        state.rebateRecords[index] = { ...state.rebateRecords[index], ...action.payload.updates };
      }
    },
    setRebateError: (state, action: PayloadAction<string>) => {
      state.rebateError = action.payload;
      state.rebateLoading = false;
    },
    
    // 推荐系统
    setReferralLoading: (state, action: PayloadAction<boolean>) => {
      state.referralLoading = action.payload;
    },
    setReferralStats: (state, action: PayloadAction<ReferralStats>) => {
      state.referralStats = action.payload;
      state.referralError = null;
    },
    setReferralLevels: (state, action: PayloadAction<ReferralLevel[]>) => {
      state.referralLevels = action.payload;
    },
    setReferralRecords: (state, action: PayloadAction<ReferralRecord[]>) => {
      state.referralRecords = action.payload;
    },
    addReferralRecord: (state, action: PayloadAction<ReferralRecord>) => {
      state.referralRecords.unshift(action.payload);
    },
    updateReferralStats: (state, action: PayloadAction<Partial<ReferralStats>>) => {
      if (state.referralStats) {
        state.referralStats = { ...state.referralStats, ...action.payload };
      }
    },
    setReferralError: (state, action: PayloadAction<string>) => {
      state.referralError = action.payload;
      state.referralLoading = false;
    },
    
    // 促销活动
    setPromotionsLoading: (state, action: PayloadAction<boolean>) => {
      state.promotionsLoading = action.payload;
    },
    setPromotions: (state, action: PayloadAction<Promotion[]>) => {
      state.promotions = action.payload;
      state.promotionsError = null;
    },
    updatePromotion: (state, action: PayloadAction<{ id: string; updates: Partial<Promotion> }>) => {
      const index = state.promotions.findIndex(promo => promo.id === action.payload.id);
      if (index !== -1) {
        state.promotions[index] = { ...state.promotions[index], ...action.payload.updates };
      }
    },
    participatePromotion: (state, action: PayloadAction<string>) => {
      const promotion = state.promotions.find(promo => promo.id === action.payload);
      if (promotion) {
        promotion.participated = true;
        promotion.progress = 0;
      }
    },
    updatePromotionProgress: (state, action: PayloadAction<{ id: string; progress: number }>) => {
      const promotion = state.promotions.find(promo => promo.id === action.payload.id);
      if (promotion) {
        promotion.progress = action.payload.progress;
      }
    },
    setPromotionsError: (state, action: PayloadAction<string>) => {
      state.promotionsError = action.payload;
      state.promotionsLoading = false;
    },
    
    // 通用操作
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.loading = false;
    },
    clearRewardsErrors: (state) => {
      state.error = null;
      state.rebateError = null;
      state.referralError = null;
      state.promotionsError = null;
    },
    resetRewardsState: (state) => {
      return { ...initialState, vipLevels: state.vipLevels };
    },
  },
});

export const {
  // VIP系统
  setVIPStatus,
  updateVIPProgress,
  upgradeVIPLevel,
  
  // 返水记录
  setRebateLoading,
  setRebateRecords,
  addRebateRecord,
  updateRebateRecord,
  setRebateError,
  
  // 推荐系统
  setReferralLoading,
  setReferralStats,
  setReferralLevels,
  setReferralRecords,
  addReferralRecord,
  updateReferralStats,
  setReferralError,
  
  // 促销活动
  setPromotionsLoading,
  setPromotions,
  updatePromotion,
  participatePromotion,
  updatePromotionProgress,
  setPromotionsError,
  
  // 通用操作
  setLoading,
  setError,
  clearRewardsErrors,
  resetRewardsState,
} = rewardsSlice.actions;

export default rewardsSlice.reducer;