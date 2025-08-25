import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Check, Search, X } from 'lucide-react';
import { cn } from '../../utils/cn';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
  icon?: React.ReactNode;
  description?: string;
}

export interface SelectProps {
  options: SelectOption[];
  value?: string | string[];
  defaultValue?: string | string[];
  placeholder?: string;
  multiple?: boolean;
  searchable?: boolean;
  clearable?: boolean;
  disabled?: boolean;
  error?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  onChange?: (value: string | string[]) => void;
  onSearch?: (query: string) => void;
}

const Select = React.forwardRef<HTMLDivElement, SelectProps>(
  ({
    options,
    value,
    defaultValue,
    placeholder = '请选择...',
    multiple = false,
    searchable = false,
    clearable = false,
    disabled = false,
    error,
    size = 'md',
    className,
    onChange,
    onSearch,
  }, ref) => {
    const [isOpen, setIsOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedValue, setSelectedValue] = useState<string | string[]>(
      value || defaultValue || (multiple ? [] : '')
    );
    
    const selectRef = useRef<HTMLDivElement>(null);
    const searchInputRef = useRef<HTMLInputElement>(null);

    // 同步外部value变化
    useEffect(() => {
      if (value !== undefined) {
        setSelectedValue(value);
      }
    }, [value]);

    // 点击外部关闭下拉菜单
    useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
          setIsOpen(false);
          setSearchQuery('');
        }
      };

      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // 过滤选项
    const filteredOptions = searchable && searchQuery
      ? options.filter(option =>
          option.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
          option.value.toLowerCase().includes(searchQuery.toLowerCase())
        )
      : options;

    // 获取选中的选项
    const getSelectedOptions = () => {
      if (multiple && Array.isArray(selectedValue)) {
        return options.filter(option => selectedValue.includes(option.value));
      } else if (!multiple && typeof selectedValue === 'string') {
        return options.find(option => option.value === selectedValue);
      }
      return null;
    };

    // 处理选项点击
    const handleOptionClick = (option: SelectOption) => {
      if (option.disabled) return;

      let newValue: string | string[];

      if (multiple) {
        const currentValues = Array.isArray(selectedValue) ? selectedValue : [];
        if (currentValues.includes(option.value)) {
          newValue = currentValues.filter(v => v !== option.value);
        } else {
          newValue = [...currentValues, option.value];
        }
      } else {
        newValue = option.value;
        setIsOpen(false);
        setSearchQuery('');
      }

      setSelectedValue(newValue);
      onChange?.(newValue);
    };

    // 清空选择
    const handleClear = (e: React.MouseEvent) => {
      e.stopPropagation();
      const newValue = multiple ? [] : '';
      setSelectedValue(newValue);
      onChange?.(newValue);
    };

    // 移除单个选项（多选模式）
    const handleRemoveOption = (optionValue: string, e: React.MouseEvent) => {
      e.stopPropagation();
      if (multiple && Array.isArray(selectedValue)) {
        const newValue = selectedValue.filter(v => v !== optionValue);
        setSelectedValue(newValue);
        onChange?.(newValue);
      }
    };

    // 处理搜索
    const handleSearch = (query: string) => {
      setSearchQuery(query);
      onSearch?.(query);
    };

    // 样式类
    const sizeClasses = {
      sm: 'px-3 py-2 text-sm',
      md: 'px-4 py-3 text-base',
      lg: 'px-5 py-4 text-lg',
    };

    const selectedOptions = getSelectedOptions();
    const hasValue = multiple 
      ? Array.isArray(selectedValue) && selectedValue.length > 0
      : selectedValue !== '';

    return (
      <div ref={ref} className={cn('relative', className)}>
        <div
          ref={selectRef}
          onClick={() => !disabled && setIsOpen(!isOpen)}
          className={cn(
            'relative w-full border-2 rounded-lg cursor-pointer transition-all duration-200',
            'focus-within:ring-2 focus-within:ring-primary-100',
            sizeClasses[size],
            disabled
              ? 'bg-gray-50 border-gray-200 cursor-not-allowed'
              : isOpen
              ? 'border-primary-500 bg-white'
              : error
              ? 'border-danger-500 bg-white hover:border-danger-600'
              : 'border-gray-200 bg-white hover:border-gray-300'
          )}
        >
          <div className="flex items-center justify-between">
            <div className="flex-1 flex items-center gap-2 min-w-0">
              {/* 显示选中的值 */}
              {hasValue ? (
                multiple && Array.isArray(selectedOptions) ? (
                  <div className="flex flex-wrap gap-1">
                    {selectedOptions.map((option) => (
                      <span
                        key={option.value}
                        className="inline-flex items-center gap-1 px-2 py-1 bg-primary-100 text-primary-800 text-sm rounded-md"
                      >
                        {option.icon && <span className="w-4 h-4">{option.icon}</span>}
                        <span>{option.label}</span>
                        <button
                          onClick={(e) => handleRemoveOption(option.value, e)}
                          className="hover:bg-primary-200 rounded-full p-0.5"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                ) : (
                  selectedOptions && typeof selectedOptions === 'object' && (
                    <div className="flex items-center gap-2">
                      {selectedOptions.icon && (
                        <span className="w-5 h-5">{selectedOptions.icon}</span>
                      )}
                      <span className="truncate">{selectedOptions.label}</span>
                    </div>
                  )
                )
              ) : (
                <span className="text-gray-500 truncate">{placeholder}</span>
              )}
            </div>

            {/* 右侧图标 */}
            <div className="flex items-center gap-2 ml-2">
              {clearable && hasValue && !disabled && (
                <button
                  onClick={handleClear}
                  className="text-gray-400 hover:text-gray-600 p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
              <ChevronDown
                className={cn(
                  'w-5 h-5 text-gray-400 transition-transform duration-200',
                  isOpen && 'rotate-180'
                )}
              />
            </div>
          </div>
        </div>

        {/* 错误信息 */}
        {error && (
          <p className="mt-1 text-sm text-danger-600">{error}</p>
        )}

        {/* 下拉菜单 */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-heavy z-50 max-h-60 overflow-hidden"
            >
              {/* 搜索框 */}
              {searchable && (
                <div className="p-3 border-b border-gray-100">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      ref={searchInputRef}
                      type="text"
                      value={searchQuery}
                      onChange={(e) => handleSearch(e.target.value)}
                      placeholder="搜索选项..."
                      className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                </div>
              )}

              {/* 选项列表 */}
              <div className="max-h-48 overflow-y-auto">
                {filteredOptions.length > 0 ? (
                  filteredOptions.map((option) => {
                    const isSelected = multiple
                      ? Array.isArray(selectedValue) && selectedValue.includes(option.value)
                      : selectedValue === option.value;

                    return (
                      <button
                        key={option.value}
                        onClick={() => handleOptionClick(option)}
                        disabled={option.disabled}
                        className={cn(
                          'w-full flex items-center justify-between px-4 py-3 text-left transition-colors duration-200',
                          'hover:bg-gray-50 focus:outline-none focus:bg-gray-50',
                          option.disabled
                            ? 'text-gray-400 cursor-not-allowed'
                            : isSelected
                            ? 'bg-primary-50 text-primary-700'
                            : 'text-gray-700'
                        )}
                      >
                        <div className="flex items-center gap-3 min-w-0 flex-1">
                          {option.icon && (
                            <span className="w-5 h-5 flex-shrink-0">{option.icon}</span>
                          )}
                          <div className="min-w-0 flex-1">
                            <div className="font-medium truncate">{option.label}</div>
                            {option.description && (
                              <div className="text-sm text-gray-500 truncate">
                                {option.description}
                              </div>
                            )}
                          </div>
                        </div>

                        {isSelected && (
                          <Check className="w-4 h-4 text-primary-600 flex-shrink-0" />
                        )}
                      </button>
                    );
                  })
                ) : (
                  <div className="px-4 py-8 text-center text-gray-500">
                    {searchQuery ? '未找到匹配的选项' : '暂无选项'}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }
);

Select.displayName = 'Select';

export { Select };