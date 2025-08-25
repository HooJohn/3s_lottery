import React, { useEffect, useContext, createContext } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface WebSocketContextType {
  connectionStatus: {
    isConnected: boolean;
    isReconnecting: boolean;
    reconnectAttempts: number;
  };
  connect: (token?: string) => Promise<void>;
  disconnect: () => void;
  sendMessage: (type: string, data: any) => boolean;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: React.ReactNode;
  autoConnect?: boolean;
  token?: string;
}

const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ 
  children, 
  autoConnect = true,
  token 
}) => {
  const { connectionStatus, connect, disconnect, sendMessage } = useWebSocket();

  // 自动连接WebSocket
  useEffect(() => {
    if (autoConnect) {
      // 从localStorage获取token（如果没有传入token）
      const authToken = token || localStorage.getItem('auth_token');
      
      if (authToken) {
        connect(authToken).catch((error) => {
          console.error('WebSocket自动连接失败:', error);
        });
      } else {
        // 即使没有token也尝试连接（用于匿名用户）
        connect().catch((error) => {
          console.error('WebSocket匿名连接失败:', error);
        });
      }
    }

    // 清理函数
    return () => {
      if (autoConnect) {
        disconnect();
      }
    };
  }, [autoConnect, token, connect, disconnect]);

  // 监听页面可见性变化，自动重连
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && !connectionStatus.isConnected) {
        const authToken = token || localStorage.getItem('auth_token');
        connect(authToken).catch((error) => {
          console.error('页面激活时WebSocket重连失败:', error);
        });
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [connectionStatus.isConnected, token, connect]);

  // 监听网络状态变化
  useEffect(() => {
    const handleOnline = () => {
      if (!connectionStatus.isConnected) {
        const authToken = token || localStorage.getItem('auth_token');
        connect(authToken).catch((error) => {
          console.error('网络恢复时WebSocket重连失败:', error);
        });
      }
    };

    const handleOffline = () => {
      console.log('网络断开，WebSocket将自动重连');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [connectionStatus.isConnected, token, connect]);

  const contextValue: WebSocketContextType = {
    connectionStatus,
    connect,
    disconnect,
    sendMessage,
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

export default WebSocketProvider;