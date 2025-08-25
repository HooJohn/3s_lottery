import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Wifi, 
  Send, 
  MessageCircle, 
  Activity,
  Bell,
  DollarSign,
  Trophy
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useWebSocket, useLotteryDrawResults, useBalanceUpdates, useRewardUpdates } from '@/hooks/useWebSocket';
import { MESSAGE_TYPES } from '@/services/websocket';
import { formatCurrency } from '@/utils/format';

/**
 * WebSocket演示组件 - 用于测试和展示WebSocket功能
 * 这个组件可以在开发环境中使用，生产环境可以移除
 */
const WebSocketDemo: React.FC = () => {
  const { connectionStatus, sendMessage } = useWebSocket();
  const { drawResult, countdown } = useLotteryDrawResults();
  const { balance, transaction } = useBalanceUpdates();
  const { reward, vipUpdate, referralReward } = useRewardUpdates();

  const [testMessage, setTestMessage] = useState('');
  const [messageHistory, setMessageHistory] = useState<any[]>([]);

  // 监听所有消息更新
  useEffect(() => {
    if (drawResult) {
      setMessageHistory(prev => [...prev, { type: 'draw_result', data: drawResult, timestamp: Date.now() }]);
    }
  }, [drawResult]);

  useEffect(() => {
    if (countdown) {
      setMessageHistory(prev => [...prev, { type: 'countdown', data: countdown, timestamp: Date.now() }]);
    }
  }, [countdown]);

  useEffect(() => {
    if (balance) {
      setMessageHistory(prev => [...prev, { type: 'balance', data: balance, timestamp: Date.now() }]);
    }
  }, [balance]);

  useEffect(() => {
    if (transaction) {
      setMessageHistory(prev => [...prev, { type: 'transaction', data: transaction, timestamp: Date.now() }]);
    }
  }, [transaction]);

  useEffect(() => {
    if (reward) {
      setMessageHistory(prev => [...prev, { type: 'reward', data: reward, timestamp: Date.now() }]);
    }
  }, [reward]);

  // 发送测试消息
  const handleSendTestMessage = () => {
    if (testMessage.trim()) {
      const success = sendMessage('test_message', { content: testMessage });
      if (success) {
        setTestMessage('');
      }
    }
  };

  // 模拟开奖结果
  const simulateDrawResult = () => {
    const mockResult = {
      draw_number: '20250121-001',
      winning_numbers: [3, 7, 9, 2, 11],
      user_winnings: Math.random() > 0.7 ? Math.floor(Math.random() * 1000) + 100 : 0
    };
    sendMessage(MESSAGE_TYPES.LOTTERY_DRAW_RESULT, mockResult);
  };

  // 模拟余额更新
  const simulateBalanceUpdate = () => {
    const mockBalance = {
      amount: Math.floor(Math.random() * 500) + 50,
      type: 'deposit',
      balance_after: Math.floor(Math.random() * 10000) + 1000
    };
    sendMessage(MESSAGE_TYPES.BALANCE_UPDATE, mockBalance);
  };

  // 模拟奖励通知
  const simulateRewardUpdate = () => {
    const mockReward = {
      type: Math.random() > 0.5 ? 'vip_rebate' : 'referral_commission',
      amount: Math.floor(Math.random() * 200) + 20,
      description: '每日返水奖励'
    };
    sendMessage(MESSAGE_TYPES.REWARD_UPDATE, mockReward);
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'draw_result':
        return <Trophy className="w-4 h-4 text-warning-500" />;
      case 'balance':
      case 'transaction':
        return <DollarSign className="w-4 h-4 text-success-500" />;
      case 'reward':
        return <Bell className="w-4 h-4 text-primary-500" />;
      default:
        return <MessageCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* 连接状态 */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold flex items-center">
            <Wifi className="w-5 h-5 mr-2" />
            WebSocket连接状态
          </h3>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">连接状态</p>
              <p className={`font-bold ${connectionStatus.isConnected ? 'text-success-600' : 'text-danger-600'}`}>
                {connectionStatus.isConnected ? '已连接' : '未连接'}
              </p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">重连状态</p>
              <p className={`font-bold ${connectionStatus.isReconnecting ? 'text-warning-600' : 'text-gray-600'}`}>
                {connectionStatus.isReconnecting ? '重连中' : '正常'}
              </p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">重连次数</p>
              <p className="font-bold text-gray-900">
                {connectionStatus.reconnectAttempts}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 测试消息发送 */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold flex items-center">
            <Send className="w-5 h-5 mr-2" />
            测试消息发送
          </h3>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex space-x-2">
              <Input
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
                placeholder="输入测试消息..."
                onKeyPress={(e) => e.key === 'Enter' && handleSendTestMessage()}
              />
              <Button 
                onClick={handleSendTestMessage}
                disabled={!connectionStatus.isConnected || !testMessage.trim()}
                icon={<Send className="w-4 h-4" />}
              >
                发送
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={simulateDrawResult}
                disabled={!connectionStatus.isConnected}
                icon={<Trophy className="w-4 h-4" />}
              >
                模拟开奖
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={simulateBalanceUpdate}
                disabled={!connectionStatus.isConnected}
                icon={<DollarSign className="w-4 h-4" />}
              >
                模拟余额更新
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={simulateRewardUpdate}
                disabled={!connectionStatus.isConnected}
                icon={<Bell className="w-4 h-4" />}
              >
                模拟奖励通知
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 消息历史 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold flex items-center">
              <Activity className="w-5 h-5 mr-2" />
              消息历史
            </h3>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setMessageHistory([])}
            >
              清空
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {messageHistory.length === 0 ? (
              <p className="text-gray-500 text-center py-8">暂无消息</p>
            ) : (
              messageHistory.slice(-20).reverse().map((msg, index) => (
                <motion.div
                  key={`${msg.timestamp}-${index}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
                >
                  {getMessageIcon(msg.type)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900 capitalize">
                        {msg.type.replace('_', ' ')}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                    <div className="mt-1">
                      <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                        {JSON.stringify(msg.data, null, 2)}
                      </pre>
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* 实时数据展示 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* 开奖信息 */}
        <Card>
          <CardHeader>
            <h4 className="font-semibold flex items-center">
              <Trophy className="w-4 h-4 mr-2 text-warning-500" />
              最新开奖
            </h4>
          </CardHeader>
          <CardContent>
            {drawResult ? (
              <div className="space-y-2">
                <p className="text-sm text-gray-600">期号: {drawResult.draw_number}</p>
                <p className="text-sm text-gray-600">
                  号码: {drawResult.winning_numbers?.join(' ') || '暂无'}
                </p>
                {drawResult.user_winnings > 0 && (
                  <p className="text-sm font-bold text-success-600">
                    中奖: {formatCurrency(drawResult.user_winnings)}
                  </p>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-500">暂无开奖数据</p>
            )}
          </CardContent>
        </Card>

        {/* 余额信息 */}
        <Card>
          <CardHeader>
            <h4 className="font-semibold flex items-center">
              <DollarSign className="w-4 h-4 mr-2 text-success-500" />
              余额更新
            </h4>
          </CardHeader>
          <CardContent>
            {balance ? (
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  变动: {balance.amount > 0 ? '+' : ''}{formatCurrency(balance.amount)}
                </p>
                <p className="text-sm text-gray-600">
                  余额: {formatCurrency(balance.balance_after)}
                </p>
                <p className="text-sm text-gray-600">类型: {balance.type}</p>
              </div>
            ) : (
              <p className="text-sm text-gray-500">暂无余额数据</p>
            )}
          </CardContent>
        </Card>

        {/* 奖励信息 */}
        <Card>
          <CardHeader>
            <h4 className="font-semibold flex items-center">
              <Bell className="w-4 h-4 mr-2 text-primary-500" />
              最新奖励
            </h4>
          </CardHeader>
          <CardContent>
            {reward ? (
              <div className="space-y-2">
                <p className="text-sm text-gray-600">类型: {reward.type}</p>
                <p className="text-sm font-bold text-primary-600">
                  金额: {formatCurrency(reward.amount)}
                </p>
                <p className="text-sm text-gray-600">{reward.description}</p>
              </div>
            ) : (
              <p className="text-sm text-gray-500">暂无奖励数据</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default WebSocketDemo;