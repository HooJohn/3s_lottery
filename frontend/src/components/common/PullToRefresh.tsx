import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, ArrowDown } from 'lucide-react';
import { cn } from '@/utils/cn';

interface PullToRefreshProps {
  onRefresh: () => Promise<void>;
  children: React.ReactNode;
  threshold?: number;
  disabled?: boolean;
  className?: string;
}

const PullToRefresh: React.FC<PullToRefreshProps> = ({
  onRefresh,
  children,
  threshold = 80,
  disabled = false,
  className,
}) => {
  const [pullDistance, setPullDistance] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [canRefresh, setCanRefresh] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const startY = useRef(0);
  const currentY = useRef(0);

  const handleTouchStart = (e: TouchEvent) => {
    if (disabled || isRefreshing) return;
    
    const container = containerRef.current;
    if (!container || container.scrollTop > 0) return;

    startY.current = e.touches[0].clientY;
  };

  const handleTouchMove = (e: TouchEvent) => {
    if (disabled || isRefreshing) return;
    
    const container = containerRef.current;
    if (!container || container.scrollTop > 0) return;

    currentY.current = e.touches[0].clientY;
    const distance = Math.max(0, currentY.current - startY.current);
    
    if (distance > 0) {
      e.preventDefault();
      const dampedDistance = Math.min(distance * 0.5, threshold * 1.5);
      setPullDistance(dampedDistance);
      setCanRefresh(dampedDistance >= threshold);
    }
  };

  const handleTouchEnd = async () => {
    if (disabled || isRefreshing) return;

    if (canRefresh && pullDistance >= threshold) {
      setIsRefreshing(true);
      try {
        await onRefresh();
      } catch (error) {
        console.error('Refresh failed:', error);
      } finally {
        setIsRefreshing(false);
      }
    }
    
    setPullDistance(0);
    setCanRefresh(false);
  };

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener('touchstart', handleTouchStart, { passive: true });
    container.addEventListener('touchmove', handleTouchMove, { passive: false });
    container.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
    };
  }, [canRefresh, pullDistance, threshold, disabled, isRefreshing]);

  const refreshProgress = Math.min(pullDistance / threshold, 1);
  const showRefreshIndicator = pullDistance > 10 || isRefreshing;

  return (
    <div
      ref={containerRef}
      className={cn('relative overflow-auto', className)}
      style={{
        transform: `translateY(${Math.min(pullDistance * 0.3, 30)}px)`,
        transition: pullDistance === 0 ? 'transform 0.3s ease-out' : 'none',
      }}
    >
      {/* 下拉刷新指示器 */}
      <AnimatePresence>
        {showRefreshIndicator && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="absolute top-0 left-0 right-0 z-10 flex items-center justify-center py-4"
            style={{
              transform: `translateY(-${Math.max(0, 60 - pullDistance)}px)`,
            }}
          >
            <div className="flex items-center space-x-2 px-4 py-2 bg-white rounded-full shadow-lg border border-gray-200">
              {isRefreshing ? (
                <>
                  <RefreshCw className="w-4 h-4 text-primary-500 animate-spin" />
                  <span className="text-sm text-gray-600">刷新中...</span>
                </>
              ) : (
                <>
                  <motion.div
                    animate={{ rotate: canRefresh ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ArrowDown className="w-4 h-4 text-primary-500" />
                  </motion.div>
                  <span className="text-sm text-gray-600">
                    {canRefresh ? '松开刷新' : '下拉刷新'}
                  </span>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 进度指示器 */}
      {pullDistance > 0 && !isRefreshing && (
        <div className="absolute top-0 left-0 right-0 h-1 bg-gray-100">
          <div
            className="h-full bg-gradient-primary transition-all duration-100"
            style={{ width: `${refreshProgress * 100}%` }}
          />
        </div>
      )}

      {/* 内容区域 */}
      <div className="relative z-0">
        {children}
      </div>
    </div>
  );
};

export default PullToRefresh;