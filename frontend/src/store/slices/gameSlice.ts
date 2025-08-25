import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface DrawInfo {
  drawNumber: string;
  drawTime: string;
  timeLeft: number;
  jackpot: number;
  totalBets: number;
  status: 'open' | 'closed' | 'drawing' | 'completed';
}

interface DrawResult {
  drawNumber: string;
  numbers: number[];
  drawTime: string;
  totalPrize: number;
  winners: number;
}

interface BetSlip {
  id: string;
  gameType: string;
  playType: string;
  selectedNumbers: number[];
  betAmount: number;
  multiplier: number;
  totalAmount: number;
  potentialWin: number;
  odds: number;
}

interface GameStats {
  hotNumbers: number[];
  coldNumbers: number[];
  frequencyData: Record<number, number>;
  trendData: Array<{
    period: string;
    numbers: number[];
  }>;
  lastUpdated: string;
}

interface GameState {
  // 11选5彩票
  lottery11x5: {
    currentDraw: DrawInfo | null;
    latestResult: DrawResult | null;
    drawHistory: DrawResult[];
    stats: GameStats | null;
    betSlips: BetSlip[];
    loading: boolean;
    error: string | null;
  };
  
  // 刮刮乐
  scratch: {
    availableCards: Array<{
      id: string;
      name: string;
      price: number;
      maxPrize: number;
      odds: number;
      image: string;
    }>;
    gameHistory: Array<{
      id: string;
      cardId: string;
      purchaseTime: string;
      result: 'win' | 'lose';
      prize: number;
    }>;
    loading: boolean;
    error: string | null;
  };
  
  // 大乐透
  superLotto: {
    currentDraw: DrawInfo | null;
    latestResult: DrawResult | null;
    drawHistory: DrawResult[];
    betSlips: BetSlip[];
    loading: boolean;
    error: string | null;
  };
  
  // 体育博彩
  sports: {
    platforms: Array<{
      id: string;
      name: string;
      logo: string;
      status: 'online' | 'maintenance' | 'offline';
      features: string[];
      balance: number;
    }>;
    betHistory: Array<{
      id: string;
      platform: string;
      event: string;
      betType: string;
      amount: number;
      odds: number;
      status: 'pending' | 'won' | 'lost' | 'cancelled';
      settledAt?: string;
    }>;
    loading: boolean;
    error: string | null;
  };
  
  // 通用状态
  soundEnabled: boolean;
  autoRefresh: boolean;
  refreshInterval: number;
}

const initialState: GameState = {
  lottery11x5: {
    currentDraw: null,
    latestResult: null,
    drawHistory: [],
    stats: null,
    betSlips: [],
    loading: false,
    error: null,
  },
  scratch: {
    availableCards: [],
    gameHistory: [],
    loading: false,
    error: null,
  },
  superLotto: {
    currentDraw: null,
    latestResult: null,
    drawHistory: [],
    betSlips: [],
    loading: false,
    error: null,
  },
  sports: {
    platforms: [],
    betHistory: [],
    loading: false,
    error: null,
  },
  soundEnabled: true,
  autoRefresh: true,
  refreshInterval: 30000, // 30秒
};

