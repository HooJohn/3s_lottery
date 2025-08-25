import React from 'react';
import { cn } from '../../utils/cn';
import { Eye, EyeOff, AlertCircle, CheckCircle } from 'lucide-react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  success?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  variant?: 'default' | 'filled' | 'outlined';
  inputSize?: 'sm' | 'md' | 'lg';
  showPasswordToggle?: boolean;
  touchOptimized?: boolean; // 移动端触摸优化
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({
    className,
    type = 'text',
    label,
    error,
    success,
    helperText,
    leftIcon,
    rightIcon,
    variant = 'outlined',
    inputSize = 'md',
    showPasswordToggle = false,
    touchOptimized = true,
    disabled,
    ...props
  }, ref) => {
    const [showPassword, setShowPassword] = React.useState(false);
    const [isFocused, setIsFocused] = React.useState(false);
    
    const isPassword = type === 'password';
    const inputType = isPassword && showPassword ? 'text' : type;
    
    const inputId = React.useId();
    const errorId = React.useId();
    const helperId = React.useId();

    const containerStyles = cn(
      'relative w-full',
      {
        'opacity-50': disabled,
      }
    );

    const labelStyles = cn(
      'block text-sm font-semibold mb-2 transition-colors duration-200',
      {
        'text-gray-700': !error && !success,
        'text-danger-600': error,
        'text-success-600': success,
      }
    );

    const inputWrapperStyles = cn(
      'relative flex items-center transition-all duration-200',
      {
        // Default variant
        'border-b-2 bg-transparent': variant === 'default',
        'border-gray-300 focus-within:border-primary-500': variant === 'default' && !error && !success,
        'border-danger-500': variant === 'default' && error,
        'border-success-500': variant === 'default' && success,
        
        // Filled variant
        'bg-gray-50 border-b-2': variant === 'filled',
        'border-gray-300 focus-within:border-primary-500 focus-within:bg-white': variant === 'filled' && !error && !success,
        'border-danger-500 bg-danger-50': variant === 'filled' && error,
        'border-success-500 bg-success-50': variant === 'filled' && success,
        
        // Outlined variant
        'border-2 rounded-lg bg-white': variant === 'outlined',
        'border-gray-200 focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-100': 
          variant === 'outlined' && !error && !success,
        'border-danger-500 focus-within:ring-2 focus-within:ring-danger-100': 
          variant === 'outlined' && error,
        'border-success-500 focus-within:ring-2 focus-within:ring-success-100': 
          variant === 'outlined' && success,
      }
    );

    const inputStyles = cn(
      'w-full bg-transparent border-none outline-none transition-all duration-200',
      'placeholder:text-gray-400 text-gray-900',
      'disabled:cursor-not-allowed disabled:opacity-50',
      
      // 移动端触摸优化
      touchOptimized && [
        'touch-manipulation', // 优化触摸响应
        'text-base', // 防止iOS缩放
      ],
      
      {
        // 尺寸样式 - 移动端优化最小触摸目标
        'px-3 py-2 text-sm': inputSize === 'sm' && !touchOptimized,
        'px-4 py-3 text-sm min-h-[40px]': inputSize === 'sm' && touchOptimized,
        'px-4 py-3 text-base': inputSize === 'md' && !touchOptimized,
        'px-4 py-3 text-base min-h-[44px]': inputSize === 'md' && touchOptimized,
        'px-5 py-4 text-lg': inputSize === 'lg' && !touchOptimized,
        'px-5 py-4 text-lg min-h-[48px]': inputSize === 'lg' && touchOptimized,
        
        // 左图标间距
        'pl-10': leftIcon && inputSize === 'sm',
        'pl-12': leftIcon && inputSize === 'md',
        'pl-14': leftIcon && inputSize === 'lg',
        
        // 右图标间距
        'pr-10': (rightIcon || isPassword || error || success) && inputSize === 'sm',
        'pr-12': (rightIcon || isPassword || error || success) && inputSize === 'md',
        'pr-14': (rightIcon || isPassword || error || success) && inputSize === 'lg',
      },
      className
    );

    const iconStyles = cn(
      'absolute text-gray-400 transition-colors duration-200',
      {
        'w-4 h-4': inputSize === 'sm',
        'w-5 h-5': inputSize === 'md',
        'w-6 h-6': inputSize === 'lg',
      }
    );

    const leftIconStyles = cn(
      iconStyles,
      {
        'left-3': inputSize === 'sm',
        'left-4': inputSize === 'md',
        'left-5': inputSize === 'lg',
      }
    );

    const rightIconStyles = cn(
      iconStyles,
      {
        'right-3': inputSize === 'sm',
        'right-4': inputSize === 'md',
        'right-5': inputSize === 'lg',
      }
    );

    const messageStyles = cn(
      'mt-2 text-sm flex items-center gap-1',
      {
        'text-gray-600': !error && !success,
        'text-danger-600': error,
        'text-success-600': success,
      }
    );

    const renderRightIcon = () => {
      if (error) {
        return <AlertCircle className={cn(rightIconStyles, 'text-danger-500')} />;
      }
      
      if (success) {
        return <CheckCircle className={cn(rightIconStyles, 'text-success-500')} />;
      }
      
      if (isPassword && showPasswordToggle) {
        return (
          <button
            type="button"
            className={cn(rightIconStyles, 'cursor-pointer hover:text-gray-600')}
            onClick={() => setShowPassword(!showPassword)}
            tabIndex={-1}
          >
            {showPassword ? <EyeOff /> : <Eye />}
          </button>
        );
      }
      
      if (rightIcon) {
        return <span className={rightIconStyles}>{rightIcon}</span>;
      }
      
      return null;
    };

    return (
      <div className={containerStyles}>
        {label && (
          <label htmlFor={inputId} className={labelStyles}>
            {label}
            {props.required && <span className="text-danger-500 ml-1">*</span>}
          </label>
        )}
        
        <div className={inputWrapperStyles}>
          {leftIcon && (
            <span className={leftIconStyles}>
              {leftIcon}
            </span>
          )}
          
          <input
            ref={ref}
            id={inputId}
            type={inputType}
            className={inputStyles}
            disabled={disabled}
            onFocus={(e) => {
              setIsFocused(true);
              props.onFocus?.(e);
            }}
            onBlur={(e) => {
              setIsFocused(false);
              props.onBlur?.(e);
            }}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={cn(
              error && errorId,
              (helperText || success) && helperId
            )}
            {...props}
          />
          
          {renderRightIcon()}
        </div>
        
        {(error || success || helperText) && (
          <div
            id={error ? errorId : helperId}
            className={messageStyles}
            role={error ? 'alert' : 'status'}
          >
            {error && (
              <>
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </>
            )}
            {success && (
              <>
                <CheckCircle className="w-4 h-4 flex-shrink-0" />
                <span>{success}</span>
              </>
            )}
            {helperText && !error && !success && (
              <span>{helperText}</span>
            )}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };