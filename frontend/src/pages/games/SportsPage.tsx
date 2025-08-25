import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Target as Football, 
  Trophy, 
  Clock,
  ExternalLink,
  Wallet,
  ArrowRightLeft,
  AlertCircle,
  Star,
  TrendingUp,
  Users,
  Play,
  Pause
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import GameEnhancer from '@/components/games/GameEnhancer';
import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/format';

// 体育平台接口
interface SportsProvider {
  id: string;
  name: string;
  logo: string;
  description: string;
  features: string[];
  isActive: boolean;
  isMaintenance: boolean;
  isRecommended: boolean;
  isHot: boolean;
  balance: number;
  loginUrl: string;
}

// 钱包转账记录
interface TransferRecord {
  id: string;
  providerId: string;
  providerName: string;
  type: 'IN' | 'OUT';
  amount: number;
  status: 'SUCCESS' | 'PENDING' | 'FAILED';
  createdAt: string;
}

const SportsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('platforms');
  const [showTransfer, setShowTransfer] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<SportsProvider | null>(null);
  const [transferAmount, setTransferAmount] = useState('');
  const [transferType, setTransferType] = useState<'IN' | 'OUT'>('IN');
  const [mainBalance, setMainBalance] = useState(25000);

  // 体育博彩平台列表
  const sportsProviders: SportsProvider[] = [
    {
      id: 'bet9ja',
      name: 'Bet9ja',
      logo: '/logos/bet9ja.png',
      description: '尼日利亚领先的体育博彩平台，提供足球、篮球等多种体育赛事投注',
      features: ['足球投注', '篮球投注', '网球投注', '虚拟体育', '现场直播'],
      isActive: true,
      isMaintenance: false,
      isRecommended: true,
      isHot: true,
      balance: 5000,
      loginUrl: 'https://bet9ja.com'
    },
    {
      id: 'sportybet',
      name: 'SportyBet',
      logo: '/logos/sportybet.png',
      description: '专业的体育博彩平台，覆盖全球主要体育赛事，赔率优势明显',
      features: ['足球投注', '篮球投注', '电竞投注', '真人娱乐', '快速结算'],
      isActive: true,
      isMaintenance: false,
      isRecommended: false,
      isHot: true,
      balance: 2500,
      loginUrl: 'https://sportybet.com'
    },
    {
      id: 'betking',
      name: 'BetKing',
      logo: '/logos/betking.png',
      description: '提供丰富的体育赛事和娱乐游戏，支持多种支付方式',
      features: ['足球投注', '篮球投注', '赛马投注', '老虎机', '移动优化'],
      isActive: true,
      isMaintenance: false,
      isRecommended: false,
      isHot: false,
      balance: 0,
      loginUrl: 'https://betking.com'
    },
    {
      id: 'nairabet',
      name: 'NairaBet',
      logo: '/logos/nairabet.png',
      description: '本土化体育博彩平台，专注于非洲体育赛事投注',
      features: ['足球投注', '篮球投注', '本地联赛', '快速提款', '本地化服务'],
      isActive: false,
      isMaintenance: true,
      isRecommended: false,
      isHot: false,
      balance: 1200,
      loginUrl: 'https://nairabet.com'
    },
    {
      id: '1xbet',
      name: '1xBet',
      logo: '/logos/1xbet.png',
      description: '国际知名体育博彩品牌，提供超过1000种体育赛事投注',
      features: ['全球赛事', '高赔率', '多语言支持', '加密货币', '24/7客服'],
      isActive: true,
      isMaintenance: false,
      isRecommended: true,
      isHot: false,
      balance: 3200,
      loginUrl: 'https://1xbet.com'
    },
  ];

  // 转账记录
  const [transferHistory, setTransferHistory] = useState<TransferRecord[]>([
    {
      id: 'tr-001',
      providerId: 'bet9ja',
      providerName: 'Bet9ja',
      type: 'IN',
      amount: 5000,
      status: 'SUCCESS',
      createdAt: '2024-01-20T10:30:00Z'
    },
    {
      id: 'tr-002',
      providerId: 'sportybet',
      providerName: 'SportyBet',
      type: 'OUT',
      amount: 1500,
      status: 'SUCCESS',
      createdAt: '2024-01-19T15:45:00Z'
    },
  ]);

  // 进入体育平台
  const enterPlatform = (provider: SportsProvider) => {
    if (!provider.isActive || provider.isMaintenance) {
      alert('该平台暂时不可用，请稍后再试');
      return;
    }

    // 检查余额提醒
    if (mainBalance < 1000) {
      const confirmed = confirm('您的中心钱包余额较低，建议先充值。是否继续进入平台？');
      if (!confirmed) return;
    }

    // 模拟跳转到第三方平台
    window.open(provider.loginUrl, '_blank');
  };

  // 打开转账模态框
  const openTransfer = (provider: SportsProvider, type: 'IN' | 'OUT') => {
    setSelectedProvider(provider);
    setTransferType(type);
    setTransferAmount('');
    setShowTransfer(true);
  };

  // 执行转账
  const executeTransfer = () => {
    if (!selectedProvider || !transferAmount) return;

    const amount = parseFloat(transferAmount);
    if (isNaN(amount) || amount <= 0) {
      alert('请输入有效的转账金额');
      return;
    }

    if (transferType === 'IN') {
      // 转入场馆
      if (mainBalance < amount) {
        alert('中心钱包余额不足');
        return;
      }
      setMainBalance(prev => prev - amount);
      // 更新场馆余额
      const updatedProviders = sportsProviders.map(p => 
        p.id === selectedProvider.id 
          ? { ...p, balance: p.balance + amount }
          : p
      );
    } else {
      // 转出场馆
      if (selectedProvider.balance < amount) {
        alert('场馆余额不足');
        return;
      }
      setMainBalance(prev => prev + amount);
      // 更新场馆余额
      const updatedProviders = sportsProviders.map(p => 
        p.id === selectedProvider.id 
          ? { ...p, balance: p.balance - amount }
          : p
      );
    }

    // 添加转账记录
    const newRecord: TransferRecord = {
      id: `tr-${Date.now()}`,
      providerId: selectedProvider.id,
      providerName: selectedProvider.name,
      type: transferType,
      amount,
      status: 'SUCCESS',
      createdAt: new Date().toISOString()
    };
    setTransferHistory(prev => [newRecord, ...prev]);

    setShowTransfer(false);
    alert(`转账成功！${transferType === 'IN' ? '转入' : '转出'}金额：${formatCurrency(amount)}`);
  };

  // 一键回收
  const recallAllFunds = () => {
    const totalBalance = sportsProviders.reduce((sum, provider) => sum + provider.balance, 0);
    if (totalBalance === 0) {
      alert('所有场馆余额为0，无需回收');
      return;
    }

    const confirmed = confirm(`确认回收所有场馆资金（共${formatCurrency(totalBalance)}）到中心钱包？`);
    if (!confirmed) return;

    setMainBalance(prev => prev + totalBalance);
    // 清空所有场馆余额
    sportsProviders.forEach(provider => {
      provider.balance = 0;
    });

    alert(`成功回收${formatCurrency(totalBalance)}到中心钱包`);
  };

  return (
    <GameEnhancer 
      gameName="体育博彩"
      showSoundControl={true}
      showFullscreen={true}
      showNotifications={true}
      showHelp={true}
    >
      <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
      {/* 页面头部 */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white px-4 py-6 lg:px-6">
        <div className="container-responsive">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold mb-1">体育博彩</h1>
              <p className="text-white text-opacity-80">
                多平台体育投注，精彩赛事不容错过
              </p>
            </div>
            <div className="text-right">
              <p className="text-white text-opacity-80 text-sm">中心钱包</p>
              <p className="text-xl font-bold">
                {formatCurrency(mainBalance)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 钱包概览 */}
      <div className="container-responsive py-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="bg-gradient-to-r from-blue-50 to-green-50 border-blue-200">
            <CardContent className="p-4">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Wallet className="w-5 h-5 text-blue-600 mr-1" />
                    <span className="text-sm text-gray-600">中心钱包</span>
                  </div>
                  <p className="text-xl font-bold text-blue-700">
                    {formatCurrency(mainBalance)}
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Trophy className="w-5 h-5 text-green-600 mr-1" />
                    <span className="text-sm text-gray-600">场馆总额</span>
                  </div>
                  <p className="text-xl font-bold text-green-700">
                    {formatCurrency(sportsProviders.reduce((sum, p) => sum + p.balance, 0))}
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Users className="w-5 h-5 text-purple-600 mr-1" />
                    <span className="text-sm text-gray-600">可用平台</span>
                  </div>
                  <p className="text-xl font-bold text-purple-700">
                    {sportsProviders.filter(p => p.isActive && !p.isMaintenance).length}
                  </p>
                </div>
                
                <div className="text-center">
                  <Button
                    variant="outline"
                    size="sm"
                    icon={<ArrowRightLeft className="w-4 h-4" />}
                    onClick={recallAllFunds}
                  >
                    一键回收
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* 标签切换 */}
      <div className="container-responsive">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-6">
          <button
            onClick={() => setActiveTab('platforms')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              activeTab === 'platforms'
                ? 'bg-white text-blue-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            体育平台
          </button>
          <button
            onClick={() => setActiveTab('transfers')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              activeTab === 'transfers'
                ? 'bg-white text-blue-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            转账记录
          </button>
        </div>
      </div>

      <div className="container-responsive space-y-6">
        {/* 体育平台列表 */}
        {activeTab === 'platforms' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-4"
          >
            {sportsProviders.map((provider) => (
              <Card key={provider.id} className={cn(
                'transition-all duration-200',
                !provider.isActive || provider.isMaintenance 
                  ? 'opacity-60 bg-gray-50' 
                  : 'hover:shadow-medium'
              )}>
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    {/* 平台Logo */}
                    <div className="flex-shrink-0">
                      <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center">
                        <Football className="w-8 h-8 text-gray-500" />
                      </div>
                    </div>
                    
                    {/* 平台信息 */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {provider.name}
                        </h3>
                        
                        {/* 标签 */}
                        <div className="flex space-x-1">
                          {provider.isRecommended && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full bg-primary-100 text-primary-700 text-xs font-medium">
                              <Star className="w-3 h-3 mr-1" />
                              推荐
                            </span>
                          )}
                          {provider.isHot && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full bg-danger-100 text-danger-700 text-xs font-medium">
                              <TrendingUp className="w-3 h-3 mr-1" />
                              热门
                            </span>
                          )}
                          {provider.isMaintenance && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full bg-warning-100 text-warning-700 text-xs font-medium">
                              <Pause className="w-3 h-3 mr-1" />
                              维护中
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <p className="text-gray-600 text-sm mb-3">
                        {provider.description}
                      </p>
                      
                      {/* 特色功能 */}
                      <div className="flex flex-wrap gap-2 mb-4">
                        {provider.features.map((feature, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded-md bg-gray-100 text-gray-700 text-xs"
                          >
                            {feature}
                          </span>
                        ))}
                      </div>
                      
                      {/* 余额和操作 */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div>
                            <p className="text-xs text-gray-500">场馆余额</p>
                            <p className="font-bold text-green-600">
                              {formatCurrency(provider.balance)}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          {/* 转账按钮 */}
                          <Button
                            variant="outline"
                            size="sm"
                            icon={<ArrowRightLeft className="w-4 h-4" />}
                            onClick={() => openTransfer(provider, 'IN')}
                            disabled={!provider.isActive || provider.isMaintenance}
                          >
                            转账
                          </Button>
                          
                          {/* 进入平台按钮 */}
                          <Button
                            variant="primary"
                            size="sm"
                            icon={provider.isActive && !provider.isMaintenance ? 
                              <ExternalLink className="w-4 h-4" /> : 
                              <AlertCircle className="w-4 h-4" />
                            }
                            onClick={() => enterPlatform(provider)}
                            disabled={!provider.isActive || provider.isMaintenance}
                          >
                            {provider.isMaintenance ? '维护中' : 
                             !provider.isActive ? '暂停服务' : '进入平台'}
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </motion.div>
        )}

        {/* 转账记录 */}
        {activeTab === 'transfers' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold text-gray-900">
                  转账记录
                </h2>
              </CardHeader>
              <CardContent className="p-0">
                {transferHistory.length === 0 ? (
                  <div className="text-center py-8">
                    <ArrowRightLeft className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">暂无转账记录</p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-200">
                    {transferHistory.map((record) => (
                      <div key={record.id} className="p-4 hover:bg-gray-50 transition-colors">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className={cn(
                              'w-10 h-10 rounded-full flex items-center justify-center',
                              record.type === 'IN' 
                                ? 'bg-blue-100 text-blue-600' 
                                : 'bg-green-100 text-green-600'
                            )}>
                              <ArrowRightLeft className="w-5 h-5" />
                            </div>
                            <div>
                              <p className="font-medium text-gray-900">
                                {record.type === 'IN' ? '转入' : '转出'} {record.providerName}
                              </p>
                              <p className="text-sm text-gray-500">
                                {new Date(record.createdAt).toLocaleString()}
                              </p>
                            </div>
                          </div>
                          
                          <div className="text-right">
                            <p className={cn(
                              'text-lg font-bold',
                              record.type === 'IN' ? 'text-blue-600' : 'text-green-600'
                            )}>
                              {record.type === 'IN' ? '-' : '+'}
                              {formatCurrency(record.amount)}
                            </p>
                            <p className={cn(
                              'text-xs',
                              record.status === 'SUCCESS' ? 'text-success-600' :
                              record.status === 'PENDING' ? 'text-warning-600' : 'text-danger-600'
                            )}>
                              {record.status === 'SUCCESS' ? '成功' :
                               record.status === 'PENDING' ? '处理中' : '失败'}
                            </p>
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
      </div>

      {/* 转账模态框 */}
      <Modal
        isOpen={showTransfer}
        onClose={() => setShowTransfer(false)}
        title={`${transferType === 'IN' ? '转入' : '转出'}场馆`}
        size="md"
      >
        {selectedProvider && (
          <div className="p-6">
            <div className="mb-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                  <Football className="w-6 h-6 text-gray-500" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {selectedProvider.name}
                  </h3>
                  <p className="text-sm text-gray-500">
                    场馆余额: {formatCurrency(selectedProvider.balance)}
                  </p>
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div>
                    <p className="text-sm text-gray-600">中心钱包</p>
                    <p className="font-bold text-blue-600">
                      {formatCurrency(mainBalance)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">场馆余额</p>
                    <p className="font-bold text-green-600">
                      {formatCurrency(selectedProvider.balance)}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* 转账方向选择 */}
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">转账方向：</p>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setTransferType('IN')}
                  className={cn(
                    'p-3 rounded-lg border-2 text-center transition-colors',
                    transferType === 'IN'
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300'
                  )}
                >
                  <ArrowRightLeft className="w-5 h-5 mx-auto mb-1" />
                  <p className="text-sm font-medium">转入场馆</p>
                </button>
                <button
                  onClick={() => setTransferType('OUT')}
                  className={cn(
                    'p-3 rounded-lg border-2 text-center transition-colors',
                    transferType === 'OUT'
                      ? 'border-green-500 bg-green-50 text-green-700'
                      : 'border-gray-200 hover:border-gray-300'
                  )}
                >
                  <ArrowRightLeft className="w-5 h-5 mx-auto mb-1" />
                  <p className="text-sm font-medium">转出场馆</p>
                </button>
              </div>
            </div>

            {/* 转账金额 */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                转账金额
              </label>
              <input
                type="number"
                value={transferAmount}
                onChange={(e) => setTransferAmount(e.target.value)}
                placeholder="请输入转账金额"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                {transferType === 'IN' 
                  ? `可转入金额: ${formatCurrency(mainBalance)}`
                  : `可转出金额: ${formatCurrency(selectedProvider.balance)}`
                }
              </p>
            </div>

            {/* 操作按钮 */}
            <div className="grid grid-cols-2 gap-4">
              <Button
                variant="outline"
                onClick={() => setShowTransfer(false)}
              >
                取消
              </Button>
              <Button
                variant="primary"
                onClick={executeTransfer}
                disabled={!transferAmount || parseFloat(transferAmount) <= 0}
              >
                确认转账
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
    </GameEnhancer>
  );
};

export default SportsPage;