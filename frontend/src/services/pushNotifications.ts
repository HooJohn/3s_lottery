/**
 * 推送通知服务 - 处理各种实时推送功能
 * 包括开奖结果、余额变动、系统公告等
 */

import { websocketService, MESSAGE_TYPES, WebSocketMessage } from './websocket';
import { toast } from 'react-hot-toast';

export interface PushNotificationConfig {
  enableSound: boolean;
  enableVibration: boolean;
  enableDesktopNotifications: boolean;
  enableDrawResults: boolean;
  enableBalanceUpdates: boolean;
  enableRewardUpdates: boolean;
  enableSystemAnnouncements: boolean;
}

export class PushNotificationService {
  private config: PushNotificationConfig;
  private audioContext: AudioContext | null = null;
  private notificationPermission: NotificationPermission = 'default';

  constructor(config: Partial<PushNotificationConfig> = {}) {
    this.config = {
      enableSound: config.enableSound ?? true,
      enableVibration: config.enableVibration ?? true,
      enableDesktopNotifications: config.enableDesktopNotifications ?? true,
      enableDrawResults: config.enableDrawResults ?? true,
      enableBalanceUpdates: config.enableBalanceUpdates ?? true,
      enableRewardUpdates: config.enableRewardUpdates ?? true,
      enableSystemAnnouncements: config.enableSystemAnnouncements ?? true,
    };

    this.initializeNotifications();
    this.setupWebSocketListeners();
  }

