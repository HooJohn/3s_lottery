import React from 'react';
import { cn } from '../../utils/cn';
import { X } from 'lucide-react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md' | 'lg';
  shape?: 'rounded' | 'pill' | 'square';
  dot?: boolean;
  count?: number;
  maxCount?: number;
  showZero?: boolean;
  closable?: boolean;
  onClose?: () => void;
  icon?: React.ReactNode;
  children?: React.ReactNode;
}

const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  size = 'md',
  shape = 'rounded',
  dot = false,
  count,
  maxCount = 99,
  showZero = false,
  closable = false,
  onClose,
  icon,
  children,
  className,
  ...props
}) => {
  // 处理数字显示
  const getDisplayCount = () => {
    if (count === undefined) return null;
    if (count === 0 && !showZero) return null;
    if (count > maxCount) return `${maxCount}+`;
    return count.toString();
  };

  const displayCount = getDisplayCount();
  const hasContent = children || displayCount !== null;

  // 如果是点状徽章且没有内容，直接返回点
  if (dot && !hasContent) {
    return (
      <span
        className={cn(
          'inline-block w-2 h-2 rounded-full',
          {
            'bg-gray-400': variant === 'default',
            'bg-primary-500': variant === 'primary',
            'bg-secondary-500': variant === 'secondary',
            'bg-success-500': variant === 'success',
            'bg-warning-500': variant === 'warning',
            'bg-danger-500': variant === 'danger',
            'bg-info-500': variant === 'info',
          },
          className
        )}
        {...props}
      />
    );
  }

  // 如果没有内容且不是点状徽章，不渲染
  if (!hasContent && !dot) {
    return null;
  }

  const baseClasses = cn(
    'inline-flex items-center justify-center font-semibold transition-all duration-200',
    
    // 尺寸样式
    {
      'px-1.5 py-0.5 text-xs min-w-[16px] h-4': size === 'sm',
      'px-2 py-1 text-xs min-w-[20px] h-5': size === 'md',
      'px-2.5 py-1 text-sm min-w-[24px] h-6': size === 'lg',
    },
    
    // 形状样式
    {
      'rounded': shape === 'rounded',
      'rounded-full': shape === 'pill',
      'rounded-none': shape === 'square',
    },
    
    // 变体样式
    {
      // Default
      'bg-gray-100 text-gray-800 border border-gray-200': variant === 'default',
      
      // Primary
      'bg-primary-500 text-white': variant === 'primary',
      
      // Secondary
      'bg-secondary-500 text-gray-900': variant === 'secondary',
      
      // Success
      'bg-success-500 text-white': variant === 'success',
      
      // Warning
      'bg-warning-500 text-white': variant === 'warning',
      
      // Danger
      'bg-danger-500 text-white': variant === 'danger',
      
      // Info
      'bg-info-500 text-white': variant === 'info',
    },
    
    className
  );

  return (
    <span className={baseClasses} {...props}>
      {icon && (
        <span className={cn(
          'flex-shrink-0',
          {
            'w-3 h-3': size === 'sm',
            'w-4 h-4': size === 'md',
            'w-5 h-5': size === 'lg',
          },
          children && 'mr-1'
        )}>
          {icon}
        </span>
      )}
      
      {children || displayCount}
      
      {closable && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onClose?.();
          }}
          className={cn(
            'flex-shrink-0 ml-1 hover:bg-black hover:bg-opacity-10 rounded-full p-0.5 transition-colors',
            {
              'w-3 h-3': size === 'sm',
              'w-4 h-4': size === 'md',
              'w-5 h-5': size === 'lg',
            }
          )}
        >
          <X className="w-full h-full" />
        </button>
      )}
    </span>
  );
};

// 带徽章的包装组件
export interface BadgeWrapperProps {
  badge?: {
    count?: number;
    dot?: boolean;
    variant?: BadgeProps['variant'];
    maxCount?: number;
    showZero?: boolean;
  };
  children: React.ReactNode;
  className?: string;
}

const BadgeWrapper: React.FC<BadgeWrapperProps> = ({
  badge,
  children,
  className,
}) => {
  if (!badge || (badge.count === 0 && !badge.showZero && !badge.dot)) {
    return <>{children}</>;
  }

  return (
    <div className={cn('relative inline-block', className)}>
      {children}
      <Badge
        {...badge}
        className="absolute -top-1 -right-1 transform translate-x-1/2 -translate-y-1/2"
      />
    </div>
  );
};

export { Badge, BadgeWrapper };