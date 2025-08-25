import React from 'react';
import { motion } from 'framer-motion';
import { 
  Crown, 
  Users, 
  Gift, 
  TrendingUp, 
  Star,
  Award,
  ArrowRight,
  DollarSign,
  Target,
  Zap,
  Gamepad2
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { formatCurrency } from '@/utils/format';

interface RewardsSummary {
  vip_level: number;
  vip_name: string;
  current_rebate_rate: number;
  daily_rebate: number;
  total_rebate: number;
  total_referrals: number;
  active_referrals: number;
  total_commission: number;
  monthly_commission: number;
  total_rewards: number;
}

const RewardsPage: React.FC = () => {
  // 模拟奖励统计数据
  const rewardsSummary: RewardsSummary = {
    vip_level: 2,
    vip_name: 'VIP2',
    current_rebate_rate: 0.52,
    daily_rebate: 125,
    total_rebate: 8500,
    total_referrals: 397,
    active_referrals: 285,
    total_commission: 22380,
    monthly_commission: 3250,
    total_rewards: 30880 // total_rebate + total_commission
  };

  // 奖励功能卡片
  const rewardFeatures = [
    {
      title: 'VIP会员中心',
      description: '专享特权，丰厚返水',
      icon: Crown,
      color: 'text-primary-600',
      bgColor: 'bg-primary-50',
      borderColor: 'border-primary-200',
      href: '/rewards/vip',
      stats: [
        { label: '当前等级', value: rewardsSummary.vip_name },
        { label: '返水比例', value: `${rewardsSummary.current_rebate_rate}%` },
        { label: '今日返水', value: formatCurrency(rewardsSummary.daily_rebate) }
      ]
    },
    {
      title: '推荐奖励',
      description: '邀请好友，共享收益',
      icon: Users,
      color: 'text-success-600',
      bgColor: 'bg-success-50',
      borderColor: 'border-success-200',
      href: '/rewards/referral',
      stats: [
        { label: '推荐人数', value: rewardsSummary.total_referrals.toString() },
        { label: '本月佣金', value: formatCurrency(rewardsSummary.monthly_commission) },
        { label: '累计佣金', value: formatCurrency(rewardsSummary.total_commission) }
      ]
    }
  ];

  // 最近奖励记录
  const recentRewards = [
    {
      id: '1',
      type: 'rebate',
      title: 'VIP返水奖励',
      amount: 27.04,
      date: '2024-01-21',
      icon: Gift,
      color: 'text-primary-600'
    },
    {
      id: '2',
      type: 'commission',
      title: '推荐佣金',
      amount: 156.00,
      date: '2024-01-21',
      icon: Users,
      color: 'text-success-600'
    },
    {
      id: '3',
      type: 'rebate',
      title: 'VIP返水奖励',
      amount: 44.20,
      date: '2024-01-20',
      icon: Gift,
      color: 'text-primary-600'
    },
    {
      id: '4',
      type: 'commission',
      title: '推荐佣金',
      amount: 76.00,
      date: '2024-01-20',
      icon: Users,
      color: 'text-success-600'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
      {/* 页面头部 */}
      <div className="bg-gradient-to-r from-primary-600 to-success-600 text-white px-4 py-8 lg:px-6">
        <div className="container-responsive">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="text-center">
              <h1 className="text-3xl font-bold mb-2 flex items-center justify-center">
                <Award className="w-8 h-8 mr-3" />
                奖励中心
              </h1>
              <p className="text-white text-opacity-80 text-lg mb-6">
                VIP返水 + 推荐佣金，双重奖励等您来拿
              </p>
              
              {/* 总奖励统计 */}
              <div className="bg-white bg-opacity-10 rounded-2xl p-6 backdrop-blur-sm">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <TrendingUp className="w-6 h-6 mr-2" />
                      <span className="text-sm opacity-80">累计奖励</span>
                    </div>
                    <p className="text-3xl font-bold">
                      {formatCurrency(rewardsSummary.total_rewards)}
                    </p>
                  </div>
                  
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <Gift className="w-6 h-6 mr-2" />
                      <span className="text-sm opacity-80">VIP返水</span>
                    </div>
                    <p className="text-2xl font-bold">
                      {formatCurrency(rewardsSummary.total_rebate)}
                    </p>
                  </div>
                  
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <Users className="w-6 h-6 mr-2" />
                      <span className="text-sm opacity-80">推荐佣金</span>
                    </div>
                    <p className="text-2xl font-bold">
                      {formatCurrency(rewardsSummary.total_commission)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      <div className="container-responsive py-6 space-y-6">
        {/* 奖励功能卡片 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        >
          {rewardFeatures.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }}
              >
                <Card className={`hover:shadow-heavy transition-all duration-300 border-2 ${feature.borderColor} ${feature.bgColor}`}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${feature.bgColor}`}>
                          <Icon className={`w-6 h-6 ${feature.color}`} />
                        </div>
                        <div>
                          <h3 className="text-xl font-bold text-gray-900">
                            {feature.title}
                          </h3>
                          <p className="text-gray-600">
                            {feature.description}
                          </p>
                        </div>
                      </div>
                      <ArrowRight className={`w-5 h-5 ${feature.color}`} />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      {feature.stats.map((stat, statIndex) => (
                        <div key={statIndex} className="text-center">
                          <p className="text-xs text-gray-500 mb-1">{stat.label}</p>
                          <p className="font-bold text-gray-900">{stat.value}</p>
                        </div>
                      ))}
                    </div>
                    <Button
                      variant="primary"
                      fullWidth
                      icon={<ArrowRight className="w-4 h-4" />}
                      onClick={() => window.location.href = feature.href}
                    >
                      立即查看
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>

        {/* 奖励规则说明 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                <Target className="w-5 h-5 mr-2 text-warning-600" />
                奖励规则
              </h2>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* VIP返水规则 */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <Crown className="w-4 h-4 mr-2 text-primary-600" />
                    VIP返水规则
                  </h3>
                  <div className="space-y-2 text-sm text-gray-600">
                    <p>• 根据VIP等级享受不同返水比例（0.38%-0.80%）</p>
                    <p>• 基于有效流水自动计算，每日结算发放</p>
                    <p>• 最低有效流水1NGN起计算返水</p>
                    <p>• VIP等级越高，返水比例越高</p>
                  </div>
                </div>

                {/* 推荐佣金规则 */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                    <Users className="w-4 h-4 mr-2 text-success-600" />
                    推荐佣金规则
                  </h3>
                  <div className="space-y-2 text-sm text-gray-600">
                    <p>• 7级推荐奖励，总佣金率高达7.6%</p>
                    <p>• 一级3%，二级2%，三级1%，四级0.7%</p>
                    <p>• 五级0.5%，六级0.3%，七级0.1%</p>
                    <p>• 基于下级用户有效流水计算佣金</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 最近奖励记录 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">
                  最近奖励
                </h2>
                <Button
                  variant="outline"
                  size="sm"
                  icon={<ArrowRight className="w-4 h-4" />}
                  onClick={() => window.location.href = '/rewards/stats'}
                >
                  查看统计
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              {recentRewards.length === 0 ? (
                <div className="text-center py-8">
                  <Gift className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">暂无奖励记录</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {recentRewards.map((reward) => {
                    const Icon = reward.icon;
                    return (
                      <div key={reward.id} className="p-4 hover:bg-gray-50 transition-colors">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                              reward.type === 'rebate' ? 'bg-primary-100' : 'bg-success-100'
                            }`}>
                              <Icon className={`w-5 h-5 ${reward.color}`} />
                            </div>
                            <div>
                              <p className="font-medium text-gray-900">
                                {reward.title}
                              </p>
                              <p className="text-sm text-gray-500">
                                {reward.date}
                              </p>
                            </div>
                          </div>
                          
                          <div className="text-right">
                            <p className="text-lg font-bold text-success-600">
                              +{formatCurrency(reward.amount)}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* 快速操作 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <Card className="bg-gradient-to-r from-primary-50 to-success-50 border-primary-200">
            <CardContent className="p-6">
              <div className="text-center">
                <Zap className="w-12 h-12 text-primary-600 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  开始赚取奖励
                </h3>
                <p className="text-gray-600 mb-6">
                  立即投注提升VIP等级，邀请好友获得推荐佣金
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Button
                    variant="primary"
                    icon={<Gamepad2 className="w-4 h-4" />}
                    onClick={() => window.location.href = '/games'}
                  >
                    立即投注
                  </Button>
                  <Button
                    variant="outline"
                    icon={<Users className="w-4 h-4" />}
                    onClick={() => window.location.href = '/rewards/referral'}
                  >
                    邀请好友
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default RewardsPage;