  /**
   * 初始化通知权限
   */
  private async initializeNotifications(): Promise<void> {
    if ('Notification' in window) {
      this.notificationPermission = await Notification.requestPermission();
    }

    // 初始化音频上下文
    if ('AudioContext' in window || 'webkitAudioContext' in window) {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
  }

  /**
   * 设置WebSocket消息监听器
   */
  private setupWebSocketListeners(): void {
    // 开奖结果推送
    websocketService.subscribe(MESSAGE_TYPES.LOTTERY_DRAW_RESULT, (message) => {
      if (this.config.enableDrawResults) {
        this.handleDrawResult(message);
      }
    });

    // 开奖倒计时推送
    websocketService.subscribe(MESSAGE_TYPES.LOTTERY_DRAW_COUNTDOWN, (message) => {
      if (this.config.enableDrawResults) {
        this.handleDrawCountdown(message);
      }
    });

    // 大乐透开奖结果
    websocketService.subscribe(MESSAGE_TYPES.SUPERLOTTO_DRAW_RESULT, (message) => {
      if (this.config.enableDrawResults) {
        this.handleSuperLottoResult(message);
      }
    });

    // 余额更新推送
    websocketService.subscribe(MESSAGE_TYPES.BALANCE_UPDATE, (message) => {
      if (this.config.enableBalanceUpdates) {
        this.handleBalanceUpdate(message);
      }
    });

    // 交易更新推送
    websocketService.subscribe(MESSAGE_TYPES.TRANSACTION_UPDATE, (message) => {
      if (this.config.enableBalanceUpdates) {
        this.handleTransactionUpdate(message);
      }
    });

    // 奖励更新推送
    websocketService.subscribe(MESSAGE_TYPES.REWARD_UPDATE, (message) => {
      if (this.config.enableRewardUpdates) {
        this.handleRewardUpdate(message);
      }
    });

    // VIP等级更新
    websocketService.subscribe(MESSAGE_TYPES.VIP_LEVEL_UPDATE, (message) => {
      if (this.config.enableRewardUpdates) {
        this.handleVipLevelUpdate(message);
      }
    });

    // 推荐奖励
    websocketService.subscribe(MESSAGE_TYPES.REFERRAL_REWARD, (message) => {
      if (this.config.enableRewardUpdates) {
        this.handleReferralReward(message);
      }
    });

    // 系统公告
    websocketService.subscribe(MESSAGE_TYPES.SYSTEM_ANNOUNCEMENT, (message) => {
      if (this.config.enableSystemAnnouncements) {
        this.handleSystemAnnouncement(message);
      }
    });

    // 维护通知
    websocketService.subscribe(MESSAGE_TYPES.MAINTENANCE_NOTICE, (message) => {
      if (this.config.enableSystemAnnouncements) {
        this.handleMaintenanceNotice(message);
      }
    });

    // 安全警报
    websocketService.subscribe(MESSAGE_TYPES.SECURITY_ALERT, (message) => {
      if (this.config.enableSystemAnnouncements) {
        this.handleSecurityAlert(message);
      }
    });

    // KYC状态更新
    websocketService.subscribe(MESSAGE_TYPES.KYC_STATUS_UPDATE, (message) => {
      this.handleKycStatusUpdate(message);
    });
  }

  /**
   * 处理开奖结果推送
   */
  private handleDrawResult(message: WebSocketMessage): void {
    const { draw_number, winning_numbers, user_winnings } = message.data;

    if (user_winnings && user_winnings > 0) {
      // 用户中奖 - 高优先级通知
      this.showNotification({
        title: '🎉 恭喜中奖！',
        body: `第${draw_number}期中奖 ₦${user_winnings.toLocaleString()}`,
        icon: '🏆',
        priority: 'high',
        persistent: true,
        sound: 'win'
      });

      // 桌面通知
      this.showDesktopNotification(
        '恭喜中奖！',
        `第${draw_number}期中奖 ₦${user_winnings.toLocaleString()}`,
        '/icons/trophy.png'
      );
    } else {
      // 普通开奖结果
      this.showNotification({
        title: '开奖结果',
        body: `第${draw_number}期: ${winning_numbers.join(' ')}`,
        icon: '🎲',
        priority: 'normal',
        sound: 'notification'
      });
    }
  }

  /**
   * 处理开奖倒计时推送
   */
  private handleDrawCountdown(message: WebSocketMessage): void {
    const { draw_number, time_remaining, phase } = message.data;

    // 只在特定时间点推送倒计时通知
    if (phase === 'closing_soon' && time_remaining <= 60) {
      this.showNotification({
        title: '⏰ 投注即将截止',
        body: `第${draw_number}期还有${time_remaining}秒截止投注`,
        icon: '⏰',
        priority: 'normal',
        sound: 'alert'
      });
    }
  }

  /**
   * 处理大乐透开奖结果
   */
  private handleSuperLottoResult(message: WebSocketMessage): void {
    const { draw_number, front_numbers, back_numbers, user_winnings, prize_level } = message.data;

    if (user_winnings && user_winnings > 0) {
      this.showNotification({
        title: '🎊 大乐透中奖！',
        body: `第${draw_number}期 ${prize_level} ₦${user_winnings.toLocaleString()}`,
        icon: '🎊',
        priority: 'high',
        persistent: true,
        sound: 'jackpot'
      });

      this.showDesktopNotification(
        '大乐透中奖！',
        `第${draw_number}期 ${prize_level} ₦${user_winnings.toLocaleString()}`,
        '/icons/jackpot.png'
      );
    } else {
      this.showNotification({
        title: '大乐透开奖',
        body: `第${draw_number}期: ${front_numbers.join(' ')} + ${back_numbers.join(' ')}`,
        icon: '🎱',
        priority: 'normal',
        sound: 'notification'
      });
    }
  }

  /**
   * 处理余额更新推送
   */
  private handleBalanceUpdate(message: WebSocketMessage): void {
    const { amount, type, balance_after, description } = message.data;

    const isPositive = amount > 0;
    const title = isPositive ? '💰 余额增加' : '💸 余额减少';
    const amountText = `${isPositive ? '+' : ''}₦${Math.abs(amount).toLocaleString()}`;

    this.showNotification({
      title,
      body: `${amountText} | 余额: ₦${balance_after.toLocaleString()}`,
      icon: isPositive ? '💰' : '💸',
      priority: 'normal',
      sound: isPositive ? 'coin' : 'notification'
    });
  }

  /**
   * 处理交易更新推送
   */
  private handleTransactionUpdate(message: WebSocketMessage): void {
    const { type, amount, status, transaction_id } = message.data;

    let title = '';
    let icon = '💳';
    let sound = 'notification';

    switch (type) {
      case 'deposit':
        title = status === 'completed' ? '✅ 存款成功' : '⏳ 存款处理中';
        icon = '💳';
        sound = status === 'completed' ? 'success' : 'notification';
        break;
      case 'withdraw':
        title = status === 'completed' ? '✅ 提款成功' : '⏳ 提款处理中';
        icon = '🏦';
        sound = status === 'completed' ? 'success' : 'notification';
        break;
      default:
        title = `${status === 'completed' ? '✅' : '⏳'} 交易${status === 'completed' ? '完成' : '处理中'}`;
    }

    this.showNotification({
      title,
      body: `金额: ₦${amount.toLocaleString()}`,
      icon,
      priority: 'normal',
      sound
    });
  }

  /**
   * 处理奖励更新推送
   */
  private handleRewardUpdate(message: WebSocketMessage): void {
    const { type, amount, description } = message.data;

    let title = '🎁 奖励到账';
    let icon = '🎁';

    if (type === 'vip_rebate') {
      title = '👑 VIP返水';
      icon = '👑';
    } else if (type === 'referral_commission') {
      title = '👥 推荐佣金';
      icon = '👥';
    }

    this.showNotification({
      title,
      body: `₦${amount.toLocaleString()} | ${description}`,
      icon,
      priority: 'normal',
      sound: 'reward',
      persistent: true
    });

    this.showDesktopNotification(
      title,
      `₦${amount.toLocaleString()} | ${description}`,
      '/icons/reward.png'
    );
  }

  /**
   * 处理VIP等级更新
   */
  private handleVipLevelUpdate(message: WebSocketMessage): void {
    const { new_level, old_level, benefits } = message.data;

    this.showNotification({
      title: '🌟 VIP等级提升！',
      body: `从 VIP${old_level} 升级到 VIP${new_level}`,
      icon: '🌟',
      priority: 'high',
      sound: 'levelup',
      persistent: true
    });

    this.showDesktopNotification(
      'VIP等级提升！',
      `从 VIP${old_level} 升级到 VIP${new_level}`,
      '/icons/vip.png'
    );
  }

  /**
   * 处理推荐奖励
   */
  private handleReferralReward(message: WebSocketMessage): void {
    const { level, amount, username } = message.data;

    this.showNotification({
      title: '👥 推荐奖励',
      body: `${level}级推荐 ₦${amount.toLocaleString()} (来自: ${username})`,
      icon: '👥',
      priority: 'normal',
      sound: 'reward'
    });
  }

  /**
   * 处理系统公告
   */
  private handleSystemAnnouncement(message: WebSocketMessage): void {
    const { title, content, priority } = message.data;

    this.showNotification({
      title: `📢 ${title}`,
      body: content,
      icon: '📢',
      priority: priority || 'normal',
      sound: priority === 'high' ? 'alert' : 'notification',
      persistent: priority === 'high'
    });

    if (priority === 'high') {
      this.showDesktopNotification(
        `系统公告: ${title}`,
        content,
        '/icons/announcement.png'
      );
    }
  }

  /**
   * 处理维护通知
   */
  private handleMaintenanceNotice(message: WebSocketMessage): void {
    const { title, content, start_time, end_time } = message.data;

    this.showNotification({
      title: `🔧 ${title}`,
      body: content,
      icon: '🔧',
      priority: 'high',
      sound: 'alert',
      persistent: true
    });

    this.showDesktopNotification(
      `维护通知: ${title}`,
      content,
      '/icons/maintenance.png'
    );
  }

  /**
   * 处理安全警报
   */
  private handleSecurityAlert(message: WebSocketMessage): void {
    const { title, content, action_required } = message.data;

    this.showNotification({
      title: `🚨 ${title}`,
      body: content,
      icon: '🚨',
      priority: 'high',
      sound: 'alarm',
      persistent: true
    });

    this.showDesktopNotification(
      `安全警报: ${title}`,
      content,
      '/icons/security.png'
    );
  }

  /**
   * 处理KYC状态更新
   */
  private handleKycStatusUpdate(message: WebSocketMessage): void {
    const { status, message: kycMessage } = message.data;

    let title = '';
    let icon = '';
    let sound = 'notification';
    let priority: 'normal' | 'high' = 'normal';

    switch (status) {
      case 'approved':
        title = '✅ KYC验证通过';
        icon = '✅';
        sound = 'success';
        priority = 'high';
        break;
      case 'rejected':
        title = '❌ KYC验证失败';
        icon = '❌';
        sound = 'error';
        priority = 'high';
        break;
      default:
        title = 'ℹ️ KYC状态更新';
        icon = 'ℹ️';
    }

    this.showNotification({
      title,
      body: kycMessage,
      icon,
      priority,
      sound,
      persistent: priority === 'high'
    });
  }

  /**
   * 显示应用内通知
   */
  private showNotification(options: {
    title: string;
    body: string;
    icon: string;
    priority: 'normal' | 'high';
    sound?: string;
    persistent?: boolean;
  }): void {
    // 播放声音
    if (this.config.enableSound && options.sound) {
      this.playSound(options.sound);
    }

    // 触发振动
    if (this.config.enableVibration && 'vibrate' in navigator) {
      const pattern = options.priority === 'high' ? [200, 100, 200] : [100];
      navigator.vibrate(pattern);
    }

    // 显示Toast通知
    const toastOptions = {
      duration: options.persistent ? 8000 : 4000,
      style: options.priority === 'high' ? {
        background: '#FEF3C7',
        color: '#92400E',
        border: '1px solid #F59E0B'
      } : undefined
    };

    if (options.priority === 'high') {
      toast.success(`${options.icon} ${options.title}\n${options.body}`, toastOptions);
    } else {
      toast(`${options.icon} ${options.title}\n${options.body}`, toastOptions);
    }
  }

  /**
   * 显示桌面通知
   */
  private showDesktopNotification(title: string, body: string, icon?: string): void {
    if (!this.config.enableDesktopNotifications || this.notificationPermission !== 'granted') {
      return;
    }

    const notification = new Notification(title, {
      body,
      icon: icon || '/icons/logo.png',
      badge: '/icons/badge.png',
      tag: 'lottery-notification',
      requireInteraction: true
    });

    // 点击通知时聚焦窗口
    notification.onclick = () => {
      window.focus();
      notification.close();
    };

    // 自动关闭通知
    setTimeout(() => {
      notification.close();
    }, 8000);
  }

  /**
   * 播放声音
   */
  private playSound(soundType: string): void {
    if (!this.audioContext) return;

    // 简单的音频生成（实际项目中应该使用音频文件）
    const oscillator = this.audioContext.createOscillator();
    const gainNode = this.audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(this.audioContext.destination);

    // 根据声音类型设置不同的频率和持续时间
    switch (soundType) {
      case 'win':
      case 'jackpot':
        oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(1200, this.audioContext.currentTime + 0.3);
        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.5);
        oscillator.start();
        oscillator.stop(this.audioContext.currentTime + 0.5);
        break;
      case 'reward':
      case 'success':
        oscillator.frequency.setValueAtTime(600, this.audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.2, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
        oscillator.start();
        oscillator.stop(this.audioContext.currentTime + 0.3);
        break;
      case 'alert':
      case 'alarm':
        oscillator.frequency.setValueAtTime(400, this.audioContext.currentTime);
        oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime + 0.1);
        oscillator.frequency.setValueAtTime(400, this.audioContext.currentTime + 0.2);
        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.4);
        oscillator.start();
        oscillator.stop(this.audioContext.currentTime + 0.4);
        break;
      default:
        oscillator.frequency.setValueAtTime(500, this.audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2);
        oscillator.start();
        oscillator.stop(this.audioContext.currentTime + 0.2);
    }
  }

  /**
   * 更新配置
   */
  updateConfig(newConfig: Partial<PushNotificationConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * 获取当前配置
   */
  getConfig(): PushNotificationConfig {
    return { ...this.config };
  }
}

// 创建全局推送通知服务实例
export const pushNotificationService = new PushNotificationService();