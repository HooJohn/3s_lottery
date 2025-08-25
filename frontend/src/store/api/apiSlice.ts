import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '../index';

// 基础查询配置
const baseQuery = fetchBaseQuery({
  baseUrl: '/api/v1/',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.accessToken;
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    headers.set('Content-Type', 'application/json');
    return headers;
  },
});

// 带有token刷新的查询
const baseQueryWithReauth = async (args: any, api: any, extraOptions: any) => {
  let result = await baseQuery(args, api, extraOptions);
  
  if (result.error && result.error.status === 401) {
    // 尝试刷新token
    const refreshToken = (api.getState() as RootState).auth.refreshToken;
    if (refreshToken) {
      const refreshResult = await baseQuery(
        {
          url: 'auth/token/refresh/',
          method: 'POST',
          body: { refresh: refreshToken },
        },
        api,
        extraOptions
      );
      
      if (refreshResult.data) {
        // 更新token
        const { updateTokens } = await import('../slices/authSlice');
        api.dispatch(updateTokens(refreshResult.data));
        
        // 重试原始请求
        result = await baseQuery(args, api, extraOptions);
      } else {
        // 刷新失败，登出用户
        const { logout } = await import('../slices/authSlice');
        api.dispatch(logout());
      }
    }
  }
  
  return result;
};

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: [
    'User',
    'Balance',
    'Transaction',
    'BankAccount',
    'Game',
    'Draw',
    'Bet',
    'VIP',
    'Referral',
    'Promotion',
    'Notification',
  ],
  endpoints: (builder) => ({
    // 用户认证
    login: builder.mutation({
      query: (credentials) => ({
        url: 'auth/login/',
        method: 'POST',
        body: credentials,
      }),
      invalidatesTags: ['User'],
    }),
    
    register: builder.mutation({
      query: (userData) => ({
        url: 'auth/register/',
        method: 'POST',
        body: userData,
      }),
    }),
    
    logout: builder.mutation({
      query: () => ({
        url: 'auth/logout/',
        method: 'POST',
      }),
    }),
    
    // 用户资料
    getUserProfile: builder.query({
      query: () => 'auth/profile/',
      providesTags: ['User'],
    }),
    
    updateUserProfile: builder.mutation({
      query: (updates) => ({
        url: 'auth/profile/',
        method: 'PATCH',
        body: updates,
      }),
      invalidatesTags: ['User'],
    }),
    
    changePassword: builder.mutation({
      query: (passwordData) => ({
        url: 'auth/password/change/',
        method: 'POST',
        body: passwordData,
      }),
    }),
    
    // KYC
    submitKYC: builder.mutation({
      query: (kycData) => ({
        url: 'auth/kyc/submit/',
        method: 'POST',
        body: kycData,
      }),
      invalidatesTags: ['User'],
    }),
    
    getKYCStatus: builder.query({
      query: () => 'auth/kyc/status/',
      providesTags: ['User'],
    }),
    
    // 财务管理
    getBalance: builder.query({
      query: () => 'finance/balance/',
      providesTags: ['Balance'],
    }),
    
    getTransactions: builder.query({
      query: (params) => ({
        url: 'finance/transactions/',
        params,
      }),
      providesTags: ['Transaction'],
    }),
    
    getBankAccounts: builder.query({
      query: () => 'finance/bank-accounts/',
      providesTags: ['BankAccount'],
    }),
    
    addBankAccount: builder.mutation({
      query: (accountData) => ({
        url: 'finance/bank-accounts/',
        method: 'POST',
        body: accountData,
      }),
      invalidatesTags: ['BankAccount'],
    }),
    
    deleteBankAccount: builder.mutation({
      query: (id) => ({
        url: `finance/bank-accounts/${id}/`,
        method: 'DELETE',
      }),
      invalidatesTags: ['BankAccount'],
    }),
    
    createDeposit: builder.mutation({
      query: (depositData) => ({
        url: 'finance/deposit/',
        method: 'POST',
        body: depositData,
      }),
      invalidatesTags: ['Balance', 'Transaction'],
    }),
    
    createWithdraw: builder.mutation({
      query: (withdrawData) => ({
        url: 'finance/withdraw/',
        method: 'POST',
        body: withdrawData,
      }),
      invalidatesTags: ['Balance', 'Transaction'],
    }),
    
    getWithdrawLimits: builder.query({
      query: () => 'finance/withdraw/limits/',
    }),
    
    // 游戏相关
    getLottery11x5CurrentDraw: builder.query({
      query: () => 'games/lottery11x5/current-draw/',
      providesTags: ['Draw'],
    }),
    
    getLottery11x5LatestResult: builder.query({
      query: () => 'games/lottery11x5/latest-result/',
      providesTags: ['Draw'],
    }),
    
    getLottery11x5DrawHistory: builder.query({
      query: (params) => ({
        url: 'games/lottery11x5/draw-history/',
        params,
      }),
      providesTags: ['Draw'],
    }),
    
    getLottery11x5Stats: builder.query({
      query: () => 'games/lottery11x5/stats/',
      providesTags: ['Game'],
    }),
    
    placeLottery11x5Bet: builder.mutation({
      query: (betData) => ({
        url: 'games/lottery11x5/bet/',
        method: 'POST',
        body: betData,
      }),
      invalidatesTags: ['Balance', 'Bet'],
    }),
    
    // VIP系统
    getVIPStatus: builder.query({
      query: () => 'auth/vip/status/',
      providesTags: ['VIP'],
    }),
    
    getRebateRecords: builder.query({
      query: (params) => ({
        url: 'rewards/rebate/records/',
        params,
      }),
      providesTags: ['VIP'],
    }),
    
    // 推荐系统
    getReferralStats: builder.query({
      query: () => 'auth/referral/tree/',
      providesTags: ['Referral'],
    }),
    
    getReferralRecords: builder.query({
      query: (params) => ({
        url: 'rewards/referral/records/',
        params,
      }),
      providesTags: ['Referral'],
    }),
    
    // 促销活动
    getPromotions: builder.query({
      query: () => 'rewards/promotions/',
      providesTags: ['Promotion'],
    }),
    
    participatePromotion: builder.mutation({
      query: (promotionId) => ({
        url: `rewards/promotions/${promotionId}/participate/`,
        method: 'POST',
      }),
      invalidatesTags: ['Promotion'],
    }),
    
    // 通知
    getNotifications: builder.query({
      query: (params) => ({
        url: 'notifications/',
        params,
      }),
      providesTags: ['Notification'],
    }),
    
    markNotificationRead: builder.mutation({
      query: (notificationId) => ({
        url: `notifications/${notificationId}/read/`,
        method: 'POST',
      }),
      invalidatesTags: ['Notification'],
    }),
  }),
});

