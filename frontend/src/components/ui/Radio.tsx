import React from 'react';
import { cn } from '@/utils/cn';

interface RadioProps {
  checked?: boolean;
  onChange?: (value: string) => void;
  disabled?: boolean;
  label?: string;
  description?: string;
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  className?: string;
  labelClassName?: string;
  id?: string;
  name?: string;
  value: string;
}

const Radio: React.FC<RadioProps> = ({
  checked = false,
  onChange,
  disabled = false,
  label,
  description,
  size = 'md',
  color = 'primary',
  className,
  labelClassName,
  id,
  name,
  value,
}) => {
  const radioId = id || `radio-${Math.random().toString(36).substr(2, 9)}`;

  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  const colorClasses = {
    primary: 'text-primary-600 focus:ring-primary-500 border-primary-300',
    secondary: 'text-secondary-600 focus:ring-secondary-500 border-secondary-300',
    success: 'text-success-600 focus:ring-success-500 border-success-300',
    warning: 'text-warning-600 focus:ring-warning-500 border-warning-300',
    danger: 'text-danger-600 focus:ring-danger-500 border-danger-300',
  };

  const dotSize = {
    sm: 'w-2 h-2',
    md: 'w-2.5 h-2.5',
    lg: 'w-3 h-3',
  };

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(event.target.value);
    }
  };

  return (
    <div className={cn('flex items-start space-x-3', className)}>
      <div className="flex items-center">
        <div className="relative">
          <input
            id={radioId}
            name={name}
            value={value}
            type="radio"
            checked={checked}
            onChange={handleChange}
            disabled={disabled}
            className={cn(
              'rounded-full border-gray-300 transition-colors duration-200',
              'focus:ring-2 focus:ring-offset-2',
              sizeClasses[size],
              colorClasses[color],
              disabled && 'opacity-50 cursor-not-allowed',
              'cursor-pointer'
            )}
          />
          
          {/* 自定义单选框外观 */}
          <div
            className={cn(
              'absolute inset-0 flex items-center justify-center pointer-events-none',
              'rounded-full transition-all duration-200',
              sizeClasses[size],
              checked
                ? `bg-${color}-600 border-${color}-600`
                : 'bg-white border-gray-300',
              disabled && 'opacity-50'
            )}
          >
            {checked && (
              <div
                className={cn(
                  'rounded-full bg-white',
                  dotSize[size]
                )}
              />
            )}
          </div>
        </div>
      </div>

      {(label || description) && (
        <div className="flex-1">
          {label && (
            <label
              htmlFor={radioId}
              className={cn(
                'block text-sm font-medium text-gray-900 cursor-pointer',
                disabled && 'opacity-50 cursor-not-allowed',
                labelClassName
              )}
            >
              {label}
            </label>
          )}
          {description && (
            <p className={cn(
              'text-sm text-gray-500 mt-1',
              disabled && 'opacity-50'
            )}>
              {description}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

// 单选框组组件
interface RadioGroupProps {
  options: Array<{
    value: string;
    label: string;
    description?: string;
    disabled?: boolean;
  }>;
  value?: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  className?: string;
  name: string;
  direction?: 'horizontal' | 'vertical';
}

export const RadioGroup: React.FC<RadioGroupProps> = ({
  options,
  value,
  onChange,
  disabled = false,
  size = 'md',
  color = 'primary',
  className,
  name,
  direction = 'vertical',
}) => {
  const handleChange = (optionValue: string) => {
    if (onChange) {
      onChange(optionValue);
    }
  };

  return (
    <div
      className={cn(
        'space-y-3',
        direction === 'horizontal' && 'flex flex-wrap gap-4 space-y-0',
        className
      )}
      role="radiogroup"
    >
      {options.map((option) => (
        <Radio
          key={option.value}
          checked={value === option.value}
          onChange={handleChange}
          disabled={disabled || option.disabled}
          label={option.label}
          description={option.description}
          size={size}
          color={color}
          name={name}
          value={option.value}
        />
      ))}
    </div>
  );
};

export default Radio;