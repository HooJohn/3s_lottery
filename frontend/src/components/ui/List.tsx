import React, { useState, useRef, useEffect, useCallback } from 'react';
import { cn } from '@/utils/cn';
import { ChevronRight } from 'lucide-react';

export interface ListProps<T> {
  dataSource: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  rowKey?: string | ((item: T) => string);
  header?: React.ReactNode;
  footer?: React.ReactNode;
  bordered?: boolean;
  size?: 'small' | 'medium' | 'large';
  split?: boolean;
  loading?: boolean;
  loadingText?: React.ReactNode;
  emptyText?: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  itemClassName?: string | ((item: T, index: number) => string);
  itemStyle?: React.CSSProperties | ((item: T, index: number) => React.CSSProperties);
  onItemClick?: (item: T, index: number) => void;
  grid?: {
    gutter?: number;
    column?: number;
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  pagination?: {
    pageSize?: number;
    current?: number;
    total?: number;
    onChange?: (page: number) => void;
  };
  virtual?: boolean;
  itemHeight?: number;
  height?: number;
  infiniteScroll?: boolean;
  hasMore?: boolean;
  loadMore?: () => void;
  loadingMore?: boolean;
  loadingMoreText?: React.ReactNode;
  endMessage?: React.ReactNode;
  threshold?: number;
}

function List<T>({
  dataSource,
  renderItem,
  rowKey = 'id',
  header,
  footer,
  bordered = false,
  size = 'medium',
  split = true,
  loading = false,
  loadingText = '加载中...',
  emptyText = '暂无数据',
  className,
  style,
  itemClassName,
  itemStyle,
  onItemClick,
  grid,
  pagination,
  virtual = false,
  itemHeight = 40,
  height = 400,
  infiniteScroll = false,
  hasMore = false,
  loadMore,
  loadingMore = false,
  loadingMoreText = '加载更多...',
  endMessage = '已经到底了',
  threshold = 250,
}: ListProps<T>) {
  const [currentPage, setCurrentPage] = useState(pagination?.current || 1);
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadingRef = useRef<HTMLDivElement>(null);

  // 处理分页
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    pagination?.onChange?.(page);
  };

  // 计算分页数据
  const paginatedData = pagination
    ? dataSource.slice(
        ((pagination.current || currentPage) - 1) * (pagination.pageSize || 10),
        (pagination.current || currentPage) * (pagination.pageSize || 10)
      )
    : dataSource;

  // 处理滚动事件
  const handleScroll = useCallback(() => {
    if (!virtual || !containerRef.current) return;
    setScrollTop(containerRef.current.scrollTop);
  }, [virtual]);

  // 计算虚拟滚动相关参数
  const totalHeight = dataSource.length * itemHeight;
  const visibleCount = Math.ceil(height / itemHeight) + 2; // 额外渲染2个项以避免滚动时出现空白
  const startIndex = virtual ? Math.max(0, Math.floor(scrollTop / itemHeight) - 1) : 0;
  const endIndex = virtual
    ? Math.min(dataSource.length, startIndex + visibleCount)
    : pagination
    ? paginatedData.length
    : dataSource.length;
  const offsetY = virtual ? startIndex * itemHeight : 0;

