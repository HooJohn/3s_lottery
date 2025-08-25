import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Clock,
  Trophy,
  TrendingUp,
  RotateCcw,
  ShoppingCart,
  Zap,
  Target,
  Dice1,
  Dice2,
  Dice3,
  Dice4,
  Dice5
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import GameEnhancer from '@/components/games/GameEnhancer';
import { cn } from '@/utils/cn';
import { formatCurrency, formatCountdown } from '@/utils/format';

const Lottery11x5Page: React.FC = () => {
  const [selectedNumbers, setSelectedNumbers] = useState<number[]>([]);
  const [playType, setPlayType] = useState<'position' | 'any2' | 'any3' | 'any4' | 'any5'>('any3');
  const [betAmount, setBetAmount] = useState(2);
  const [multiplier, setMultiplier] = useState(1);
  const [timeLeft, setTimeLeft] = useState(125); // 2分5秒

  // 开奖结果相关状态
  const [drawResults, setDrawResults] = useState<any[]>([]);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [isDrawing, setIsDrawing] = useState<boolean>(false);
  const [selectedDraw, setSelectedDraw] = useState<any>(null);
  const [showDrawResults, setShowDrawResults] = useState<boolean>(false);

  // 走势分析相关状态
  const [trendPeriod, setTrendPeriod] = useState<10 | 30 | 50 | 100>(30);
  const [showTrendDetails, setShowTrendDetails] = useState<boolean>(false);
  const [selectedTrendNumber, setSelectedTrendNumber] = useState<number | null>(null);
  const [trendViewType, setTrendViewType] = useState<'frequency' | 'missing' | 'sum' | 'span'>('frequency');
  const [showTrendChart, setShowTrendChart] = useState<boolean>(false);

  // 模拟当前期次数据
  const currentDraw = {
    drawNumber: '20240121-089',
    drawTime: '2024-01-21T14:00:00Z',
    jackpot: 1350000,
    totalBets: 18420,
  };

  // 模拟最新开奖结果
  const latestResult = {
    drawNumber: '20240121-088',
    numbers: [1, 5, 8, 10, 11],
    drawTime: '2024-01-21T13:55:00Z',
  };

  // 模拟热号冷号数据
  const hotNumbers = [3, 7, 11, 1, 9];
  const coldNumbers = [6, 10, 4, 8, 2];

  // 模拟开奖结果数据
  const mockDrawResults = [
    {
      drawId: '20240121-088',
      drawTime: '2024-01-21T13:55:00Z',
      numbers: [1, 5, 8, 10, 11],
      winningAmount: 2850000,
      winnerCount: 15,
      totalBets: 15420,
    },
    {
      drawId: '20240121-087',
      drawTime: '2024-01-21T13:50:00Z',
      numbers: [2, 4, 6, 9, 11],
      winningAmount: 2650000,
      winnerCount: 12,
      totalBets: 14280,
    },
    {
      drawId: '20240121-086',
      drawTime: '2024-01-21T13:45:00Z',
      numbers: [3, 5, 7, 8, 10],
      winningAmount: 3120000,
      winnerCount: 18,
      totalBets: 16850,
    },
    {
      drawId: '20240121-085',
      drawTime: '2024-01-21T13:40:00Z',
      numbers: [1, 3, 6, 9, 11],
      winningAmount: 2480000,
      winnerCount: 9,
      totalBets: 13950,
    },
    {
      drawId: '20240121-084',
      drawTime: '2024-01-21T13:35:00Z',
      numbers: [2, 5, 7, 10, 11],
      winningAmount: 2890000,
      winnerCount: 14,
      totalBets: 15680,
    },
    {
      drawId: '20240121-083',
      drawTime: '2024-01-21T13:30:00Z',
      numbers: [4, 6, 8, 9, 11],
      winningAmount: 2320000,
      winnerCount: 8,
      totalBets: 12450,
    },
    {
      drawId: '20240121-082',
      drawTime: '2024-01-21T13:25:00Z',
      numbers: [1, 2, 5, 7, 10],
      winningAmount: 2750000,
      winnerCount: 13,
      totalBets: 14890,
    },
    {
      drawId: '20240121-081',
      drawTime: '2024-01-21T13:20:00Z',
      numbers: [3, 4, 6, 8, 11],
      winningAmount: 2980000,
      winnerCount: 16,
      totalBets: 15670,
    },
  ];

  // 模拟历史开奖数据
  const historyResults = mockDrawResults;

  // 模拟用户投注记录
  const userBets = [
    {
      id: 'BET-001',
      drawNumber: '20240121-088',
      betType: 'any5',
      numbers: [1, 5, 8, 10, 11],
      amount: 10,
      multiple: 1,
      status: 'WON',
      payout: 5400,
      betTime: '2024-01-21T13:52:00Z',
    },
    {
      id: 'BET-002',
      drawNumber: '20240121-087',
      betType: 'any3',
      numbers: [2, 4, 6],
      amount: 5,
      multiple: 2,
      status: 'WON',
      payout: 190,
      betTime: '2024-01-21T13:47:00Z',
    },
    {
      id: 'BET-003',
      drawNumber: '20240121-086',
      betType: 'any4',
      numbers: [1, 2, 9, 11],
      amount: 8,
      multiple: 1,
      status: 'LOST',
      payout: 0,
      betTime: '2024-01-21T13:42:00Z',
    },
  ];

  // 倒计时效果
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => (prev > 0 ? prev - 1 : 125));
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // 玩法配置
  const playTypes = [
    { key: 'position', label: '定位胆', icon: Target, desc: '预测指定位置号码' },
    { key: 'any2', label: '任选二', icon: Dice2, desc: '选择2个号码' },
    { key: 'any3', label: '任选三', icon: Dice3, desc: '选择3个号码' },
    { key: 'any4', label: '任选四', icon: Dice4, desc: '选择4个号码' },
    { key: 'any5', label: '任选五', icon: Dice5, desc: '选择5个号码' },
  ];

  // 号码选择处理
  const handleNumberSelect = (number: number) => {
    setSelectedNumbers(prev => {
      if (prev.includes(number)) {
        return prev.filter(n => n !== number);
      } else {
        const maxSelection = playType === 'position' ? 5 : parseInt(playType.slice(-1));
        if (prev.length < maxSelection) {
          return [...prev, number].sort((a, b) => a - b);
        }
        return prev;
      }
    });
  };

  // 快捷选择
  const quickSelect = (type: string) => {
    switch (type) {
      case 'all':
        setSelectedNumbers([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
        break;
      case 'big':
        setSelectedNumbers([6, 7, 8, 9, 10, 11]);
        break;
      case 'small':
        setSelectedNumbers([1, 2, 3, 4, 5]);
        break;
      case 'odd':
        setSelectedNumbers([1, 3, 5, 7, 9, 11]);
        break;
      case 'even':
        setSelectedNumbers([2, 4, 6, 8, 10]);
        break;
      case 'clear':
        setSelectedNumbers([]);
        break;
      case 'hot':
        setSelectedNumbers(hotNumbers);
        break;
      case 'cold':
        setSelectedNumbers(coldNumbers);
        break;
    }
  };

  // 计算投注金额
  const calculateTotalAmount = () => {
    const requiredCount = playType === 'position' ? 1 : parseInt(playType.slice(-1));
    if (selectedNumbers.length < requiredCount) return 0;

    let combinations = 1;
    if (playType !== 'position' && selectedNumbers.length > requiredCount) {
      // 计算组合数
      const n = selectedNumbers.length;
      const r = requiredCount;
      combinations = factorial(n) / (factorial(r) * factorial(n - r));
    }

    return combinations * betAmount * multiplier;
  };

  // 计算阶乘
  const factorial = (n: number): number => {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
  };

  // 计算预计奖金
  const calculatePotentialWin = () => {
    const odds = {
      position: 9.8,
      any2: 6.5,
      any3: 19.0,
      any4: 78.0,
      any5: 540.0,
    };

    return calculateTotalAmount() * odds[playType];
  };

  // 开奖动画效果
  const startDrawAnimation = () => {
    setIsDrawing(true);

    // 模拟开奖过程，3秒后显示结果
    setTimeout(() => {
      setIsDrawing(false);
      // 这里可以更新最新开奖结果
    }, 3000);
  };

  // 生成走势分析数据
  const generateTrendData = (period: number) => {
    const trendData: { [key: number]: { count: number, missing: number, lastAppear: number } } = {};

    // 初始化数据
    for (let i = 1; i <= 11; i++) {
      trendData[i] = { count: 0, missing: 0, lastAppear: 0 };
    }

    // 基于历史开奖数据计算走势
    const recentResults = historyResults.slice(0, period);
    recentResults.forEach((result, index) => {
      result.numbers.forEach((number: number) => {
        trendData[number].count++;
        trendData[number].lastAppear = index;
      });
    });

    // 计算遗漏值
    Object.keys(trendData).forEach(key => {
      const num = parseInt(key);
      trendData[num].missing = trendData[num].lastAppear;
    });

    return trendData;
  };

  // 获取当前期数的走势数据
  const currentTrendData = generateTrendData(trendPeriod);

  // 获取热号和冷号（基于选择的期数）
  const getTrendNumbers = () => {
    const sortedByCount = Object.entries(currentTrendData)
      .sort(([, a], [, b]) => b.count - a.count);

    const hotNums = sortedByCount.slice(0, 5).map(([num]) => parseInt(num));
    const coldNums = sortedByCount.slice(-5).map(([num]) => parseInt(num));

    return { hotNums, coldNums };
  };

  const { hotNums, coldNums } = getTrendNumbers();

  // 计算和值走势数据
  const generateSumTrendData = (period: number) => {
    const sumData: { [key: number]: number } = {};

    const recentResults = historyResults.slice(0, period);
    recentResults.forEach((result) => {
      const sum = result.numbers.reduce((a: number, b: number) => a + b, 0);
      sumData[sum] = (sumData[sum] || 0) + 1;
    });

    return sumData;
  };

  // 计算跨度走势数据
  const generateSpanTrendData = (period: number) => {
    const spanData: { [key: number]: number } = {};

    const recentResults = historyResults.slice(0, period);
    recentResults.forEach((result) => {
      const sortedNumbers = [...result.numbers].sort((a, b) => a - b);
      const span = sortedNumbers[sortedNumbers.length - 1] - sortedNumbers[0];
      spanData[span] = (spanData[span] || 0) + 1;
    });

    return spanData;
  };

  // 计算连号分析数据
  const generateConsecutiveAnalysis = (period: number) => {
    const consecutiveData = {
      consecutive2: 0,
      consecutive3: 0,
      consecutive4: 0,
      consecutive5: 0,
    };

    const recentResults = historyResults.slice(0, period);
    recentResults.forEach((result) => {
      const sortedNumbers = [...result.numbers].sort((a, b) => a - b);

      // 检查连号
      let maxConsecutive = 1;
      let currentConsecutive = 1;

      for (let i = 1; i < sortedNumbers.length; i++) {
        if (sortedNumbers[i] === sortedNumbers[i - 1] + 1) {
          currentConsecutive++;
          maxConsecutive = Math.max(maxConsecutive, currentConsecutive);
        } else {
          currentConsecutive = 1;
        }
      }

      if (maxConsecutive >= 2) consecutiveData.consecutive2++;
      if (maxConsecutive >= 3) consecutiveData.consecutive3++;
      if (maxConsecutive >= 4) consecutiveData.consecutive4++;
      if (maxConsecutive >= 5) consecutiveData.consecutive5++;
    });

    return consecutiveData;
  };

  // 获取当前分析数据
  const currentSumData = generateSumTrendData(trendPeriod);
  const currentSpanData = generateSpanTrendData(trendPeriod);
  const currentConsecutiveData = generateConsecutiveAnalysis(trendPeriod);

  return (
    <GameEnhancer
      gameName="11选5彩票"
      showSoundControl={true}
      showFullscreen={true}
      showNotifications={true}
      showHelp={true}
    >
      <div className="min-h-screen bg-gray-50 pb-32 lg:pb-0">
        {/* 页面头部 */}
        <div className="bg-gradient-primary text-white px-4 py-6 lg:px-6">
          <div className="container-responsive">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold mb-1">11选5彩票</h1>
                <p className="text-white text-opacity-80">
                  每期5分钟，天天开奖
                </p>
              </div>
              <div className="text-right">
                <p className="text-white text-opacity-80 text-sm">奖池金额</p>
                <p className="text-xl font-bold">
                  {formatCurrency(currentDraw.jackpot)}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="container-responsive py-6 space-y-6">
          {/* 期次信息和倒计时 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">当前期次</p>
                    <p className="text-xl font-bold text-gray-900">
                      {currentDraw.drawNumber}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      总投注: {currentDraw.totalBets.toLocaleString()} 注
                    </p>
                  </div>

                  <div className="text-center">
                    <div className="flex items-center space-x-1 mb-2">
                      <Clock className="w-5 h-5 text-danger-500" />
                      <span className="text-sm text-gray-600">距离封盘</span>
                    </div>
                    <div className="flex space-x-1">
                      {formatCountdown(timeLeft).split(':').map((digit, index) => (
                        <React.Fragment key={index}>
                          <div className="countdown-digit">
                            {digit}
                          </div>
                          {index < 2 && <span className="text-danger-500 font-bold">:</span>}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* 最新开奖结果 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">
                    最新开奖
                  </h2>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">
                      {latestResult.drawNumber}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={startDrawAnimation}
                      disabled={isDrawing}
                      className="text-xs"
                    >
                      {isDrawing ? '开奖中...' : '模拟开奖'}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center space-x-3">
                  {isDrawing ? (
                    // 开奖动画效果
                    Array.from({ length: 5 }, (_, index) => (
                      <motion.div
                        key={index}
                        className="lottery-ball drawing"
                        animate={{
                          rotate: [0, 360],
                          scale: [1, 1.1, 1],
                        }}
                        transition={{
                          duration: 0.5,
                          repeat: Infinity,
                          delay: index * 0.1,
                        }}
                      >
                        <motion.span
                          animate={{
                            opacity: [1, 0.3, 1],
                          }}
                          transition={{
                            duration: 0.3,
                            repeat: Infinity,
                            delay: index * 0.05,
                          }}
                        >
                          ?
                        </motion.span>
                      </motion.div>
                    ))
                  ) : (
                    // 正常开奖结果显示
                    latestResult.numbers.map((number, index) => (
                      <motion.div
                        key={index}
                        initial={{ scale: 0, rotate: 180 }}
                        animate={{ scale: 1, rotate: 0 }}
                        transition={{
                          duration: 0.5,
                          delay: index * 0.1,
                          type: "spring",
                          stiffness: 200
                        }}
                        className="lottery-ball winning"
                      >
                        {number.toString().padStart(2, '0')}
                      </motion.div>
                    ))
                  )}
                </div>

                {/* 开奖统计信息 */}
                <div className="mt-4 grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-xs text-gray-500">总投注</p>
                    <p className="font-medium text-gray-900">
                      {latestResult.numbers.reduce((a, b) => a + b, 0) * 1000} 注
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">中奖人数</p>
                    <p className="font-medium text-success-600">
                      {Math.floor(Math.random() * 20) + 5} 人
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">奖金池</p>
                    <p className="font-medium text-primary-600">
                      {formatCurrency(Math.floor(Math.random() * 1000000) + 500000)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* 玩法选择 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold text-gray-900">
                  选择玩法
                </h2>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
                  {playTypes.map((type) => {
                    const Icon = type.icon;
                    return (
                      <button
                        key={type.key}
                        onClick={() => {
                          setPlayType(type.key as any);
                          setSelectedNumbers([]);
                        }}
                        className={cn(
                          'p-4 rounded-lg border-2 transition-all duration-200 text-center',
                          playType === type.key
                            ? 'border-primary-500 bg-primary-50 text-primary-700'
                            : 'border-gray-200 hover:border-gray-300 text-gray-600'
                        )}
                      >
                        <Icon className="w-6 h-6 mx-auto mb-2" />
                        <p className="font-medium text-sm">{type.label}</p>
                        <p className="text-xs opacity-75 mt-1">{type.desc}</p>
                      </button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* 号码选择区域 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">
                    选择号码
                  </h2>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <span>已选</span>
                    <span className="font-bold text-primary-600">
                      {selectedNumbers.length}
                    </span>
                    <span>个号码</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* 快捷选择按钮 */}
                <div className="flex flex-wrap gap-2 mb-6">
                  {[
                    { key: 'all', label: '全选' },
                    { key: 'big', label: '大号' },
                    { key: 'small', label: '小号' },
                    { key: 'odd', label: '奇数' },
                    { key: 'even', label: '偶数' },
                    { key: 'hot', label: '热号' },
                    { key: 'cold', label: '冷号' },
                    { key: 'clear', label: '清空' },
                  ].map((item) => (
                    <Button
                      key={item.key}
                      variant="outline"
                      size="sm"
                      onClick={() => quickSelect(item.key)}
                      className="text-xs"
                    >
                      {item.label}
                    </Button>
                  ))}
                </div>

                {/* 号码网格 */}
                <div className="grid grid-cols-6 lg:grid-cols-11 gap-3">
                  {Array.from({ length: 11 }, (_, i) => i + 1).map((number) => (
                    <motion.button
                      key={number}
                      onClick={() => handleNumberSelect(number)}
                      className={cn(
                        'lottery-ball transition-all duration-200',
                        selectedNumbers.includes(number) && 'selected',
                        hotNumbers.includes(number) && !selectedNumbers.includes(number) && 'ring-2 ring-danger-200',
                        coldNumbers.includes(number) && !selectedNumbers.includes(number) && 'ring-2 ring-info-200'
                      )}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {number.toString().padStart(2, '0')}
                    </motion.button>
                  ))}
                </div>

                {/* 号码说明 */}
                <div className="flex items-center justify-center space-x-6 mt-4 text-xs text-gray-500">
                  <div className="flex items-center space-x-1">
                    <div className="w-3 h-3 rounded-full ring-2 ring-danger-200"></div>
                    <span>热号</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-3 h-3 rounded-full ring-2 ring-info-200"></div>
                    <span>冷号</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-3 h-3 rounded-full bg-primary-500"></div>
                    <span>已选</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* 投注面板 */}
          <AnimatePresence>
            {selectedNumbers.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 50 }}
                transition={{ duration: 0.3 }}
                className="fixed bottom-20 lg:bottom-6 left-4 right-4 lg:left-auto lg:right-6 lg:w-80 z-40"
              >
                <Card className="shadow-heavy border-primary-200">
                  <CardContent className="p-4">
                    {/* 选中号码 */}
                    <div className="mb-4">
                      <p className="text-sm text-gray-600 mb-2">已选号码</p>
                      <div className="flex flex-wrap gap-2">
                        {selectedNumbers.map((number) => (
                          <span
                            key={number}
                            className="inline-flex items-center justify-center w-8 h-8 bg-primary-500 text-white rounded-full text-sm font-bold"
                          >
                            {number.toString().padStart(2, '0')}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* 投注设置 */}
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm text-gray-600 mb-1">
                          单注金额
                        </label>
                        <select
                          value={betAmount}
                          onChange={(e) => setBetAmount(Number(e.target.value))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        >
                          <option value={2}>2元</option>
                          <option value={20}>2角</option>
                          <option value={200}>2分</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm text-gray-600 mb-1">
                          倍数
                        </label>
                        <div className="flex items-center">
                          <button
                            onClick={() => setMultiplier(Math.max(1, multiplier - 1))}
                            className="w-8 h-8 bg-gray-200 text-gray-600 rounded-l-lg hover:bg-gray-300"
                          >
                            -
                          </button>
                          <input
                            type="number"
                            value={multiplier}
                            onChange={(e) => setMultiplier(Math.max(1, Number(e.target.value)))}
                            className="w-full px-2 py-2 text-center border-t border-b border-gray-300 focus:ring-2 focus:ring-primary-500"
                            min="1"
                            max="99"
                          />
                          <button
                            onClick={() => setMultiplier(Math.min(99, multiplier + 1))}
                            className="w-8 h-8 bg-gray-200 text-gray-600 rounded-r-lg hover:bg-gray-300"
                          >
                            +
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* 投注信息 */}
                    <div className="bg-gray-50 rounded-lg p-3 mb-4 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">投注金额:</span>
                        <span className="font-medium">
                          {formatCurrency(calculateTotalAmount())}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">预计奖金:</span>
                        <span className="font-medium text-success-600">
                          {formatCurrency(calculatePotentialWin())}
                        </span>
                      </div>
                    </div>

                    {/* 投注按钮 */}
                    <div className="grid grid-cols-2 gap-3">
                      <Button
                        variant="outline"
                        icon={<ShoppingCart className="w-4 h-4" />}
                        disabled={calculateTotalAmount() === 0}
                      >
                        加入购彩篮
                      </Button>
                      <Button
                        variant="primary"
                        icon={<Zap className="w-4 h-4" />}
                        disabled={calculateTotalAmount() === 0}
                      >
                        立即投注
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          {/* 历史开奖结果 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">
                    历史开奖
                  </h2>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<Trophy className="w-4 h-4" />}
                      onClick={() => setShowDrawResults(!showDrawResults)}
                    >
                      {showDrawResults ? '隐藏详情' : '查看详情'}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<RotateCcw className="w-4 h-4" />}
                      onClick={() => {
                        setDrawResults(mockDrawResults);
                        setCurrentPage(1);
                      }}
                    >
                      刷新
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* 开奖结果列表 */}
                <div className="space-y-4">
                  {historyResults.slice(0, showDrawResults ? 8 : 3).map((result, index) => (
                    <motion.div
                      key={result.drawId}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-pointer"
                      onClick={() => setSelectedDraw(result)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-4">
                            <div>
                              <p className="font-medium text-gray-900">{result.drawId}</p>
                              <p className="text-sm text-gray-500">
                                {new Date(result.drawTime).toLocaleString('zh-CN')}
                              </p>
                            </div>

                            {/* 开奖号码 */}
                            <div className="flex space-x-2">
                              {result.numbers.map((number, numIndex) => (
                                <div
                                  key={numIndex}
                                  className="w-8 h-8 bg-primary-500 text-white rounded-full flex items-center justify-center text-sm font-bold"
                                >
                                  {number.toString().padStart(2, '0')}
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>

                        {/* 开奖信息 */}
                        <div className="text-right">
                          <p className="text-sm text-gray-600">
                            中奖人数: <span className="font-medium">{result.winnerCount}</span>
                          </p>
                          <p className="text-sm text-success-600 font-medium">
                            奖金: {formatCurrency(result.winningAmount)}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* 分页控制 */}
                {showDrawResults && (
                  <div className="flex items-center justify-center space-x-2 mt-6">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={currentPage === 1}
                      onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    >
                      上一页
                    </Button>
                    <span className="text-sm text-gray-600">
                      第 {currentPage} 页
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(prev => prev + 1)}
                    >
                      下一页
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* 我的投注记录 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold text-gray-900">
                  我的投注记录
                </h2>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {userBets.map((bet, index) => (
                    <motion.div
                      key={bet.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className={cn(
                        'border rounded-lg p-4 transition-all duration-200',
                        bet.status === 'WON'
                          ? 'border-success-200 bg-success-50'
                          : 'border-gray-200 bg-gray-50'
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <div>
                              <p className="font-medium text-gray-900">{bet.drawNumber}</p>
                              <p className="text-sm text-gray-500">
                                {bet.betType.toUpperCase()} · {bet.amount}元 × {bet.multiple}倍
                              </p>
                            </div>

                            {/* 投注号码 */}
                            <div className="flex space-x-1">
                              {bet.numbers.map((number, numIndex) => (
                                <div
                                  key={numIndex}
                                  className="w-6 h-6 bg-gray-300 text-gray-700 rounded-full flex items-center justify-center text-xs font-bold"
                                >
                                  {number.toString().padStart(2, '0')}
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>

                        {/* 中奖状态 */}
                        <div className="text-right">
                          <div className={cn(
                            'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                            bet.status === 'WON'
                              ? 'bg-success-100 text-success-800'
                              : 'bg-gray-100 text-gray-800'
                          )}>
                            {bet.status === 'WON' ? '已中奖' : '未中奖'}
                          </div>
                          {bet.status === 'WON' && (
                            <p className="text-sm text-success-600 font-medium mt-1">
                              +{formatCurrency(bet.payout)}
                            </p>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* 走势分析 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">
                    走势分析
                  </h2>
                  <div className="flex items-center space-x-2">
                    {/* 分析类型选择 */}
                    <div className="flex items-center space-x-1">
                      {[
                        { key: 'frequency', label: '频率' },
                        { key: 'missing', label: '遗漏' },
                        { key: 'sum', label: '和值' },
                        { key: 'span', label: '跨度' }
                      ].map((type) => (
                        <button
                          key={type.key}
                          onClick={() => setTrendViewType(type.key as any)}
                          className={cn(
                            'px-2 py-1 text-xs rounded transition-all duration-200',
                            trendViewType === type.key
                              ? 'bg-info-500 text-white'
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                          )}
                        >
                          {type.label}
                        </button>
                      ))}
                    </div>
                    {/* 期数选择 */}
                    <div className="flex items-center space-x-1">
                      {[10, 30, 50, 100].map((period) => (
                        <button
                          key={period}
                          onClick={() => setTrendPeriod(period as any)}
                          className={cn(
                            'px-3 py-1 text-xs rounded-full transition-all duration-200',
                            trendPeriod === period
                              ? 'bg-primary-500 text-white'
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                          )}
                        >
                          {period}期
                        </button>
                      ))}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<TrendingUp className="w-4 h-4" />}
                      onClick={() => setShowTrendDetails(!showTrendDetails)}
                    >
                      {showTrendDetails ? '简化视图' : '详细分析'}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* 根据分析类型显示不同内容 */}
                {trendViewType === 'frequency' && (
                  <>
                    {/* 冷热号码分析 */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                      <div>
                        <h3 className="font-medium text-gray-900 mb-3">
                          热号 (近{trendPeriod}期)
                        </h3>
                        <div className="space-y-2">
                          {hotNums.map((number, index) => (
                            <motion.div
                              key={number}
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ duration: 0.3, delay: index * 0.1 }}
                              className="flex items-center justify-between p-3 bg-danger-50 rounded-lg cursor-pointer hover:bg-danger-100 transition-colors"
                              onClick={() => setSelectedTrendNumber(selectedTrendNumber === number ? null : number)}
                            >
                              <div className="flex items-center space-x-3">
                                <div className="trend-number hot">
                                  {number.toString().padStart(2, '0')}
                                </div>
                                <div>
                                  <p className="text-sm font-medium text-gray-900">
                                    第{index + 1}热号
                                  </p>
                                  <p className="text-xs text-gray-500">
                                    出现{currentTrendData[number]?.count || 0}次
                                  </p>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                                  <div
                                    className="h-full bg-danger-500 transition-all duration-500"
                                    style={{
                                      width: `${Math.min(100, (currentTrendData[number]?.count || 0) / Math.max(...hotNums.map(n => currentTrendData[n]?.count || 0)) * 100)}%`
                                    }}
                                  />
                                </div>
                                <p className="text-xs text-gray-500 mt-1">
                                  {Math.round((currentTrendData[number]?.count || 0) / trendPeriod * 100)}%
                                </p>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h3 className="font-medium text-gray-900 mb-3">
                          冷号 (近{trendPeriod}期)
                        </h3>
                        <div className="space-y-2">
                          {coldNums.map((number, index) => (
                            <motion.div
                              key={number}
                              initial={{ opacity: 0, x: 10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ duration: 0.3, delay: index * 0.1 }}
                              className="flex items-center justify-between p-3 bg-info-50 rounded-lg cursor-pointer hover:bg-info-100 transition-colors"
                              onClick={() => setSelectedTrendNumber(selectedTrendNumber === number ? null : number)}
                            >
                              <div className="flex items-center space-x-3">
                                <div className="trend-number cold">
                                  {number.toString().padStart(2, '0')}
                                </div>
                                <div>
                                  <p className="text-sm font-medium text-gray-900">
                                    第{index + 1}冷号
                                  </p>
                                  <p className="text-xs text-gray-500">
                                    出现{currentTrendData[number]?.count || 0}次
                                  </p>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                                  <div
                                    className="h-full bg-info-500 transition-all duration-500"
                                    style={{
                                      width: `${Math.min(100, (currentTrendData[number]?.count || 0) / Math.max(...coldNums.map(n => currentTrendData[n]?.count || 0)) * 100)}%`
                                    }}
                                  />
                                </div>
                                <p className="text-xs text-gray-500 mt-1">
                                  {Math.round((currentTrendData[number]?.count || 0) / trendPeriod * 100)}%
                                </p>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* 详细走势分析 */}
                    <AnimatePresence>
                      {showTrendDetails && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.3 }}
                          className="border-t pt-6"
                        >
                          {/* 号码出现频率图表 */}
                          <div className="mb-6">
                            <h4 className="font-medium text-gray-900 mb-4">
                              号码出现频率 (近{trendPeriod}期)
                            </h4>
                            <div className="grid grid-cols-11 gap-2">
                              {Array.from({ length: 11 }, (_, i) => i + 1).map((number) => {
                                const data = currentTrendData[number];
                                const maxCount = Math.max(...Object.values(currentTrendData).map(d => d.count));
                                const percentage = data ? (data.count / maxCount) * 100 : 0;

                                return (
                                  <motion.div
                                    key={number}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.3, delay: (number - 1) * 0.05 }}
                                    className={cn(
                                      'text-center cursor-pointer transition-all duration-200',
                                      selectedTrendNumber === number && 'ring-2 ring-primary-500 rounded-lg'
                                    )}
                                    onClick={() => setSelectedTrendNumber(selectedTrendNumber === number ? null : number)}
                                  >
                                    <div className="mb-2">
                                      <div className={cn(
                                        'w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold mx-auto',
                                        hotNums.includes(number) ? 'bg-danger-100 text-danger-800' :
                                          coldNums.includes(number) ? 'bg-info-100 text-info-800' :
                                            'bg-gray-100 text-gray-800'
                                      )}>
                                        {number.toString().padStart(2, '0')}
                                      </div>
                                    </div>
                                    <div className="h-20 flex items-end justify-center">
                                      <motion.div
                                        initial={{ height: 0 }}
                                        animate={{ height: `${percentage}%` }}
                                        transition={{ duration: 0.5, delay: (number - 1) * 0.1 }}
                                        className={cn(
                                          'w-4 rounded-t transition-colors duration-200',
                                          hotNums.includes(number) ? 'bg-danger-400' :
                                            coldNums.includes(number) ? 'bg-info-400' :
                                              'bg-gray-400'
                                        )}
                                      />
                                    </div>
                                    <div className="mt-2 text-xs">
                                      <p className="font-medium text-gray-900">
                                        {data?.count || 0}
                                      </p>
                                      <p className="text-gray-500">
                                        {Math.round((data?.count || 0) / trendPeriod * 100)}%
                                      </p>
                                    </div>
                                  </motion.div>
                                );
                              })}
                            </div>
                          </div>

                          {/* 遗漏值分析 */}
                          <div className="mb-6">
                            <h4 className="font-medium text-gray-900 mb-4">
                              号码遗漏分析
                            </h4>
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                              <div>
                                <h5 className="text-sm font-medium text-gray-700 mb-2">最大遗漏</h5>
                                <div className="space-y-2">
                                  {Object.entries(currentTrendData)
                                    .sort(([, a], [, b]) => b.missing - a.missing)
                                    .slice(0, 5)
                                    .map(([num, data], index) => (
                                      <div key={num} className="flex items-center justify-between p-2 bg-warning-50 rounded">
                                        <div className="flex items-center space-x-2">
                                          <span className="text-xs text-gray-500">#{index + 1}</span>
                                          <div className="w-6 h-6 bg-warning-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                                            {num.padStart(2, '0')}
                                          </div>
                                        </div>
                                        <span className="text-sm font-medium text-warning-800">
                                          {data.missing}期未出
                                        </span>
                                      </div>
                                    ))}
                                </div>
                              </div>

                              <div>
                                <h5 className="text-sm font-medium text-gray-700 mb-2">最近出现</h5>
                                <div className="space-y-2">
                                  {Object.entries(currentTrendData)
                                    .sort(([, a], [, b]) => a.lastAppear - b.lastAppear)
                                    .slice(0, 5)
                                    .map(([num, data], index) => (
                                      <div key={num} className="flex items-center justify-between p-2 bg-success-50 rounded">
                                        <div className="flex items-center space-x-2">
                                          <span className="text-xs text-gray-500">#{index + 1}</span>
                                          <div className="w-6 h-6 bg-success-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                                            {num.padStart(2, '0')}
                                          </div>
                                        </div>
                                        <span className="text-sm font-medium text-success-800">
                                          {data.lastAppear}期前
                                        </span>
                                      </div>
                                    ))}
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* 选中号码详情 */}
                          <AnimatePresence>
                            {selectedTrendNumber && (
                              <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: 10 }}
                                className="bg-primary-50 rounded-lg p-4"
                              >
                                <div className="flex items-center justify-between mb-3">
                                  <h5 className="font-medium text-gray-900">
                                    号码 {selectedTrendNumber.toString().padStart(2, '0')} 详细分析
                                  </h5>
                                  <button
                                    onClick={() => setSelectedTrendNumber(null)}
                                    className="text-gray-400 hover:text-gray-600"
                                  >
                                    ✕
                                  </button>
                                </div>
                                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                                  <div className="text-center">
                                    <p className="text-2xl font-bold text-primary-600">
                                      {currentTrendData[selectedTrendNumber]?.count || 0}
                                    </p>
                                    <p className="text-xs text-gray-600">出现次数</p>
                                  </div>
                                  <div className="text-center">
                                    <p className="text-2xl font-bold text-warning-600">
                                      {currentTrendData[selectedTrendNumber]?.missing || 0}
                                    </p>
                                    <p className="text-xs text-gray-600">遗漏期数</p>
                                  </div>
                                  <div className="text-center">
                                    <p className="text-2xl font-bold text-info-600">
                                      {Math.round((currentTrendData[selectedTrendNumber]?.count || 0) / trendPeriod * 100)}%
                                    </p>
                                    <p className="text-xs text-gray-600">出现概率</p>
                                  </div>
                                  <div className="text-center">
                                    <p className="text-2xl font-bold text-success-600">
                                      {currentTrendData[selectedTrendNumber]?.lastAppear || 0}
                                    </p>
                                    <p className="text-xs text-gray-600">上次出现</p>
                                  </div>
                                </div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </>
                )}

                {/* 遗漏分析视图 */}
                {trendViewType === 'missing' && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div>
                        <h3 className="font-medium text-gray-900 mb-4">最大遗漏排行</h3>
                        <div className="space-y-3">
                          {Object.entries(currentTrendData)
                            .sort(([, a], [, b]) => b.missing - a.missing)
                            .slice(0, 8)
                            .map(([num, data], index) => (
                              <motion.div
                                key={num}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.3, delay: index * 0.1 }}
                                className="flex items-center justify-between p-3 bg-warning-50 rounded-lg hover:bg-warning-100 transition-colors cursor-pointer"
                                onClick={() => setSelectedTrendNumber(selectedTrendNumber === parseInt(num) ? null : parseInt(num))}
                              >
                                <div className="flex items-center space-x-3">
                                  <span className="text-sm text-gray-500 font-medium">#{index + 1}</span>
                                  <div className="w-8 h-8 bg-warning-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                    {num.padStart(2, '0')}
                                  </div>
                                  <div>
                                    <p className="text-sm font-medium text-gray-900">号码 {num}</p>
                                    <p className="text-xs text-gray-500">已遗漏 {data.missing} 期</p>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                      className="h-full bg-warning-500 transition-all duration-500"
                                      style={{
                                        width: `${Math.min(100, (data.missing / Math.max(...Object.values(currentTrendData).map(d => d.missing))) * 100)}%`
                                      }}
                                    />
                                  </div>
                                  <p className="text-xs text-warning-600 font-medium mt-1">
                                    {data.missing}期
                                  </p>
                                </div>
                              </motion.div>
                            ))}
                        </div>
                      </div>

                      <div>
                        <h3 className="font-medium text-gray-900 mb-4">最近出现排行</h3>
                        <div className="space-y-3">
                          {Object.entries(currentTrendData)
                            .sort(([, a], [, b]) => a.lastAppear - b.lastAppear)
                            .slice(0, 8)
                            .map(([num, data], index) => (
                              <motion.div
                                key={num}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ duration: 0.3, delay: index * 0.1 }}
                                className="flex items-center justify-between p-3 bg-success-50 rounded-lg hover:bg-success-100 transition-colors cursor-pointer"
                                onClick={() => setSelectedTrendNumber(selectedTrendNumber === parseInt(num) ? null : parseInt(num))}
                              >
                                <div className="flex items-center space-x-3">
                                  <span className="text-sm text-gray-500 font-medium">#{index + 1}</span>
                                  <div className="w-8 h-8 bg-success-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                    {num.padStart(2, '0')}
                                  </div>
                                  <div>
                                    <p className="text-sm font-medium text-gray-900">号码 {num}</p>
                                    <p className="text-xs text-gray-500">{data.lastAppear} 期前出现</p>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                      className="h-full bg-success-500 transition-all duration-500"
                                      style={{
                                        width: `${Math.min(100, 100 - (data.lastAppear / Math.max(...Object.values(currentTrendData).map(d => d.lastAppear))) * 100)}%`
                                      }}
                                    />
                                  </div>
                                  <p className="text-xs text-success-600 font-medium mt-1">
                                    {data.lastAppear}期前
                                  </p>
                                </div>
                              </motion.div>
                            ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 和值分析视图 */}
                {trendViewType === 'sum' && (
                  <div className="space-y-6">
                    <div>
                      <h3 className="font-medium text-gray-900 mb-4">和值分布 (近{trendPeriod}期)</h3>
                      <div className="grid grid-cols-6 lg:grid-cols-12 gap-2">
                        {Array.from({ length: 40 }, (_, i) => i + 15).map((sum) => {
                          const count = currentSumData[sum] || 0;
                          const maxCount = Math.max(...Object.values(currentSumData));
                          const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;

                          return (
                            <motion.div
                              key={sum}
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ duration: 0.3, delay: (sum - 15) * 0.02 }}
                              className="text-center cursor-pointer transition-all duration-200 hover:bg-gray-50 rounded-lg p-2"
                            >
                              <div className="mb-2">
                                <div className={cn(
                                  'w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold mx-auto',
                                  count > 0 ? 'bg-primary-100 text-primary-800' : 'bg-gray-100 text-gray-500'
                                )}>
                                  {sum}
                                </div>
                              </div>
                              <div className="h-12 flex items-end justify-center">
                                <motion.div
                                  initial={{ height: 0 }}
                                  animate={{ height: `${percentage}%` }}
                                  transition={{ duration: 0.5, delay: (sum - 15) * 0.05 }}
                                  className="w-3 bg-primary-400 rounded-t"
                                />
                              </div>
                              <div className="mt-1 text-xs">
                                <p className="font-medium text-gray-900">{count}</p>
                                <p className="text-gray-500">
                                  {Math.round((count / trendPeriod) * 100)}%
                                </p>
                              </div>
                            </motion.div>
                          );
                        })}
                      </div>
                    </div>

                    {/* 和值统计 */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                      <div className="bg-info-50 rounded-lg p-4 text-center">
                        <p className="text-2xl font-bold text-info-600">
                          {Object.keys(currentSumData).length}
                        </p>
                        <p className="text-sm text-gray-600">出现和值种类</p>
                      </div>
                      <div className="bg-success-50 rounded-lg p-4 text-center">
                        <p className="text-2xl font-bold text-success-600">
                          {Math.max(...Object.values(currentSumData))}
                        </p>
                        <p className="text-sm text-gray-600">最高出现次数</p>
                      </div>
                      <div className="bg-warning-50 rounded-lg p-4 text-center">
                        <p className="text-2xl font-bold text-warning-600">
                          {Object.entries(currentSumData).sort(([, a], [, b]) => b - a)[0]?.[0] || '-'}
                        </p>
                        <p className="text-sm text-gray-600">最热和值</p>
                      </div>
                      <div className="bg-danger-50 rounded-lg p-4 text-center">
                        <p className="text-2xl font-bold text-danger-600">
                          {Math.round(Object.entries(currentSumData).reduce((sum, [val, count]) => sum + parseInt(val) * count, 0) / trendPeriod)}
                        </p>
                        <p className="text-sm text-gray-600">平均和值</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* 跨度分析视图 */}
                {trendViewType === 'span' && (
                  <div className="space-y-6">
                    <div>
                      <h3 className="font-medium text-gray-900 mb-4">跨度分布 (近{trendPeriod}期)</h3>
                      <div className="grid grid-cols-5 lg:grid-cols-10 gap-3">
                        {Array.from({ length: 10 }, (_, i) => i + 1).map((span) => {
                          const count = currentSpanData[span] || 0;
                          const maxCount = Math.max(...Object.values(currentSpanData));
                          const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;

                          return (
                            <motion.div
                              key={span}
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ duration: 0.3, delay: span * 0.1 }}
                              className="text-center cursor-pointer transition-all duration-200 hover:bg-gray-50 rounded-lg p-3"
                            >
                              <div className="mb-3">
                                <div className={cn(
                                  'w-12 h-12 rounded-full flex items-center justify-center text-sm font-bold mx-auto',
                                  count > 0 ? 'bg-secondary-100 text-secondary-800' : 'bg-gray-100 text-gray-500'
                                )}>
                                  {span}
                                </div>
                              </div>
                              <div className="h-16 flex items-end justify-center">
                                <motion.div
                                  initial={{ height: 0 }}
                                  animate={{ height: `${percentage}%` }}
                                  transition={{ duration: 0.5, delay: span * 0.1 }}
                                  className="w-4 bg-secondary-400 rounded-t"
                                />
                              </div>
                              <div className="mt-2 text-xs">
                                <p className="font-medium text-gray-900">{count}次</p>
                                <p className="text-gray-500">
                                  {Math.round((count / trendPeriod) * 100)}%
                                </p>
                              </div>
                            </motion.div>
                          );
                        })}
                      </div>
                    </div>

                    {/* 跨度统计和连号分析 */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-medium text-gray-900 mb-4">跨度统计</h4>
                        <div className="space-y-3">
                          <div className="bg-primary-50 rounded-lg p-4">
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-600">最常见跨度</span>
                              <span className="font-bold text-primary-600">
                                {Object.entries(currentSpanData).sort(([, a], [, b]) => b - a)[0]?.[0] || '-'}
                              </span>
                            </div>
                          </div>
                          <div className="bg-info-50 rounded-lg p-4">
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-600">平均跨度</span>
                              <span className="font-bold text-info-600">
                                {Math.round(Object.entries(currentSpanData).reduce((sum, [val, count]) => sum + parseInt(val) * count, 0) / trendPeriod * 10) / 10}
                              </span>
                            </div>
                          </div>
                          <div className="bg-success-50 rounded-lg p-4">
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-600">跨度种类</span>
                              <span className="font-bold text-success-600">
                                {Object.keys(currentSpanData).length}种
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium text-gray-900 mb-4">连号分析</h4>
                        <div className="space-y-3">
                          <div className="bg-warning-50 rounded-lg p-4">
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-600">2连号出现</span>
                              <span className="font-bold text-warning-600">
                                {currentConsecutiveData.consecutive2}次
                              </span>
                            </div>
                            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-warning-500 h-2 rounded-full transition-all duration-500"
                                style={{ width: `${(currentConsecutiveData.consecutive2 / trendPeriod) * 100}%` }}
                              />
                            </div>
                          </div>
                          <div className="bg-danger-50 rounded-lg p-4">
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-600">3连号出现</span>
                              <span className="font-bold text-danger-600">
                                {currentConsecutiveData.consecutive3}次
                              </span>
                            </div>
                            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-danger-500 h-2 rounded-full transition-all duration-500"
                                style={{ width: `${(currentConsecutiveData.consecutive3 / trendPeriod) * 100}%` }}
                              />
                            </div>
                          </div>
                          <div className="bg-purple-50 rounded-lg p-4">
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-600">4连号出现</span>
                              <span className="font-bold text-purple-600">
                                {currentConsecutiveData.consecutive4}次
                              </span>
                            </div>
                            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                                style={{ width: `${(currentConsecutiveData.consecutive4 / trendPeriod) * 100}%` }}
                              />
                            </div>
                          </div>
                          <div className="bg-indigo-50 rounded-lg p-4">
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-600">5连号出现</span>
                              <span className="font-bold text-indigo-600">
                                {currentConsecutiveData.consecutive5}次
                              </span>
                            </div>
                            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
                                style={{ width: `${(currentConsecutiveData.consecutive5 / trendPeriod) * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 选中号码详情（适用于所有分析类型） */}
                <AnimatePresence>
                  {selectedTrendNumber && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      className="bg-primary-50 rounded-lg p-4 mt-6"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <h5 className="font-medium text-gray-900">
                          号码 {selectedTrendNumber.toString().padStart(2, '0')} 详细分析
                        </h5>
                        <button
                          onClick={() => setSelectedTrendNumber(null)}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          ✕
                        </button>
                      </div>
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-primary-600">
                            {currentTrendData[selectedTrendNumber]?.count || 0}
                          </p>
                          <p className="text-xs text-gray-600">出现次数</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-warning-600">
                            {currentTrendData[selectedTrendNumber]?.missing || 0}
                          </p>
                          <p className="text-xs text-gray-600">遗漏期数</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-info-600">
                            {Math.round((currentTrendData[selectedTrendNumber]?.count || 0) / trendPeriod * 100)}%
                          </p>
                          <p className="text-xs text-gray-600">出现概率</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-success-600">
                            {currentTrendData[selectedTrendNumber]?.lastAppear || 0}
                          </p>
                          <p className="text-xs text-gray-600">上次出现</p>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </GameEnhancer>
  );
};

export default Lottery11x5Page;