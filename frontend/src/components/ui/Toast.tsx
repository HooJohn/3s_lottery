import React, { createContext, useContext, useState, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { cn } from '../../utils/cn';

export interface ToastProps {
  id: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  duration?: number;
  closable?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
  onClose?: () => void;
}

export interface ToastContextType {
  toasts: ToastProps[];
  addToast: (toast: Omit<ToastProps, 'id'>) => string;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

// 单个Toast组件
const Toast: React.FC<ToastProps & { onRemove: (id: string) => void }> = ({
  id,
  type = 'info',
  title,
  message,
  duration = 5000,
  closable = true,
  action,
  onClose,
  onRemove,
}) => {
  const [isVisible, setIsVisible] = React.useState(true);

  // 自动关闭
  React.useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration]);

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
    setTimeout(() => onRemove(id), 300); // 等待动画完成
  };

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5" />;
      case 'error':
        return <AlertCircle className="w-5 h-5" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5" />;
      default:
        return <Info className="w-5 h-5" />;
    }
  };

  const getTypeStyles = () => {
    switch (type) {
      case 'success':
        return 'border-success-200 bg-success-50 text-success-800';
      case 'error':
        return 'border-danger-200 bg-danger-50 text-danger-800';
      case 'warning':
        return 'border-warning-200 bg-warning-50 text-warning-800';
      default:
        return 'border-info-200 bg-info-50 text-info-800';
    }
  };

  const getIconColor = () => {
    switch (type) {
      case 'success':
        return 'text-success-500';
      case 'error':
        return 'text-danger-500';
      case 'warning':
        return 'text-warning-500';
      default:
        return 'text-info-500';
    }
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, x: 300, scale: 0.3 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          exit={{ opacity: 0, x: 300, scale: 0.5 }}
          transition={{ duration: 0.3 }}
          className={cn(
            'relative flex items-start gap-3 p-4 rounded-lg border shadow-medium max-w-md',
            getTypeStyles()
          )}
        >
          {/* 图标 */}
          <div className={cn('flex-shrink-0 mt-0.5', getIconColor())}>
            {getIcon()}
          </div>

          {/* 内容 */}
          <div className="flex-1 min-w-0">
            {title && (
              <h4 className="font-semibold text-sm mb-1">{title}</h4>
            )}
            <p className="text-sm leading-relaxed">{message}</p>
            
            {action && (
              <button
                onClick={action.onClick}
                className="mt-2 text-sm font-medium underline hover:no-underline"
              >
                {action.label}
              </button>
            )}
          </div>

          {/* 关闭按钮 */}
          {closable && (
            <button
              onClick={handleClose}
              className="flex-shrink-0 p-1 rounded-md hover:bg-black hover:bg-opacity-10 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          {/* 进度条 */}
          {duration > 0 && (
            <motion.div
              initial={{ width: '100%' }}
              animate={{ width: '0%' }}
              transition={{ duration: duration / 1000, ease: 'linear' }}
              className="absolute bottom-0 left-0 h-1 bg-current opacity-30 rounded-b-lg"
            />
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// Toast容器组件
const ToastContainer: React.FC<{ toasts: ToastProps[]; onRemove: (id: string) => void }> = ({
  toasts,
  onRemove,
}) => {
  if (toasts.length === 0) return null;

  return createPortal(
    <div className="fixed top-4 right-4 z-50 space-y-3 pointer-events-none">
      <AnimatePresence>
        {toasts.map((toast) => (
          <div key={toast.id} className="pointer-events-auto">
            <Toast {...toast} onRemove={onRemove} />
          </div>
        ))}
      </AnimatePresence>
    </div>,
    document.body
  );
};

// Toast Provider组件
export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastProps[]>([]);

  const addToast = useCallback((toast: Omit<ToastProps, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast: ToastProps = { ...toast, id };
    
    setToasts((prev) => [...prev, newToast]);
    return id;
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const clearToasts = useCallback(() => {
    setToasts([]);
  }, []);

  const contextValue: ToastContextType = {
    toasts,
    addToast,
    removeToast,
    clearToasts,
  };

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
};

// 便捷的toast函数
export const toast = {
  success: (message: string, options?: Partial<Omit<ToastProps, 'id' | 'type' | 'message'>>) => {
    // 这个函数需要在ToastProvider内部使用
    console.warn('toast.success should be used within ToastProvider context');
  },
  error: (message: string, options?: Partial<Omit<ToastProps, 'id' | 'type' | 'message'>>) => {
    console.warn('toast.error should be used within ToastProvider context');
  },
  warning: (message: string, options?: Partial<Omit<ToastProps, 'id' | 'type' | 'message'>>) => {
    console.warn('toast.warning should be used within ToastProvider context');
  },
  info: (message: string, options?: Partial<Omit<ToastProps, 'id' | 'type' | 'message'>>) => {
    console.warn('toast.info should be used within ToastProvider context');
  },
};

export { Toast };