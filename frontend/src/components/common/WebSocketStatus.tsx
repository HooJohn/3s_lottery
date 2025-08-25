import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Wifi, 
  WifiOff, 
  RotateCcw,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { cn } from '@/utils/cn';

interface WebSocketStatusProps {
  className?: string;
  showText?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const WebSocketStatus: React.FC<WebSocketStatusProps> = ({ 
  className,
  showText = false,
  size = 'md'
}) => {
  const { connectionStatus } = useWebSocket();

  const getStatusConfig = () => {
    if (connectionStatus.isConnected) {
      return {
        icon: CheckCircle,
        color: 'text-success-500',
        bgColor: 'bg-success-100',
        text: '已连接',
        pulse: false
      };
    }
    
    if (connectionStatus.isReconnecting) {
      return {
        icon: RotateCcw,
        color: 'text-warning-500',
        bgColor: 'bg-warning-100',
        text: `重连中 (${connectionStatus.reconnectAttempts})`,
        pulse: true
      };
    }
    
    return {
      icon: WifiOff,
      color: 'text-danger-500',
      bgColor: 'bg-danger-100',
      text: '连接断开',
      pulse: false
    };
  };

  const sizeConfig = {
    sm: {
      icon: 'w-3 h-3',
      container: 'w-6 h-6',
      text: 'text-xs'
    },
    md: {
      icon: 'w-4 h-4',
      container: 'w-8 h-8',
      text: 'text-sm'
    },
    lg: {
      icon: 'w-5 h-5',
      container: 'w-10 h-10',
      text: 'text-base'
    }
  };

  const config = getStatusConfig();
  const sizes = sizeConfig[size];
  const Icon = config.icon;

  return (
    <div className={cn('flex items-center space-x-2', className)}>
      <div className={cn(
        'rounded-full flex items-center justify-center',
        sizes.container,
        config.bgColor
      )}>
        <motion.div
          animate={config.pulse ? { rotate: 360 } : {}}
          transition={config.pulse ? { 
            duration: 1, 
            repeat: Infinity, 
            ease: 'linear' 
          } : {}}
        >
          <Icon className={cn(sizes.icon, config.color)} />
        </motion.div>
      </div>
      
      <AnimatePresence>
        {showText && (
          <motion.span
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            className={cn(
              'font-medium',
              sizes.text,
              config.color
            )}
          >
            {config.text}
          </motion.span>
        )}
      </AnimatePresence>
    </div>
  );
};

export default WebSocketStatus;