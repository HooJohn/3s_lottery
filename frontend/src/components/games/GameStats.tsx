import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  PieChart, 
  Calendar,
  Clock,
  Trophy,
  Target,
  Zap,
  Users,
  DollarSign,
  Percent
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/format';

interface GameStatsProps {
  gameType: 'lottery11x5' | 'superlotto' | 'scratch' | 'sports';
  className?: string;
}

interface StatItem {
  label: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'stable';
  icon: React.ComponentType<any>;
  color: string;
}

interface TrendData {
  period: string;
  value: number;
  label: string;
}

const GameStats: React.FC<GameStatsProps> = ({ gameType, className }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('7d');

  // 根据游戏类型生成统计数据
  const getStatsData = (): StatItem[] => {
    switch (gameType) {
      case 'lottery11x5':
        return [
          {
            label: '今日投注',
            value: formatCurrency(125000),
            change: 12.5,
            trend: 'up',
            icon: DollarSign,
            color: 'text-primary-600'
          },
          {
            label: '中奖率',
            value: '23.8%',
            change: 2.1,
            trend: 'up',
            icon: Target,
            color: 'text-success-600'
          },
          {
            label: '参与人数',
            value: 1250,
            change: -5.2,
            trend: 'down',
            icon: Users,
            color: 'text-info-600'
          },
          {
            label: '平均奖金',
            value: formatCurrency(850),
            change: 8.3,
            trend: 'up',
            icon: Trophy,
            color: 'text-warning-600'
          }
        ];
      
      case 'superlotto':
        return [
          {
            label: '当期销量',
            value: formatCurrency(52000000),
            change: 15.2,
            trend: 'up',
            icon: DollarSign,
            color: 'text-primary-600'
          },
          {
            label: '奖池金额',
            value: formatCurrency(125000000),
            change: 8.5,
            trend: 'up',
            icon: Trophy,
            color: 'text-secondary-600'
          },
          {
            label: '参与人数',
            value: 3420,
            change: 22.1,
            trend: 'up',
            icon: Users,
            color: 'text-info-600'
          },
          {
            label: '中奖概率',
            value: '1/21,425,712',
            trend: 'stable',
            icon: Percent,
            color: 'text-gray-600'
          }
        ];
      
      case 'scratch':
        return [
          {
            label: '今日销量',
            value: formatCurrency(45000),
            change: 18.7,
            trend: 'up',
            icon: DollarSign,
            color: 'text-primary-600'
          },
          {
            label: '中奖率',
            value: '28.5%',
            change: 3.2,
            trend: 'up',
            icon: Target,
            color: 'text-success-600'
          },
          {
            label: '活跃玩家',
            value: 890,
            change: 12.3,
            trend: 'up',
            icon: Users,
            color: 'text-info-600'
          },
          {
            label: '最高奖金',
            value: formatCurrency(100000),
            trend: 'stable',
            icon: Trophy,
            color: 'text-warning-600'
          }
        ];
      
      case 'sports':
        return [
          {
            label: '今日投注',
            value: formatCurrency(180000),
            change: 25.4,
            trend: 'up',
            icon: DollarSign,
            color: 'text-primary-600'
          },
          {
            label: '胜率',
            value: '45.2%',
            change: -2.1,
            trend: 'down',
            icon: Target,
            color: 'text-success-600'
          },
          {
            label: '活跃用户',
            value: 2100,
            change: 8.9,
            trend: 'up',
            icon: Users,
            color: 'text-info-600'
          },
          {
            label: '平均赔率',
            value: '2.35',
            change: 0.15,
            trend: 'up',
            icon: TrendingUp,
            color: 'text-warning-600'
          }
        ];
      
      default:
        return [];
    }
  };

  // 生成趋势数据
  const getTrendData = (): TrendData[] => {
    const baseData = [
      { period: '1天前', value: 100, label: '基准' },
      { period: '2天前', value: 120, label: '上升' },
      { period: '3天前', value: 95, label: '下降' },
      { period: '4天前', value: 140, label: '高峰' },
      { period: '5天前', value: 110, label: '稳定' },
      { period: '6天前', value: 130, label: '增长' },
      { period: '7天前', value: 105, label: '平稳' },
    ];
    
    return baseData.reverse();
  };

  const statsData = getStatsData();
  const trendData = getTrendData();

  const tabs = [
    { key: 'overview', label: '概览', icon: BarChart3 },
    { key: 'trends', label: '趋势', icon: TrendingUp },
    { key: 'analysis', label: '分析', icon: PieChart },
  ];

  const timeRanges = [
    { key: '1d', label: '今日' },
    { key: '7d', label: '7天' },
    { key: '30d', label: '30天' },
    { key: '90d', label: '90天' },
  ];

  return (
    <div className={cn('space-y-6', className)}>
      {/* 标签和时间范围选择 */}
      <div className="flex items-center justify-between">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={cn(
                  'flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                  activeTab === tab.key
                    ? 'bg-white text-primary-700 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          {timeRanges.map((range) => (
            <button
              key={range.key}
              onClick={() => setTimeRange(range.key)}
              className={cn(
                'px-3 py-1 rounded-md text-sm font-medium transition-colors',
                timeRange === range.key
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              )}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      {/* 概览标签 */}
      {activeTab === 'overview' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          {statsData.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card className="hover:shadow-medium transition-shadow duration-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Icon className={cn('w-5 h-5', stat.color)} />
                      {stat.change !== undefined && (
                        <div className={cn(
                          'flex items-center text-xs font-medium',
                          stat.trend === 'up' ? 'text-success-600' :
                          stat.trend === 'down' ? 'text-danger-600' : 'text-gray-500'
                        )}>
                          {stat.trend === 'up' && <TrendingUp className="w-3 h-3 mr-1" />}
                          {stat.trend === 'down' && <TrendingDown className="w-3 h-3 mr-1" />}
                          {stat.change > 0 ? '+' : ''}{stat.change}%
                        </div>
                      )}
                    </div>
                    <div className="space-y-1">
                      <p className="text-2xl font-bold text-gray-900">
                        {stat.value}
                      </p>
                      <p className="text-sm text-gray-600">
                        {stat.label}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>
      )}

      {/* 趋势标签 */}
      {activeTab === 'trends' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  数据趋势
                </h3>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <Clock className="w-4 h-4" />
                  <span>最近{timeRange === '1d' ? '24小时' : timeRange === '7d' ? '7天' : timeRange === '30d' ? '30天' : '90天'}</span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* 简单的趋势图表 */}
                <div className="h-48 flex items-end space-x-2">
                  {trendData.map((data, index) => {
                    const height = (data.value / 150) * 100; // 标准化高度
                    return (
                      <div key={index} className="flex-1 flex flex-col items-center">
                        <motion.div
                          initial={{ height: 0 }}
                          animate={{ height: `${height}%` }}
                          transition={{ duration: 0.5, delay: index * 0.1 }}
                          className="w-full bg-gradient-to-t from-primary-500 to-primary-400 rounded-t-sm min-h-[20px]"
                        />
                        <div className="mt-2 text-xs text-gray-500 text-center">
                          <p>{data.period.replace('天前', '')}</p>
                          <p className="font-medium text-gray-700">{data.value}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* 趋势说明 */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <TrendingUp className="w-5 h-5 text-success-600 mr-1" />
                      <span className="text-sm font-medium text-gray-700">上升趋势</span>
                    </div>
                    <p className="text-xs text-gray-500">
                      相比上期增长 12.5%
                    </p>
                  </div>
                  
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <Target className="w-5 h-5 text-primary-600 mr-1" />
                      <span className="text-sm font-medium text-gray-700">平均值</span>
                    </div>
                    <p className="text-xs text-gray-500">
                      期间平均值 115
                    </p>
                  </div>
                  
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      <Zap className="w-5 h-5 text-warning-600 mr-1" />
                      <span className="text-sm font-medium text-gray-700">峰值</span>
                    </div>
                    <p className="text-xs text-gray-500">
                      最高值 140
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* 分析标签 */}
      {activeTab === 'analysis' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        >
          {/* 热门时段分析 */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-gray-900">
                热门时段
              </h3>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { time: '20:00-22:00', percentage: 85, label: '晚间高峰' },
                  { time: '12:00-14:00', percentage: 65, label: '午间时段' },
                  { time: '08:00-10:00', percentage: 45, label: '早间时段' },
                  { time: '14:00-18:00', percentage: 35, label: '下午时段' },
                ].map((item, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium text-gray-700">{item.time}</span>
                      <span className="text-gray-500">{item.percentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${item.percentage}%` }}
                        transition={{ duration: 0.8, delay: index * 0.1 }}
                        className="bg-gradient-to-r from-primary-500 to-primary-600 h-2 rounded-full"
                      />
                    </div>
                    <p className="text-xs text-gray-500">{item.label}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 用户行为分析 */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-gray-900">
                用户行为
              </h3>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { label: '新用户', value: 25, color: 'bg-primary-500' },
                  { label: '活跃用户', value: 45, color: 'bg-success-500' },
                  { label: '回流用户', value: 20, color: 'bg-warning-500' },
                  { label: '流失用户', value: 10, color: 'bg-gray-400' },
                ].map((item, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className={cn('w-3 h-3 rounded-full', item.color)} />
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700">
                          {item.label}
                        </span>
                        <span className="text-sm text-gray-500">
                          {item.value}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-1.5">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${item.value}%` }}
                          transition={{ duration: 0.8, delay: index * 0.1 }}
                          className={cn('h-1.5 rounded-full', item.color)}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
};

export default GameStats;