export const {
  // 用户认证
  useLoginMutation,
  useRegisterMutation,
  useLogoutMutation,
  
  // 用户资料
  useGetUserProfileQuery,
  useUpdateUserProfileMutation,
  useChangePasswordMutation,
  
  // KYC
  useSubmitKYCMutation,
  useGetKYCStatusQuery,
  
  // 财务管理
  useGetBalanceQuery,
  useGetTransactionsQuery,
  useGetBankAccountsQuery,
  useAddBankAccountMutation,
  useDeleteBankAccountMutation,
  useCreateDepositMutation,
  useCreateWithdrawMutation,
  useGetWithdrawLimitsQuery,
  
  // 游戏相关
  useGetLottery11x5CurrentDrawQuery,
  useGetLottery11x5LatestResultQuery,
  useGetLottery11x5DrawHistoryQuery,
  useGetLottery11x5StatsQuery,
  usePlaceLottery11x5BetMutation,
  
  // VIP系统
  useGetVIPStatusQuery,
  useGetRebateRecordsQuery,
  
  // 推荐系统
  useGetReferralStatsQuery,
  useGetReferralRecordsQuery,
  
  // 促销活动
  useGetPromotionsQuery,
  useParticipatePromotionMutation,
  
  // 通知
  useGetNotificationsQuery,
  useMarkNotificationReadMutation,
} = apiSlice;