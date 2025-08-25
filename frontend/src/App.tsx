import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'

// 布局组件
import Layout from '@/components/layout/Layout'

// 页面组件
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import ForgotPasswordPage from '@/pages/auth/ForgotPasswordPage'
import KYCPage from '@/pages/auth/KYCPage'
import WalletPage from '@/pages/wallet/WalletPage'
import DepositPage from '@/pages/wallet/DepositPage'
import WithdrawPage from '@/pages/wallet/WithdrawPage'
import TransactionHistoryPage from '@/pages/wallet/TransactionHistoryPage'
import GamesPage from '@/pages/games/GamesPage'
import Lottery11x5Page from '@/pages/games/Lottery11x5Page'
import ScratchCardPage from '@/pages/games/ScratchCardPage'
import SuperLottoPage from '@/pages/games/SuperLottoPage'
import SportsPage from '@/pages/games/SportsPage'
import VipPage from '@/pages/rewards/VipPage'
import ReferralPage from '@/pages/rewards/ReferralPage'
import RewardsPage from '@/pages/rewards/RewardsPage'
import RewardsStatsPage from '@/pages/rewards/RewardsStatsPage'
import ProfilePage from '@/pages/profile/ProfilePage'

function App() {
  // 模拟认证状态 (稍后会从Redux store获取)
  const isAuthenticated = true // 临时设为true以便测试

  return (
    <div className="App">
            <Routes>
              {/* 公开路由 - 认证页面 */}
              <Route path="/auth/login" element={<LoginPage />} />
              <Route path="/auth/register" element={<RegisterPage />} />
              <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/auth/kyc" element={
                isAuthenticated ? <KYCPage /> : <Navigate to="/auth/login" replace />
              } />
              
              {/* 受保护的路由 - 需要登录 */}
              <Route path="/dashboard" element={
                isAuthenticated ? (
                  <Layout>
                    <div className="p-6">
                      <h1 className="text-2xl font-bold text-gray-900 mb-4">欢迎来到非洲彩票平台</h1>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <div className="bg-white p-6 rounded-xl shadow-light">
                          <h2 className="text-lg font-semibold mb-2">11选5彩票</h2>
                          <p className="text-gray-600 mb-4">每期5分钟，天天开奖</p>
                          <a href="/games/lottery11x5" className="text-primary-600 hover:text-primary-700 font-medium">
                            立即投注 →
                          </a>
                        </div>
                        <div className="bg-white p-6 rounded-xl shadow-light">
                          <h2 className="text-lg font-semibold mb-2">我的钱包</h2>
                          <p className="text-gray-600 mb-4">管理您的资金</p>
                          <a href="/wallet" className="text-primary-600 hover:text-primary-700 font-medium">
                            查看详情 →
                          </a>
                        </div>
                        <div className="bg-white p-6 rounded-xl shadow-light">
                          <h2 className="text-lg font-semibold mb-2">VIP奖励</h2>
                          <p className="text-gray-600 mb-4">享受专属特权</p>
                          <a href="/rewards" className="text-primary-600 hover:text-primary-700 font-medium">
                            了解更多 →
                          </a>
                        </div>
                      </div>
                    </div>
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              <Route path="/wallet" element={
                isAuthenticated ? (
                  <Layout>
                    <WalletPage />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              <Route path="/wallet/deposit" element={
                isAuthenticated ? (
                  <Layout>
                    <DepositPage />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              <Route path="/wallet/withdraw" element={
                isAuthenticated ? (
                  <Layout>
                    <WithdrawPage />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              <Route path="/wallet/transactions" element={
                isAuthenticated ? (
                  <Layout>
                    <TransactionHistoryPage />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              <Route path="/games" element={
                isAuthenticated ? (
                  <Layout>
                    <GamesPage />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              <Route path="/games/lottery11x5" element={
                isAuthenticated ? (
                  <Layout>
                    <Lottery11x5Page />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              <Route path="/games/scratch" element={
                isAuthenticated ? (
                  <Layout>
                    <ScratchCardPage />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              <Route path="/games/superlotto" element={
                isAuthenticated ? (
                  <Layout>
                    <SuperLottoPage />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              <Route path="/games/sports" element={
                isAuthenticated ? (
                  <Layout>
                    <SportsPage />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              {/* 奖励系统路由 */}
              <Route path="/rewards/vip" element={
                isAuthenticated ? (
                  <Layout>
                    <VipPage />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              <Route path="/rewards/referral" element={
                isAuthenticated ? (
                  <Layout>
                    <ReferralPage />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              <Route path="/rewards/stats" element={
                isAuthenticated ? (
                  <Layout>
                    <RewardsStatsPage />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              <Route path="/rewards" element={
                isAuthenticated ? (
                  <Layout>
                    <RewardsPage />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              {/* 个人中心路由 */}
              <Route path="/profile" element={
                isAuthenticated ? (
                  <Layout>
                    <ProfilePage />
                  </Layout>
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              {/* 默认重定向 */}
              <Route path="/" element={
                isAuthenticated ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Navigate to="/auth/login" replace />
                )
              } />
              
              {/* 404页面 */}
              <Route path="*" element={
                <div className="min-h-screen flex items-center justify-center bg-gray-50">
                  <div className="text-center">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
                    <p className="text-gray-600 mb-8">页面未找到</p>
                    <a 
                      href={isAuthenticated ? "/dashboard" : "/auth/login"}
                      className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                    >
                      {isAuthenticated ? "返回首页" : "返回登录"}
                    </a>
                  </div>
                </div>
              } />
            </Routes>
            
    </div>
  )
}

export default App;