import React, { useState, useEffect, useMemo } from 'react';
import { ChevronDown, ChevronUp, ChevronLeft, ChevronRight, Search, Filter, X } from 'lucide-react';
import { cn } from '@/utils/cn';
import { Input } from './Input';
import { Button } from './Button';

export interface TableColumn<T> {
  key: string;
  title: string;
  dataIndex?: string;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  sorter?: boolean | ((a: T, b: T) => number);
  sortDirections?: ('ascend' | 'descend')[];
  defaultSortOrder?: 'ascend' | 'descend';
  width?: number | string;
  align?: 'left' | 'center' | 'right';
  fixed?: 'left' | 'right';
  ellipsis?: boolean;
  className?: string;
  headerClassName?: string;
  cellClassName?: string;
  filterable?: boolean;
  filterOptions?: { value: string; label: string }[];
  onFilter?: (value: string, record: T) => boolean;
}

export interface TableProps<T> {
  columns: TableColumn<T>[];
  dataSource: T[];
  rowKey?: string | ((record: T) => string);
  loading?: boolean;
  pagination?: boolean | {
    pageSize?: number;
    current?: number;
    total?: number;
    onChange?: (page: number, pageSize: number) => void;
    showSizeChanger?: boolean;
    pageSizeOptions?: string[];
    showTotal?: (total: number, range: [number, number]) => React.ReactNode;
  };
  bordered?: boolean;
  size?: 'small' | 'medium' | 'large';
  scroll?: { x?: number | string; y?: number | string };
  showHeader?: boolean;
  title?: () => React.ReactNode;
  footer?: () => React.ReactNode;
  rowClassName?: string | ((record: T, index: number) => string);
  onRow?: (record: T, index: number) => React.HTMLAttributes<HTMLTableRowElement>;
  onChange?: (pagination: any, filters: any, sorter: any) => void;
  emptyText?: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  sticky?: boolean;
  summary?: (data: readonly T[]) => React.ReactNode;
  expandable?: {
    expandedRowRender: (record: T, index: number) => React.ReactNode;
    expandRowByClick?: boolean;
    expandIcon?: (props: { expanded: boolean; record: T; onExpand: (record: T) => void }) => React.ReactNode;
    expandedRowKeys?: React.Key[];
    onExpand?: (expanded: boolean, record: T) => void;
    rowExpandable?: (record: T) => boolean;
  };
}

