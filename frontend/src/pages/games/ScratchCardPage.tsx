import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  RotateCcw, 
  Play, 
  Pause, 
  Volume2, 
  VolumeX,
  Trophy,
  Coins,
  Zap,
  Gift
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import GameEnhancer from '@/components/games/GameEnhancer';
import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/format';

interface ScratchArea {
  id: number;
  symbol: string;
  isScratched: boolean;
  isWinning: boolean;
  winAmount?: number;
}

interface ScratchCard {
  id: string;
  price: number;
  areas: ScratchArea[];
  totalWinnings: number;
  isComplete: boolean;
}

const ScratchCardPage: React.FC = () => {
  const [currentCard, setCurrentCard] = useState<ScratchCard | null>(null);
  const [isScratching, setIsScratching] = useState(false);
  const [autoScratch, setAutoScratch] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [showWinModal, setShowWinModal] = useState(false);
  const [totalWinnings, setTotalWinnings] = useState(0);
  const [balance, setBalance] = useState(15420.50);
  const [isPlaying, setIsPlaying] = useState(false);
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [scratchedPixels, setScratchedPixels] = useState(0);

  // 卡片价格选项
  const cardPrices = [
    { value: 10, label: '10元', winRate: '15%', maxPrize: 1000 },
    { value: 50, label: '50元', winRate: '20%', maxPrize: 5000 },
    { value: 100, label: '100元', winRate: '25%', maxPrize: 10000 },
    { value: 500, label: '500元', winRate: '30%', maxPrize: 50000 },
    { value: 1000, label: '1000元', winRate: '35%', maxPrize: 100000 },
  ];
  const [selectedPrice, setSelectedPrice] = useState(100);

  // 生成新卡片
  const generateNewCard = (price: number): ScratchCard => {
    const areas: ScratchArea[] = [];
    const symbols = ['6', '66', '666', '7', '77', '777', '8', '88', '888'];
    
    // 生成9个刮奖区域
    for (let i = 0; i < 9; i++) {
      const randomSymbol = symbols[Math.floor(Math.random() * symbols.length)];
      areas.push({
        id: i,
        symbol: randomSymbol,
        isScratched: false,
        isWinning: false,
        winAmount: 0,
      });
    }

    // 计算中奖逻辑
    let totalWinnings = 0;
    const symbolCounts: { [key: string]: number } = {};
    
    areas.forEach(area => {
      symbolCounts[area.symbol] = (symbolCounts[area.symbol] || 0) + 1;
    });

    // 检查中奖组合
    Object.entries(symbolCounts).forEach(([symbol, count]) => {
      if (count >= 3) {
        const baseAmount = price * 0.1; // 基础奖金为卡片价格的10%
        let multiplier = 1;
        
        if (symbol === '6') multiplier = 1;
        else if (symbol === '66') multiplier = 2;
        else if (symbol === '666') multiplier = 3;
        else if (symbol === '7') multiplier = 1.5;
        else if (symbol === '77') multiplier = 3;
        else if (symbol === '777') multiplier = 5;
        else if (symbol === '8') multiplier = 2;
        else if (symbol === '88') multiplier = 4;
        else if (symbol === '888') multiplier = 8;

        const winAmount = baseAmount * multiplier;
        totalWinnings += winAmount;

        // 标记中奖区域
        areas.forEach(area => {
          if (area.symbol === symbol) {
            area.isWinning = true;
            area.winAmount = winAmount / count; // 平分奖金
          }
        });
      }
    });

    return {
      id: Date.now().toString(),
      price,
      areas,
      totalWinnings,
      isComplete: false,
    };
  };

  // 购买新卡片
  const buyNewCard = () => {
    if (balance < selectedPrice) {
      alert('余额不足！');
      return;
    }

    const newCard = generateNewCard(selectedPrice);
    setCurrentCard(newCard);
    setBalance(prev => prev - selectedPrice);
    setScratchedPixels(0);
    setIsPlaying(true);
    
    // 初始化画布
    initializeCanvas();
  };

  // 初始化画布
  const initializeCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 设置画布尺寸
    canvas.width = 300;
    canvas.height = 200;

    // 绘制刮刮层
    ctx.fillStyle = '#C0C0C0';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 添加纹理效果
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, '#E0E0E0');
    gradient.addColorStop(0.5, '#C0C0C0');
    gradient.addColorStop(1, '#A0A0A0');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 添加文字提示
    ctx.fillStyle = '#666';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('刮开查看结果', canvas.width / 2, canvas.height / 2);
  };

  // 处理刮奖
  const handleScratch = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!currentCard || currentCard.isComplete) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // 设置刮除效果
    ctx.globalCompositeOperation = 'destination-out';
    ctx.beginPath();
    ctx.arc(x, y, 20, 0, 2 * Math.PI);
    ctx.fill();

    // 计算刮除进度
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const pixels = imageData.data;
    let transparentPixels = 0;

    for (let i = 3; i < pixels.length; i += 4) {
      if (pixels[i] === 0) {
        transparentPixels++;
      }
    }

    const scratchPercentage = (transparentPixels / (canvas.width * canvas.height)) * 100;
    setScratchedPixels(scratchPercentage);

    // 如果刮除超过70%，自动完成
    if (scratchPercentage > 70) {
      completeScratch();
    }
  };

  // 完成刮奖
  const completeScratch = () => {
    if (!currentCard) return;

    const updatedCard = {
      ...currentCard,
      isComplete: true,
      areas: currentCard.areas.map(area => ({ ...area, isScratched: true }))
    };

    setCurrentCard(updatedCard);
    setIsPlaying(false);

    // 如果中奖，显示中奖弹窗
    if (updatedCard.totalWinnings > 0) {
      setTotalWinnings(updatedCard.totalWinnings);
      setBalance(prev => prev + updatedCard.totalWinnings);
      setShowWinModal(true);
    }

    // 清除画布
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
  };

  // 自动刮奖
  const handleAutoScratch = () => {
    if (!currentCard) return;
    
    setAutoScratch(true);
    
    // 模拟自动刮奖动画
    const interval = setInterval(() => {
      setScratchedPixels(prev => {
        const newProgress = prev + 10;
        if (newProgress >= 100) {
          clearInterval(interval);
          setAutoScratch(false);
          completeScratch();
          return 100;
        }
        return newProgress;
      });
    }, 100);
  };

  // 重新开始
  const resetGame = () => {
    setCurrentCard(null);
    setIsPlaying(false);
    setAutoScratch(false);
    setScratchedPixels(0);
  };

  useEffect(() => {
    if (currentCard && !currentCard.isComplete) {
      initializeCanvas();
    }
  }, [currentCard]);

  return (
    <GameEnhancer 
      gameName="666刮刮乐"
      showSoundControl={true}
      showFullscreen={true}
      showNotifications={true}
      showHelp={true}
      onSoundToggle={setSoundEnabled}
    >
      <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
      {/* 页面头部 */}
      <div className="bg-gradient-to-r from-secondary-500 to-secondary-600 text-gray-900 px-4 py-6 lg:px-6">
        <div className="container-responsive">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold mb-1">666刮刮乐</h1>
              <p className="text-gray-800 opacity-80">
                刮开惊喜，即时中奖
              </p>
            </div>
            <div className="text-right">
              <p className="text-gray-800 opacity-80 text-sm">账户余额</p>
              <p className="text-xl font-bold">
                {formatCurrency(balance)}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="container-responsive py-6 space-y-6">
        {/* 游戏控制面板 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">
                  游戏设置
                </h2>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setSoundEnabled(!soundEnabled)}
                    className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    {soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
                  </button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {/* 卡片价格选择 */}
                <div className="lg:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    选择卡片价格
                  </label>
                  <div className="grid grid-cols-2 lg:grid-cols-3 gap-2">
                    {cardPrices.map((price) => (
                      <button
                        key={price.value}
                        onClick={() => setSelectedPrice(price.value)}
                        className={cn(
                          'p-3 rounded-lg border-2 transition-all duration-200 text-center',
                          selectedPrice === price.value
                            ? 'border-secondary-500 bg-secondary-50 text-secondary-700'
                            : 'border-gray-200 hover:border-gray-300 text-gray-600'
                        )}
                      >
                        <div className="font-bold text-sm">{price.label}</div>
                        <div className="text-xs opacity-75 mt-1">
                          中奖率: {price.winRate}
                        </div>
                        <div className="text-xs opacity-75">
                          最高: {formatCurrency(price.maxPrize)}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* 操作按钮 */}
                <div className="lg:col-span-2 flex flex-col justify-end">
                  <div className="grid grid-cols-2 gap-3">
                    <Button
                      variant="primary"
                      onClick={buyNewCard}
                      disabled={isPlaying || balance < selectedPrice}
                      icon={<Coins className="w-4 h-4" />}
                    >
                      购买卡片
                    </Button>
                    <Button
                      variant="outline"
                      onClick={resetGame}
                      disabled={isPlaying}
                      icon={<RotateCcw className="w-4 h-4" />}
                    >
                      重新开始
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 刮刮卡游戏区域 */}
        {currentCard && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Card className="overflow-hidden">
              <CardContent className="p-6">
                <div className="text-center mb-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {formatCurrency(currentCard.price)} 刮刮卡
                  </h3>
                  <p className="text-gray-600">
                    刮开3个相同符号即可中奖
                  </p>
                </div>

                {/* 刮奖区域 */}
                <div className="relative mx-auto max-w-md">
                  {/* 背景奖项显示 */}
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    {currentCard.areas.map((area) => (
                      <div
                        key={area.id}
                        className={cn(
                          'aspect-square rounded-lg flex items-center justify-center text-2xl font-bold transition-all duration-300',
                          area.isWinning && currentCard.isComplete
                            ? 'bg-gradient-secondary text-gray-900 animate-bounce-in'
                            : 'bg-gray-100 text-gray-400'
                        )}
                      >
                        {currentCard.isComplete || area.isScratched ? area.symbol : '?'}
                      </div>
                    ))}
                  </div>

                  {/* 刮奖画布 */}
                  {!currentCard.isComplete && (
                    <div className="relative">
                      <canvas
                        ref={canvasRef}
                        className="absolute inset-0 w-full h-full cursor-pointer rounded-lg"
                        onMouseMove={isScratching ? handleScratch : undefined}
                        onMouseDown={() => setIsScratching(true)}
                        onMouseUp={() => setIsScratching(false)}
                        onMouseLeave={() => setIsScratching(false)}
                      />
                      
                      {/* 刮奖进度 */}
                      <div className="absolute bottom-2 left-2 right-2">
                        <div className="bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                          刮开进度: {Math.round(scratchedPixels)}%
                        </div>
                      </div>
                    </div>
                  )}

                  {/* 自动刮奖按钮 */}
                  {!currentCard.isComplete && (
                    <div className="flex justify-center mt-4 space-x-3">
                      <Button
                        variant="secondary"
                        onClick={handleAutoScratch}
                        disabled={autoScratch}
                        icon={autoScratch ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                      >
                        {autoScratch ? '自动刮奖中...' : '自动刮奖'}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={completeScratch}
                        icon={<Zap className="w-4 h-4" />}
                      >
                        立即揭晓
                      </Button>
                    </div>
                  )}
                </div>

                {/* 结果显示 */}
                {currentCard.isComplete && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="text-center mt-6"
                  >
                    {currentCard.totalWinnings > 0 ? (
                      <div className="bg-gradient-to-r from-success-50 to-secondary-50 p-6 rounded-xl">
                        <Trophy className="w-12 h-12 text-secondary-600 mx-auto mb-3" />
                        <h3 className="text-2xl font-bold text-success-700 mb-2">
                          恭喜中奖！
                        </h3>
                        <p className="text-3xl font-bold text-secondary-600">
                          {formatCurrency(currentCard.totalWinnings)}
                        </p>
                      </div>
                    ) : (
                      <div className="bg-gray-50 p-6 rounded-xl">
                        <Gift className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <h3 className="text-xl font-medium text-gray-600 mb-2">
                          很遗憾，未中奖
                        </h3>
                        <p className="text-gray-500">
                          再试一次，好运就在下一张！
                        </p>
                      </div>
                    )}
                    
                    <Button
                      variant="primary"
                      onClick={buyNewCard}
                      disabled={balance < selectedPrice}
                      className="mt-4"
                      icon={<Sparkles className="w-4 h-4" />}
                    >
                      再来一张
                    </Button>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* 游戏规则 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold text-gray-900">
                游戏规则
              </h2>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-medium text-gray-900 mb-3">中奖规则</h3>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li className="flex items-center space-x-2">
                      <span className="w-2 h-2 bg-secondary-500 rounded-full"></span>
                      <span>刮开3个相同"6"符号 = 1倍基础奖金</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-2 h-2 bg-secondary-500 rounded-full"></span>
                      <span>刮开3个相同"66"符号 = 2倍基础奖金</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-2 h-2 bg-secondary-500 rounded-full"></span>
                      <span>刮开3个相同"666"符号 = 3倍基础奖金</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-2 h-2 bg-danger-500 rounded-full"></span>
                      <span>多个中奖组合可累计奖金</span>
                    </li>
                  </ul>
                </div>
                
                <div>
                  <h3 className="font-medium text-gray-900 mb-3">操作说明</h3>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li className="flex items-center space-x-2">
                      <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
                      <span>选择卡片价格并购买</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
                      <span>用鼠标刮开银色涂层</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
                      <span>可使用自动刮奖功能</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
                      <span>中奖金额立即到账</span>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* 中奖弹窗 */}
      <Modal
        isOpen={showWinModal}
        onClose={() => setShowWinModal(false)}
        title="🎉 恭喜中奖！"
        size="sm"
      >
        <div className="p-6 text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200 }}
            className="w-20 h-20 bg-gradient-secondary rounded-full flex items-center justify-center mx-auto mb-4"
          >
            <Trophy className="w-10 h-10 text-gray-900" />
          </motion.div>
          
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            中奖金额
          </h3>
          <p className="text-4xl font-bold text-secondary-600 mb-4">
            {formatCurrency(totalWinnings)}
          </p>
          <p className="text-gray-600 mb-6">
            奖金已自动添加到您的账户余额
          </p>
          
          <div className="grid grid-cols-2 gap-3">
            <Button
              variant="outline"
              onClick={() => setShowWinModal(false)}
            >
              继续游戏
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                setShowWinModal(false);
                buyNewCard();
              }}
            >
              再来一张
            </Button>
          </div>
        </div>
      </Modal>
    </div>
    </GameEnhancer>
  );
};

export default ScratchCardPage;