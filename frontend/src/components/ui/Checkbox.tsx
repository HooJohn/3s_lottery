import React from 'react';
import { Check, Minus } from 'lucide-react';
import { cn } from '@/utils/cn';

interface CheckboxProps {
  checked?: boolean;
  indeterminate?: boolean;
  onChange?: (checked: boolean) => void;
  disabled?: boolean;
  label?: string;
  description?: string;
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  className?: string;
  labelClassName?: string;
  id?: string;
  name?: string;
  value?: string;
}

const Checkbox: React.FC<CheckboxProps> = ({
  checked = false,
  indeterminate = false,
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
  const checkboxId = id || `checkbox-${Math.random().toString(36).substr(2, 9)}`;

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

  const iconSize = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(event.target.checked);
    }
  };

  return (
    <div className={cn('flex items-start space-x-3', className)}>
      <div className="flex items-center">
        <div className="relative">
          <input
            id={checkboxId}
            name={name}
            value={value}
            type="checkbox"
            checked={checked}
            onChange={handleChange}
            disabled={disabled}
            className={cn(
              'rounded border-gray-300 transition-colors duration-200',
              'focus:ring-2 focus:ring-offset-2',
              sizeClasses[size],
              colorClasses[color],
              disabled && 'opacity-50 cursor-not-allowed',
              'cursor-pointer'
            )}
          />
          
          {/* 自定义复选框外观 */}
          <div
            className={cn(
              'absolute inset-0 flex items-center justify-center pointer-events-none',
              'rounded transition-all duration-200',
              sizeClasses[size],
              checked || indeterminate
                ? `bg-${color}-600 border-${color}-600`
                : 'bg-white border-gray-300',
              disabled && 'opacity-50'
            )}
          >
            {indeterminate ? (
              <Minus className={cn('text-white', iconSize[size])} />
            ) : checked ? (
              <Check className={cn('text-white', iconSize[size])} />
            ) : null}
          </div>
        </div>
      </div>

      {(label || description) && (
        <div className="flex-1">
          {label && (
            <label
              htmlFor={checkboxId}
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

// 复选框组组件
interface CheckboxGroupProps {
  options: Array<{
    value: string;
    label: string;
    description?: string;
    disabled?: boolean;
  }>;
  value?: string[];
  onChange?: (value: string[]) => void;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  className?: string;
  name?: string;
  direction?: 'horizontal' | 'vertical';
}

export const CheckboxGroup: React.FC<CheckboxGroupProps> = ({
  options,
  value = [],
  onChange,
  disabled = false,
  size = 'md',
  color = 'primary',
  className,
  name,
  direction = 'vertical',
}) => {
  const handleChange = (optionValue: string, checked: boolean) => {
    if (!onChange) return;

    if (checked) {
      onChange([...value, optionValue]);
    } else {
      onChange(value.filter(v => v !== optionValue));
    }
  };

  return (
    <div
      className={cn(
        'space-y-3',
        direction === 'horizontal' && 'flex flex-wrap gap-4 space-y-0',
        className
      )}
    >
      {options.map((option) => (
        <Checkbox
          key={option.value}
          checked={value.includes(option.value)}
          onChange={(checked) => handleChange(option.value, checked)}
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

export default Checkbox;