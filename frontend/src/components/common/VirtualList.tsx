import React, { useState, useRef, useMemo, useCallback, memo } from 'react'
import { cn } from '@/utils/cn'
import { useThrottle, useEventListener, useCleanup } from '@/utils/performance'

interface VirtualListProps<T> {
  items: T[]
  itemHeight: number | ((index: number) => number)
  containerHeight: number
  renderItem: (item: T, index: number) => React.ReactNode
  overscan?: number
  className?: string
  onScroll?: (scrollTop: number) => void
  estimatedItemHeight?: number
  getItemKey?: (item: T, index: number) => string | number
  loadMore?: () => void
  hasNextPage?: boolean
  isLoading?: boolean
  threshold?: number
  loadingComponent?: React.ReactNode
  emptyComponent?: React.ReactNode
}

interface ItemCache {
  height: number
  offset: number
}

// 优化的虚拟列表项组件
const VirtualListItem = memo<{
  item: any
  index: number
  style: React.CSSProperties
  renderItem: (item: any, index: number) => React.ReactNode
  itemKey: string | number
}>(({ item, index, style, renderItem, itemKey }) => {
  return (
    <div key={itemKey} style={style}>
      {renderItem(item, index)}
    </div>
  )
})

VirtualListItem.displayName = 'VirtualListItem'

function VirtualList<T>({
  items,
  itemHeight,
  containerHeight,
  renderItem,
  overscan = 5,
  className = '',
  onScroll,
  estimatedItemHeight = 50,
  getItemKey,
  loadMore,
  hasNextPage = false,
  isLoading = false,
  threshold = 200,
  loadingComponent,
  emptyComponent
}: VirtualListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)
  const itemCacheRef = useRef<Map<number, ItemCache>>(new Map())

  // 节流滚动处理，提高性能
  const throttledScrollHandler = useThrottle((scrollTop: number) => {
    setScrollTop(scrollTop)
    onScroll?.(scrollTop)
  }, 16) // 60fps

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const scrollTop = e.currentTarget.scrollTop
    throttledScrollHandler(scrollTop)

    // 无限滚动检测
    if (loadMore && hasNextPage && !isLoading) {
      const scrollHeight = e.currentTarget.scrollHeight
      const clientHeight = e.currentTarget.clientHeight
      
      if (scrollTop + clientHeight >= scrollHeight - threshold) {
        loadMore()
      }
    }
  }, [throttledScrollHandler, loadMore, hasNextPage, isLoading, threshold])

  // 计算项目高度
  const getItemHeight = useCallback((index: number): number => {
    if (typeof itemHeight === 'function') {
      return itemHeight(index)
    }
    return itemHeight
  }, [itemHeight])

  // 计算项目偏移
  const getItemOffset = useCallback((index: number): number => {
    if (typeof itemHeight === 'number') {
      return index * itemHeight
    }

    let offset = 0
    for (let i = 0; i < index; i++) {
      const cached = itemCacheRef.current.get(i)
      if (cached) {
        offset += cached.height
      } else {
        offset += estimatedItemHeight
      }
    }
    return offset
  }, [itemHeight, estimatedItemHeight])

  // 计算可见范围
  const visibleRange = useMemo(() => {
    if (items.length === 0) {
      return { start: 0, end: 0 }
    }

    let startIndex = 0
    let endIndex = items.length - 1

    if (typeof itemHeight === 'number') {
      // 固定高度的快速计算
      startIndex = Math.floor(scrollTop / itemHeight)
      endIndex = Math.min(
        startIndex + Math.ceil(containerHeight / itemHeight),
        items.length - 1
      )
    } else {
      // 动态高度的二分查找
      let currentOffset = 0
      for (let i = 0; i < items.length; i++) {
        const height = getItemHeight(i)
        if (currentOffset + height > scrollTop) {
          startIndex = i
          break
        }
        currentOffset += height
      }

      currentOffset = getItemOffset(startIndex)
      for (let i = startIndex; i < items.length; i++) {
        if (currentOffset > scrollTop + containerHeight) {
          endIndex = i - 1
          break
        }
        currentOffset += getItemHeight(i)
      }
    }

    return {
      start: Math.max(0, startIndex - overscan),
      end: Math.min(items.length - 1, endIndex + overscan)
    }
  }, [scrollTop, containerHeight, items.length, overscan, itemHeight, getItemHeight, getItemOffset])

  // 生成可见项目
  const visibleItems = useMemo(() => {
    const result = []
    let currentOffset = getItemOffset(visibleRange.start)

    for (let i = visibleRange.start; i <= visibleRange.end; i++) {
      const height = getItemHeight(i)
      const key = getItemKey ? getItemKey(items[i], i) : i

      result.push({
        index: i,
        key,
        item: items[i],
        style: {
          position: 'absolute' as const,
          top: currentOffset,
          left: 0,
          right: 0,
          height: height
        }
      })

      currentOffset += height
    }

    return result
  }, [visibleRange, items, getItemHeight, getItemOffset, getItemKey])

  // 计算总高度
  const totalHeight = useMemo(() => {
    if (typeof itemHeight === 'number') {
      return items.length * itemHeight
    }

    let height = 0
    for (let i = 0; i < items.length; i++) {
      height += getItemHeight(i)
    }
    return height
  }, [items.length, itemHeight, getItemHeight])

  // 监听窗口大小变化
  useEventListener('resize', () => {
    // 重新计算可见范围
    if (containerRef.current) {
      setScrollTop(prev => prev)
    }
  })

  // 清理资源
  useCleanup(() => {
    itemCacheRef.current.clear()
  })

  // 空状态
  if (items.length === 0 && !isLoading) {
    return (
      <div 
        className={cn('flex items-center justify-center', className)}
        style={{ height: containerHeight }}
      >
        {emptyComponent || (
          <div className="text-center text-gray-500">
            <p>暂无数据</p>
          </div>
        )}
      </div>
    )
  }

  // 渲染加载指示器
  const renderLoadingIndicator = () => {
    if (!isLoading) return null

    return (
      <div 
        className="flex items-center justify-center py-4"
        style={{
          position: 'absolute',
          top: totalHeight,
          left: 0,
          right: 0,
          height: 60
        }}
      >
        {loadingComponent || (
          <>
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
            <span className="ml-2 text-gray-600">加载中...</span>
          </>
        )}
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      className={cn('overflow-auto', className)}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
    >
      <div style={{ 
        height: totalHeight + (isLoading ? 60 : 0), 
        position: 'relative' 
      }}>
        {visibleItems.map(({ key, index, item, style }) => (
          <VirtualListItem
            key={key}
            item={item}
            index={index}
            style={style}
            renderItem={renderItem}
            itemKey={key}
          />
        ))}
        {renderLoadingIndicator()}
      </div>
    </div>
  )
}

