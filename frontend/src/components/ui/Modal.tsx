import React from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '../../utils/cn';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  variant?: 'modal' | 'drawer' | 'dialog';
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
  showCloseButton?: boolean;
  className?: string;
}

export interface DrawerProps extends Omit<ModalProps, 'variant'> {
  position?: 'left' | 'right' | 'top' | 'bottom';
}

export interface DialogProps extends Omit<ModalProps, 'variant'> {
  type?: 'info' | 'warning' | 'error' | 'success' | 'confirm';
  onConfirm?: () => void;
  onCancel?: () => void;
  confirmText?: string;
  cancelText?: string;
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  variant = 'modal',
  closeOnOverlayClick = true,
  closeOnEscape = true,
  showCloseButton = true,
  className,
}) => {
  // 处理ESC键关闭
  React.useEffect(() => {
    if (!closeOnEscape) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // 防止背景滚动
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, closeOnEscape, onClose]);

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4',
  };

  const modalContent = (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* 背景遮罩 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
            onClick={closeOnOverlayClick ? onClose : undefined}
          />

          {/* 模态框内容 */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            className={cn(
              'relative w-full bg-white rounded-2xl shadow-heavy max-h-[90vh] overflow-hidden',
              sizeClasses[size],
              className
            )}
            onClick={(e) => e.stopPropagation()}
          >
            {/* 模态框头部 */}
            {(title || showCloseButton) && (
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                {title && (
                  <h2 className="text-xl font-semibold text-gray-900">
                    {title}
                  </h2>
                )}
                {showCloseButton && (
                  <button
                    onClick={onClose}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    aria-label="关闭"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            )}

            {/* 模态框内容 */}
            <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
              {children}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );

  // 使用Portal渲染到body
  return createPortal(modalContent, document.body);
};

// 抽屉组件
const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  children,
  position = 'right',
  closeOnOverlayClick = true,
  closeOnEscape = true,
  showCloseButton = true,
  className,
}) => {
  React.useEffect(() => {
    if (!closeOnEscape) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, closeOnEscape, onClose]);

  const getDrawerStyles = () => {
    const baseStyles = 'fixed bg-white shadow-heavy z-50';
    
    switch (position) {
      case 'left':
        return `${baseStyles} left-0 top-0 h-full w-80 max-w-[80vw]`;
      case 'right':
        return `${baseStyles} right-0 top-0 h-full w-80 max-w-[80vw]`;
      case 'top':
        return `${baseStyles} top-0 left-0 w-full h-80 max-h-[80vh]`;
      case 'bottom':
        return `${baseStyles} bottom-0 left-0 w-full h-80 max-h-[80vh] rounded-t-2xl`;
      default:
        return `${baseStyles} right-0 top-0 h-full w-80 max-w-[80vw]`;
    }
  };

  const getAnimationProps = () => {
    switch (position) {
      case 'left':
        return {
          initial: { x: '-100%' },
          animate: { x: 0 },
          exit: { x: '-100%' },
        };
      case 'right':
        return {
          initial: { x: '100%' },
          animate: { x: 0 },
          exit: { x: '100%' },
        };
      case 'top':
        return {
          initial: { y: '-100%' },
          animate: { y: 0 },
          exit: { y: '-100%' },
        };
      case 'bottom':
        return {
          initial: { y: '100%' },
          animate: { y: 0 },
          exit: { y: '100%' },
        };
      default:
        return {
          initial: { x: '100%' },
          animate: { x: 0 },
          exit: { x: '100%' },
        };
    }
  };

  const drawerContent = (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* 背景遮罩 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-40"
            onClick={closeOnOverlayClick ? onClose : undefined}
          />

          {/* 抽屉内容 */}
          <motion.div
            {...getAnimationProps()}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className={cn(getDrawerStyles(), className)}
          >
            {/* 抽屉头部 */}
            {(title || showCloseButton) && (
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                {title && (
                  <h2 className="text-xl font-semibold text-gray-900">
                    {title}
                  </h2>
                )}
                {showCloseButton && (
                  <button
                    onClick={onClose}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    aria-label="关闭"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            )}

            {/* 抽屉内容 */}
            <div className="flex-1 overflow-y-auto p-6">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );

  return createPortal(drawerContent, document.body);
};

// 确认对话框组件
const Dialog: React.FC<DialogProps> = ({
  isOpen,
  onClose,
  title,
  children,
  type = 'info',
  onConfirm,
  onCancel,
  confirmText = '确认',
  cancelText = '取消',
  closeOnOverlayClick = false,
  closeOnEscape = true,
  className,
}) => {
  const handleConfirm = () => {
    onConfirm?.();
    onClose();
  };

  const handleCancel = () => {
    onCancel?.();
    onClose();
  };

  const getTypeStyles = () => {
    switch (type) {
      case 'warning':
        return 'text-warning-600';
      case 'error':
        return 'text-danger-600';
      case 'success':
        return 'text-success-600';
      default:
        return 'text-info-600';
    }
  };

  const getTypeIcon = () => {
    switch (type) {
      case 'warning':
        return '⚠️';
      case 'error':
        return '❌';
      case 'success':
        return '✅';
      case 'confirm':
        return '❓';
      default:
        return 'ℹ️';
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
      closeOnOverlayClick={closeOnOverlayClick}
      closeOnEscape={closeOnEscape}
      showCloseButton={false}
      className={className}
    >
      <div className="p-6">
        <div className="flex items-start gap-4 mb-6">
          <div className={cn('text-2xl', getTypeStyles())}>
            {getTypeIcon()}
          </div>
          <div className="flex-1">
            {children}
          </div>
        </div>
        
        <div className="flex justify-end gap-3">
          {type === 'confirm' && (
            <button
              onClick={handleCancel}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            >
              {cancelText}
            </button>
          )}
          <button
            onClick={handleConfirm}
            className={cn(
              'px-4 py-2 rounded-lg font-medium transition-colors',
              type === 'error' || type === 'warning'
                ? 'bg-danger-500 hover:bg-danger-600 text-white'
                : 'bg-primary-500 hover:bg-primary-600 text-white'
            )}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </Modal>
  );
};

export { Modal, Drawer, Dialog };