const gameSlice = createSlice({
  name: 'game',
  initialState,
  reducers: {
    // 11选5彩票
    setLottery11x5CurrentDraw: (state, action: PayloadAction<DrawInfo>) => {
      state.lottery11x5.currentDraw = action.payload;
    },
    setLottery11x5LatestResult: (state, action: PayloadAction<DrawResult>) => {
      state.lottery11x5.latestResult = action.payload;
    },
    setLottery11x5DrawHistory: (state, action: PayloadAction<DrawResult[]>) => {
      state.lottery11x5.drawHistory = action.payload;
    },
    setLottery11x5Stats: (state, action: PayloadAction<GameStats>) => {
      state.lottery11x5.stats = action.payload;
    },
    addLottery11x5BetSlip: (state, action: PayloadAction<BetSlip>) => {
      state.lottery11x5.betSlips.push(action.payload);
    },
    removeLottery11x5BetSlip: (state, action: PayloadAction<string>) => {
      state.lottery11x5.betSlips = state.lottery11x5.betSlips.filter(slip => slip.id !== action.payload);
    },
    clearLottery11x5BetSlips: (state) => {
      state.lottery11x5.betSlips = [];
    },
    setLottery11x5Loading: (state, action: PayloadAction<boolean>) => {
      state.lottery11x5.loading = action.payload;
    },
    setLottery11x5Error: (state, action: PayloadAction<string | null>) => {
      state.lottery11x5.error = action.payload;
    },
    
    // 刮刮乐
    setScratchCards: (state, action: PayloadAction<GameState['scratch']['availableCards']>) => {
      state.scratch.availableCards = action.payload;
    },
    addScratchGameHistory: (state, action: PayloadAction<GameState['scratch']['gameHistory'][0]>) => {
      state.scratch.gameHistory.unshift(action.payload);
    },
    setScratchLoading: (state, action: PayloadAction<boolean>) => {
      state.scratch.loading = action.payload;
    },
    setScratchError: (state, action: PayloadAction<string | null>) => {
      state.scratch.error = action.payload;
    },
    
    // 大乐透
    setSuperLottoCurrentDraw: (state, action: PayloadAction<DrawInfo>) => {
      state.superLotto.currentDraw = action.payload;
    },
    setSuperLottoLatestResult: (state, action: PayloadAction<DrawResult>) => {
      state.superLotto.latestResult = action.payload;
    },
    addSuperLottoBetSlip: (state, action: PayloadAction<BetSlip>) => {
      state.superLotto.betSlips.push(action.payload);
    },
    clearSuperLottoBetSlips: (state) => {
      state.superLotto.betSlips = [];
    },
    
    // 体育博彩
    setSportsPlatforms: (state, action: PayloadAction<GameState['sports']['platforms']>) => {
      state.sports.platforms = action.payload;
    },
    updateSportsPlatformBalance: (state, action: PayloadAction<{ platformId: string; balance: number }>) => {
      const platform = state.sports.platforms.find(p => p.id === action.payload.platformId);
      if (platform) {
        platform.balance = action.payload.balance;
      }
    },
    addSportsBetHistory: (state, action: PayloadAction<GameState['sports']['betHistory'][0]>) => {
      state.sports.betHistory.unshift(action.payload);
    },
    
    // 通用设置
    toggleSound: (state) => {
      state.soundEnabled = !state.soundEnabled;
    },
    setSoundEnabled: (state, action: PayloadAction<boolean>) => {
      state.soundEnabled = action.payload;
    },
    toggleAutoRefresh: (state) => {
      state.autoRefresh = !state.autoRefresh;
    },
    setRefreshInterval: (state, action: PayloadAction<number>) => {
      state.refreshInterval = action.payload;
    },
    
    // 清除错误
    clearGameErrors: (state) => {
      state.lottery11x5.error = null;
      state.scratch.error = null;
      state.superLotto.error = null;
      state.sports.error = null;
    },
  },
});

export const {
  // 11选5彩票
  setLottery11x5CurrentDraw,
  setLottery11x5LatestResult,
  setLottery11x5DrawHistory,
  setLottery11x5Stats,
  addLottery11x5BetSlip,
  removeLottery11x5BetSlip,
  clearLottery11x5BetSlips,
  setLottery11x5Loading,
  setLottery11x5Error,
  
  // 刮刮乐
  setScratchCards,
  addScratchGameHistory,
  setScratchLoading,
  setScratchError,
  
  // 大乐透
  setSuperLottoCurrentDraw,
  setSuperLottoLatestResult,
  addSuperLottoBetSlip,
  clearSuperLottoBetSlips,
  
  // 体育博彩
  setSportsPlatforms,
  updateSportsPlatformBalance,
  addSportsBetHistory,
  
  // 通用设置
  toggleSound,
  setSoundEnabled,
  toggleAutoRefresh,
  setRefreshInterval,
  clearGameErrors,
} = gameSlice.actions;

export default gameSlice.reducer;