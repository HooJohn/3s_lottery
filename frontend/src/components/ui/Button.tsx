import React from 'react';
import { cn } from '../../utils/cn';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  touchOptimized?: boolean; // 移动端触摸优化
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({
    className,
    variant = 'primary',
    size = 'md',
    loading = false,
    icon,
    iconPosition = 'left',
    fullWidth = false,
    touchOptimized = true,
    disabled,
    children,
    ...props
  }, ref) => {
    const baseStyles = cn(
      // 基础样式
      'inline-flex items-center justify-center font-semibold transition-all duration-200',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'relative overflow-hidden select-none',
      
      // 移动端触摸优化
      touchOptimized && [
        'touch-manipulation', // 优化触摸响应
        'active:scale-95', // 触摸反馈
        'active:transition-transform active:duration-75', // 快速反馈
      ],
      
      // 尺寸样式 - 移动端优化最小触摸目标
      {
        'px-3 py-1.5 text-sm rounded-md': size === 'sm' && !touchOptimized,
        'px-4 py-2.5 text-sm rounded-md min-h-[40px]': size === 'sm' && touchOptimized,
        'px-4 py-2 text-base rounded-lg': size === 'md' && !touchOptimized,
        'px-6 py-3 text-base rounded-lg min-h-[44px]': size === 'md' && touchOptimized,
        'px-6 py-3 text-lg rounded-lg': size === 'lg' && !touchOptimized,
        'px-8 py-4 text-lg rounded-lg min-h-[48px]': size === 'lg' && touchOptimized,
        'px-8 py-4 text-xl rounded-xl': size === 'xl' && !touchOptimized,
        'px-10 py-5 text-xl rounded-xl min-h-[52px]': size === 'xl' && touchOptimized,
      },
      
      // 变体样式
      {
        // Primary - 主要按钮 (尼日利亚绿色)
        'bg-gradient-primary text-white shadow-primary hover:shadow-primary-lg focus:ring-primary-500': 
          variant === 'primary',
        'hover:bg-gradient-to-r hover:from-primary-600 hover:to-primary-700': 
          variant === 'primary',
        
        // Secondary - 次要按钮 (喀麦隆黄色)
        'bg-gradient-secondary text-gray-900 shadow-medium hover:shadow-heavy focus:ring-secondary-500': 
          variant === 'secondary',
        'hover:bg-gradient-to-r hover:from-secondary-600 hover:to-secondary-700': 
          variant === 'secondary',
        
        // Danger - 危险按钮 (喀麦隆红色)
        'bg-gradient-danger text-white shadow-medium hover:shadow-heavy focus:ring-danger-500': 
          variant === 'danger',
        'hover:bg-gradient-to-r hover:from-danger-600 hover:to-danger-700': 
          variant === 'danger',
        
        // Success - 成功按钮
        'bg-gradient-to-r from-success-500 to-success-600 text-white shadow-medium hover:shadow-heavy focus:ring-success-500': 
          variant === 'success',
        'hover:from-success-600 hover:to-success-700': 
          variant === 'success',
        
        // Ghost - 透明按钮
        'text-primary-600 hover:bg-primary-50 focus:ring-primary-500': 
          variant === 'ghost',
        
        // Outline - 边框按钮
        'border-2 border-primary-500 text-primary-600 hover:bg-primary-500 hover:text-white focus:ring-primary-500': 
          variant === 'outline',
      },
      
      // 全宽样式
      {
        'w-full': fullWidth,
      },
      
      className
    );

    const iconStyles = cn(
      'flex-shrink-0',
      {
        'w-4 h-4': size === 'sm',
        'w-5 h-5': size === 'md',
        'w-6 h-6': size === 'lg',
        'w-7 h-7': size === 'xl',
      }
    );

    const renderIcon = (iconNode: React.ReactNode) => (
      <span className={iconStyles}>
        {iconNode}
      </span>
    );

    const renderContent = () => {
      if (loading) {
        return (
          <>
            <Loader2 className={cn(iconStyles, 'animate-spin')} />
            {children && <span className="ml-2">{children}</span>}
          </>
        );
      }

      if (icon && iconPosition === 'left') {
        return (
          <>
            {renderIcon(icon)}
            {children && <span className="ml-2">{children}</span>}
          </>
        );
      }

      if (icon && iconPosition === 'right') {
        return (
          <>
            {children && <span className="mr-2">{children}</span>}
            {renderIcon(icon)}
          </>
        );
      }

      return children;
    };

    return (
      <button
        ref={ref}
        className={baseStyles}
        disabled={disabled || loading}
        {...props}
      >
        {/* 点击波纹效果 */}
        <span className="absolute inset-0 overflow-hidden rounded-inherit">
          <span className="absolute inset-0 rounded-inherit bg-white opacity-0 transition-opacity duration-300 hover:opacity-10" />
        </span>
        
        {/* 按钮内容 */}
        <span className="relative z-10 flex items-center">
          {renderContent()}
        </span>
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };