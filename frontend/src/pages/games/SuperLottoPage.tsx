import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Trophy, 
  Clock, 
  Star,
  Info,
  ShoppingCart,
  Zap,
  TrendingUp,
  Calendar,
  Users,
  Gift,
  Target,
  Sparkles
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import GameEnhancer from '@/components/games/GameEnhancer';
import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/format';

// 大乐透投注类型
interface SuperLottoBet {
  id: string;
  frontNumbers: number[];
  backNumbers: number[];
  betType: 'single' | 'multiple' | 'drag';
  multiplier: number;
  amount: number;
  drawNumber: string;
  createdAt: string;
}

// 开奖信息
interface DrawInfo {
  drawNumber: string;
  drawTime: string;
  jackpot: number;
  salesAmount: number;
  status: 'OPEN' | 'CLOSED' | 'DRAWN';
  timeLeft: string;
  winningNumbers?: {
    front: number[];
    back: number[];
  };
}

// 中奖等级
interface PrizeLevel {
  level: number;
  name: string;
  condition: string;
  prize: string;
  winners?: number;
  totalPrize?: number;
}

const SuperLottoPage: React.FC = () => {
  const [selectedFrontNumbers, setSelectedFrontNumbers] = useState<number[]>([]);
  const [selectedBackNumbers, setSelectedBackNumbers] = useState<number[]>([]);
  const [betType, setBetType] = useState<'single' | 'multiple' | 'drag'>('single');
  const [multiplier, setMultiplier] = useState(1);
  const [showRules, setShowRules] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showCart, setShowCart] = useState(false);
  const [cart, setCart] = useState<SuperLottoBet[]>([]);
  const [balance, setBalance] = useState(25000);
  const [activeTab, setActiveTab] = useState('bet');

  // 模拟当前期次信息
  const [currentDraw, setCurrentDraw] = useState<DrawInfo>({
    drawNumber: '25009',
    drawTime: '2024-01-24 21:30:00',
    jackpot: 125000000,
    salesAmount: 52000000,
    status: 'OPEN',
    timeLeft: '1天8:25:30'
  });

  // 中奖等级配置
  const prizeLevels: PrizeLevel[] = [
    { level: 1, name: '一等奖', condition: '5+2', prize: '奖池75%' },
    { level: 2, name: '二等奖', condition: '5+1', prize: '奖池18%' },
    { level: 3, name: '三等奖', condition: '5+0', prize: '10,000元' },
    { level: 4, name: '四等奖', condition: '4+2', prize: '3,000元' },
    { level: 5, name: '五等奖', condition: '4+1', prize: '300元' },
    { level: 6, name: '六等奖', condition: '3+2', prize: '200元' },
    { level: 7, name: '七等奖', condition: '4+0', prize: '100元' },
    { level: 8, name: '八等奖', condition: '3+1或2+2', prize: '15元' },
    { level: 9, name: '九等奖', condition: '3+0或1+2或2+1或0+2', prize: '5元' },
  ];

  // 历史开奖记录
  const historyDraws = [
    {
      drawNumber: '25007',
      drawTime: '2024-01-20 21:30:00',
      winningNumbers: { front: [5, 12, 18, 23, 31], back: [3, 9] },
      jackpot: 115000000,
      winners: [0, 3, 45, 234, 1567, 3421, 8765, 23456, 67890]
    },
    {
      drawNumber: '25006',
      drawTime: '2024-01-17 21:30:00',
      winningNumbers: { front: [2, 8, 15, 27, 34], back: [1, 11] },
      jackpot: 108000000,
      winners: [1, 2, 38, 189, 1234, 2987, 7654, 19876, 54321]
    },
  ];

  // 选择前区号码
  const selectFrontNumber = (number: number) => {
    if (selectedFrontNumbers.includes(number)) {
      setSelectedFrontNumbers(prev => prev.filter(n => n !== number));
    } else if (selectedFrontNumbers.length < 5) {
      setSelectedFrontNumbers(prev => [...prev, number].sort((a, b) => a - b));
    }
  };

  // 选择后区号码
  const selectBackNumber = (number: number) => {
    if (selectedBackNumbers.includes(number)) {
      setSelectedBackNumbers(prev => prev.filter(n => n !== number));
    } else if (selectedBackNumbers.length < 2) {
      setSelectedBackNumbers(prev => [...prev, number].sort((a, b) => a - b));
    }
  };

  // 随机选号
  const randomSelect = () => {
    // 随机选择5个前区号码
    const frontNumbers: number[] = [];
    while (frontNumbers.length < 5) {
      const num = Math.floor(Math.random() * 35) + 1;
      if (!frontNumbers.includes(num)) {
        frontNumbers.push(num);
      }
    }
    
    // 随机选择2个后区号码
    const backNumbers: number[] = [];
    while (backNumbers.length < 2) {
      const num = Math.floor(Math.random() * 12) + 1;
      if (!backNumbers.includes(num)) {
        backNumbers.push(num);
      }
    }
    
    setSelectedFrontNumbers(frontNumbers.sort((a, b) => a - b));
    setSelectedBackNumbers(backNumbers.sort((a, b) => a - b));
  };

  // 清空选号
  const clearSelection = () => {
    setSelectedFrontNumbers([]);
    setSelectedBackNumbers([]);
  };

  // 计算投注金额
  const calculateBetAmount = () => {
    if (selectedFrontNumbers.length === 5 && selectedBackNumbers.length === 2) {
      return 2 * multiplier; // 每注2元
    }
    return 0;
  };

  // 添加到购彩篮
  const addToCart = () => {
    if (selectedFrontNumbers.length === 5 && selectedBackNumbers.length === 2) {
      const newBet: SuperLottoBet = {
        id: `bet-${Date.now()}`,
        frontNumbers: [...selectedFrontNumbers],
        backNumbers: [...selectedBackNumbers],
        betType,
        multiplier,
        amount: calculateBetAmount(),
        drawNumber: currentDraw.drawNumber,
        createdAt: new Date().toISOString()
      };
      
      setCart(prev => [...prev, newBet]);
      clearSelection();
    }
  };

  // 立即投注
  const placeBet = () => {
    const amount = calculateBetAmount();
    if (amount > 0 && balance >= amount) {
      setBalance(prev => prev - amount);
      // 这里应该调用API提交投注
      alert(`投注成功！投注金额：${formatCurrency(amount)}`);
      clearSelection();
    }
  };

  // 购彩篮投注
  const placeCartBets = () => {
    const totalAmount = cart.reduce((sum, bet) => sum + bet.amount, 0);
    if (totalAmount > 0 && balance >= totalAmount) {
      setBalance(prev => prev - totalAmount);
      setCart([]);
      setShowCart(false);
      alert(`投注成功！总投注金额：${formatCurrency(totalAmount)}`);
    }
  };

  // 倒计时更新
  useEffect(() => {
    const timer = setInterval(() => {
      // 这里应该从API获取最新的倒计时
      // 模拟倒计时更新
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <GameEnhancer 
      gameName="大乐透"
      showSoundControl={true}
      showFullscreen={true}
      showNotifications={true}
      showHelp={true}
    >
      <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
      {/* 页面头部 */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white px-4 py-6 lg:px-6">
        <div className="container-responsive">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold mb-1">大乐透</h1>
              <p className="text-white text-opacity-80">
                每周三、六、日开奖，亿元大奖等你来
              </p>
            </div>
            <div className="text-right">
              <p className="text-white text-opacity-80 text-sm">我的余额</p>
              <p className="text-xl font-bold">
                {formatCurrency(balance)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 当前期次信息 */}
      <div className="container-responsive py-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
            <CardContent className="p-4">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Trophy className="w-5 h-5 text-purple-600 mr-1" />
                    <span className="text-sm text-gray-600">当前期号</span>
                  </div>
                  <p className="text-xl font-bold text-purple-700">
                    第{currentDraw.drawNumber}期
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Gift className="w-5 h-5 text-purple-600 mr-1" />
                    <span className="text-sm text-gray-600">奖池金额</span>
                  </div>
                  <p className="text-xl font-bold text-purple-700">
                    {formatCurrency(currentDraw.jackpot)}
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Clock className="w-5 h-5 text-purple-600 mr-1" />
                    <span className="text-sm text-gray-600">距离截止</span>
                  </div>
                  <p className="text-lg font-bold text-danger-600">
                    {currentDraw.timeLeft}
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Users className="w-5 h-5 text-purple-600 mr-1" />
                    <span className="text-sm text-gray-600">销售金额</span>
                  </div>
                  <p className="text-lg font-bold text-purple-700">
                    {formatCurrency(currentDraw.salesAmount)}
                  </p>
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
            onClick={() => setActiveTab('bet')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              activeTab === 'bet'
                ? 'bg-white text-purple-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            投注选号
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              activeTab === 'history'
                ? 'bg-white text-purple-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            开奖历史
          </button>
          <button
            onClick={() => setActiveTab('prizes')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              activeTab === 'prizes'
                ? 'bg-white text-purple-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            奖级说明
          </button>
        </div>
      </div>

      <div className="container-responsive space-y-6">
        {/* 投注选号 */}
        {activeTab === 'bet' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
          >
            {/* 前区选号 */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">
                    前区号码 (35选5)
                  </h2>
                  <div className="text-sm text-gray-600">
                    已选 {selectedFrontNumbers.length}/5
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-7 gap-2 mb-4">
                  {Array.from({ length: 35 }, (_, i) => i + 1).map((number) => (
                    <button
                      key={number}
                      onClick={() => selectFrontNumber(number)}
                      className={cn(
                        'w-10 h-10 rounded-full border-2 text-sm font-medium transition-all duration-200',
                        selectedFrontNumbers.includes(number)
                          ? 'bg-purple-600 border-purple-600 text-white shadow-md'
                          : 'border-gray-300 text-gray-700 hover:border-purple-400 hover:bg-purple-50'
                      )}
                    >
                      {number.toString().padStart(2, '0')}
                    </button>
                  ))}
                </div>
                
                {selectedFrontNumbers.length > 0 && (
                  <div className="bg-purple-50 rounded-lg p-3">
                    <p className="text-sm text-gray-600 mb-2">已选前区号码：</p>
                    <div className="flex flex-wrap gap-2">
                      {selectedFrontNumbers.map((number) => (
                        <span
                          key={number}
                          className="inline-flex items-center px-2 py-1 rounded-full bg-purple-600 text-white text-sm"
                        >
                          {number.toString().padStart(2, '0')}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 后区选号 */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">
                    后区号码 (12选2)
                  </h2>
                  <div className="text-sm text-gray-600">
                    已选 {selectedBackNumbers.length}/2
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-6 gap-2 mb-4">
                  {Array.from({ length: 12 }, (_, i) => i + 1).map((number) => (
                    <button
                      key={number}
                      onClick={() => selectBackNumber(number)}
                      className={cn(
                        'w-10 h-10 rounded-full border-2 text-sm font-medium transition-all duration-200',
                        selectedBackNumbers.includes(number)
                          ? 'bg-pink-600 border-pink-600 text-white shadow-md'
                          : 'border-gray-300 text-gray-700 hover:border-pink-400 hover:bg-pink-50'
                      )}
                    >
                      {number.toString().padStart(2, '0')}
                    </button>
                  ))}
                </div>
                
                {selectedBackNumbers.length > 0 && (
                  <div className="bg-pink-50 rounded-lg p-3">
                    <p className="text-sm text-gray-600 mb-2">已选后区号码：</p>
                    <div className="flex flex-wrap gap-2">
                      {selectedBackNumbers.map((number) => (
                        <span
                          key={number}
                          className="inline-flex items-center px-2 py-1 rounded-full bg-pink-600 text-white text-sm"
                        >
                          {number.toString().padStart(2, '0')}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 操作按钮 */}
            <Card>
              <CardContent className="p-4">
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <Button
                    variant="outline"
                    icon={<Sparkles className="w-4 h-4" />}
                    onClick={randomSelect}
                  >
                    随机选号
                  </Button>
                  <Button
                    variant="outline"
                    onClick={clearSelection}
                  >
                    清空选号
                  </Button>
                </div>

                {/* 倍数选择 */}
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-2">投注倍数：</p>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setMultiplier(Math.max(1, multiplier - 1))}
                      disabled={multiplier <= 1}
                    >
                      -
                    </Button>
                    <span className="px-4 py-2 bg-gray-100 rounded-md font-medium">
                      {multiplier}倍
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setMultiplier(Math.min(99, multiplier + 1))}
                      disabled={multiplier >= 99}
                    >
                      +
                    </Button>
                  </div>
                </div>

                {/* 投注金额 */}
                <div className="bg-gray-50 rounded-lg p-3 mb-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">投注金额：</span>
                    <span className="text-lg font-bold text-purple-700">
                      {formatCurrency(calculateBetAmount())}
                    </span>
                  </div>
                </div>

                {/* 投注按钮 */}
                <div className="grid grid-cols-2 gap-4">
                  <Button
                    variant="outline"
                    icon={<ShoppingCart className="w-5 h-5" />}
                    onClick={addToCart}
                    disabled={selectedFrontNumbers.length !== 5 || selectedBackNumbers.length !== 2}
                  >
                    加入购彩篮
                  </Button>
                  <Button
                    variant="primary"
                    icon={<Zap className="w-5 h-5" />}
                    onClick={placeBet}
                    disabled={selectedFrontNumbers.length !== 5 || selectedBackNumbers.length !== 2 || balance < calculateBetAmount()}
                  >
                    立即投注
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* 开奖历史 */}
        {activeTab === 'history' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-4"
          >
            {historyDraws.map((draw) => (
              <Card key={draw.drawNumber}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        第{draw.drawNumber}期
                      </h3>
                      <p className="text-sm text-gray-500">
                        {new Date(draw.drawTime).toLocaleString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">奖池</p>
                      <p className="font-bold text-purple-700">
                        {formatCurrency(draw.jackpot)}
                      </p>
                    </div>
                  </div>

                  {/* 开奖号码 */}
                  <div className="bg-gray-50 rounded-lg p-3 mb-3">
                    <p className="text-sm text-gray-600 mb-2">开奖号码：</p>
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        {draw.winningNumbers.front.map((number, index) => (
                          <span
                            key={index}
                            className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-bold"
                          >
                            {number.toString().padStart(2, '0')}
                          </span>
                        ))}
                      </div>
                      <span className="text-gray-400">+</span>
                      <div className="flex space-x-1">
                        {draw.winningNumbers.back.map((number, index) => (
                          <span
                            key={index}
                            className="w-8 h-8 bg-pink-600 text-white rounded-full flex items-center justify-center text-sm font-bold"
                          >
                            {number.toString().padStart(2, '0')}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* 中奖统计 */}
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-xs text-gray-500">一等奖</p>
                      <p className="font-bold text-danger-600">
                        {draw.winners[0]}注
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">二等奖</p>
                      <p className="font-bold text-warning-600">
                        {draw.winners[1]}注
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">三等奖</p>
                      <p className="font-bold text-success-600">
                        {draw.winners[2]}注
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </motion.div>
        )}

        {/* 奖级说明 */}
        {activeTab === 'prizes' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold text-gray-900">
                  奖级设置
                </h2>
              </CardHeader>
              <CardContent className="p-0">
                <div className="divide-y divide-gray-200">
                  {prizeLevels.map((prize) => (
                    <div key={prize.level} className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={cn(
                            'w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold',
                            prize.level <= 3 ? 'bg-danger-500' :
                            prize.level <= 6 ? 'bg-warning-500' : 'bg-success-500'
                          )}>
                            {prize.level}
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">
                              {prize.name}
                            </p>
                            <p className="text-sm text-gray-500">
                              {prize.condition}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-gray-900">
                            {prize.prize}
                          </p>
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

      {/* 购彩篮 */}
      {cart.length > 0 && (
        <div className="fixed bottom-20 lg:bottom-4 right-4 z-50">
          <Button
            variant="primary"
            size="lg"
            icon={<ShoppingCart className="w-5 h-5" />}
            onClick={() => setShowCart(true)}
            className="shadow-lg"
          >
            购彩篮 ({cart.length})
          </Button>
        </div>
      )}

      {/* 购彩篮模态框 */}
      <Modal
        isOpen={showCart}
        onClose={() => setShowCart(false)}
        title="购彩篮"
        size="lg"
      >
        <div className="p-6">
          {cart.length === 0 ? (
            <div className="text-center py-8">
              <ShoppingCart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">购彩篮为空</p>
            </div>
          ) : (
            <>
              <div className="space-y-4 mb-6">
                {cart.map((bet) => (
                  <div key={bet.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">第{bet.drawNumber}期</span>
                      <span className="font-bold text-purple-700">
                        {formatCurrency(bet.amount)}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm">
                      <div className="flex space-x-1">
                        {bet.frontNumbers.map((number, index) => (
                          <span
                            key={index}
                            className="w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-xs"
                          >
                            {number.toString().padStart(2, '0')}
                          </span>
                        ))}
                      </div>
                      <span className="text-gray-400">+</span>
                      <div className="flex space-x-1">
                        {bet.backNumbers.map((number, index) => (
                          <span
                            key={index}
                            className="w-6 h-6 bg-pink-600 text-white rounded-full flex items-center justify-center text-xs"
                          >
                            {number.toString().padStart(2, '0')}
                          </span>
                        ))}
                      </div>
                      <span className="text-gray-500">
                        {bet.multiplier}倍
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="border-t pt-4">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-lg font-medium">总金额：</span>
                  <span className="text-xl font-bold text-purple-700">
                    {formatCurrency(cart.reduce((sum, bet) => sum + bet.amount, 0))}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Button
                    variant="outline"
                    onClick={() => setCart([])}
                  >
                    清空购彩篮
                  </Button>
                  <Button
                    variant="primary"
                    onClick={placeCartBets}
                    disabled={balance < cart.reduce((sum, bet) => sum + bet.amount, 0)}
                  >
                    确认投注
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>
      </Modal>

      {/* 游戏规则模态框 */}
      <Modal
        isOpen={showRules}
        onClose={() => setShowRules(false)}
        title="大乐透游戏规则"
        size="lg"
      >
        <div className="p-6 space-y-4">
          <div>
            <h3 className="font-semibold text-lg mb-2">基本规则</h3>
            <ul className="list-disc pl-5 space-y-2 text-gray-700">
              <li>前区从01-35中选择5个号码</li>
              <li>后区从01-12中选择2个号码</li>
              <li>每注基本投注金额为2元</li>
              <li>每周三、六、日21:30开奖</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-lg mb-2">投注方式</h3>
            <ul className="list-disc pl-5 space-y-2 text-gray-700">
              <li>单式投注：选择5+2个号码组成一注</li>
              <li>复式投注：选择超过5+2个号码的多注组合</li>
              <li>胆拖投注：选择胆码和拖码的组合投注</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-lg mb-2">中奖说明</h3>
            <p className="text-gray-700 mb-2">
              根据投注号码与开奖号码相符的个数确定中奖等级：
            </p>
            <ul className="list-disc pl-5 space-y-1 text-gray-700">
              <li>一等奖：前区5个号码+后区2个号码</li>
              <li>二等奖：前区5个号码+后区1个号码</li>
              <li>三等奖：前区5个号码+后区0个号码</li>
              <li>其他等级详见奖级说明</li>
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
    </GameEnhancer>
  );
};

export default SuperLottoPage;