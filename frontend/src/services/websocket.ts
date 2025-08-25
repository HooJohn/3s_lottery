/**
 * WebSocket服务 - 实时通信管理
 * 支持开奖结果推送、余额更新、系统通知等实时功能
 */

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
  user_id?: string;
}

export interface WebSocketConfig {
  url: string;
  reconnectInterval: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
}

export type MessageHandler = (message: WebSocketMessage) => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private messageHandlers: Map<string, MessageHandler[]> = new Map();
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private isConnected = false;
  private isReconnecting = false;
  private token: string | null = null;

  constructor(config: Partial<WebSocketConfig> = {}) {
    this.config = {
      url: config.url || 'ws://localhost:8000/ws/',
      reconnectInterval: config.reconnectInterval || 3000,
      maxReconnectAttempts: config.maxReconnectAttempts || 10,
      heartbeatInterval: config.heartbeatInterval || 30000,
    };
  }

  /**
   * 连接WebSocket
   */
  connect(token?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        if (token) {
          this.token = token;
        }

        const wsUrl = this.token 
          ? `${this.config.url}?token=${this.token}`
          : this.config.url;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('WebSocket连接已建立');
          this.isConnected = true;
          this.isReconnecting = false;
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('WebSocket消息解析失败:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket连接已关闭:', event.code, event.reason);
          this.isConnected = false;
          this.stopHeartbeat();
          
          if (!this.isReconnecting && this.reconnectAttempts < this.config.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket连接错误:', error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * 断开WebSocket连接
   */
  disconnect(): void {
    this.isReconnecting = false;
    this.stopHeartbeat();
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.isConnected = false;
  }

  /**
   * 发送消息
   */
  send(type: string, data: any): boolean {
    if (!this.isConnected || !this.ws) {
      console.warn('WebSocket未连接，无法发送消息');
      return false;
    }

    try {
      const message: WebSocketMessage = {
        type,
        data,
        timestamp: Date.now(),
      };

      this.ws.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('发送WebSocket消息失败:', error);
      return false;
    }
  }

  /**
   * 订阅消息类型
   */
  subscribe(messageType: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, []);
    }
    
    this.messageHandlers.get(messageType)!.push(handler);

    // 返回取消订阅函数
    return () => {
      const handlers = this.messageHandlers.get(messageType);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index > -1) {
          handlers.splice(index, 1);
        }
      }
    };
  }

  /**
   * 取消订阅消息类型
   */
  unsubscribe(messageType: string, handler?: MessageHandler): void {
    if (!handler) {
      this.messageHandlers.delete(messageType);
      return;
    }

    const handlers = this.messageHandlers.get(messageType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * 获取连接状态
   */
  getConnectionStatus(): {
    isConnected: boolean;
    isReconnecting: boolean;
    reconnectAttempts: number;
  } {
    return {
      isConnected: this.isConnected,
      isReconnecting: this.isReconnecting,
      reconnectAttempts: this.reconnectAttempts,
    };
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(message: WebSocketMessage): void {
    const handlers = this.messageHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error(`处理WebSocket消息失败 (${message.type}):`, error);
        }
      });
    }
  }

  /**
   * 安排重连
   */
  private scheduleReconnect(): void {
    if (this.isReconnecting) return;

    this.isReconnecting = true;
    this.reconnectAttempts++;

    console.log(`WebSocket重连尝试 ${this.reconnectAttempts}/${this.config.maxReconnectAttempts}`);

    this.reconnectTimer = setTimeout(() => {
      this.connect(this.token).catch(() => {
        if (this.reconnectAttempts < this.config.maxReconnectAttempts) {
          this.scheduleReconnect();
        } else {
          console.error('WebSocket重连失败，已达到最大重试次数');
          this.isReconnecting = false;
        }
      });
    }, this.config.reconnectInterval);
  }

  /**
   * 开始心跳
   */
  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected) {
        this.send('ping', { timestamp: Date.now() });
      }
    }, this.config.heartbeatInterval);
  }

  /**
   * 停止心跳
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }
}

// 创建全局WebSocket服务实例
export const websocketService = new WebSocketService({
  url: process.env.NODE_ENV === 'production' 
    ? 'wss://api.lottery.africa/ws/' 
    : 'ws://localhost:8000/ws/',
});

// 消息类型常量
export const MESSAGE_TYPES = {
  // 开奖相关
  LOTTERY_DRAW_RESULT: 'lottery_draw_result',
  LOTTERY_DRAW_COUNTDOWN: 'lottery_draw_countdown',
  SUPERLOTTO_DRAW_RESULT: 'superlotto_draw_result',
  
  // 余额相关
  BALANCE_UPDATE: 'balance_update',
  TRANSACTION_UPDATE: 'transaction_update',
  
  // 奖励相关
  REWARD_UPDATE: 'reward_update',
  VIP_LEVEL_UPDATE: 'vip_level_update',
  REFERRAL_REWARD: 'referral_reward',
  
  // 系统通知
  SYSTEM_ANNOUNCEMENT: 'system_announcement',
  MAINTENANCE_NOTICE: 'maintenance_notice',
  SECURITY_ALERT: 'security_alert',
  
  // 用户状态
  USER_STATUS_UPDATE: 'user_status_update',
  KYC_STATUS_UPDATE: 'kyc_status_update',
  
  // 心跳
  PING: 'ping',
  PONG: 'pong',
} as const;

export type MessageType = typeof MESSAGE_TYPES[keyof typeof MESSAGE_TYPES];