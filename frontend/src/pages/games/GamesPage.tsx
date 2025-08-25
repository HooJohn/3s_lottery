import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Gamepad2, 
  Trophy, 
  Clock, 
  TrendingUp, 
  Star,
  Play,
  Pause,
  Settings,
  BarChart3,
  Users,
  Zap,
  Gift,
  Target,
  Dice1,
  Target as Football,
  Sparkles
} from 'lucide-react';

import { Card, CardContent, CardHeader, GameCard } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/format';

interface GameInfo {
  id: string;
  name: string;
  description: string;
  path: string;
  icon: React.ComponentType<any>;
  status: 'active' | 'maintenance' | 'inactive';
  badge?: string;
  stats: {
    players: number;
    jackpot: number;
    nextDraw?: string;
  };
  features: string[];
}

const GamesPage: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState('all');

  // 游戏列表
  const games: GameInfo[] = [
    {
      id: 'lottery11x5',
      name: '11选5彩票',
      description: '每期5分钟，天天开奖，简单易玩',
      path: '/games/lottery11x5',
      icon: Target,
      status: 'active',
      badge: '热门',
      stats: {
        players: 1250,
        jackpot: 125000,
        nextDraw: '2分30秒'
      },
      features: ['5分钟一期', '多种玩法', '高中奖率']
    },
    {
      id: 'superlotto',
      name: '大乐透',
      description: '亿元大奖等你来，每周三、六、日开奖',
      path: '/games/superlotto',
      icon: Trophy,
      status: 'active',
      badge: '大奖',
      stats: {
        players: 3420,
        jackpot: 120000000,
        nextDraw: '2天15小时'
      },
      features: ['亿元大奖', '全国联销', '35选5+12选2']
    },
    {
      id: 'scratch',
      name: '666刮刮乐',
      description: '刮开惊喜，即时中奖，多种面值可选',
      path: '/games/scratch',
      icon: Sparkles,
      status: 'active',
      stats: {
        players: 890,
        jackpot: 50000,
      },
      features: ['即时开奖', '多种面值', '趣味性强']
    },
    {
      id: 'sports',
      name: '体育博彩',
      description: '多平台体育投注，精彩赛事不容错过',
      path: '/games/sports',
      icon: Football,
      status: 'active',
      badge: '新上线',
      stats: {
        players: 2100,
        jackpot: 0,
      },
      features: ['多平台接入', '实时赔率', '丰富赛事']
    }
  ];

  // 分类选项
  const categories = [
    { key: 'all', label: '全部游戏', icon: Gamepad2 },
    { key: 'lottery', label: '彩票游戏', icon: Target },
    { key: 'instant', label: '即时游戏', icon: Zap },
    { key: 'sports', label: '体育博彩', icon: Football },
  ];

  // 筛选游戏
  const filteredGames = games.filter(game => {
    if (activeCategory === 'all') return true;
    if (activeCategory === 'lottery') return ['lottery11x5', 'superlotto'].includes(game.id);
    if (activeCategory === 'instant') return game.id === 'scratch';
    if (activeCategory === 'sports') return game.id === 'sports';
    return true;
  });

  // 统计数据
  const totalStats = {
    totalPlayers: games.reduce((sum, game) => sum + game.stats.players, 0),
    totalJackpot: games.reduce((sum, game) => sum + game.stats.jackpot, 0),
    activeGames: games.filter(game => game.status === 'active').length,
    hotGames: games.filter(game => game.badge === '热门').length,
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
      {/* 页面头部 */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white px-4 py-8 lg:px-6">
        <div className="container-responsive">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2">游戏中心</h1>
                <p className="text-white text-opacity-80 text-lg">
                  精彩游戏，丰厚奖励，尽在非洲彩票平台
                </p>
              </div>
              <div className="hidden lg:block">
                <Gamepad2 className="w-16 h-16 text-white text-opacity-30" />
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* 统计概览 */}
      <div className="container-responsive py-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card className="bg-gradient-to-r from-primary-50 to-secondary-50 border-primary-200">
            <CardContent className="p-6">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Users className="w-6 h-6 text-primary-600 mr-2" />
                    <span className="text-sm text-gray-600">在线玩家</span>
                  </div>
                  <p className="text-2xl font-bold text-primary-700">
                    {totalStats.totalPlayers.toLocaleString()}
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Gift className="w-6 h-6 text-secondary-600 mr-2" />
                    <span className="text-sm text-gray-600">总奖池</span>
                  </div>
                  <p className="text-2xl font-bold text-secondary-700">
                    {formatCurrency(totalStats.totalJackpot)}
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Play className="w-6 h-6 text-success-600 mr-2" />
                    <span className="text-sm text-gray-600">可用游戏</span>
                  </div>
                  <p className="text-2xl font-bold text-success-700">
                    {totalStats.activeGames}
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Star className="w-6 h-6 text-warning-600 mr-2" />
                    <span className="text-sm text-gray-600">热门游戏</span>
                  </div>
                  <p className="text-2xl font-bold text-warning-700">
                    {totalStats.hotGames}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* 分类筛选 */}
      <div className="container-responsive mb-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="flex space-x-2 overflow-x-auto pb-2">
            {categories.map((category) => {
              const Icon = category.icon;
              return (
                <button
                  key={category.key}
                  onClick={() => setActiveCategory(category.key)}
                  className={cn(
                    'flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 whitespace-nowrap',
                    activeCategory === category.key
                      ? 'bg-primary-600 text-white shadow-medium'
                      : 'bg-white text-gray-600 hover:bg-gray-50 hover:text-gray-900 shadow-light'
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span>{category.label}</span>
                </button>
              );
            })}
          </div>
        </motion.div>
      </div>

      {/* 游戏列表 */}
      <div className="container-responsive">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {filteredGames.map((game, index) => (
            <motion.div
              key={game.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 * index }}
            >
              <Card className="overflow-hidden hover:shadow-heavy hover:-translate-y-2 transition-all duration-300 group">
                <div className="relative">
                  {/* 游戏图标区域 */}
                  <div className="h-32 bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center relative overflow-hidden">
                    <game.icon className="w-16 h-16 text-white opacity-80 group-hover:scale-110 transition-transform duration-300" />
                    
                    {/* 状态徽章 */}
                    {game.status !== 'active' && (
                      <div className={cn(
                        'absolute top-3 right-3 px-2 py-1 rounded-full text-xs font-semibold text-white',
                        game.status === 'maintenance' ? 'bg-warning-500' : 'bg-gray-500'
                      )}>
                        {game.status === 'maintenance' ? '维护中' : '暂停'}
                      </div>
                    )}
                    
                    {/* 自定义徽章 */}
                    {game.badge && game.status === 'active' && (
                      <div className="absolute top-3 right-3 px-2 py-1 rounded-full text-xs font-semibold bg-secondary-500 text-gray-900">
                        {game.badge}
                      </div>
                    )}
                    
                    {/* 悬停遮罩 */}
                    <div className="absolute inset-0 bg-black opacity-0 group-hover:opacity-20 transition-opacity duration-300" />
                  </div>
                  
                  {/* 游戏信息 */}
                  <CardContent className="p-6">
                    <div className="mb-4">
                      <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                        {game.name}
                      </h3>
                      <p className="text-gray-600 text-sm line-clamp-2">
                        {game.description}
                      </p>
                    </div>
                    
                    {/* 游戏统计 */}
                    <div className="space-y-3 mb-4">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">在线玩家</span>
                        <span className="font-medium text-gray-900">
                          {game.stats.players.toLocaleString()}
                        </span>
                      </div>
                      
                      {game.stats.jackpot > 0 && (
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-500">奖池金额</span>
                          <span className="font-bold text-primary-600">
                            {formatCurrency(game.stats.jackpot)}
                          </span>
                        </div>
                      )}
                      
                      {game.stats.nextDraw && (
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-500">下期开奖</span>
                          <span className="font-medium text-danger-600">
                            {game.stats.nextDraw}
                          </span>
                        </div>
                      )}
                    </div>
                    
                    {/* 游戏特色 */}
                    <div className="mb-4">
                      <div className="flex flex-wrap gap-2">
                        {game.features.map((feature, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center px-2 py-1 rounded-md bg-gray-100 text-gray-700 text-xs"
                          >
                            {feature}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    {/* 操作按钮 */}
                    <div className="flex space-x-3">
                      <Button
                        variant="primary"
                        size="sm"
                        fullWidth
                        icon={<Play className="w-4 h-4" />}
                        onClick={() => window.location.href = game.path}
                        disabled={game.status !== 'active'}
                      >
                        {game.status === 'maintenance' ? '维护中' : 
                         game.status === 'inactive' ? '暂停服务' : '立即游戏'}
                      </Button>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        icon={<BarChart3 className="w-4 h-4" />}
                        disabled={game.status !== 'active'}
                      >
                        统计
                      </Button>
                    </div>
                  </CardContent>
                </div>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* 游戏公告 */}
      <div className="container-responsive py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">
                  游戏公告
                </h2>
                <Button variant="ghost" size="sm">
                  查看更多
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="text-gray-900 font-medium">11选5彩票系统升级完成</p>
                    <p className="text-gray-600 text-sm mt-1">
                      新增多种投注方式，优化用户体验，欢迎体验！
                    </p>
                    <p className="text-gray-400 text-xs mt-2">2024-01-20 10:30</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-secondary-500 rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="text-gray-900 font-medium">大乐透奖池突破1.2亿</p>
                    <p className="text-gray-600 text-sm mt-1">
                      本期大乐透奖池金额已突破1.2亿，机会难得，快来投注！
                    </p>
                    <p className="text-gray-400 text-xs mt-2">2024-01-19 15:45</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-success-500 rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <p className="text-gray-900 font-medium">体育博彩平台正式上线</p>
                    <p className="text-gray-600 text-sm mt-1">
                      多平台体育投注现已开放，支持足球、篮球等多种体育赛事。
                    </p>
                    <p className="text-gray-400 text-xs mt-2">2024-01-18 09:00</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default GamesPage;