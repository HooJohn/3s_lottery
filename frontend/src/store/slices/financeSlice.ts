import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Balance {
  mainBalance: number;
  bonusBalance: number;
  frozenBalance: number;
  totalBalance: number;
  currency: string;
  lastUpdated: string;
}

interface Transaction {
  id: string;
  type: 'deposit' | 'withdraw' | 'bet' | 'win' | 'bonus' | 'refund' | 'transfer';
  amount: number;
  currency: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  description: string;
  reference?: string;
  createdAt: string;
  completedAt?: string;
  balanceAfter: number;
  fee?: number;
  method?: string;
}

interface BankAccount {
  id: string;
  bankName: string;
  accountNumber: string;
  accountName: string;
  bankCode: string;
  isDefault: boolean;
  isVerified: boolean;
  createdAt: string;
}

interface PaymentMethod {
  id: string;
  name: string;
  type: 'bank_transfer' | 'card' | 'mobile_money' | 'crypto';
  logo: string;
  minAmount: number;
  maxAmount: number;
  fee: number;
  feeType: 'fixed' | 'percentage';
  processingTime: string;
  isActive: boolean;
  supportedCurrencies: string[];
}

interface DepositRequest {
  id: string;
  amount: number;
  currency: string;
  method: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'expired';
  reference: string;
  paymentUrl?: string;
  createdAt: string;
  expiresAt: string;
  completedAt?: string;
  fee: number;
}

interface WithdrawRequest {
  id: string;
  amount: number;
  currency: string;
  bankAccountId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  reference: string;
  createdAt: string;
  processedAt?: string;
  fee: number;
  netAmount: number;
  reason?: string;
}

interface WithdrawLimits {
  dailyLimit: number;
  remainingDaily: number;
  dailyTimes: number;
  remainingTimes: number;
  minAmount: number;
  maxAmount: number;
  fee: number;
  feeType: 'fixed' | 'percentage';
}

interface FinanceState {
  balance: Balance | null;
  transactions: Transaction[];
  bankAccounts: BankAccount[];
  paymentMethods: PaymentMethod[];
  depositRequests: DepositRequest[];
  withdrawRequests: WithdrawRequest[];
  withdrawLimits: WithdrawLimits | null;
  
  // 加载状态
  balanceLoading: boolean;
  transactionsLoading: boolean;
  bankAccountsLoading: boolean;
  depositLoading: boolean;
  withdrawLoading: boolean;
  
  // 错误状态
  balanceError: string | null;
  transactionsError: string | null;
  bankAccountsError: string | null;
  depositError: string | null;
  withdrawError: string | null;
  