// 高性能虚拟表格组件
interface VirtualTableProps<T> {
  items: T[]
  columns: Array<{
    key: string
    title: string
    width?: number
    render: (item: T, index: number) => React.ReactNode
  }>
  rowHeight: number
  containerHeight: number
  containerWidth: number
  className?: string
  onRowClick?: (item: T, index: number) => void
}

export function VirtualTable<T>({
  items,
  columns,
  rowHeight,
  containerHeight,
  containerWidth,
  className = '',
  onRowClick
}: VirtualTableProps<T>) {
  const renderRow = useCallback((item: T, index: number) => {
    return (
      <div 
        className={cn(
          'flex border-b border-gray-200 hover:bg-gray-50',
          onRowClick && 'cursor-pointer'
        )}
        onClick={() => onRowClick?.(item, index)}
      >
        {columns.map((column) => (
          <div
            key={column.key}
            className="px-4 py-2 flex items-center"
            style={{ 
              width: column.width || containerWidth / columns.length,
              minWidth: column.width || containerWidth / columns.length
            }}
          >
            {column.render(item, index)}
          </div>
        ))}
      </div>
    )
  }, [columns, containerWidth, onRowClick])

  return (
    <div className={className}>
      {/* 表头 */}
      <div className="flex bg-gray-100 border-b-2 border-gray-200 sticky top-0 z-10">
        {columns.map((column) => (
          <div
            key={column.key}
            className="px-4 py-3 font-medium text-gray-900"
            style={{ 
              width: column.width || containerWidth / columns.length,
              minWidth: column.width || containerWidth / columns.length
            }}
          >
            {column.title}
          </div>
        ))}
      </div>

      {/* 虚拟化表格体 */}
      <VirtualList
        items={items}
        itemHeight={rowHeight}
        containerHeight={containerHeight - 48} // 减去表头高度
        renderItem={renderRow}
        className="border border-gray-200"
      />
    </div>
  )
}

export default memo(VirtualList)