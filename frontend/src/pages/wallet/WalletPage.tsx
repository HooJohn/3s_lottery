import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Wallet, 
  Plus, 
  Minus, 
  ArrowUpRight, 
  ArrowDownLeft,
  Eye,
  EyeOff,
  RefreshCw,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { cn } from '../../utils/cn';
import { formatCurrency, formatDateTime, formatRelativeTime } from '../../utils/format';

const WalletPage: React.FC = () => {
  const navigate = useNavigate();
  const [showBalance, setShowBalance] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('week');

  // 模拟用户余额数据
  const balanceData = {
    mainBalance: 15420.50,
    bonusBalance: 2850.00,
    frozenBalance: 500.00,
    totalBalance: 18270.50,
    availableBalance: 17770.50,
    lastUpdated: new Date().toISOString(),
  };

  // 模拟交易记录
  const transactions = [
    {
      id: '1',
      type: 'DEPOSIT',
      amount: 5000,
      status: 'COMPLETED',
      description: '通过Paystack存款',
      createdAt: '2024-01-20T10:30:00Z',
      reference: 'DEP-20240120-001',
    },
    {
      id: '2',
      type: 'BET',
      amount: -200,
      status: 'COMPLETED',
      description: '11选5投注',
      createdAt: '2024-01-20T09:15:00Z',
      reference: 'BET-20240120-002',
    },
    {
      id: '3',
      type: 'WIN',
      amount: 1500,
      status: 'COMPLETED',
      description: '11选5中奖',
      createdAt: '2024-01-20T09:20:00Z',
      reference: 'WIN-20240120-003',
    },
    {
      id: '4',
      type: 'WITHDRAW',
      amount: -3000,
      status: 'PROCESSING',
      description: '提款到Access Bank',
      createdAt: '2024-01-19T16:45:00Z',
      reference: 'WTH-20240119-004',
    },
    {
      id: '5',
      type: 'REWARD',
      amount: 150,
      status: 'COMPLETED',
      description: 'VIP返水奖励',
      createdAt: '2024-01-19T00:00:00Z',
      reference: 'RWD-20240119-005',
    },
  ];

  // 交易类型配置
  const transactionConfig = {
    DEPOSIT: {
      icon: ArrowDownLeft,
      color: 'text-success-600',
      bgColor: 'bg-success-100',
      label: '存款',
    },
    WITHDRAW: {
      icon: ArrowUpRight,
      color: 'text-warning-600',
      bgColor: 'bg-warning-100',
      label: '提款',
    },
    BET: {
      icon: Minus,
      color: 'text-danger-600',
      bgColor: 'bg-danger-100',
      label: '投注',
    },
    WIN: {
      icon: Plus,
      color: 'text-success-600',
      bgColor: 'bg-success-100',
      label: '中奖',
    },
    REWARD: {
      icon: TrendingUp,
      color: 'text-secondary-600',
      bgColor: 'bg-secondary-100',
      label: '奖励',
    },
  };

  // 状态配置
  const statusConfig = {
    COMPLETED: {
      icon: CheckCircle,
      color: 'text-success-600',
      bgColor: 'bg-success-100',
      label: '已完成',
    },
    PROCESSING: {
      icon: Clock,
      color: 'text-warning-600',
      bgColor: 'bg-warning-100',
      label: '处理中',
    },
    PENDING: {
      icon: AlertCircle,
      color: 'text-info-600',
      bgColor: 'bg-info-100',
      label: '待处理',
    },
    FAILED: {
      icon: XCircle,
      color: 'text-danger-600',
      bgColor: 'bg-danger-100',
      label: '失败',
    },
  };

  const periods = [
    { key: 'today', label: '今天' },
    { key: 'week', label: '本周' },
    { key: 'month', label: '本月' },
    { key: 'all', label: '全部' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
      {/* 页面头部 */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 lg:px-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">我的钱包</h1>
            <p className="text-sm text-gray-600 mt-1">
              管理您的资金和交易记录
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            icon={<RefreshCw className="w-4 h-4" />}
            className="text-gray-600"
          >
            刷新
          </Button>
        </div>
      </div>

      <div className="container-responsive py-6 space-y-6">
        {/* 余额卡片 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="bg-gradient-primary text-white overflow-hidden relative">
            {/* 背景装饰 */}
            <div className="absolute top-0 right-0 w-32 h-32 opacity-10">
              <div className="w-full h-full rounded-full border-4 border-white transform translate-x-8 -translate-y-8" />
            </div>
            <div className="absolute bottom-0 left-0 w-24 h-24 opacity-10">
              <div className="w-full h-full rounded-full border-4 border-white transform -translate-x-6 translate-y-6" />
            </div>

            <CardContent className="relative z-10 p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-2">
                  <Wallet className="w-6 h-6" />
                  <span className="text-lg font-semibold">账户余额</span>
                </div>
                <button
                  onClick={() => setShowBalance(!showBalance)}
                  className="p-2 hover:bg-white hover:bg-opacity-10 rounded-lg transition-colors"
                >
                  {showBalance ? (
                    <Eye className="w-5 h-5" />
                  ) : (
                    <EyeOff className="w-5 h-5" />
                  )}
                </button>
              </div>

              {/* 总余额 */}
              <div className="mb-6">
                <p className="text-white text-opacity-80 text-sm mb-1">
                  总余额
                </p>
                <p className="text-4xl font-bold">
                  {showBalance ? formatCurrency(balanceData.totalBalance) : '****'}
                </p>
              </div>

              {/* 余额详情 */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white bg-opacity-10 rounded-lg p-4">
                  <p className="text-white text-opacity-80 text-sm mb-1">
                    可用余额
                  </p>
                  <p className="text-xl font-bold">
                    {showBalance ? formatCurrency(balanceData.availableBalance) : '****'}
                  </p>
                </div>
                <div className="bg-white bg-opacity-10 rounded-lg p-4">
                  <p className="text-white text-opacity-80 text-sm mb-1">
                    奖金余额
                  </p>
                  <p className="text-xl font-bold">
                    {showBalance ? formatCurrency(balanceData.bonusBalance) : '****'}
                  </p>
                </div>
              </div>

              {/* 最后更新时间 */}
              <div className="mt-4 text-center">
                <p className="text-white text-opacity-60 text-xs">
                  最后更新: {formatRelativeTime(balanceData.lastUpdated)}
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 快捷操作 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="grid grid-cols-2 gap-4"
        >
          <Button
            variant="primary"
            size="lg"
            icon={<Plus className="w-5 h-5" />}
            className="h-16 text-lg"
            fullWidth
            onClick={() => navigate('/wallet/deposit')}
          >
            存款
          </Button>
          <Button
            variant="outline"
            size="lg"
            icon={<Minus className="w-5 h-5" />}
            className="h-16 text-lg"
            fullWidth
            onClick={() => navigate('/wallet/withdraw')}
          >
            提款
          </Button>
        </motion.div>

        {/* 交易记录 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">
                  交易记录
                </h2>
                <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
                  {periods.map((period) => (
                    <button
                      key={period.key}
                      onClick={() => setSelectedPeriod(period.key)}
                      className={cn(
                        'px-3 py-1 text-sm font-medium rounded-md transition-colors',
                        selectedPeriod === period.key
                          ? 'bg-white text-primary-600 shadow-sm'
                          : 'text-gray-600 hover:text-gray-900'
                      )}
                    >
                      {period.label}
                    </button>
                  ))}
                </div>
              </div>
            </CardHeader>

            <CardContent className="p-0">
              <div className="divide-y divide-gray-200">
                {transactions.map((transaction, index) => {
                  const typeConfig = transactionConfig[transaction.type as keyof typeof transactionConfig];
                  const statusConfig_ = statusConfig[transaction.status as keyof typeof statusConfig];
                  const TypeIcon = typeConfig.icon;
                  const StatusIcon = statusConfig_.icon;

                  return (
                    <motion.div
                      key={transaction.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="p-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center space-x-4">
                        {/* 交易类型图标 */}
                        <div className={cn(
                          'w-12 h-12 rounded-full flex items-center justify-center',
                          typeConfig.bgColor
                        )}>
                          <TypeIcon className={cn('w-6 h-6', typeConfig.color)} />
                        </div>

                        {/* 交易信息 */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="font-medium text-gray-900 truncate">
                              {transaction.description}
                            </p>
                            <p className={cn(
                              'font-bold text-lg',
                              transaction.amount > 0 ? 'text-success-600' : 'text-gray-900'
                            )}>
                              {transaction.amount > 0 ? '+' : ''}
                              {formatCurrency(Math.abs(transaction.amount))}
                            </p>
                          </div>
                          
                          <div className="flex items-center justify-between mt-1">
                            <div className="flex items-center space-x-2">
                              <span className="text-sm text-gray-500">
                                {formatDateTime(transaction.createdAt, 'MM-dd HH:mm')}
                              </span>
                              <span className="text-xs text-gray-400">
                                {transaction.reference}
                              </span>
                            </div>
                            
                            {/* 状态标识 */}
                            <div className={cn(
                              'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                              statusConfig_.bgColor,
                              statusConfig_.color
                            )}>
                              <StatusIcon className="w-3 h-3 mr-1" />
                              {statusConfig_.label}
                            </div>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>

              {/* 查看更多 */}
              <div className="p-4 text-center border-t border-gray-200">
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => navigate('/wallet/transactions')}
                >
                  查看完整交易记录
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 统计卡片 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4"
        >
          <Card className="text-center">
            <CardContent className="p-6">
              <div className="w-12 h-12 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <ArrowDownLeft className="w-6 h-6 text-success-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900 mb-1">
                {formatCurrency(25000)}
              </p>
              <p className="text-sm text-gray-600">本月存款</p>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardContent className="p-6">
              <div className="w-12 h-12 bg-warning-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <ArrowUpRight className="w-6 h-6 text-warning-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900 mb-1">
                {formatCurrency(8500)}
              </p>
              <p className="text-sm text-gray-600">本月提款</p>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardContent className="p-6">
              <div className="w-12 h-12 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-6 h-6 text-secondary-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900 mb-1">
                {formatCurrency(1250)}
              </p>
              <p className="text-sm text-gray-600">本月收益</p>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default WalletPage;