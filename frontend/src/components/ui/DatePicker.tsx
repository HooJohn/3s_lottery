import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, X } from 'lucide-react';
import { cn } from '@/utils/cn';

interface DatePickerProps {
  value?: Date | null;
  onChange?: (date: Date | null) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  format?: string;
  minDate?: Date;
  maxDate?: Date;
  clearable?: boolean;
}

interface DateRangePickerProps {
  value?: [Date | null, Date | null];
  onChange?: (dates: [Date | null, Date | null]) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  format?: string;
  minDate?: Date;
  maxDate?: Date;
  clearable?: boolean;
}

// 日期格式化函数
const formatDate = (date: Date, format: string = 'YYYY-MM-DD'): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day);
};

// 获取月份的天数
const getDaysInMonth = (year: number, month: number): number => {
  return new Date(year, month + 1, 0).getDate();
};

// 获取月份第一天是星期几
const getFirstDayOfMonth = (year: number, month: number): number => {
  return new Date(year, month, 1).getDay();
};

// 检查日期是否相同
const isSameDay = (date1: Date | null, date2: Date | null): boolean => {
  if (!date1 || !date2) return false;
  return date1.toDateString() === date2.toDateString();
};

// 检查日期是否在范围内
const isDateInRange = (date: Date, start: Date | null, end: Date | null): boolean => {
  if (!start || !end) return false;
  return date >= start && date <= end;
};

// 日历组件
interface CalendarProps {
  selectedDate?: Date | null;
  selectedRange?: [Date | null, Date | null];
  onDateSelect: (date: Date) => void;
  minDate?: Date;
  maxDate?: Date;
  isRange?: boolean;
}

const Calendar: React.FC<CalendarProps> = ({
  selectedDate,
  selectedRange,
  onDateSelect,
  minDate,
  maxDate,
  isRange = false,
}) => {
  const [currentMonth, setCurrentMonth] = useState(
    selectedDate ? selectedDate.getMonth() : new Date().getMonth()
  );
  const [currentYear, setCurrentYear] = useState(
    selectedDate ? selectedDate.getFullYear() : new Date().getFullYear()
  );

  const monthNames = [
    '一月', '二月', '三月', '四月', '五月', '六月',
    '七月', '八月', '九月', '十月', '十一月', '十二月'
  ];

  const weekDays = ['日', '一', '二', '三', '四', '五', '六'];

  const daysInMonth = getDaysInMonth(currentYear, currentMonth);
  const firstDayOfMonth = getFirstDayOfMonth(currentYear, currentMonth);

  // 生成日历天数数组
  const calendarDays = [];
  
  // 上个月的天数（填充）
  const prevMonth = currentMonth === 0 ? 11 : currentMonth - 1;
  const prevYear = currentMonth === 0 ? currentYear - 1 : currentYear;
  const daysInPrevMonth = getDaysInMonth(prevYear, prevMonth);
  
  for (let i = firstDayOfMonth - 1; i >= 0; i--) {
    calendarDays.push({
      day: daysInPrevMonth - i,
      isCurrentMonth: false,
      date: new Date(prevYear, prevMonth, daysInPrevMonth - i),
    });
  }

  // 当前月的天数
  for (let day = 1; day <= daysInMonth; day++) {
    calendarDays.push({
      day,
      isCurrentMonth: true,
      date: new Date(currentYear, currentMonth, day),
    });
  }

  // 下个月的天数（填充到42天）
  const remainingDays = 42 - calendarDays.length;
  const nextMonth = currentMonth === 11 ? 0 : currentMonth + 1;
  const nextYear = currentMonth === 11 ? currentYear + 1 : currentYear;
  
  for (let day = 1; day <= remainingDays; day++) {
    calendarDays.push({
      day,
      isCurrentMonth: false,
      date: new Date(nextYear, nextMonth, day),
    });
  }

  const goToPrevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
  };

  const goToNextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
  };

  const isDateDisabled = (date: Date): boolean => {
    if (minDate && date < minDate) return true;
    if (maxDate && date > maxDate) return true;
    return false;
  };

  return (
    <div className="p-4 bg-white">
      {/* 月份导航 */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={goToPrevMonth}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        
        <h3 className="text-lg font-semibold">
          {currentYear}年 {monthNames[currentMonth]}
        </h3>
        
        <button
          onClick={goToNextMonth}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* 星期标题 */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {weekDays.map((day) => (
          <div
            key={day}
            className="h-8 flex items-center justify-center text-sm font-medium text-gray-500"
          >
            {day}
          </div>
        ))}
      </div>

      {/* 日期网格 */}
      <div className="grid grid-cols-7 gap-1">
        {calendarDays.map((calendarDay, index) => {
          const isSelected = isRange
            ? selectedRange && (
                isSameDay(calendarDay.date, selectedRange[0]) ||
                isSameDay(calendarDay.date, selectedRange[1])
              )
            : isSameDay(calendarDay.date, selectedDate);
          
          const isInRange = isRange && selectedRange
            ? isDateInRange(calendarDay.date, selectedRange[0], selectedRange[1])
            : false;

          const isDisabled = isDateDisabled(calendarDay.date);
          const isToday = isSameDay(calendarDay.date, new Date());

          return (
            <button
              key={index}
              onClick={() => !isDisabled && onDateSelect(calendarDay.date)}
              disabled={isDisabled}
              className={cn(
                'h-8 w-8 flex items-center justify-center text-sm rounded-lg transition-colors',
                'hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500',
                !calendarDay.isCurrentMonth && 'text-gray-400',
                isSelected && 'bg-primary-600 text-white hover:bg-primary-700',
                isInRange && !isSelected && 'bg-primary-100 text-primary-700',
                isToday && !isSelected && 'bg-gray-200 font-semibold',
                isDisabled && 'opacity-50 cursor-not-allowed hover:bg-transparent'
              )}
            >
              {calendarDay.day}
            </button>
          );
        })}
      </div>
    </div>
  );
};

