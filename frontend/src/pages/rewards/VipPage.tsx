import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Crown, 
  Star, 
  Gift, 
  TrendingUp, 
  Wallet, 
  Clock,
  Users,
  Award,
  Zap,
  Target,
  ArrowRight,
  CheckCircle,
  Lock,
  Trophy
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/format';

interface VIPLevel {
  level: number;
  name: string;
  required_turnover: number;
  rebate_rate: number;
  daily_withdraw_limit: number;
  daily_withdraw_times: number;
  withdraw_fee_rate: number;
  color: string;
  bgColor: string;
  icon: React.ComponentType<any>;
}

interface UserVIPInfo {
  current_level: number;
  total_turnover: number;
  current_rebate_rate: number;
  daily_rebate_amount: number;
  total_rebate_received: number;
  next_level_progress: number;
  remaining_turnover: number;
}

const VipPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('levels');

  // VIP等级配置
  const vipLevels: VIPLevel[] = [
    {
      level: 0,
      name: 'VIP0',
      required_turnover: 0,
      rebate_rate: 0.38,
      daily_withdraw_limit: 50000,
      daily_withdraw_times: 3,
      withdraw_fee_rate: 2.0,
      color: 'text-gray-600',
      bgColor: 'bg-gray-100',
      icon: Users
    },
    {
      level: 1,
      name: 'VIP1',
      required_turnover: 10000,
      rebate_rate: 0.45,
      daily_withdraw_limit: 100000,
      daily_withdraw_times: 4,
      withdraw_fee_rate: 1.8,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      icon: Star
    },
    {
      level: 2,
      name: 'VIP2',
      required_turnover: 50000,
      rebate_rate: 0.52,
      daily_withdraw_limit: 200000,
      daily_withdraw_times: 5,
      withdraw_fee_rate: 1.5,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      icon: Award
    },
    {
      level: 3,
      name: 'VIP3',
      required_turnover: 200000,
      rebate_rate: 0.60,
      daily_withdraw_limit: 500000,
      daily_withdraw_times: 6,
      withdraw_fee_rate: 1.2,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
      icon: Trophy
    },
    {
      level: 4,
      name: 'VIP4',
      required_turnover: 500000,
      rebate_rate: 0.68,
      daily_withdraw_limit: 1000000,
      daily_withdraw_times: 8,
      withdraw_fee_rate: 1.0,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      icon: Target
    },
    {
      level: 5,
      name: 'VIP5',
      required_turnover: 1000000,
      rebate_rate: 0.75,
      daily_withdraw_limit: 2000000,
      daily_withdraw_times: 10,
      withdraw_fee_rate: 0.5,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      icon: Zap
    },
    {
      level: 6,
      name: 'VIP6',
      required_turnover: 2000000,
      rebate_rate: 0.78,
      daily_withdraw_limit: 5000000,
      daily_withdraw_times: 15,
      withdraw_fee_rate: 0.2,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      icon: Crown
    },
    {
      level: 7,
      name: 'VIP7',
      required_turnover: 5000000,
      rebate_rate: 0.80,
      daily_withdraw_limit: 10000000,
      daily_withdraw_times: 20,
      withdraw_fee_rate: 0,
      color: 'text-gradient-primary',
      bgColor: 'bg-gradient-to-r from-primary-100 to-secondary-100',
      icon: Crown
    }
  ];

  // 模拟用户VIP信息
  const userVipInfo: UserVIPInfo = {
    current_level: 2,
    total_turnover: 75000,
    current_rebate_rate: 0.52,
    daily_rebate_amount: 125,
    total_rebate_received: 8500,
    next_level_progress: 37.5, // (75000 - 50000) / (200000 - 50000) * 100
    remaining_turnover: 125000 // 200000 - 75000
  };

  const currentLevel = vipLevels[userVipInfo.current_level];
  const nextLevel = vipLevels[userVipInfo.current_level + 1];

  // 返水记录数据
  const rebateRecords = [
    {
      id: '1',
      date: '2024-01-21',
      turnover: 5200,
      rebate_rate: 0.52,
      rebate_amount: 27.04,
      status: 'completed'
    },
    {
      id: '2',
      date: '2024-01-20',
      turnover: 8500,
      rebate_rate: 0.52,
      rebate_amount: 44.20,
      status: 'completed'
    },
    {
      id: '3',
      date: '2024-01-19',
      turnover: 3200,
      rebate_rate: 0.52,
      rebate_amount: 16.64,
      status: 'completed'
    },
    {
      id: '4',
      date: '2024-01-18',
      turnover: 6800,
      rebate_rate: 0.52,
      rebate_amount: 35.36,
      status: 'pending'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
      {/* 页面头部 */}
      <div className="bg-gradient-to-r from-primary-600 to-secondary-600 text-white px-4 py-8 lg:px-6">
        <div className="container-responsive">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2 flex items-center">
                  <Crown className="w-8 h-8 mr-3" />
                  VIP会员中心
                </h1>
                <p className="text-white text-opacity-80 text-lg">
                  专享特权，丰厚返水，尊贵体验
                </p>
              </div>
              <div className="hidden lg:block">
                <div className="text-right">
                  <p className="text-white text-opacity-80 text-sm">当前等级</p>
                  <div className="flex items-center justify-end">
                    <currentLevel.icon className="w-6 h-6 mr-2" />
                    <span className="text-2xl font-bold">{currentLevel.name}</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* 用户VIP状态卡片 */}
      <div className="container-responsive py-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card className="bg-gradient-to-r from-primary-50 to-secondary-50 border-primary-200">
            <CardContent className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* 当前等级信息 */}
                <div className="text-center lg:text-left">
                  <div className="flex items-center justify-center lg:justify-start mb-3">
                    <div className={cn('w-12 h-12 rounded-full flex items-center justify-center mr-3', currentLevel.bgColor)}>
                      <currentLevel.icon className={cn('w-6 h-6', currentLevel.color)} />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">{currentLevel.name}</h3>
                      <p className="text-sm text-gray-600">当前等级</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">返水比例</p>
                      <p className="font-bold text-primary-600">{currentLevel.rebate_rate}%</p>
                    </div>
                    <div>
                      <p className="text-gray-500">日提款次数</p>
                      <p className="font-bold text-gray-900">{currentLevel.daily_withdraw_times}次</p>
                    </div>
                  </div>
                </div>

                {/* 升级进度 */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">升级进度</span>
                    <span className="text-sm font-medium text-primary-600">
                      {userVipInfo.next_level_progress.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${userVipInfo.next_level_progress}%` }}
                      transition={{ duration: 1, delay: 0.5 }}
                      className="bg-gradient-to-r from-primary-500 to-secondary-500 h-3 rounded-full"
                    />
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <div>
                      <p className="text-gray-500">当前流水</p>
                      <p className="font-bold text-gray-900">
                        {formatCurrency(userVipInfo.total_turnover)}
                      </p>
                    </div>
                    {nextLevel && (
                      <div className="text-right">
                        <p className="text-gray-500">升级还需</p>
                        <p className="font-bold text-primary-600">
                          {formatCurrency(userVipInfo.remaining_turnover)}
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* 返水统计 */}
                <div className="text-center lg:text-right">
                  <div className="grid grid-cols-1 gap-4">
                    <div>
                      <p className="text-gray-500 text-sm">今日返水</p>
                      <p className="text-2xl font-bold text-success-600">
                        {formatCurrency(userVipInfo.daily_rebate_amount)}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500 text-sm">累计返水</p>
                      <p className="text-xl font-bold text-gray-900">
                        {formatCurrency(userVipInfo.total_rebate_received)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* 标签切换 */}
      <div className="container-responsive mb-6">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('levels')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              activeTab === 'levels'
                ? 'bg-white text-primary-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            VIP等级
          </button>
          <button
            onClick={() => setActiveTab('rebate')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              activeTab === 'rebate'
                ? 'bg-white text-primary-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            返水记录
          </button>
          <button
            onClick={() => setActiveTab('benefits')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              activeTab === 'benefits'
                ? 'bg-white text-primary-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            会员特权
          </button>
        </div>
      </div>

      <div className="container-responsive space-y-6">
        {/* VIP等级标签 */}
        {activeTab === 'levels' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
          >
            {vipLevels.map((level, index) => {
              const Icon = level.icon;
              const isCurrentLevel = level.level === userVipInfo.current_level;
              const isUnlocked = level.level <= userVipInfo.current_level;
              
              return (
                <motion.div
                  key={level.level}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <Card className={cn(
                    'relative overflow-hidden transition-all duration-300',
                    isCurrentLevel 
                      ? 'ring-2 ring-primary-500 shadow-heavy transform scale-105' 
                      : 'hover:shadow-medium',
                    !isUnlocked && 'opacity-60'
                  )}>
                    {isCurrentLevel && (
                      <div className="absolute top-0 right-0 bg-primary-500 text-white px-2 py-1 text-xs font-bold rounded-bl-lg">
                        当前
                      </div>
                    )}
                    
                    <CardContent className="p-6 text-center">
                      <div className={cn('w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center', level.bgColor)}>
                        <Icon className={cn('w-8 h-8', level.color)} />
                      </div>
                      
                      <h3 className="text-xl font-bold text-gray-900 mb-2">
                        {level.name}
                      </h3>
                      
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-500">所需流水:</span>
                          <span className="font-medium">
                            {level.required_turnover === 0 ? '无要求' : formatCurrency(level.required_turnover)}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-500">返水比例:</span>
                          <span className="font-bold text-primary-600">
                            {level.rebate_rate}%
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-500">日提款限额:</span>
                          <span className="font-medium">
                            {formatCurrency(level.daily_withdraw_limit)}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-500">提现手续费:</span>
                          <span className="font-medium">
                            {level.withdraw_fee_rate === 0 ? '免费' : `${level.withdraw_fee_rate}%`}
                          </span>
                        </div>
                      </div>
                      
                      {!isUnlocked && (
                        <div className="mt-4 flex items-center justify-center text-gray-400">
                          <Lock className="w-4 h-4 mr-1" />
                          <span className="text-xs">未解锁</span>
                        </div>
                      )}
                      
                      {isCurrentLevel && (
                        <div className="mt-4">
                          <Button variant="primary" size="sm" fullWidth>
                            当前等级
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </motion.div>
        )}

        {/* 返水记录标签 */}
        {activeTab === 'rebate' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">
                    返水记录
                  </h2>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <TrendingUp className="w-4 h-4" />
                    <span>最近30天</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                {rebateRecords.length === 0 ? (
                  <div className="text-center py-8">
                    <Gift className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">暂无返水记录</p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-200">
                    {rebateRecords.map((record) => (
                      <div key={record.id} className="p-4 hover:bg-gray-50 transition-colors">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-success-100 text-success-600 rounded-full flex items-center justify-center">
                              <Gift className="w-5 h-5" />
                            </div>
                            <div>
                              <p className="font-medium text-gray-900">
                                日返水奖励
                              </p>
                              <p className="text-sm text-gray-500">
                                {record.date} • 流水: {formatCurrency(record.turnover)}
                              </p>
                            </div>
                          </div>
                          
                          <div className="text-right">
                            <p className="text-lg font-bold text-success-600">
                              +{formatCurrency(record.rebate_amount)}
                            </p>
                            <div className="flex items-center">
                              <span className="text-xs text-gray-500 mr-2">
                                {record.rebate_rate}% 返水
                              </span>
                              {record.status === 'completed' ? (
                                <CheckCircle className="w-4 h-4 text-success-500" />
                              ) : (
                                <Clock className="w-4 h-4 text-warning-500" />
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* 会员特权标签 */}
        {activeTab === 'benefits' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            {/* 专属特权 */}
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Star className="w-5 h-5 mr-2 text-primary-600" />
                  专属特权
                </h3>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { icon: TrendingUp, title: '每日返水', desc: `${currentLevel.rebate_rate}% 流水返水，每日自动发放` },
                    { icon: Wallet, title: '提款特权', desc: `每日可提款 ${currentLevel.daily_withdraw_times} 次，限额 ${formatCurrency(currentLevel.daily_withdraw_limit)}` },
                    { icon: Gift, title: '手续费优惠', desc: `提现手续费仅 ${currentLevel.withdraw_fee_rate === 0 ? '免费' : currentLevel.withdraw_fee_rate + '%'}` },
                    { icon: Users, title: '专属客服', desc: 'VIP专属客服通道，优先处理问题' },
                  ].map((benefit, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center flex-shrink-0">
                        <benefit.icon className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{benefit.title}</p>
                        <p className="text-sm text-gray-600">{benefit.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 升级奖励 */}
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Award className="w-5 h-5 mr-2 text-secondary-600" />
                  升级奖励
                </h3>
              </CardHeader>
              <CardContent>
                {nextLevel ? (
                  <div className="space-y-4">
                    <div className="text-center p-4 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg">
                      <nextLevel.icon className={cn('w-12 h-12 mx-auto mb-2', nextLevel.color)} />
                      <h4 className="font-bold text-gray-900 mb-1">升级到 {nextLevel.name}</h4>
                      <p className="text-sm text-gray-600 mb-3">
                        还需流水 {formatCurrency(userVipInfo.remaining_turnover)}
                      </p>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-primary-500 to-secondary-500 h-2 rounded-full"
                          style={{ width: `${userVipInfo.next_level_progress}%` }}
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">返水比例提升:</span>
                        <span className="font-bold text-success-600">
                          {currentLevel.rebate_rate}% → {nextLevel.rebate_rate}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">日提款次数:</span>
                        <span className="font-bold text-primary-600">
                          {currentLevel.daily_withdraw_times} → {nextLevel.daily_withdraw_times} 次
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">手续费降低:</span>
                        <span className="font-bold text-success-600">
                          {currentLevel.withdraw_fee_rate}% → {nextLevel.withdraw_fee_rate === 0 ? '免费' : nextLevel.withdraw_fee_rate + '%'}
                        </span>
                      </div>
                    </div>
                    
                    <Button variant="primary" fullWidth icon={<ArrowRight className="w-4 h-4" />}>
                      立即投注升级
                    </Button>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Crown className="w-12 h-12 text-primary-600 mx-auto mb-4" />
                    <h4 className="font-bold text-gray-900 mb-2">已达最高等级</h4>
                    <p className="text-gray-600">
                      恭喜您已达到最高VIP等级，享受所有专属特权！
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default VipPage;