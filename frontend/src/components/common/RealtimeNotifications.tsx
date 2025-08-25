import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { 
  Trophy,
  DollarSign,
  Gift,
  Crown,
  Users,
  AlertTriangle,
  Info,
  CheckCircle,
  Bell
} from 'lucide-react';

import { 
  useLotteryDrawResults,
  useBalanceUpdates,
  useRewardUpdates,
  useSystemNotifications,
  useUserStatusUpdates
} from '@/hooks/useWebSocket';
import { formatCurrency } from '@/utils/format';

const RealtimeNotifications: React.FC = () => {
  // 开奖结果通知
  const { drawResult } = useLotteryDrawResults();
  
  // 余额更新通知
  const { balance, transaction } = useBalanceUpdates();
  
  // 奖励更新通知
  const { reward, vipUpdate, referralReward } = useRewardUpdates();
  
  // 系统通知
  const { announcement, maintenance, securityAlert } = useSystemNotifications();
  
  // 用户状态更新
  const { userStatus, kycStatus } = useUserStatusUpdates();

  // 处理开奖结果通知
  useEffect(() => {
    if (drawResult) {
      const { draw_number, winning_numbers, user_winnings } = drawResult;
      
      if (user_winnings && user_winnings > 0) {
        // 用户中奖通知
        toast.success(
          <div className="flex items-center space-x-3">
            <Trophy className="w-6 h-6 text-warning-500" />
            <div>
              <p className="font-bold">恭喜中奖！</p>
              <p className="text-sm">第{draw_number}期 中奖金额: {formatCurrency(user_winnings)}</p>
            </div>
          </div>,
          {
            duration: 8000,
            style: {
              background: '#FEF3C7',
              color: '#92400E',
              border: '1px solid #F59E0B'
            }
          }
        );
      } else {
        // 普通开奖结果通知
        toast(
          <div className="flex items-center space-x-3">
            <Bell className="w-5 h-5 text-primary-500" />
            <div>
              <p className="font-medium">开奖结果</p>
              <p className="text-sm">第{draw_number}期: {winning_numbers.join(' ')}</p>
            </div>
          </div>,
          {
            duration: 5000
          }
        );
      }
    }
  }, [drawResult]);

  // 处理余额更新通知
  useEffect(() => {
    if (balance) {
      const { amount, type, balance_after } = balance;
      
      const isPositive = amount > 0;
      const icon = isPositive ? CheckCircle : AlertTriangle;
      const color = isPositive ? 'text-success-500' : 'text-warning-500';
      
      toast(
        <div className="flex items-center space-x-3">
          <DollarSign className={`w-5 h-5 ${color}`} />
          <div>
            <p className="font-medium">余额变动</p>
            <p className="text-sm">
              {isPositive ? '+' : ''}{formatCurrency(amount)} | 余额: {formatCurrency(balance_after)}
            </p>
          </div>
        </div>,
        {
          duration: 4000
        }
      );
    }
  }, [balance]);

  // 处理交易更新通知
  useEffect(() => {
    if (transaction) {
      const { type, amount, status } = transaction;
      
      let message = '';
      let icon = Info;
      let color = 'text-primary-500';
      
      switch (type) {
        case 'deposit':
          message = `存款${status === 'completed' ? '成功' : '处理中'}`;
          icon = CheckCircle;
          color = 'text-success-500';
          break;
        case 'withdraw':
          message = `提款${status === 'completed' ? '成功' : '处理中'}`;
          icon = DollarSign;
          color = 'text-primary-500';
          break;
        default:
          message = `交易${status === 'completed' ? '完成' : '处理中'}`;
      }
      
      toast(
        <div className="flex items-center space-x-3">
          <icon className={`w-5 h-5 ${color}`} />
          <div>
            <p className="font-medium">{message}</p>
            <p className="text-sm">金额: {formatCurrency(amount)}</p>
          </div>
        </div>,
        {
          duration: 5000
        }
      );
    }
  }, [transaction]);

  // 处理奖励更新通知
  useEffect(() => {
    if (reward) {
      const { type, amount, description } = reward;
      
      let icon = Gift;
      let title = '奖励到账';
      
      if (type === 'vip_rebate') {
        icon = Crown;
        title = 'VIP返水';
      } else if (type === 'referral_commission') {
        icon = Users;
        title = '推荐佣金';
      }
      
      toast.success(
        <div className="flex items-center space-x-3">
          <icon className="w-6 h-6 text-success-500" />
          <div>
            <p className="font-bold">{title}</p>
            <p className="text-sm">{formatCurrency(amount)} | {description}</p>
          </div>
        </div>,
        {
          duration: 6000,
          style: {
            background: '#ECFDF5',
            color: '#065F46',
            border: '1px solid #10B981'
          }
        }
      );
    }
  }, [reward]);

  // 处理VIP等级更新通知
  useEffect(() => {
    if (vipUpdate) {
      const { new_level, old_level, benefits } = vipUpdate;
      
      toast.success(
        <div className="flex items-center space-x-3">
          <Crown className="w-6 h-6 text-warning-500" />
          <div>
            <p className="font-bold">VIP等级提升！</p>
            <p className="text-sm">从 VIP{old_level} 升级到 VIP{new_level}</p>
            {benefits && <p className="text-xs text-gray-600">{benefits}</p>}
          </div>
        </div>,
        {
          duration: 8000,
          style: {
            background: '#FEF3C7',
            color: '#92400E',
            border: '1px solid #F59E0B'
          }
        }
      );
    }
  }, [vipUpdate]);

  // 处理推荐奖励通知
  useEffect(() => {
    if (referralReward) {
      const { level, amount, username } = referralReward;
      
      toast.success(
        <div className="flex items-center space-x-3">
          <Users className="w-6 h-6 text-success-500" />
          <div>
            <p className="font-bold">推荐奖励</p>
            <p className="text-sm">{level}级推荐 {formatCurrency(amount)}</p>
            <p className="text-xs text-gray-600">来自用户: {username}</p>
          </div>
        </div>,
        {
          duration: 6000,
          style: {
            background: '#ECFDF5',
            color: '#065F46',
            border: '1px solid #10B981'
          }
        }
      );
    }
  }, [referralReward]);

  // 处理系统公告
  useEffect(() => {
    if (announcement) {
      const { title, content, priority } = announcement;
      
      const isImportant = priority === 'high';
      
      toast(
        <div className="flex items-start space-x-3">
          <Info className={`w-5 h-5 mt-0.5 ${isImportant ? 'text-warning-500' : 'text-primary-500'}`} />
          <div>
            <p className="font-medium">{title}</p>
            <p className="text-sm text-gray-600">{content}</p>
          </div>
        </div>,
        {
          duration: isImportant ? 10000 : 6000,
          style: isImportant ? {
            background: '#FEF3C7',
            color: '#92400E',
            border: '1px solid #F59E0B'
          } : undefined
        }
      );
    }
  }, [announcement]);

  // 处理维护通知
  useEffect(() => {
    if (maintenance) {
      const { title, content, start_time, end_time } = maintenance;
      
      toast(
        <div className="flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 mt-0.5 text-warning-500" />
          <div>
            <p className="font-medium">{title}</p>
            <p className="text-sm text-gray-600">{content}</p>
            {start_time && end_time && (
              <p className="text-xs text-gray-500">
                {new Date(start_time).toLocaleString()} - {new Date(end_time).toLocaleString()}
              </p>
            )}
          </div>
        </div>,
        {
          duration: 12000,
          style: {
            background: '#FEF3C7',
            color: '#92400E',
            border: '1px solid #F59E0B'
          }
        }
      );
    }
  }, [maintenance]);

  // 处理安全警报
  useEffect(() => {
    if (securityAlert) {
      const { title, content, action_required } = securityAlert;
      
      toast.error(
        <div className="flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 mt-0.5 text-danger-500" />
          <div>
            <p className="font-bold">{title}</p>
            <p className="text-sm">{content}</p>
            {action_required && (
              <p className="text-xs font-medium mt-1">请立即处理</p>
            )}
          </div>
        </div>,
        {
          duration: 15000,
          style: {
            background: '#FEF2F2',
            color: '#991B1B',
            border: '1px solid #EF4444'
          }
        }
      );
    }
  }, [securityAlert]);

  // 处理KYC状态更新
  useEffect(() => {
    if (kycStatus) {
      const { status, message } = kycStatus;
      
      let icon = Info;
      let toastType = toast;
      let style = {};
      
      if (status === 'approved') {
        icon = CheckCircle;
        toastType = toast.success;
        style = {
          background: '#ECFDF5',
          color: '#065F46',
          border: '1px solid #10B981'
        };
      } else if (status === 'rejected') {
        icon = AlertTriangle;
        toastType = toast.error;
        style = {
          background: '#FEF2F2',
          color: '#991B1B',
          border: '1px solid #EF4444'
        };
      }
      
      toastType(
        <div className="flex items-center space-x-3">
          <icon className="w-5 h-5 text-current" />
          <div>
            <p className="font-medium">KYC状态更新</p>
            <p className="text-sm">{message}</p>
          </div>
        </div>,
        {
          duration: 8000,
          style
        }
      );
    }
  }, [kycStatus]);

  // 这个组件不渲染任何UI，只处理通知
  return null;
};

export default RealtimeNotifications;