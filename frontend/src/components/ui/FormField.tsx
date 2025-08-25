import React from 'react';
import { cn } from '@/utils/cn';

interface FormFieldProps {
  label?: string;
  error?: string;
  hint?: string;
  required?: boolean;
  children: React.ReactNode;
  className?: string;
  labelClassName?: string;
  errorClassName?: string;
  hintClassName?: string;
  id?: string;
}

const FormField: React.FC<FormFieldProps> = ({
  label,
  error,
  hint,
  required = false,
  children,
  className,
  labelClassName,
  errorClassName,
  hintClassName,
  id,
}) => {
  const fieldId = id || `field-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className={cn('space-y-2', className)}>
      {/* 标签 */}
      {label && (
        <label
          htmlFor={fieldId}
          className={cn(
            'block text-sm font-medium text-gray-700',
            'transition-colors duration-200',
            error && 'text-danger-600',
            labelClassName
          )}
        >
          {label}
          {required && (
            <span className="ml-1 text-danger-500" aria-label="必填">
              *
            </span>
          )}
        </label>
      )}

      {/* 输入控件 */}
      <div className="relative">
        {React.cloneElement(children as React.ReactElement, {
          id: fieldId,
          'aria-invalid': !!error,
          'aria-describedby': error ? `${fieldId}-error` : hint ? `${fieldId}-hint` : undefined,
          className: cn(
            (children as React.ReactElement).props.className,
            error && 'border-danger-300 focus:border-danger-500 focus:ring-danger-500'
          ),
        })}
      </div>

      {/* 提示文本 */}
      {hint && !error && (
        <p
          id={`${fieldId}-hint`}
          className={cn(
            'text-sm text-gray-500',
            hintClassName
          )}
        >
          {hint}
        </p>
      )}

      {/* 错误信息 */}
      {error && (
        <p
          id={`${fieldId}-error`}
          className={cn(
            'text-sm text-danger-600',
            'flex items-center space-x-1',
            errorClassName
          )}
          role="alert"
        >
          <svg
            className="w-4 h-4 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <span>{error}</span>
        </p>
      )}
    </div>
  );
};

export default FormField;