  // 设置无限滚动的观察者
  useEffect(() => {
    if (!infiniteScroll || !loadMore || !hasMore || !loadingRef.current) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting && hasMore && !loadingMore) {
          loadMore();
        }
      },
      {
        root: null,
        rootMargin: `0px 0px ${threshold}px 0px`,
        threshold: 0.1,
      }
    );

    observerRef.current.observe(loadingRef.current);

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [infiniteScroll, loadMore, hasMore, loadingMore, threshold]);

  // 样式类
  const sizeClasses = {
    small: 'py-1 px-3 text-xs',
    medium: 'py-2 px-4 text-sm',
    large: 'py-3 px-5 text-base',
  };

  // 网格布局列数
  const getColumnCount = () => {
    if (!grid) return 1;
    
    // 响应式列数
    if (typeof window !== 'undefined') {
      const width = window.innerWidth;
      if (width < 576 && grid.xs) return grid.xs;
      if (width < 768 && grid.sm) return grid.sm;
      if (width < 992 && grid.md) return grid.md;
      if (width < 1200 && grid.lg) return grid.lg;
      if (grid.xl) return grid.xl;
    }
    
    return grid.column || 4;
  };

  const columnCount = getColumnCount();
  const gridGap = grid?.gutter || 16;

  // 渲染列表项
  const renderListItem = (item: T, index: number) => {
    const key = typeof rowKey === 'function' ? rowKey(item) : item[rowKey as keyof T];
    
    const itemClassNameValue = typeof itemClassName === 'function'
      ? itemClassName(item, index)
      : itemClassName;
    
    const itemStyleValue = typeof itemStyle === 'function'
      ? itemStyle(item, index)
      : itemStyle;
    
    return (
      <li
        key={key as React.Key}
        className={cn(
          'list-none',
          !grid && sizeClasses[size],
          !grid && split && index < (pagination ? paginatedData.length - 1 : dataSource.length - 1) && 'border-b border-gray-200',
          !grid && 'transition-colors hover:bg-gray-50',
          onItemClick && 'cursor-pointer',
          itemClassNameValue
        )}
        style={{
          ...(virtual && !grid ? { height: itemHeight } : {}),
          ...itemStyleValue,
        }}
        onClick={() => onItemClick?.(item, index)}
      >
        {renderItem(item, index)}
      </li>
    );
  };

  // 渲染网格布局
  const renderGrid = () => {
    const items = pagination ? paginatedData : dataSource;
    
    return (
      <ul
        className="grid gap-4"
        style={{
          gridTemplateColumns: `repeat(${columnCount}, minmax(0, 1fr))`,
          gap: gridGap,
        }}
      >
        {items.map((item, index) => renderListItem(item, index))}
      </ul>
    );
  };

  // 渲染虚拟滚动列表
  const renderVirtualList = () => {
    return (
      <div
        ref={containerRef}
        className="overflow-auto"
        style={{ height }}
        onScroll={handleScroll}
      >
        <ul
          className="relative w-full"
          style={{ height: totalHeight }}
        >
          <div
            className="absolute left-0 right-0"
            style={{ transform: `translateY(${offsetY}px)` }}
          >
            {dataSource.slice(startIndex, endIndex).map((item, index) => 
              renderListItem(item, startIndex + index)
            )}
          </div>
        </ul>
      </div>
    );
  };

  // 渲染普通列表
  const renderList = () => {
    const items = pagination ? paginatedData : dataSource;
    
    return (
      <ul className="w-full">
        {items.map((item, index) => renderListItem(item, index))}
      </ul>
    );
  };

  // 渲染分页器
  const renderPagination = () => {
    if (!pagination) return null;
    
    const { total = 0, pageSize = 10 } = pagination;
    const totalPages = Math.ceil(total / pageSize);
    
    if (totalPages <= 1) return null;
    
    return (
      <div className="flex justify-center items-center mt-4 space-x-1">
        <button
          className={cn(
            'px-3 py-1 rounded-md text-sm',
            currentPage === 1
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
          )}
          disabled={currentPage === 1}
          onClick={() => handlePageChange(currentPage - 1)}
        >
          上一页
        </button>
        
        {Array.from({ length: Math.min(5, totalPages) }).map((_, i) => {
          let pageNum: number;
          
          if (totalPages <= 5) {
            pageNum = i + 1;
          } else if (currentPage <= 3) {
            pageNum = i + 1;
          } else if (currentPage >= totalPages - 2) {
            pageNum = totalPages - 4 + i;
          } else {
            pageNum = currentPage - 2 + i;
          }
          
          return (
            <button
              key={pageNum}
              className={cn(
                'w-8 h-8 rounded-md text-sm',
                currentPage === pageNum
                  ? 'bg-primary-600 text-white'
                  : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              )}
              onClick={() => handlePageChange(pageNum)}
            >
              {pageNum}
            </button>
          );
        })}
        
        <button
          className={cn(
            'px-3 py-1 rounded-md text-sm',
            currentPage === totalPages
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
          )}
          disabled={currentPage === totalPages}
          onClick={() => handlePageChange(currentPage + 1)}
        >
          下一页
        </button>
      </div>
    );
  };

  // 渲染加载状态
  const renderLoading = () => {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="flex flex-col items-center">
          <div className="w-8 h-8 border-4 border-gray-200 border-t-primary-500 rounded-full animate-spin mb-2"></div>
          <span className="text-gray-500 text-sm">{loadingText}</span>
        </div>
      </div>
    );
  };

  // 渲染空状态
  const renderEmpty = () => {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="flex flex-col items-center">
          <svg
            className="w-16 h-16 text-gray-300 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          <span className="text-gray-500">{emptyText}</span>
        </div>
      </div>
    );
  };

  // 渲染无限滚动加载状态
  const renderInfiniteScrollLoading = () => {
    if (!infiniteScroll) return null;
    
    return (
      <div ref={loadingRef} className="py-4 text-center">
        {loadingMore ? (
          <div className="flex justify-center items-center space-x-2">
            <div className="w-5 h-5 border-2 border-gray-200 border-t-primary-500 rounded-full animate-spin"></div>
            <span className="text-gray-500 text-sm">{loadingMoreText}</span>
          </div>
        ) : hasMore ? (
          <span className="text-gray-400 text-sm">滚动加载更多</span>
        ) : (
          <span className="text-gray-400 text-sm">{endMessage}</span>
        )}
      </div>
    );
  };

  return (
    <div
      className={cn(
        'w-full',
        bordered && 'border border-gray-200 rounded-lg overflow-hidden',
        className
      )}
      style={style}
    >
      {/* 列表头部 */}
      {header && (
        <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
          {header}
        </div>
      )}
      
      {/* 列表内容 */}
      <div className={cn('w-full', !header && !bordered && 'rounded-t-lg')}>
        {loading ? (
          renderLoading()
        ) : dataSource.length === 0 ? (
          renderEmpty()
        ) : (
          <>
            {grid ? (
              renderGrid()
            ) : virtual ? (
              renderVirtualList()
            ) : (
              renderList()
            )}
            
            {renderInfiniteScrollLoading()}
            {renderPagination()}
          </>
        )}
      </div>
      
      {/* 列表底部 */}
      {footer && (
        <div className="bg-gray-50 px-4 py-3 border-t border-gray-200">
          {footer}
        </div>
      )}
    </div>
  );
}

