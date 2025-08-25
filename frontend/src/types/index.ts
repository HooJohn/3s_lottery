// 用户相关类型定义
export interface User {
  id: string;
  username: string;
  email: string;
  phone: string;
  full_name: string;
  country: 'NG' | 'CM';
  vip_level: number;
  total_turnover: number;
  referral_code: string;
  kyc_status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  avatar?: string;
  birth_date?: string;
  gender?: 'M' | 'F' | 'O';
  address?: string;
  city?: string;
  state?: string;
  language: 'en' | 'fr' | 'zh';
  timezone: string;
  email_notifications: boolean;
  sms_notifications: boolean;
}

export interface UserBalance {
  main_balance: number;
  bonus_balance: number;
  frozen_balance: number;
  total_balance: number;
  available_balance: number;
  updated_at: string;
}

// 认证相关类型
export interface LoginRequest {
  username: string; // 可以是用户名、邮箱或手机号
  password: string;
  remember_me?: boolean;
}

export interface RegisterRequest {
  username: string;
  email: string;
  phone: string;
  full_name: string;
  password: string;
  confirm_password: string;
  country: 'NG' | 'CM';
  referral_code?: string;
  agree_terms: boolean;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
  expires_in: number;
}

// KYC相关类型
export interface KYCDocument {
  id: string;
  document_type: 'NIN' | 'PASSPORT' | 'DRIVERS_LICENSE' | 'VOTERS_CARD';
  document_number: string;
  front_image: string;
  back_image?: string;
  selfie_image: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED';
  rejection_reason?: string;
  created_at: string;
  updated_at: string;
}

// 财务相关类型
export interface Transaction {
  id: string;
  type: 'DEPOSIT' | 'WITHDRAW' | 'BET' | 'WIN' | 'REWARD' | 'REFUND' | 'ADJUSTMENT';
  amount: number;
  fee: number;
  actual_amount: number;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  description: string;
  reference_id: string;
  created_at: string;
  updated_at: string;
}

export interface BankAccount {
  id: string;
  bank_code: string;
  bank_name: string;
  account_number: string;
  account_name: string;
  is_verified: boolean;
  is_default: boolean;
  created_at: string;
}

export interface PaymentMethod {
  id: string;
  name: string;
  method_type: 'BANK_TRANSFER' | 'MOBILE_MONEY' | 'PAYMENT_GATEWAY';
  provider: 'PAYSTACK' | 'FLUTTERWAVE' | 'OPAY' | 'PALMPAY' | 'MONIEPOINT' | 'MANUAL';
  min_amount: number;
  max_amount: number;
  fee_type: 'FIXED' | 'PERCENTAGE';
  fee_value: number;
  is_active: boolean;
  is_deposit_enabled: boolean;
  is_withdraw_enabled: boolean;
}

// 游戏相关类型
export interface Game {
  id: string;
  name: string;
  code: string;
  game_type: string;
  status: 'ACTIVE' | 'INACTIVE' | 'MAINTENANCE';
  description: string;
  min_bet: number;
  max_bet: number;
  created_at: string;
}

export interface Draw {
  id: string;
  game: string;
  draw_number: string;
  draw_time: string;
  close_time: string;
  status: 'OPEN' | 'CLOSED' | 'COMPLETED';
  winning_numbers?: string;
  total_bets: number;
  total_amount: number;
  total_payout: number;
  profit: number;
}

export interface Bet {
  id: string;
  game: string;
  draw: string;
  bet_type: string;
  numbers: number[];
  amount: number;
  odds: number;
  potential_payout: number;
  actual_payout?: number;
  status: 'PENDING' | 'WON' | 'LOST' | 'CANCELLED';
  bet_time: string;
  settled_at?: string;
}

// 11选5相关类型
export interface Lottery11x5Bet extends Bet {
  bet_method: 'POSITION' | 'ANY' | 'GROUP';
  positions?: number[];
  selected_count?: number;
  is_multiple: boolean;
  multiple_count: number;
}

export interface Lottery11x5Result {
  draw: string;
  numbers: number[];
  sum_value: number;
  odd_count: number;
  even_count: number;
  big_count: number;
  small_count: number;
  span_value: number;
}

// 大乐透相关类型
export interface SuperLottoBet extends Bet {
  bet_type: 'SINGLE' | 'MULTIPLE' | 'SYSTEM';
  front_numbers: number[];
  back_numbers: number[];
  front_dan_numbers?: number[];
  front_tuo_numbers?: number[];
  back_dan_numbers?: number[];
  back_tuo_numbers?: number[];
  multiplier: number;
  bet_count: number;
  single_amount: number;
  total_amount: number;
}

// 刮刮乐相关类型
export interface ScratchCard {
  id: string;
  card_type: string;
  price: number;
  areas: ScratchArea[];
  total_winnings: number;
  is_scratched: boolean;
  created_at: string;
}

export interface ScratchArea {
  id: number;
  symbol: string;
  is_scratched: boolean;
  is_winning: boolean;
  winning_amount?: number;
}

// VIP和奖励相关类型
export interface VIPLevel {
  level: number;
  name: string;
  required_turnover: number;
  rebate_rate: number;
  daily_withdraw_limit: number;
  daily_withdraw_times: number;
  withdraw_fee_rate: number;
}

export interface RewardRecord {
  id: string;
  type: 'REBATE' | 'REFERRAL' | 'BONUS';
  amount: number;
  description: string;
  status: 'PENDING' | 'COMPLETED';
  created_at: string;
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
  page_size: number;
  current_page: number;
  total_pages: number;
}

// 表单相关类型
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'tel' | 'number' | 'select' | 'checkbox' | 'radio';
  placeholder?: string;
  required?: boolean;
  validation?: any;
  options?: { value: string; label: string }[];
}

// 通知相关类型
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// 语言相关类型
export type Language = 'en' | 'fr' | 'zh';

export interface LanguageOption {
  code: Language;
  name: string;
  flag: string;
}

// 主题相关类型
export interface Theme {
  name: string;
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: string;
  };
}

// 路由相关类型
export interface RouteConfig {
  path: string;
  component: React.ComponentType;
  exact?: boolean;
  protected?: boolean;
  roles?: string[];
  title?: string;
  icon?: string;
}

// 菜单相关类型
export interface MenuItem {
  key: string;
  label: string;
  icon?: string;
  path?: string;
  children?: MenuItem[];
  badge?: string | number;
  disabled?: boolean;
}

// 统计相关类型
export interface Statistics {
  total_users: number;
  total_bets: number;
  total_winnings: number;
  total_deposits: number;
  total_withdrawals: number;
  profit_rate: number;
}

// 设备相关类型
export interface DeviceInfo {
  type: 'mobile' | 'tablet' | 'desktop';
  os: string;
  browser: string;
  screen_size: {
    width: number;
    height: number;
  };
}

// 错误相关类型
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
}

// 加载状态类型
export interface LoadingState {
  isLoading: boolean;
  error?: string | null;
  lastUpdated?: string;
}

// 分页参数类型
export interface PaginationParams {
  page?: number;
  page_size?: number;
  ordering?: string;
  search?: string;
}

// 筛选参数类型
export interface FilterParams {
  start_date?: string;
  end_date?: string;
  status?: string;
  type?: string;
  game_type?: string;
}

export default {};