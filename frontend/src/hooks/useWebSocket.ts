import { useEffect, useRef, useCallback, useState } from 'react';
import { websocketService, WebSocketMessage, MessageHandler, MESSAGE_TYPES } from '@/services/websocket';

/**
 * WebSocket Hook - 管理WebSocket连接和消息订阅
 */
export const useWebSocket = () => {
  const [connectionStatus, setConnectionStatus] = useState(websocketService.getConnectionStatus());
  const statusUpdateTimer = useRef<NodeJS.Timeout | null>(null);

  // 更新连接状态
  const updateConnectionStatus = useCallback(() => {
    setConnectionStatus(websocketService.getConnectionStatus());
  }, []);

  // 定期更新连接状态
  useEffect(() => {
    statusUpdateTimer.current = setInterval(updateConnectionStatus, 1000);
    
    return () => {
      if (statusUpdateTimer.current) {
        clearInterval(statusUpdateTimer.current);
      }
    };
  }, [updateConnectionStatus]);

  // 连接WebSocket
  const connect = useCallback(async (token?: string) => {
    try {
      await websocketService.connect(token);
      updateConnectionStatus();
    } catch (error) {
      console.error('WebSocket连接失败:', error);
      throw error;
    }
  }, [updateConnectionStatus]);

  // 断开WebSocket
  const disconnect = useCallback(() => {
    websocketService.disconnect();
    updateConnectionStatus();
  }, [updateConnectionStatus]);

  // 发送消息
  const sendMessage = useCallback((type: string, data: any) => {
    return websocketService.send(type, data);
  }, []);

  // 订阅消息
  const subscribe = useCallback((messageType: string, handler: MessageHandler) => {
    return websocketService.subscribe(messageType, handler);
  }, []);

  // 取消订阅
  const unsubscribe = useCallback((messageType: string, handler?: MessageHandler) => {
    websocketService.unsubscribe(messageType, handler);
  }, []);

  return {
    connectionStatus,
    connect,
    disconnect,
    sendMessage,
    subscribe,
    unsubscribe,
  };
};

/**
 * 开奖结果订阅Hook
 */
export const useLotteryDrawResults = () => {
  const [drawResult, setDrawResult] = useState<any>(null);
  const [countdown, setCountdown] = useState<any>(null);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    // 订阅11选5开奖结果
    const unsubscribeResult = subscribe(MESSAGE_TYPES.LOTTERY_DRAW_RESULT, (message: WebSocketMessage) => {
      setDrawResult(message.data);
    });

    // 订阅开奖倒计时
    const unsubscribeCountdown = subscribe(MESSAGE_TYPES.LOTTERY_DRAW_COUNTDOWN, (message: WebSocketMessage) => {
      setCountdown(message.data);
    });

    return () => {
      unsubscribeResult();
      unsubscribeCountdown();
    };
  }, [subscribe]);

  return { drawResult, countdown };
};

/**
 * 余额更新订阅Hook
 */
export const useBalanceUpdates = () => {
  const [balance, setBalance] = useState<any>(null);
  const [transaction, setTransaction] = useState<any>(null);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    // 订阅余额更新
    const unsubscribeBalance = subscribe(MESSAGE_TYPES.BALANCE_UPDATE, (message: WebSocketMessage) => {
      setBalance(message.data);
    });

    // 订阅交易更新
    const unsubscribeTransaction = subscribe(MESSAGE_TYPES.TRANSACTION_UPDATE, (message: WebSocketMessage) => {
      setTransaction(message.data);
    });

    return () => {
      unsubscribeBalance();
      unsubscribeTransaction();
    };
  }, [subscribe]);

  return { balance, transaction };
};

/**
 * 奖励更新订阅Hook
 */
export const useRewardUpdates = () => {
  const [reward, setReward] = useState<any>(null);
  const [vipUpdate, setVipUpdate] = useState<any>(null);
  const [referralReward, setReferralReward] = useState<any>(null);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    // 订阅奖励更新
    const unsubscribeReward = subscribe(MESSAGE_TYPES.REWARD_UPDATE, (message: WebSocketMessage) => {
      setReward(message.data);
    });

    // 订阅VIP等级更新
    const unsubscribeVip = subscribe(MESSAGE_TYPES.VIP_LEVEL_UPDATE, (message: WebSocketMessage) => {
      setVipUpdate(message.data);
    });

    // 订阅推荐奖励
    const unsubscribeReferral = subscribe(MESSAGE_TYPES.REFERRAL_REWARD, (message: WebSocketMessage) => {
      setReferralReward(message.data);
    });

    return () => {
      unsubscribeReward();
      unsubscribeVip();
      unsubscribeReferral();
    };
  }, [subscribe]);

  return { reward, vipUpdate, referralReward };
};

/**
 * 系统通知订阅Hook
 */
export const useSystemNotifications = () => {
  const [announcement, setAnnouncement] = useState<any>(null);
  const [maintenance, setMaintenance] = useState<any>(null);
  const [securityAlert, setSecurityAlert] = useState<any>(null);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    // 订阅系统公告
    const unsubscribeAnnouncement = subscribe(MESSAGE_TYPES.SYSTEM_ANNOUNCEMENT, (message: WebSocketMessage) => {
      setAnnouncement(message.data);
    });

    // 订阅维护通知
    const unsubscribeMaintenance = subscribe(MESSAGE_TYPES.MAINTENANCE_NOTICE, (message: WebSocketMessage) => {
      setMaintenance(message.data);
    });

    // 订阅安全警报
    const unsubscribeSecurity = subscribe(MESSAGE_TYPES.SECURITY_ALERT, (message: WebSocketMessage) => {
      setSecurityAlert(message.data);
    });

    return () => {
      unsubscribeAnnouncement();
      unsubscribeMaintenance();
      unsubscribeSecurity();
    };
  }, [subscribe]);

  return { announcement, maintenance, securityAlert };
};

/**
 * 用户状态更新订阅Hook
 */
export const useUserStatusUpdates = () => {
  const [userStatus, setUserStatus] = useState<any>(null);
  const [kycStatus, setKycStatus] = useState<any>(null);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    // 订阅用户状态更新
    const unsubscribeUser = subscribe(MESSAGE_TYPES.USER_STATUS_UPDATE, (message: WebSocketMessage) => {
      setUserStatus(message.data);
    });

    // 订阅KYC状态更新
    const unsubscribeKyc = subscribe(MESSAGE_TYPES.KYC_STATUS_UPDATE, (message: WebSocketMessage) => {
      setKycStatus(message.data);
    });

    return () => {
      unsubscribeUser();
      unsubscribeKyc();
    };
  }, [subscribe]);

  return { userStatus, kycStatus };
};