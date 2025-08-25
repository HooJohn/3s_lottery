import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import PullToRefresh from '@/components/common/PullToRefresh';
import { 
  TrendingUp, 
  Users, 
  Trophy, 
  Gift,
  Clock,
  Star,
  ArrowRight,
  Play,
  Zap,
  Target,
  Crown
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { cn } from '@/utils/cn';
import { formatCurrency, formatNumber } from '@/utils/format';

interface GameCard {
  id: string;
  name: string;
  description: string;
  image: string;
  href: string;
  isHot?: boolean;
  isNew?: boolean;
  jackpot?: number;
  nextDraw?: string;
}

interface Announcement {
  id: string;
  title: string;
  content: string;
  type: 'info' | 'warning' | 'success';
  createdAt: string;
}

interface LatestResult {
  game: string;
  drawNumber: string;
  numbers: number[];
  drawTime: string;
  jackpot: number;
}

const HomePage: React.FC = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [user] = useState({
    name: 'John Doe',
    balance: 15420.50,
    vipLevel: 2,
    totalWinnings: 45680.00,
    gamesPlayed: 156,
  });

  // 更新时间
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // 游戏卡片数据
  const gameCards: GameCard[] = [
    {
      id: '11x5',
      name: '11选5彩票',
      description: '每期5分钟，天天开奖',
      image: '/images/games/11x5.jpg',
      href: '/games/lottery11x5',
      isHot: true,
      jackpot: 1350000,
      nextDraw: '02:45:30',
    },
    {
      id: 'superlotto',
      name: '大乐透',
      description: '超级大奖等你来',
      image: '/images/games/superlotto.jpg',
      href: '/games/superlotto',
      jackpot: 50000000,
      nextDraw: '每周三、六',
    },
    {
      id: 'scratch',
      name: '刮刮乐',
      description: '即刮即中，惊喜不断',
      image: '/images/games/scratch.jpg',
      href: '/games/scratch',
      isNew: true,
    },
    {
      id: 'sports',
      name: '体育博彩',
      description: '精彩赛事，激情投注',
      image: '/images/games/sports.jpg',
      href: '/games/sports',
    },
  ];

  // 公告数据
  const announcements: Announcement[] = [
    {
      id: '1',
      title: '🎉 新用户注册送100奈拉体验金',
      content: '新用户完成注册即可获得100奈拉体验金，快来体验吧！',
      type: 'success',
      createdAt: '2024-01-21T10:00:00Z',
    },
    {
      id: '2',
      title: '⚡ 11选5彩票火热进行中',
      content: '每期5分钟开奖，奖池金额已达135万奈拉！',
      type: 'info',
      createdAt: '2024-01-21T09:30:00Z',
    },
    {
      id: '3',
      title: '🏆 VIP会员专享福利升级',
      content: 'VIP会员返水比例提升，更多专属特权等你解锁！',
      type: 'warning',
      createdAt: '2024-01-21T08:00:00Z',
    },
  ];

  // 最新开奖结果
  const latestResults: LatestResult[] = [
    {
      game: '11选5',
      drawNumber: '20240121-088',
      numbers: [1, 5, 8, 10, 11],
      drawTime: '2024-01-21T13:55:00Z',
      jackpot: 1350000,
    },
    {
      game: '大乐透',
      drawNumber: '24008',
      numbers: [5, 12, 18, 25, 33, 7, 11],
      drawTime: '2024-01-20T20:30:00Z',
      jackpot: 50000000,
    },
  ];

  // 统计数据
  const stats = [
    {
      label: '今日中奖用户',
      value: '2,847',
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      label: '今日派奖金额',
      value: formatCurrency(8945600),
      icon: Trophy,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      label: '在线用户',
      value: '15,234',
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      label: '累计奖池',
      value: formatCurrency(125000000),
      icon: Gift,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];

  // 下拉刷新处理
  const handleRefresh = async () => {
    // 模拟刷新数据
    await new Promise(resolve => setTimeout(resolve, 1500));
    console.log('首页数据已刷新');
  };

  return (
    <PullToRefresh onRefresh={handleRefresh} className="min-h-screen">
      <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
        {/* 欢迎横幅 - 移动端优化 */}
        <div className="bg-gradient-to-r from-primary-600 via-primary-500 to-secondary-500 text-white">
          <div className="container-responsive py-6 sm:py-8 container-mobile">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
              <div className="flex-1">
                <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold mb-2">
                  欢迎回来，{user.name}！
                </h1>
                <p className="text-primary-100 mb-3 sm:mb-4 text-sm sm:text-base">
                  {currentTime.toLocaleString('zh-CN', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
                <div className="flex flex-wrap items-center gap-3 sm:gap-4 text-xs sm:text-sm">
                  <div className="flex items-center space-x-1 touch-target">
                    <Crown className="w-3 h-3 sm:w-4 sm:h-4" />
                    <span>VIP{user.vipLevel}</span>
                  </div>
                  <div className="flex items-center space-x-1 touch-target">
                    <Trophy className="w-3 h-3 sm:w-4 sm:h-4" />
                    <span className="hidden sm:inline">总中奖: </span>
                    <span className="sm:hidden">中奖: </span>
                    <span>{formatCurrency(user.totalWinnings)}</span>
                  </div>
                  <div className="flex items-center space-x-1 touch-target">
                    <Target className="w-3 h-3 sm:w-4 sm:h-4" />
                    <span className="hidden sm:inline">游戏次数: </span>
                    <span className="sm:hidden">游戏: </span>
                    <span>{user.gamesPlayed}</span>
                  </div>
                </div>
              </div>
              <div className="text-center sm:text-right">
                <p className="text-primary-100 text-xs sm:text-sm mb-1">账户余额</p>
                <p className="text-2xl sm:text-3xl font-bold">{formatCurrency(user.balance)}</p>
                <div className="flex justify-center sm:justify-end space-x-2 mt-3">
                  <Link to="/wallet">
                    <Button variant="secondary" size="sm" touchOptimized className="btn-mobile">
                      充值
                    </Button>
                  </Link>
                  <Link to="/wallet">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      touchOptimized
                      className="text-white border-white hover:bg-white hover:text-primary-600 btn-mobile"
                    >
                      提现
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="container-responsive py-4 sm:py-6 space-y-6 sm:space-y-8 container-mobile">
          {/* 统计数据 - 移动端优化 */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <Card className="text-center card-mobile touch-feedback">
                    <CardContent className="p-3 sm:p-6">
                      <div className={cn('w-8 h-8 sm:w-12 sm:h-12 rounded-full flex items-center justify-center mx-auto mb-2 sm:mb-3', stat.bgColor)}>
                        <Icon className={cn('w-4 h-4 sm:w-6 sm:h-6', stat.color)} />
                      </div>
                      <p className="text-lg sm:text-2xl font-bold text-gray-900 mb-1">{stat.value}</p>
                      <p className="text-xs sm:text-sm text-gray-600">{stat.label}</p>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>

          {/* 热门游戏 - 移动端优化 */}
          <section>
            <div className="flex items-center justify-between mb-4 sm:mb-6">
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900">热门游戏</h2>
              <Link to="/games" className="text-primary-600 hover:text-primary-700 font-medium flex items-center touch-target">
                查看全部
                <ArrowRight className="w-3 h-3 sm:w-4 sm:h-4 ml-1" />
              </Link>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
              {gameCards.map((game, index) => (
                <motion.div
                  key={game.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <Link to={game.href}>
                    <Card className="game-card group cursor-pointer card-mobile touch-feedback">
                      <div className="relative">
                        <div className="h-32 sm:h-40 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-t-xl flex items-center justify-center">
                          <div className="text-white text-center">
                            <Play className="w-8 h-8 sm:w-12 sm:h-12 mx-auto mb-2" />
                            <h3 className="font-bold text-base sm:text-lg">{game.name}</h3>
                          </div>
                        </div>
                        
                        {/* 标签 */}
                        <div className="absolute top-2 sm:top-3 left-2 sm:left-3 flex space-x-1 sm:space-x-2">
                          {game.isHot && (
                            <span className="bg-danger-500 text-white text-xs px-2 py-1 rounded-full font-medium">
                              🔥 热门
                            </span>
                          )}
                          {game.isNew && (
                            <span className="bg-success-500 text-white text-xs px-2 py-1 rounded-full font-medium">
                              ✨ 新游戏
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <CardContent className="p-3 sm:p-4">
                        <p className="text-gray-600 text-xs sm:text-sm mb-2 sm:mb-3">{game.description}</p>
                        
                        {game.jackpot && (
                          <div className="mb-2 sm:mb-3">
                            <p className="text-xs text-gray-500 mb-1">奖池金额</p>
                            <p className="text-sm sm:text-lg font-bold text-primary-600">
                              ₦{(game.jackpot / 1000).toFixed(0)}K
                            </p>
                          </div>
                        )}
                        
                        {game.nextDraw && (
                          <div className="flex items-center text-xs text-gray-500 mb-3">
                            <Clock className="w-3 h-3 mr-1" />
                            <span>下期: {game.nextDraw}</span>
                          </div>
                        )}
                        
                        <Button
                          variant="primary"
                          size="sm"
                          fullWidth
                          touchOptimized
                          className="mt-2 sm:mt-4 group-hover:bg-primary-700 btn-mobile"
                        >
                          <Zap className="w-3 h-3 sm:w-4 sm:h-4 mr-2" />
                          立即游戏
                        </Button>
                      </CardContent>
                    </Card>
                  </Link>
                </motion.div>
              ))}
            </div>
          </section>

          {/* 最新开奖 - 移动端优化 */}
          <section>
            <div className="flex items-center justify-between mb-4 sm:mb-6">
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900">最新开奖</h2>
              <Link to="/results" className="text-primary-600 hover:text-primary-700 font-medium flex items-center touch-target">
                查看更多
                <ArrowRight className="w-3 h-3 sm:w-4 sm:h-4 ml-1" />
              </Link>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
              {latestResults.map((result, index) => (
                <motion.div
                  key={result.drawNumber}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.2 }}
                >
                  <Card className="card-mobile touch-feedback">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-gray-900 text-sm sm:text-base">{result.game}</h3>
                        <span className="text-xs sm:text-sm text-gray-500">期次: {result.drawNumber}</span>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-center space-x-1 sm:space-x-2 mb-3 sm:mb-4">
                        {result.numbers.map((number, idx) => (
                          <div
                            key={idx}
                            className={cn(
                              'w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center font-bold text-white text-xs sm:text-sm',
                              result.game === '11选5' 
                                ? 'bg-gradient-primary' 
                                : idx < 5 
                                ? 'bg-gradient-primary' 
                                : 'bg-gradient-secondary text-gray-900'
                            )}
                          >
                            {number.toString().padStart(2, '0')}
                          </div>
                        ))}
                      </div>
                      <div className="text-center text-xs sm:text-sm text-gray-600">
                        <p>开奖时间: {new Date(result.drawTime).toLocaleString('zh-CN')}</p>
                        <p className="mt-1">奖池: ₦{(result.jackpot / 1000).toFixed(0)}K</p>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </section>

          {/* 公告栏 - 移动端优化 */}
          <section>
            <div className="flex items-center justify-between mb-4 sm:mb-6">
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900">最新公告</h2>
            </div>
            
            <div className="space-y-3 sm:space-y-4">
              {announcements.map((announcement, index) => (
                <motion.div
                  key={announcement.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <Card className="hover:shadow-medium transition-shadow duration-200 card-mobile touch-feedback">
                    <CardContent className="p-3 sm:p-4">
                      <div className="flex items-start space-x-3">
                        <div className={cn(
                          'w-2 h-2 rounded-full mt-2 flex-shrink-0',
                          announcement.type === 'success' ? 'bg-success-500' :
                          announcement.type === 'warning' ? 'bg-warning-500' :
                          'bg-info-500'
                        )} />
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-gray-900 mb-1 text-sm sm:text-base">
                            {announcement.title}
                          </h3>
                          <p className="text-xs sm:text-sm text-gray-600 mb-2">
                            {announcement.content}
                          </p>
                          <p className="text-xs text-gray-500">
                            {new Date(announcement.createdAt).toLocaleString('zh-CN')}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </section>

          {/* 快速操作 - 移动端优化 */}
          <section>
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 sm:mb-6">快速操作</h2>
            
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
              {[
                { name: '充值', href: '/wallet', icon: '💰', color: 'bg-green-500' },
                { name: '提现', href: '/wallet', icon: '💸', color: 'bg-blue-500' },
                { name: 'VIP特权', href: '/rewards/vip', icon: '👑', color: 'bg-purple-500' },
                { name: '推荐好友', href: '/rewards/referral', icon: '🎁', color: 'bg-orange-500' },
              ].map((action, index) => (
                <motion.div
                  key={action.name}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Link to={action.href}>
                    <Card className="text-center hover:shadow-medium transition-all duration-200 hover:-translate-y-1 card-mobile touch-feedback">
                      <CardContent className="p-4 sm:p-6">
                        <div className={cn('w-10 h-10 sm:w-12 sm:h-12 rounded-full flex items-center justify-center mx-auto mb-2 sm:mb-3 text-white text-lg sm:text-xl', action.color)}>
                          {action.icon}
                        </div>
                        <p className="font-medium text-gray-900 text-sm sm:text-base">{action.name}</p>
                      </CardContent>
                    </Card>
                  </Link>
                </motion.div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </PullToRefresh>
  );
};

export default HomePage;