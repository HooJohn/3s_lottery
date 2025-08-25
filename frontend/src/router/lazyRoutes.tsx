import { lazy, Suspense } from 'react'
import { Loading } from '@/components/ui/Loading'

// 创建懒加载组件的高阶函数
const createLazyComponent = (importFunc: () => Promise<any>) => {
  const LazyComponent = lazy(importFunc)
  
  return (props: any) => (
    <Suspense fallback={<Loading />}>
      <LazyComponent {...props} />
    </Suspense>
  )
}

// 认证相关页面 - 按需加载
export const LoginPage = createLazyComponent(() => import('@/pages/auth/LoginPage'))
export const RegisterPage = createLazyComponent(() => import('@/pages/auth/RegisterPage'))
export const ForgotPasswordPage = createLazyComponent(() => import('@/pages/auth/ForgotPasswordPage'))
export const KYCPage = createLazyComponent(() => import('@/pages/auth/KYCPage'))

// 游戏相关页面 - 按需加载
export const GamesPage = createLazyComponent(() => import('@/pages/games/GamesPage'))
export const Lottery11x5Page = createLazyComponent(() => import('@/pages/games/Lottery11x5Page'))
export const ScratchCardPage = createLazyComponent(() => import('@/pages/games/ScratchCardPage'))
export const SuperLottoPage = createLazyComponent(() => import('@/pages/games/SuperLottoPage'))
export const SportsPage = createLazyComponent(() => import('@/pages/games/SportsPage'))

// 钱包相关页面 - 按需加载
export const WalletPage = createLazyComponent(() => import('@/pages/wallet/WalletPage'))
export const DepositPage = createLazyComponent(() => import('@/pages/wallet/DepositPage'))
export const WithdrawPage = createLazyComponent(() => import('@/pages/wallet/WithdrawPage'))
export const TransactionHistoryPage = createLazyComponent(() => import('@/pages/wallet/TransactionHistoryPage'))

// 奖励相关页面 - 按需加载
export const RewardsPage = createLazyComponent(() => import('@/pages/rewards/RewardsPage'))
export const VipPage = createLazyComponent(() => import('@/pages/rewards/VipPage'))
export const RebateQueryPage = createLazyComponent(() => import('@/pages/rewards/RebateQueryPage'))
export const ReferralPage = createLazyComponent(() => import('@/pages/rewards/ReferralPage'))
export const RewardsStatsPage = createLazyComponent(() => import('@/pages/rewards/RewardsStatsPage'))

// 个人中心页面 - 按需加载
export const ProfilePage = createLazyComponent(() => import('@/pages/profile/ProfilePage'))

// 首页 - 预加载
export const HomePage = createLazyComponent(() => import('@/pages/home/HomePage'))

// 预加载函数 - 在用户可能访问前预加载关键页面
export const preloadCriticalRoutes = () => {
  // 预加载首页
  import('@/pages/home/HomePage')
  
  // 预加载认证页面（用户很可能需要登录）
  import('@/pages/auth/LoginPage')
  import('@/pages/auth/RegisterPage')
  
  // 预加载游戏页面（核心功能）
  import('@/pages/games/GamesPage')
}

// 预加载用户相关页面（登录后）
export const preloadUserRoutes = () => {
  import('@/pages/wallet/WalletPage')
  import('@/pages/rewards/RewardsPage')
  import('@/pages/profile/ProfilePage')
}

// 预加载游戏页面（用户进入游戏模块后）
export const preloadGameRoutes = () => {
  import('@/pages/games/Lottery11x5Page')
  import('@/pages/games/ScratchCardPage')
  import('@/pages/games/SuperLottoPage')
}