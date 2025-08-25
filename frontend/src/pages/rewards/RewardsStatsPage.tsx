import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  Calendar, 
  Filter,
  Download,
  Eye,
  Gift,
  Users,
  Crown,
  DollarSign,
  ArrowUp,
  ArrowDown,
  Minus
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/format';

interface RewardStats {
  period: string;
  vip_rebate: number;
  referral_commission: number;
  total_rewards: number;
  change_percentage: number;
  change_type: 'increase' | 'decrease' | 'stable';
}

interface MonthlyBreakdown {
  month: string;
  vip_rebate: number;
  referral_commission: number;
  total_rewards: number;
  days_active: number;
}

const RewardsStatsPage: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('7days');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // 时间周期选项
  const periodOptions = [
    { value: '7days', label: '最近7天' },
    { value: '30days', label: '最近30天' },
    { value: '3months', label: '最近3个月' },
    { value: '6months', label: '最近6个月' },
    { value: '1year', label: '最近1年' }
  ];

  // 奖励类别选项
  const categoryOptions = [
    { value: 'all', label: '全部奖励' },
    { value: 'vip', label: 'VIP返水' },
    { value: 'referral', label: '推荐佣金' }
  ];

  // 奖励统计数据
  const rewardStats: RewardStats[] = [
    {
      period: '今日',
      vip_rebate: 125.50,
      referral_commission: 280.00,
      total_rewards: 405.50,
      change_percentage: 15.2,
      change_type: 'increase'
    },
    {
      period: '昨日',
      vip_rebate: 98.30,
      referral_commission: 245.00,
      total_rewards: 343.30,
      change_percentage: -8.5,
      change_type: 'decrease'
    },
    {
      period: '本周',
      vip_rebate: 875.20,
      referral_commission: 1650.00,
      total_rewards: 2525.20,
      change_percentage: 22.8,
      change_type: 'increase'
    },
    {
      period: '本月',
      vip_rebate: 3250.80,
      referral_commission: 6800.00,
      total_rewards: 10050.80,
      change_percentage: 18.5,
      change_type: 'increase'
    }
  ];

  // 月度奖励明细
  const monthlyBreakdown: MonthlyBreakdown[] = [
    {
      month: '2024年1月',
      vip_rebate: 3250.80,
      referral_commission: 6800.00,
      total_rewards: 10050.80,
      days_active: 21
    },
    {
      month: '2023年12月',
      vip_rebate: 2890.50,
      referral_commission: 5420.00,
      total_rewards: 8310.50,
      days_active: 25
    },
    {
      month: '2023年11月',
      vip_rebate: 2650.30,
      referral_commission: 4980.00,
      total_rewards: 7630.30,
      days_active: 23
    },
    {
      month: '2023年10月',
      vip_rebate: 2180.90,
      referral_commission: 4200.00,
      total_rewards: 6380.90,
      days_active: 20
    },
    {
      month: '2023年9月',
      vip_rebate: 1950.60,
      referral_commission: 3650.00,
      total_rewards: 5600.60,
      days_active: 18
    },
    {
      month: '2023年8月',
      vip_rebate: 1720.40,
      referral_commission: 3100.00,
      total_rewards: 4820.40,
      days_active: 16
    }
  ];

  // 获取变化图标
  const getChangeIcon = (type: string) => {
    switch (type) {
      case 'increase':
        return <ArrowUp className="w-4 h-4 text-success-500" />;
      case 'decrease':
        return <ArrowDown className="w-4 h-4 text-danger-500" />;
      default:
        return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  // 获取变化颜色
  const getChangeColor = (type: string) => {
    switch (type) {
      case 'increase':
        return 'text-success-600';
      case 'decrease':
        return 'text-danger-600';
      default:
        return 'text-gray-600';
    }
  };

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
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2 flex items-center">
                  <BarChart3 className="w-8 h-8 mr-3" />
                  奖励统计
                </h1>
                <p className="text-white text-opacity-80 text-lg">
                  详细的奖励收益分析和趋势统计
                </p>
              </div>
              <div className="hidden lg:block">
                <Button
                  variant="ghost"
                  icon={<Download className="w-4 h-4" />}
                  className="text-white hover:bg-white hover:bg-opacity-20"
                >
                  导出报表
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      <div className="container-responsive py-6 space-y-6">
        {/* 筛选器 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
                <div className="flex items-center space-x-4">
                  <Filter className="w-5 h-5 text-gray-500" />
                  <span className="font-medium text-gray-700">筛选条件:</span>
                </div>
                
                <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
                  {/* 时间周期选择 */}
                  <select
                    value={selectedPeriod}
                    onChange={(e) => setSelectedPeriod(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {periodOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  
                  {/* 奖励类别选择 */}
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {categoryOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 奖励概览卡片 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          {rewardStats.map((stat, index) => (
            <motion.div
              key={stat.period}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
            >
              <Card className="hover:shadow-medium transition-shadow duration-200">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {stat.period}
                    </h3>
                    <div className="flex items-center space-x-1">
                      {getChangeIcon(stat.change_type)}
                      <span className={cn('text-sm font-medium', getChangeColor(stat.change_type))}>
                        {Math.abs(stat.change_percentage)}%
                      </span>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Crown className="w-4 h-4 text-primary-600" />
                        <span className="text-sm text-gray-600">VIP返水</span>
                      </div>
                      <span className="font-bold text-primary-600">
                        {formatCurrency(stat.vip_rebate)}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Users className="w-4 h-4 text-success-600" />
                        <span className="text-sm text-gray-600">推荐佣金</span>
                      </div>
                      <span className="font-bold text-success-600">
                        {formatCurrency(stat.referral_commission)}
                      </span>
                    </div>
                    
                    <div className="pt-2 border-t border-gray-200">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">总奖励</span>
                        <span className="text-lg font-bold text-gray-900">
                          {formatCurrency(stat.total_rewards)}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* 月度奖励趋势 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-primary-600" />
                  月度奖励趋势
                </h2>
                <Button
                  variant="outline"
                  size="sm"
                  icon={<Eye className="w-4 h-4" />}
                >
                  查看图表
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        月份
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        VIP返水
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        推荐佣金
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        总奖励
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        活跃天数
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {monthlyBreakdown.map((month, index) => (
                      <tr key={month.month} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <Calendar className="w-4 h-4 text-gray-400 mr-2" />
                            <span className="text-sm font-medium text-gray-900">
                              {month.month}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <Crown className="w-4 h-4 text-primary-600 mr-2" />
                            <span className="text-sm font-bold text-primary-600">
                              {formatCurrency(month.vip_rebate)}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <Users className="w-4 h-4 text-success-600 mr-2" />
                            <span className="text-sm font-bold text-success-600">
                              {formatCurrency(month.referral_commission)}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <DollarSign className="w-4 h-4 text-gray-600 mr-2" />
                            <span className="text-sm font-bold text-gray-900">
                              {formatCurrency(month.total_rewards)}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                            {month.days_active} 天
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 奖励分析洞察 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
        >
          {/* 收益分析 */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2 text-primary-600" />
                收益分析
              </h3>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-primary-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-primary-700">VIP返水占比</span>
                    <span className="text-sm font-bold text-primary-700">32.3%</span>
                  </div>
                  <div className="w-full bg-primary-200 rounded-full h-2">
                    <div className="bg-primary-600 h-2 rounded-full" style={{ width: '32.3%' }} />
                  </div>
                </div>
                
                <div className="p-4 bg-success-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-success-700">推荐佣金占比</span>
                    <span className="text-sm font-bold text-success-700">67.7%</span>
                  </div>
                  <div className="w-full bg-success-200 rounded-full h-2">
                    <div className="bg-success-600 h-2 rounded-full" style={{ width: '67.7%' }} />
                  </div>
                </div>
                
                <div className="pt-3 border-t border-gray-200">
                  <p className="text-sm text-gray-600">
                    推荐佣金是您的主要收益来源，建议继续扩大推荐团队规模。
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 增长趋势 */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-success-600" />
                增长趋势
              </h3>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-success-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-success-700">月度增长率</p>
                    <p className="text-xs text-success-600">相比上月</p>
                  </div>
                  <div className="flex items-center space-x-1">
                    <ArrowUp className="w-4 h-4 text-success-500" />
                    <span className="text-lg font-bold text-success-700">+18.5%</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-primary-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-primary-700">周度增长率</p>
                    <p className="text-xs text-primary-600">相比上周</p>
                  </div>
                  <div className="flex items-center space-x-1">
                    <ArrowUp className="w-4 h-4 text-primary-500" />
                    <span className="text-lg font-bold text-primary-700">+22.8%</span>
                  </div>
                </div>
                
                <div className="pt-3 border-t border-gray-200">
                  <p className="text-sm text-gray-600">
                    您的奖励收益呈现稳定增长趋势，继续保持当前策略。
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default RewardsStatsPage;