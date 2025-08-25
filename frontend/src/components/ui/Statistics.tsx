import React, { useState, useEffect, useRef } from 'react';
import { motion, useAnimation, AnimatePresence } from 'framer-motion';
import { cn } from '@/utils/cn';
import { Card } from './Card';
import { ArrowUp, ArrowDown, ArrowRight, TrendingUp, TrendingDown, Minus } from 'lucide-react';

// 统计数据项接口
export interface StatisticProps {
  title: React.ReactNode;
  value: number | string;
  precision?: number;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
  loading?: boolean;
  formatter?: (value: number | string) => React.ReactNode;
  decimalSeparator?: string;
  groupSeparator?: string;
  className?: string;
  style?: React.CSSProperties;
  valueStyle?: React.CSSProperties;
  titleStyle?: React.CSSProperties;
  animation?: boolean;
  animationDuration?: number;
  animationDelay?: number;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: number | string;
  trendPercentage?: number;
  trendColor?: boolean;
  icon?: React.ReactNode;
  description?: React.ReactNode;
  onClick?: () => void;
  size?: 'small' | 'medium' | 'large';
  status?: 'default' | 'success' | 'warning' | 'danger';
  layout?: 'horizontal' | 'vertical';
}

// 统计数据组件
export const Statistic: React.FC<StatisticProps> = ({
  title,
  value,
  precision,
  prefix,
  suffix,
  loading = false,
  formatter,
  decimalSeparator = '.',
  groupSeparator = ',',
  className,
  style,
  valueStyle,
  titleStyle,
  animation = true,
  animationDuration = 1000,
  animationDelay = 0,
  trend,
  trendValue,
  trendPercentage,
  trendColor = true,
  icon,
  description,
  onClick,
  size = 'medium',
  status = 'default',
  layout = 'vertical',
}) => {
  const [displayValue, setDisplayValue] = useState<number | string>(0);
  const prevValueRef = useRef<number | string>(0);
  const controls = useAnimation();
  
  // 格式化数值
  const formatValue = (val: number | string): string => {
    if (formatter) {
      return formatter(val).toString();
    }
    
    if (typeof val === 'string') {
      return val;
    }
    
    // 处理数字格式化
    const numValue = Number(val);
    if (isNaN(numValue)) {
      return val.toString();
    }
    
    // 处理精度
    const fixedValue = precision !== undefined
      ? numValue.toFixed(precision)
      : numValue.toString();
    
    // 分割整数和小数部分
    const [integerPart, decimalPart] = fixedValue.split('.');
    
    // 添加千位分隔符
    const formattedInteger = integerPart.replace(
      /\B(?=(\d{3})+(?!\d))/g,
      groupSeparator
    );
    
    // 组合整数和小数部分
    return decimalPart !== undefined
      ? `${formattedInteger}${decimalSeparator}${decimalPart}`
      : formattedInteger;
  };

  // 处理数值动画
  useEffect(() => {
    if (!animation || loading) {
      setDisplayValue(value);
      return;
    }
    
    const prevValue = prevValueRef.current;
    prevValueRef.current = value;
    
    // 如果是字符串或不是数字，直接设置
    if (typeof value === 'string' || typeof prevValue === 'string' || isNaN(Number(value)) || isNaN(Number(prevValue))) {
      setDisplayValue(value);
      return;
    }
    
    const startValue = Number(prevValue) || 0;
    const endValue = Number(value);
    const duration = animationDuration;
    const frameRate = 1000 / 60; // 60fps
    const totalFrames = Math.round(duration / frameRate);
    const valueIncrement = (endValue - startValue) / totalFrames;
    
    let currentFrame = 0;
    let currentValue = startValue;
    
    // 延迟开始动画
    const delayTimeout = setTimeout(() => {
      const animationInterval = setInterval(() => {
        currentFrame++;
        currentValue += valueIncrement;
        
        if (currentFrame >= totalFrames) {
          clearInterval(animationInterval);
          setDisplayValue(endValue);
        } else {
          setDisplayValue(currentValue);
        }
      }, frameRate);
      
      return () => clearInterval(animationInterval);
    }, animationDelay);
    
    return () => clearTimeout(delayTimeout);
  }, [value, animation, animationDuration, animationDelay, loading]);

  // 处理进入动画
  useEffect(() => {
    if (!loading) {
      controls.start({
        opacity: 1,
        y: 0,
        transition: { duration: 0.5, delay: animationDelay / 1000 }
      });
    }
  }, [controls, loading, animationDelay]);

  // 获取趋势颜色
  const getTrendColor = () => {
    if (!trendColor) return undefined;
    
    if (trend === 'up') return 'text-success-600';
    if (trend === 'down') return 'text-danger-600';
    return 'text-gray-500';
  };

  // 获取状态颜色
  const getStatusColor = () => {
    switch (status) {
      case 'success':
        return 'text-success-600';
      case 'warning':
        return 'text-warning-600';
      case 'danger':
        return 'text-danger-600';
      default:
        return '';
    }
  };

  // 获取尺寸类
  const getSizeClasses = () => {
    switch (size) {
      case 'small':
        return {
          title: 'text-xs',
          value: 'text-lg',
          trend: 'text-xs',
        };
      case 'large':
        return {
          title: 'text-base',
          value: 'text-4xl',
          trend: 'text-base',
        };
      default:
        return {
          title: 'text-sm',
          value: 'text-2xl',
          trend: 'text-sm',
        };
    }
  };

  const sizeClasses = getSizeClasses();

  // 渲染趋势指示器
  const renderTrendIndicator = () => {
    if (!trend) return null;
    
    const trendIcon = trend === 'up' ? (
      <TrendingUp className="w-4 h-4" />
    ) : trend === 'down' ? (
      <TrendingDown className="w-4 h-4" />
    ) : (
      <Minus className="w-4 h-4" />
    );
    
    return (
      <div className={cn(
        'flex items-center space-x-1',
        sizeClasses.trend,
        getTrendColor()
      )}>
        {trendIcon}
        {trendPercentage !== undefined && (
          <span>{Math.abs(trendPercentage)}%</span>
        )}
        {trendValue !== undefined && !trendPercentage && (
          <span>{trendValue}</span>
        )}
      </div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={controls}
      className={cn(
        'group',
        onClick && 'cursor-pointer hover:shadow-md transition-shadow duration-200',
        className
      )}
      style={style}
      onClick={onClick}
    >
      <div className={cn(
        'flex',
        layout === 'horizontal' ? 'flex-row items-center space-x-4' : 'flex-col space-y-2'
      )}>
        {/* 图标 */}
        {icon && (
          <div className="flex-shrink-0">
            {icon}
          </div>
        )}
        
        <div className="flex-1">
          {/* 标题 */}
          <div
            className={cn(
              'text-gray-500 font-medium',
              sizeClasses.title
            )}
            style={titleStyle}
          >
            {title}
          </div>
          
          {/* 数值和趋势 */}
          <div className="flex items-end space-x-2">
            <div
              className={cn(
                'font-semibold',
                sizeClasses.value,
                getStatusColor(),
                loading && 'animate-pulse'
              )}
              style={valueStyle}
            >
              {prefix && <span className="mr-1">{prefix}</span>}
              {loading ? (
                <div className="h-6 w-16 bg-gray-200 rounded animate-pulse"></div>
              ) : (
                <AnimatePresence mode="wait">
                  <motion.span
                    key={value.toString()}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                  >
                    {formatValue(displayValue)}
                  </motion.span>
                </AnimatePresence>
              )}
              {suffix && <span className="ml-1">{suffix}</span>}
            </div>
            
            {renderTrendIndicator()}
          </div>
          
          {/* 描述 */}
          {description && (
            <div className="text-xs text-gray-500 mt-1">
              {description}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// 统计数据组接口
export interface StatisticsGroupProps {
  children: React.ReactNode;
  title?: React.ReactNode;
  layout?: 'grid' | 'flex';
  columns?: number;
  gutter?: number | [number, number];
  bordered?: boolean;
  className?: string;
  style?: React.CSSProperties;
  loading?: boolean;
}

// 统计数据组组件
export const StatisticsGroup: React.FC<StatisticsGroupProps> = ({
  children,
  title,
  layout = 'grid',
  columns = 4,
  gutter = 16,
  bordered = false,
  className,
  style,
  loading = false,
}) => {
  // 处理间距
  const [horizontalGutter, verticalGutter] = Array.isArray(gutter)
    ? gutter
    : [gutter, gutter];

  return (
    <Card
      className={cn(
        bordered && 'border border-gray-200',
        className
      )}
      style={style}
    >
      {title && (
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
      )}
      
      <div className="p-6">
        <div
          className={cn(
            layout === 'grid'
              ? 'grid gap-x-4 gap-y-6'
              : 'flex flex-wrap'
          )}
          style={{
            gridTemplateColumns: layout === 'grid' ? `repeat(${columns}, minmax(0, 1fr))` : undefined,
            gap: layout === 'grid' ? `${verticalGutter}px ${horizontalGutter}px` : undefined,
            margin: layout === 'flex' ? `-${verticalGutter / 2}px -${horizontalGutter / 2}px` : undefined,
          }}
        >
          {React.Children.map(children, (child, index) => {
            if (!React.isValidElement(child)) return child;
            
            return layout === 'grid' ? (
              React.cloneElement(child, {
                loading: loading || child.props.loading,
                animationDelay: index * 100,
              })
            ) : (
              <div
                style={{
                  padding: `${verticalGutter / 2}px ${horizontalGutter / 2}px`,
                  width: `${100 / columns}%`,
                }}
              >
                {React.cloneElement(child, {
                  loading: loading || child.props.loading,
                  animationDelay: index * 100,
                })}
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
};

// 计数器组件
export interface CounterProps {
  start?: number;
  end: number;
  duration?: number;
  delay?: number;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
  separator?: string;
  decimals?: number;
  decimal?: string;
  className?: string;
  style?: React.CSSProperties;
  onComplete?: () => void;
}

export const Counter: React.FC<CounterProps> = ({
  start = 0,
  end,
  duration = 2000,
  delay = 0,
  prefix,
  suffix,
  separator = ',',
  decimals = 0,
  decimal = '.',
  className,
  style,
  onComplete,
}) => {
  const [count, setCount] = useState(start);
  const countRef = useRef(start);
  
  useEffect(() => {
    let startTime: number;
    let animationFrame: number;
    const startValue = countRef.current;
    const endValue = end;
    
    const updateCount = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = timestamp - startTime;
      const percentage = Math.min(progress / duration, 1);
      
      // 使用缓动函数使动画更自然
      const easeOutQuart = 1 - Math.pow(1 - percentage, 4);
      const currentCount = startValue + (endValue - startValue) * easeOutQuart;
      
      setCount(currentCount);
      countRef.current = currentCount;
      
      if (percentage < 1) {
        animationFrame = requestAnimationFrame(updateCount);
      } else {
        setCount(endValue);
        countRef.current = endValue;
        onComplete?.();
      }
    };
    
    const delayTimeout = setTimeout(() => {
      animationFrame = requestAnimationFrame(updateCount);
    }, delay);
    
    return () => {
      clearTimeout(delayTimeout);
      cancelAnimationFrame(animationFrame);
    };
  }, [end, duration, delay, onComplete]);
  
  // 格式化数字
  const formatNumber = (num: number): string => {
    const fixedNumber = num.toFixed(decimals);
    const [integerPart, decimalPart] = fixedNumber.split('.');
    
    // 添加千位分隔符
    const formattedInteger = integerPart.replace(
      /\B(?=(\d{3})+(?!\d))/g,
      separator
    );
    
    // 组合整数和小数部分
    return decimalPart !== undefined
      ? `${formattedInteger}${decimal}${decimalPart}`
      : formattedInteger;
  };
  
  return (
    <span className={className} style={style}>
      {prefix}
      {formatNumber(count)}
      {suffix}
    </span>
  );
};

// 导出组件
export { Statistic as Statistics };