  // 分页信息
  transactionsPagination: {
    page: number;
    totalPages: number;
    totalCount: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
  
  // 筛选条件
  transactionsFilter: {
    type?: string;
    status?: string;
    dateFrom?: string;
    dateTo?: string;
    minAmount?: number;
    maxAmount?: number;
  };
}

const initialState: FinanceState = {
  balance: null,
  transactions: [],
  bankAccounts: [],
  paymentMethods: [],
  depositRequests: [],
  withdrawRequests: [],
  withdrawLimits: null,
  
  balanceLoading: false,
  transactionsLoading: false,
  bankAccountsLoading: false,
  depositLoading: false,
  withdrawLoading: false,
  
  balanceError: null,
  transactionsError: null,
  bankAccountsError: null,
  depositError: null,
  withdrawError: null,
  
  transactionsPagination: {
    page: 1,
    totalPages: 1,
    totalCount: 0,
    hasNext: false,
    hasPrev: false,
  },
  
  transactionsFilter: {},
};

const financeSlice = createSlice({
  name: 'finance',
  initialState,
  reducers: {
    // 余额管理
    setBalanceLoading: (state, action: PayloadAction<boolean>) => {
      state.balanceLoading = action.payload;
    },
    setBalance: (state, action: PayloadAction<Balance>) => {
      state.balance = action.payload;
      state.balanceError = null;
    },
    setBalanceError: (state, action: PayloadAction<string>) => {
      state.balanceError = action.payload;
      state.balanceLoading = false;
    },
    updateBalance: (state, action: PayloadAction<Partial<Balance>>) => {
      if (state.balance) {
        state.balance = { ...state.balance, ...action.payload };
      }
    },
    
    // 交易记录
    setTransactionsLoading: (state, action: PayloadAction<boolean>) => {
      state.transactionsLoading = action.payload;
    },
    setTransactions: (state, action: PayloadAction<{ transactions: Transaction[]; pagination: any }>) => {
      state.transactions = action.payload.transactions;
      state.transactionsPagination = action.payload.pagination;
      state.transactionsError = null;
    },
    addTransaction: (state, action: PayloadAction<Transaction>) => {
      state.transactions.unshift(action.payload);
    },
    updateTransaction: (state, action: PayloadAction<{ id: string; updates: Partial<Transaction> }>) => {
      const index = state.transactions.findIndex(t => t.id === action.payload.id);
      if (index !== -1) {
        state.transactions[index] = { ...state.transactions[index], ...action.payload.updates };
      }
    },
    setTransactionsError: (state, action: PayloadAction<string>) => {
      state.transactionsError = action.payload;
      state.transactionsLoading = false;
    },
    setTransactionsFilter: (state, action: PayloadAction<FinanceState['transactionsFilter']>) => {
      state.transactionsFilter = action.payload;
    },
    
    // 银行账户
    setBankAccountsLoading: (state, action: PayloadAction<boolean>) => {
      state.bankAccountsLoading = action.payload;
    },
    setBankAccounts: (state, action: PayloadAction<BankAccount[]>) => {
      state.bankAccounts = action.payload;
      state.bankAccountsError = null;
    },
    addBankAccount: (state, action: PayloadAction<BankAccount>) => {
      state.bankAccounts.push(action.payload);
    },
    updateBankAccount: (state, action: PayloadAction<{ id: string; updates: Partial<BankAccount> }>) => {
      const index = state.bankAccounts.findIndex(acc => acc.id === action.payload.id);
      if (index !== -1) {
        state.bankAccounts[index] = { ...state.bankAccounts[index], ...action.payload.updates };
      }
    },
    removeBankAccount: (state: FinanceState, action: PayloadAction<string>) => {
      state.bankAccounts = state.bankAccounts.filter(acc => acc.id !== action.payload);
    },
    setDefaultBankAccount: (state: FinanceState, action: PayloadAction<string>) => {
      state.bankAccounts.forEach(acc => {
        acc.isDefault = acc.id === action.payload;
      });
    },
    setBankAccountsError: (state: FinanceState, action: PayloadAction<string>) => {
      state.bankAccountsError = action.payload;
      state.bankAccountsLoading = false;
    },
    
    // 支付方式
    setPaymentMethods: (state, action: PayloadAction<PaymentMethod[]>) => {
      state.paymentMethods = action.payload;
    },
    
    // 存款
    setDepositLoading: (state, action: PayloadAction<boolean>) => {
      state.depositLoading = action.payload;
    },
    setDepositRequests: (state, action: PayloadAction<DepositRequest[]>) => {
      state.depositRequests = action.payload;
    },
    addDepositRequest: (state, action: PayloadAction<DepositRequest>) => {
      state.depositRequests.unshift(action.payload);
    },
    updateDepositRequest: (state, action: PayloadAction<{ id: string; updates: Partial<DepositRequest> }>) => {
      const index = state.depositRequests.findIndex(req => req.id === action.payload.id);
      if (index !== -1) {
        state.depositRequests[index] = { ...state.depositRequests[index], ...action.payload.updates };
      }
    },
    setDepositError: (state, action: PayloadAction<string>) => {
      state.depositError = action.payload;
      state.depositLoading = false;
    },
    
    // 提款
    setWithdrawLoading: (state, action: PayloadAction<boolean>) => {
      state.withdrawLoading = action.payload;
    },
    setWithdrawRequests: (state, action: PayloadAction<WithdrawRequest[]>) => {
      state.withdrawRequests = action.payload;
    },
    addWithdrawRequest: (state, action: PayloadAction<WithdrawRequest>) => {
      state.withdrawRequests.unshift(action.payload);
    },
    updateWithdrawRequest: (state, action: PayloadAction<{ id: string; updates: Partial<WithdrawRequest> }>) => {
      const index = state.withdrawRequests.findIndex(req => req.id === action.payload.id);
      if (index !== -1) {
        state.withdrawRequests[index] = { ...state.withdrawRequests[index], ...action.payload.updates };
      }
    },
    setWithdrawLimits: (state, action: PayloadAction<WithdrawLimits>) => {
      state.withdrawLimits = action.payload;
    },
    setWithdrawError: (state, action: PayloadAction<string>) => {
      state.withdrawError = action.payload;
      state.withdrawLoading = false;
    },
    
    // 清除错误
    clearFinanceErrors: (state) => {
      state.balanceError = null;
      state.transactionsError = null;
      state.bankAccountsError = null;
      state.depositError = null;
      state.withdrawError = null;
    },
    
    // 重置状态
    resetFinanceState: (state) => {
      return initialState;
    },
  },
});

export const {
  // 余额管理
  setBalanceLoading,
  setBalance,
  setBalanceError,
  updateBalance,
  
  // 交易记录
  setTransactionsLoading,
  setTransactions,
  addTransaction,
  updateTransaction,
  setTransactionsError,
  setTransactionsFilter,
  
  // 银行账户
  setBankAccountsLoading,
  setBankAccounts,
  addBankAccount,
  updateBankAccount,
  removeBankAccount,
  setDefaultBankAccount,
  setBankAccountsError,
  
  // 支付方式
  setPaymentMethods,
  
  // 存款
  setDepositLoading,
  setDepositRequests,
  addDepositRequest,
  updateDepositRequest,
  setDepositError,
  
  // 提款
  setWithdrawLoading,
  setWithdrawRequests,
  addWithdrawRequest,
  updateWithdrawRequest,
  setWithdrawLimits,
  setWithdrawError,
  
  // 清除错误
  clearFinanceErrors,
  resetFinanceState,
} = financeSlice.actions;

export default financeSlice.reducer;