// 单日期选择器
const DatePicker: React.FC<DatePickerProps> = ({
  value,
  onChange,
  placeholder = '选择日期',
  disabled = false,
  error,
  size = 'md',
  className,
  format = 'YYYY-MM-DD',
  minDate,
  maxDate,
  clearable = true,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const pickerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-base',
    lg: 'px-5 py-4 text-lg',
  };

  const handleDateSelect = (date: Date) => {
    onChange?.(date);
    setIsOpen(false);
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange?.(null);
  };

  return (
    <div ref={pickerRef} className={cn('relative', className)}>
      <div
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
          <div className="flex-1">
            {value ? (
              <span className="text-gray-900">{formatDate(value, format)}</span>
            ) : (
              <span className="text-gray-500">{placeholder}</span>
            )}
          </div>
          
          <div className="flex items-center gap-2 ml-2">
            {clearable && value && !disabled && (
              <button
                onClick={handleClear}
                className="text-gray-400 hover:text-gray-600 p-1"
              >
                <X className="w-4 h-4" />
              </button>
            )}
            <Calendar className="w-5 h-5 text-gray-400" />
          </div>
        </div>
      </div>

      {error && (
        <p className="mt-1 text-sm text-danger-600">{error}</p>
      )}

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full left-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-heavy z-50"
          >
            <Calendar
              selectedDate={value}
              onDateSelect={handleDateSelect}
              minDate={minDate}
              maxDate={maxDate}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// 日期范围选择器
export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  value,
  onChange,
  placeholder = '选择日期范围',
  disabled = false,
  error,
  size = 'md',
  className,
  format = 'YYYY-MM-DD',
  minDate,
  maxDate,
  clearable = true,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [tempRange, setTempRange] = useState<[Date | null, Date | null]>([null, null]);
  const pickerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setTempRange([null, null]);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-base',
    lg: 'px-5 py-4 text-lg',
  };

  const handleDateSelect = (date: Date) => {
    const [start, end] = tempRange;
    
    if (!start || (start && end)) {
      // 开始新的选择
      setTempRange([date, null]);
    } else {
      // 完成范围选择
      const newRange: [Date, Date] = start <= date ? [start, date] : [date, start];
      setTempRange([null, null]);
      onChange?.(newRange);
      setIsOpen(false);
    }
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange?.([null, null]);
    setTempRange([null, null]);
  };

  const displayValue = () => {
    if (value && value[0] && value[1]) {
      return `${formatDate(value[0], format)} - ${formatDate(value[1], format)}`;
    }
    return placeholder;
  };

  const currentRange = tempRange[0] ? tempRange : value;

  return (
    <div ref={pickerRef} className={cn('relative', className)}>
      <div
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
          <div className="flex-1">
            <span className={cn(
              value && value[0] && value[1] ? 'text-gray-900' : 'text-gray-500'
            )}>
              {displayValue()}
            </span>
          </div>
          
          <div className="flex items-center gap-2 ml-2">
            {clearable && value && value[0] && value[1] && !disabled && (
              <button
                onClick={handleClear}
                className="text-gray-400 hover:text-gray-600 p-1"
              >
                <X className="w-4 h-4" />
              </button>
            )}
            <Calendar className="w-5 h-5 text-gray-400" />
          </div>
        </div>
      </div>

      {error && (
        <p className="mt-1 text-sm text-danger-600">{error}</p>
      )}

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full left-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-heavy z-50"
          >
            <Calendar
              selectedRange={currentRange}
              onDateSelect={handleDateSelect}
              minDate={minDate}
              maxDate={maxDate}
              isRange={true}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DatePicker;