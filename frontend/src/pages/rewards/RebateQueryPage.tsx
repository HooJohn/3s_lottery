import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Gift, 
  TrendingUp, 
  Calendar, 
  Calculator,
  Info,
  Clock,
  DollarSign,
  BarChart3,
  Filter,
  Download,
  CheckCircle,
  AlertCircle,
  HelpCircle
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/format';

interface RebateRecord {
  id: string;
  date: string;
  turnover: number;
  rebate_rate: number;
  rebate_amount: number;
  status: 'completed' | 'pending' | 'processing';
  game_type: string;
}

interface MonthlyRebate {
  month: string;
  total_turnover: number;
  total_rebate: number;
  avg_rate: number;
  days_active: number;
}

const RebateQueryPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('records');
  const [selectedPeriod, setSelectedPeriod] = useState('30days');
  const [showCalculator, setShowCalculator] = useState(false);
  const [showRules, setShowRules] = useState(false);
  const [calculatorAmount, setCalculatorAmount] = useState('');
  const [calculatorVipLevel, setCalculatorVipLevel] = useState(2);

  // 返水记录数据
  const rebateRecords: RebateRecord[] = [
    {
      id: 'RB-001',
      date: '2024-01-21',
      turnover: 5200,
      rebate_rate: 0.52,
      rebate_amount: 27.04,
      status: 'completed',
      game_type: '11选5'
    },
    {
      id: 'RB-002',
      date: '2024-01-20',
      turnover: 8500,
      rebate_rate: 0.52,
      rebate_amount: 44.20,
      status: 'completed',
      game_type: '大乐透'
    },
    {
      id: 'RB-003',
      date: '2024-01-19',
      turnover: 3200,
      rebate_rate: 0.52,
      rebate_amount: 16.64,
      status: 'completed',
      game_type: '刮刮乐'
    },
    {
      id: 'RB-004',
      date: '2024-01-18',
      turnover: 6800,
      rebate_rate: 0.52,
      rebate_amount: 35.36,
      status: 'processing',
      game_type: '体育博彩'
    },
    {
      id: 'RB-005',
      date: '2024-01-17',
      turnover: 4500,
      rebate_rate: 0.52,
      rebate_amount: 23.40,
      status: 'pending',
      game_type: '11选5'
    }
  ];

  // 月度返水趋势数据
  const monthlyRebates: MonthlyRebate[] = [
    {
      month: '2024-01',
      total_turnover: 125000,
      total_rebate: 650,
      avg_rate: 0.52,
      days_active: 21
    },
    {
      month: '2023-12',
      total_turnover: 98000,
      total_rebate: 490,
      avg_rate: 0.50,
      days_active: 25
    },
    {
      month: '2023-11',
      total_turnover: 87000,
      total_rebate: 435,
      avg_rate: 0.50,
      days_active: 23
    },
    {
      month: '2023-10',
      total_turnover: 76000,
      total_rebate: 380,
      avg_rate: 0.50,
      days_active: 20
    },
    {
      month: '2023-09',
      total_turnover: 65000,
      total_rebate: 325,
      avg_rate: 0.50,
      days_active: 18
    },
    {
      month: '2023-08',
      total_turnover: 54000,
      total_rebate: 270,
      avg_rate: 0.50,
      days_active: 16
    }
  ];

  // VIP等级返水比例
  const vipRebateRates = [
    { level: 0, rate: 0.38, name: 'VIP0' },
    { level: 1, rate: 0.45, name: 'VIP1' },
    { level: 2, rate: 0.52, name: 'VIP2' },
    { level: 3, rate: 0.60, name: 'VIP3' },
    { level: 4, rate: 0.68, name: 'VIP4' },
    { level: 5, rate: 0.75, name: 'VIP5' },
    { level: 6, rate: 0.78, name: 'VIP6' },
    { level: 7, rate: 0.80, name: 'VIP7' }
  ];

  // 获取状态图标
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-success-500" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-warning-500" />;
      case 'pending':
        return <AlertCircle className="w-4 h-4 text-info-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  // 获取状态文本
  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '已发放';
      case 'processing':
        return '处理中';
      case 'pending':
        return '待发放';
      default:
        return '未知';
    }
  };

  // 计算预估返水
  const calculateRebate = () => {
    const amount = parseFloat(calculatorAmount);
    if (isNaN(amount) || amount <= 0) return 0;
    
    const rate = vipRebateRates[calculatorVipLevel].rate;
    return (amount * rate) / 100;
  };

  // 统计数据
  const totalRebateThisMonth = rebateRecords
    .filter(record => record.date.startsWith('2024-01'))
    .reduce((sum, record) => sum + record.rebate_amount, 0);

  const totalTurnoverThisMonth = rebateRecords
    .filter(record => record.date.startsWith('2024-01'))
    .reduce((sum, record) => sum + record.turnover, 0);

  const avgRebateRate = totalTurnoverThisMonth > 0 ? (totalRebateThisMonth / totalTurnoverThisMonth) * 100 : 0;

  return (
    <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
      {/* 页面头部 */}
      <div className="bg-gradient-to-r from-success-600 to-primary-600 text-white px-4 py-8 lg:px-6">
        <div className="container-responsive">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2 flex items-center">
                  <Gift className="w-8 h-8 mr-3" />
                  返水查询
                </h1>
                <p className="text-white text-opacity-80 text-lg">
                  查看返水记录，了解收益趋势，计算预估返水
                </p>
              </div>
              <div className="hidden lg:flex items-center space-x-3">
                <Button
                  variant="ghost"
                  icon={<Calculator className="w-4 h-4" />}
                  onClick={() => setShowCalculator(true)}
                  className="text-white hover:bg-white hover:bg-opacity-20"
                >
                  返水计算器
                </Button>
                <Button
                  variant="ghost"
                  icon={<Download className="w-4 h-4" />}
                  className="text-white hover:bg-white hover:bg-opacity-20"
                >
                  导出记录
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* 返水概览 */}
      <div className="container-responsive py-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6"
        >
          <Card className="bg-gradient-to-r from-success-50 to-success-100 border-success-200">
            <CardContent className="p-6 text-center">
              <Gift className="w-8 h-8 text-success-600 mx-auto mb-3" />
              <p className="text-sm text-success-700 mb-1">本月返水</p>
              <p className="text-2xl font-bold text-success-800">
                {formatCurrency(totalRebateThisMonth)}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-primary-50 to-primary-100 border-primary-200">
            <CardContent className="p-6 text-center">
              <DollarSign className="w-8 h-8 text-primary-600 mx-auto mb-3" />
              <p className="text-sm text-primary-700 mb-1">本月流水</p>
              <p className="text-2xl font-bold text-primary-800">
                {formatCurrency(totalTurnoverThisMonth)}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-warning-50 to-warning-100 border-warning-200">
            <CardContent className="p-6 text-center">
              <BarChart3 className="w-8 h-8 text-warning-600 mx-auto mb-3" />
              <p className="text-sm text-warning-700 mb-1">平均返水率</p>
              <p className="text-2xl font-bold text-warning-800">
                {avgRebateRate.toFixed(2)}%
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* 标签切换 */}
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-6">
          <button
            onClick={() => setActiveTab('records')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              activeTab === 'records'
                ? 'bg-white text-success-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            返水记录
          </button>
          <button
            onClick={() => setActiveTab('trends')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              activeTab === 'trends'
                ? 'bg-white text-success-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            趋势统计
          </button>
          <button
            onClick={() => setActiveTab('calculator')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors lg:hidden',
              activeTab === 'calculator'
                ? 'bg-white text-success-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            返水计算器
          </button>
        </div>

        {/* 返水记录列表 */}
        {activeTab === 'records' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">
                    返水记录列表
                  </h2>
                  <div className="flex items-center space-x-2">
                    <Filter className="w-4 h-4 text-gray-500" />
                    <select
                      value={selectedPeriod}
                      onChange={(e) => setSelectedPeriod(e.target.value)}
                      className="text-sm border border-gray-300 rounded px-2 py-1"
                    >
                      <option value="7days">最近7天</option>
                      <option value="30days">最近30天</option>
                      <option value="3months">最近3个月</option>
                    </select>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          日期
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          游戏类型
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          有效流水
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          返水比例
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          返水金额
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          状态
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {rebateRecords.map((record) => (
                        <tr key={record.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {record.date}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                              {record.game_type}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {formatCurrency(record.turnover)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-success-600 font-medium">
                            {record.rebate_rate}%
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-success-700">
                            {formatCurrency(record.rebate_amount)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center space-x-1">
                              {getStatusIcon(record.status)}
                              <span className="text-sm text-gray-600">
                                {getStatusText(record.status)}
                              </span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* 月度返水趋势 */}
        {activeTab === 'trends' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
          >
            {/* 趋势图表 */}
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-success-600" />
                  月度返水趋势
                </h2>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {monthlyRebates.map((month, index) => (
                    <motion.div
                      key={month.month}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center space-x-4">
                        <Calendar className="w-5 h-5 text-gray-500" />
                        <div>
                          <p className="font-medium text-gray-900">{month.month}</p>
                          <p className="text-sm text-gray-500">
                            活跃 {month.days_active} 天
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-6">
                        <div className="text-right">
                          <p className="text-sm text-gray-500">流水</p>
                          <p className="font-medium text-gray-900">
                            {formatCurrency(month.total_turnover)}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-500">返水</p>
                          <p className="font-bold text-success-600">
                            {formatCurrency(month.total_rebate)}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-500">平均比例</p>
                          <p className="font-medium text-primary-600">
                            {month.avg_rate}%
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 累计返水金额 */}
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-gray-900">
                  累计返水统计
                </h3>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-success-50 rounded-lg">
                    <p className="text-sm text-success-700 mb-1">累计返水金额</p>
                    <p className="text-2xl font-bold text-success-800">
                      {formatCurrency(monthlyRebates.reduce((sum, month) => sum + month.total_rebate, 0))}
                    </p>
                  </div>
                  <div className="text-center p-4 bg-primary-50 rounded-lg">
                    <p className="text-sm text-primary-700 mb-1">累计有效流水</p>
                    <p className="text-2xl font-bold text-primary-800">
                      {formatCurrency(monthlyRebates.reduce((sum, month) => sum + month.total_turnover, 0))}
                    </p>
                  </div>
                  <div className="text-center p-4 bg-warning-50 rounded-lg">
                    <p className="text-sm text-warning-700 mb-1">整体返水率</p>
                    <p className="text-2xl font-bold text-warning-800">
                      {(monthlyRebates.reduce((sum, month) => sum + month.total_rebate, 0) / 
                        monthlyRebates.reduce((sum, month) => sum + month.total_turnover, 0) * 100).toFixed(2)}%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* 移动端返水计算器 */}
        {activeTab === 'calculator' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="lg:hidden"
          >
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Calculator className="w-5 h-5 mr-2 text-primary-600" />
                  返水计算器
                </h2>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      投注金额
                    </label>
                    <input
                      type="number"
                      value={calculatorAmount}
                      onChange={(e) => setCalculatorAmount(e.target.value)}
                      placeholder="请输入投注金额"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      VIP等级
                    </label>
                    <select
                      value={calculatorVipLevel}
                      onChange={(e) => setCalculatorVipLevel(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    >
                      {vipRebateRates.map((vip) => (
                        <option key={vip.level} value={vip.level}>
                          {vip.name} - {vip.rate}%
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="p-4 bg-success-50 rounded-lg">
                    <p className="text-sm text-success-700 mb-1">预估返水金额</p>
                    <p className="text-2xl font-bold text-success-800">
                      {formatCurrency(calculateRebate())}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>

      {/* 返水计算器模态框 */}
      <Modal
        isOpen={showCalculator}
        onClose={() => setShowCalculator(false)}
        title="返水计算器"
        size="md"
      >
        <div className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                投注金额
              </label>
              <input
                type="number"
                value={calculatorAmount}
                onChange={(e) => setCalculatorAmount(e.target.value)}
                placeholder="请输入投注金额"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                VIP等级
              </label>
              <select
                value={calculatorVipLevel}
                onChange={(e) => setCalculatorVipLevel(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                {vipRebateRates.map((vip) => (
                  <option key={vip.level} value={vip.level}>
                    {vip.name} - {vip.rate}%
                  </option>
                ))}
              </select>
            </div>
            
            <div className="p-4 bg-success-50 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm text-success-700">预估返水金额:</span>
                <span className="text-xl font-bold text-success-800">
                  {formatCurrency(calculateRebate())}
                </span>
              </div>
            </div>
            
            <div className="pt-4 border-t border-gray-200">
              <Button
                variant="outline"
                icon={<HelpCircle className="w-4 h-4" />}
                onClick={() => setShowRules(true)}
                fullWidth
              >
                查看返水规则
              </Button>
            </div>
          </div>
        </div>
      </Modal>

      {/* 返水规则说明模态框 */}
      <Modal
        isOpen={showRules}
        onClose={() => setShowRules(false)}
        title="返水规则说明"
        size="lg"
      >
        <div className="p-6 space-y-4">
          <div>
            <h3 className="font-semibold text-lg mb-2">返水计算方式</h3>
            <ul className="list-disc pl-5 space-y-2 text-gray-700">
              <li>返水金额 = 有效流水 × VIP等级返水比例</li>
              <li>只有产生有效流水的投注才计入返水计算</li>
              <li>不同游戏类型的有效流水计算方式可能不同</li>
              <li>返水比例根据您的VIP等级确定</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-lg mb-2">发放时间</h3>
            <ul className="list-disc pl-5 space-y-2 text-gray-700">
              <li>返水每日凌晨2:00自动结算发放</li>
              <li>节假日可能会有延迟，但不会影响金额</li>
              <li>返水直接发放到您的主账户余额</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-lg mb-2">使用规则</h3>
            <ul className="list-disc pl-5 space-y-2 text-gray-700">
              <li>返水金额无需申请，系统自动发放</li>
              <li>返水金额可直接用于投注或提款</li>
              <li>返水金额不设置流水要求</li>
              <li>如有疑问请联系客服处理</li>
            </ul>
          </div>
          
          <div className="pt-4 border-t border-gray-200">
            <Button
              variant="primary"
              fullWidth
              onClick={() => setShowRules(false)}
            >
              我已了解
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default RebateQueryPage;