// 列表项组件
interface ListItemProps {
  children: React.ReactNode;
  extra?: React.ReactNode;
  actions?: React.ReactNode[];
  title?: React.ReactNode;
  description?: React.ReactNode;
  avatar?: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}

const ListItem: React.FC<ListItemProps> = ({
  children,
  extra,
  actions,
  title,
  description,
  avatar,
  className,
  style,
  onClick,
}) => {
  // 如果有结构化内容，则使用结构化布局
  const hasStructuredContent = title || description || avatar || extra || actions;
  
  if (!hasStructuredContent) {
    return (
      <div
        className={cn(
          'w-full',
          onClick && 'cursor-pointer',
          className
        )}
        style={style}
        onClick={onClick}
      >
        {children}
      </div>
    );
  }
  
  return (
    <div
      className={cn(
        'w-full flex items-center',
        onClick && 'cursor-pointer',
        className
      )}
      style={style}
      onClick={onClick}
    >
      {/* 头像 */}
      {avatar && (
        <div className="flex-shrink-0 mr-4">
          {avatar}
        </div>
      )}
      
      {/* 内容区域 */}
      <div className="flex-1 min-w-0">
        {/* 标题和描述 */}
        {(title || description) && (
          <div className="space-y-1">
            {title && (
              <div className="text-sm font-medium text-gray-900 truncate">
                {title}
              </div>
            )}
            {description && (
              <div className="text-sm text-gray-500">
                {description}
              </div>
            )}
          </div>
        )}
        
        {/* 自定义内容 */}
        {children && (
          <div className="mt-2">
            {children}
          </div>
        )}
        
        {/* 操作按钮 */}
        {actions && actions.length > 0 && (
          <div className="mt-2 flex items-center space-x-4">
            {actions.map((action, index) => (
              <div key={index} className="text-sm text-gray-500">
                {action}
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* 额外内容 */}
      {extra && (
        <div className="flex-shrink-0 ml-4">
          {extra}
        </div>
      )}
    </div>
  );
};

// 列表项元信息组件
interface ListItemMetaProps {
  avatar?: React.ReactNode;
  title?: React.ReactNode;
  description?: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

const ListItemMeta: React.FC<ListItemMetaProps> = ({
  avatar,
  title,
  description,
  className,
  style,
}) => {
  return (
    <div
      className={cn(
        'flex items-center',
        className
      )}
      style={style}
    >
      {avatar && (
        <div className="flex-shrink-0 mr-4">
          {avatar}
        </div>
      )}
      
      <div className="flex-1 min-w-0">
        {title && (
          <div className="text-sm font-medium text-gray-900 truncate">
            {title}
          </div>
        )}
        {description && (
          <div className="text-sm text-gray-500">
            {description}
          </div>
        )}
      </div>
    </div>
  );
};

List.Item = ListItem;
List.Item.Meta = ListItemMeta;

export { List };