function Table<T extends Record<string, any>>({
  columns,
  dataSource,
  rowKey = 'id',
  loading = false,
  pagination = true,
  bordered = false,
  size = 'medium',
  scroll,
  showHeader = true,
  title,
  footer,
  rowClassName,
  onRow,
  onChange,
  emptyText = '暂无数据',
  className,
  style,
  sticky = false,
  summary,
  expandable,
}: TableProps<T>) {
  // 状态管理
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(pagination && typeof pagination === 'object' ? pagination.pageSize || 10 : 10);
  const [sortState, setSortState] = useState<{ key: string; order: 'ascend' | 'descend' | null }>({ key: '', order: null });
  const [filters, setFilters] = useState<Record<string, string[]>>({});
  const [searchText, setSearchText] = useState('');
  const [expandedRows, setExpandedRows] = useState<React.Key[]>([]);

  // 设置默认排序
  useEffect(() => {
    const defaultSortColumn = columns.find(col => col.defaultSortOrder);
    if (defaultSortColumn) {
      setSortState({
        key: defaultSortColumn.key,
        order: defaultSortColumn.defaultSortOrder || 'ascend'
      });
    }
  }, [columns]);

  // 处理排序
  const handleSort = (column: TableColumn<T>) => {
    if (!column.sorter) return;

    let newOrder: 'ascend' | 'descend' | null = 'ascend';
    if (sortState.key === column.key) {
      if (sortState.order === 'ascend') {
        newOrder = 'descend';
      } else if (sortState.order === 'descend') {
        newOrder = null;
      }
    }

    setSortState({ key: column.key, order: newOrder });
    
    if (onChange) {
      onChange(
        { current: currentPage, pageSize },
        filters,
        { column, columnKey: column.key, order: newOrder }
      );
    }
  };

  // 处理筛选
  const handleFilter = (columnKey: string, value: string[]) => {
    const newFilters = { ...filters, [columnKey]: value };
    setFilters(newFilters);
    setCurrentPage(1); // 重置到第一页
    
    if (onChange) {
      onChange(
        { current: 1, pageSize },
        newFilters,
        sortState.order ? { columnKey: sortState.key, order: sortState.order } : {}
      );
    }
  };

  // 处理分页
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    
    if (onChange) {
      onChange(
        { current: page, pageSize },
        filters,
        sortState.order ? { columnKey: sortState.key, order: sortState.order } : {}
      );
    }
    
    if (pagination && typeof pagination === 'object' && pagination.onChange) {
      pagination.onChange(page, pageSize);
    }
  };

  // 处理每页条数变化
  const handlePageSizeChange = (size: number) => {
    setPageSize(size);
    setCurrentPage(1); // 重置到第一页
    
    if (onChange) {
      onChange(
        { current: 1, pageSize: size },
        filters,
        sortState.order ? { columnKey: sortState.key, order: sortState.order } : {}
      );
    }
    
    if (pagination && typeof pagination === 'object' && pagination.onChange) {
      pagination.onChange(1, size);
    }
  };

  // 处理搜索
  const handleSearch = (value: string) => {
    setSearchText(value);
    setCurrentPage(1); // 重置到第一页
  };

  // 处理展开行
  const handleExpand = (record: T) => {
    const key = typeof rowKey === 'function' ? rowKey(record) : record[rowKey];
    const expanded = expandedRows.includes(key);
    
    let newExpandedRows: React.Key[];
    if (expanded) {
      newExpandedRows = expandedRows.filter(k => k !== key);
    } else {
      newExpandedRows = [...expandedRows, key];
    }
    
    setExpandedRows(newExpandedRows);
    
    if (expandable && expandable.onExpand) {
      expandable.onExpand(!expanded, record);
    }
  };

  // 处理数据过滤和排序
  const processedData = useMemo(() => {
    let result = [...dataSource];
    
    // 应用筛选
    Object.entries(filters).forEach(([key, values]) => {
      if (values && values.length > 0) {
        const column = columns.find(col => col.key === key);
        if (column && column.onFilter) {
          result = result.filter(record => 
            values.some(value => column.onFilter!(value, record))
          );
        }
      }
    });
    
    // 应用搜索
    if (searchText) {
      const searchLower = searchText.toLowerCase();
      result = result.filter(record => {
        return columns.some(column => {
          const dataIndex = column.dataIndex || column.key;
          const value = record[dataIndex];
          return value && String(value).toLowerCase().includes(searchLower);
        });
      });
    }
    
    // 应用排序
    if (sortState.key && sortState.order) {
      const column = columns.find(col => col.key === sortState.key);
      if (column && column.sorter) {
        const sorter = typeof column.sorter === 'function'
          ? column.sorter
          : (a: T, b: T) => {
              const aValue = a[column.dataIndex || column.key];
              const bValue = b[column.dataIndex || column.key];
              if (aValue < bValue) return -1;
              if (aValue > bValue) return 1;
              return 0;
            };
        
        result.sort((a, b) => {
          const result = sorter(a, b);
          return sortState.order === 'ascend' ? result : -result;
        });
      }
    }
    
    return result;
  }, [dataSource, columns, filters, searchText, sortState]);

  // 分页数据
  const paginatedData = useMemo(() => {
    if (!pagination) return processedData;
    
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return processedData.slice(startIndex, endIndex);
  }, [processedData, pagination, currentPage, pageSize]);

  // 计算总页数
  const totalPages = useMemo(() => {
    return Math.ceil(processedData.length / pageSize);
  }, [processedData, pageSize]);

  // 计算当前显示范围
  const currentRange = useMemo(() => {
    const start = (currentPage - 1) * pageSize + 1;
    const end = Math.min(currentPage * pageSize, processedData.length);
    return [start, end] as [number, number];
  }, [currentPage, pageSize, processedData.length]);

  // 样式类
  const sizeClasses = {
    small: 'text-xs',
    medium: 'text-sm',
    large: 'text-base',
  };

  const cellPaddingClasses = {
    small: 'px-2 py-1',
    medium: 'px-4 py-2',
    large: 'px-6 py-3',
  };

  return (
    <div className={cn(
      'w-full overflow-hidden',
      bordered && 'border border-gray-200 rounded-lg',
      className
    )} style={style}>
      {/* 表格标题和搜索栏 */}
      {(title || columns.some(col => col.filterable)) && (
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-4 border-b border-gray-200 bg-gray-50">
          {title && <div className="mb-4 sm:mb-0">{title()}</div>}
          
          <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
            {/* 搜索框 */}
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                value={searchText}
                onChange={(e) => handleSearch(e.target.value)}
                placeholder="搜索..."
                className="pl-10"
              />
              {searchText && (
                <button
                  onClick={() => handleSearch('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
            
            {/* 筛选按钮 */}
            {columns.some(col => col.filterable) && (
              <div className="relative">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-1"
                >
                  <Filter className="w-4 h-4" />
                  <span>筛选</span>
                </Button>
                {/* 筛选面板 - 这里可以实现一个弹出的筛选面板 */}
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* 表格容器 */}
      <div className={cn(
        'w-full overflow-auto',
        scroll?.y && 'max-h-[--scroll-y]',
        scroll?.x && 'max-w-[--scroll-x]'
      )} style={{
        '--scroll-y': typeof scroll?.y === 'number' ? `${scroll.y}px` : scroll?.y,
        '--scroll-x': typeof scroll?.x === 'number' ? `${scroll.x}px` : scroll?.x,
      } as React.CSSProperties}>
        <table className={cn(
          'w-full border-collapse',
          sizeClasses[size]
        )}>
          {/* 表头 */}
          {showHeader && (
            <thead className={cn(
              'bg-gray-50',
              sticky && 'sticky top-0 z-10'
            )}>
              <tr>
                {/* 展开列 */}
                {expandable && (
                  <th className={cn(
                    'font-semibold text-left',
                    cellPaddingClasses[size],
                    bordered && 'border border-gray-200'
                  )} style={{ width: 50 }}>
                    <span className="sr-only">展开</span>
                  </th>
                )}
                
                {/* 数据列 */}
                {columns.map(column => (
                  <th
                    key={column.key}
                    className={cn(
                      'font-semibold',
                      column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left',
                      cellPaddingClasses[size],
                      bordered && 'border border-gray-200',
                      column.sorter && 'cursor-pointer hover:bg-gray-100',
                      column.headerClassName
                    )}
                    style={{ width: column.width }}
                    onClick={() => column.sorter && handleSort(column)}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className={column.ellipsis ? 'truncate' : ''}>
                        {column.title}
                      </span>
                      
                      {column.sorter && (
                        <div className="flex flex-col">
                          <ChevronUp
                            className={cn(
                              'w-3 h-3 -mb-1',
                              sortState.key === column.key && sortState.order === 'ascend'
                                ? 'text-primary-600'
                                : 'text-gray-400'
                            )}
                          />
                          <ChevronDown
                            className={cn(
                              'w-3 h-3',
                              sortState.key === column.key && sortState.order === 'descend'
                                ? 'text-primary-600'
                                : 'text-gray-400'
                            )}
                          />
                        </div>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
          )}
          
          {/* 表格主体 */}
          <tbody>
            {loading ? (
              // 加载状态
              <tr>
                <td
                  colSpan={columns.length + (expandable ? 1 : 0)}
                  className={cn(
                    'text-center py-8',
                    bordered && 'border border-gray-200'
                  )}
                >
                  <div className="flex flex-col items-center justify-center">
                    <div className="w-8 h-8 border-4 border-gray-200 border-t-primary-500 rounded-full animate-spin mb-2"></div>
                    <span className="text-gray-500">加载中...</span>
                  </div>
                </td>
              </tr>
            ) : paginatedData.length > 0 ? (
              // 数据行
              paginatedData.map((record, index) => {
                const key = typeof rowKey === 'function' ? rowKey(record) : record[rowKey];
                const isExpanded = expandedRows.includes(key);
                const isExpandable = expandable?.rowExpandable ? expandable.rowExpandable(record) : true;
                
                const rowClassNameValue = typeof rowClassName === 'function'
                  ? rowClassName(record, index)
                  : rowClassName;
                
                const rowProps = onRow ? onRow(record, index) : {};
                
                return (
                  <React.Fragment key={key}>
                    <tr
                      className={cn(
                        'transition-colors hover:bg-gray-50',
                        rowClassNameValue
                      )}
                      {...rowProps}
                      onClick={expandable?.expandRowByClick && isExpandable
                        ? () => handleExpand(record)
                        : undefined
                      }
                    >
                      {/* 展开图标列 */}
                      {expandable && (
                        <td className={cn(
                          cellPaddingClasses[size],
                          bordered && 'border border-gray-200'
                        )}>
                          {isExpandable && (
                            expandable.expandIcon ? (
                              expandable.expandIcon({
                                expanded: isExpanded,
                                record,
                                onExpand: () => handleExpand(record)
                              })
                            ) : (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleExpand(record);
                                }}
                                className="p-1 rounded-full hover:bg-gray-200 transition-colors"
                              >
                                {isExpanded ? (
                                  <ChevronDown className="w-4 h-4" />
                                ) : (
                                  <ChevronRight className="w-4 h-4" />
                                )}
                              </button>
                            )
                          )}
                        </td>
                      )}
                      
                      {/* 数据列 */}
                      {columns.map(column => {
                        const dataIndex = column.dataIndex || column.key;
                        const value = record[dataIndex];
                        
                        return (
                          <td
                            key={column.key}
                            className={cn(
                              column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left',
                              cellPaddingClasses[size],
                              bordered && 'border border-gray-200',
                              column.ellipsis && 'max-w-xs truncate',
                              column.cellClassName
                            )}
                          >
                            {column.render
                              ? column.render(value, record, index)
                              : value
                            }
                          </td>
                        );
                      })}
                    </tr>
                    
                    {/* 展开行 */}
                    {expandable && isExpandable && isExpanded && (
                      <tr>
                        <td
                          colSpan={columns.length + 1}
                          className={cn(
                            'bg-gray-50',
                            bordered && 'border border-gray-200'
                          )}
                        >
                          {expandable.expandedRowRender(record, index)}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })
            ) : (
              // 空数据
              <tr>
                <td
                  colSpan={columns.length + (expandable ? 1 : 0)}
                  className={cn(
                    'text-center py-8',
                    bordered && 'border border-gray-200'
                  )}
                >
                  <div className="flex flex-col items-center justify-center text-gray-500">
                    {emptyText}
                  </div>
                </td>
              </tr>
            )}
          </tbody>
          
          {/* 表格摘要 */}
          {summary && (
            <tfoot className="bg-gray-50">
              {summary(dataSource)}
            </tfoot>
          )}
        </table>
      </div>
      
      {/* 表格底部和分页 */}
      <div className="flex flex-col sm:flex-row justify-between items-center p-4 border-t border-gray-200 bg-gray-50">
        {footer && <div className="mb-4 sm:mb-0">{footer()}</div>}
        
        {pagination && (
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <div className="text-sm text-gray-500">
              {typeof pagination === 'object' && pagination.showTotal
                ? pagination.showTotal(processedData.length, currentRange)
                : `显示 ${currentRange[0]}-${currentRange[1]}，共 ${processedData.length} 条`
              }
            </div>
            
            <div className="flex items-center gap-1">
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage === 1}
                onClick={() => handlePageChange(1)}
              >
                <span className="sr-only">第一页</span>
                <ChevronLeft className="w-3 h-3 mr-1" />
                <ChevronLeft className="w-3 h-3" />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage === 1}
                onClick={() => handlePageChange(currentPage - 1)}
              >
                <span className="sr-only">上一页</span>
                <ChevronLeft className="w-4 h-4" />
              </Button>
              
              {/* 页码 */}
              <div className="flex items-center gap-1 mx-2">
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
                    <Button
                      key={pageNum}
                      variant={currentPage === pageNum ? 'default' : 'outline'}
                      size="sm"
                      className="w-8 h-8 p-0"
                      onClick={() => handlePageChange(pageNum)}
                    >
                      {pageNum}
                    </Button>
                  );
                })}
              </div>
              
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage === totalPages}
                onClick={() => handlePageChange(currentPage + 1)}
              >
                <span className="sr-only">下一页</span>
                <ChevronRight className="w-4 h-4" />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage === totalPages}
                onClick={() => handlePageChange(totalPages)}
              >
                <span className="sr-only">最后一页</span>
                <ChevronRight className="w-3 h-3 mr-1" />
                <ChevronRight className="w-3 h-3" />
              </Button>
            </div>
            
            {/* 每页条数选择器 */}
            {typeof pagination === 'object' && pagination.showSizeChanger && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">每页</span>
                <select
                  value={pageSize}
                  onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                  className="border border-gray-300 rounded-md text-sm py-1 px-2"
                >
                  {(pagination.pageSizeOptions || ['10', '20', '50', '100']).map(size => (
                    <option key={size} value={size}>{size}</option>
                  ))}
                </select>
                <span className="text-sm text-gray-500">条</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export { Table };