import React, { useRef, useEffect, useState } from 'react';
import { cn } from '@/utils/cn';
import { Card } from './Card';
import { Loading } from './Loading';

// 导入Chart.js
// 注意：需要在项目中安装 chart.js 和 react-chartjs-2
// npm install chart.js react-chartjs-2

// 这里使用动态导入以避免SSR问题
let Chart: any;
let registerables: any;
let LineChart: React.ComponentType<any>;
let BarChart: React.ComponentType<any>;
let PieChart: React.ComponentType<any>;
let DoughnutChart: React.ComponentType<any>;
let RadarChart: React.ComponentType<any>;
let PolarAreaChart: React.ComponentType<any>;
let ScatterChart: React.ComponentType<any>;
let BubbleChart: React.ComponentType<any>;

// 在客户端环境中导入Chart.js
if (typeof window !== 'undefined') {
  import('chart.js').then((ChartJS) => {
    Chart = ChartJS.Chart;
    registerables = ChartJS.registerables;
    Chart.register(...registerables);
  });
  
  import('react-chartjs-2').then((ReactChartJS) => {
    LineChart = ReactChartJS.Line;
    BarChart = ReactChartJS.Bar;
    PieChart = ReactChartJS.Pie;
    DoughnutChart = ReactChartJS.Doughnut;
    RadarChart = ReactChartJS.Radar;
    PolarAreaChart = ReactChartJS.PolarArea;
    ScatterChart = ReactChartJS.Scatter;
    BubbleChart = ReactChartJS.Bubble;
  });
}

// 图表类型
export type ChartType = 
  | 'line' 
  | 'bar' 
  | 'pie' 
  | 'doughnut' 
  | 'radar' 
  | 'polarArea' 
  | 'scatter' 
  | 'bubble';

// 图表数据接口
export interface ChartData {
  labels?: string[];
  datasets: {
    label?: string;
    data: number[] | { x: number; y: number }[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
    fill?: boolean;
    tension?: number;
    pointBackgroundColor?: string | string[];
    pointBorderColor?: string | string[];
    pointHoverBackgroundColor?: string | string[];
    pointHoverBorderColor?: string | string[];
    [key: string]: any;
  }[];
}

// 图表选项接口
export interface ChartOptions {
  responsive?: boolean;
  maintainAspectRatio?: boolean;
  plugins?: {
    legend?: {
      display?: boolean;
      position?: 'top' | 'left' | 'bottom' | 'right';
      align?: 'start' | 'center' | 'end';
      [key: string]: any;
    };
    title?: {
      display?: boolean;
      text?: string;
      position?: 'top' | 'left' | 'bottom' | 'right';
      align?: 'start' | 'center' | 'end';
      [key: string]: any;
    };
    tooltip?: {
      enabled?: boolean;
      [key: string]: any;
    };
    [key: string]: any;
  };
  scales?: {
    x?: {
      display?: boolean;
      title?: {
        display?: boolean;
        text?: string;
      };
      grid?: {
        display?: boolean;
        color?: string;
      };
      [key: string]: any;
    };
    y?: {
      display?: boolean;
      title?: {
        display?: boolean;
        text?: string;
      };
      grid?: {
        display?: boolean;
        color?: string;
      };
      [key: string]: any;
    };
    [key: string]: any;
  };
  animation?: {
    duration?: number;
    easing?: string;
    [key: string]: any;
  };
  [key: string]: any;
}

// 图表组件属性
export interface ChartProps {
  type: ChartType;
  data: ChartData;
  options?: ChartOptions;
  width?: number | string;
  height?: number | string;
  className?: string;
  style?: React.CSSProperties;
  loading?: boolean;
  error?: string;
  title?: string;
  description?: string;
  showLegend?: boolean;
  legendPosition?: 'top' | 'left' | 'bottom' | 'right';
  theme?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  animation?: boolean;
  animationDuration?: number;
  responsive?: boolean;
  maintainAspectRatio?: boolean;
  onDataPointClick?: (datasetIndex: number, index: number, value: any) => void;
}

// 默认颜色主题
const defaultColors = {
  default: {
    backgroundColor: [
      'rgba(99, 125, 255, 0.2)',
      'rgba(255, 99, 132, 0.2)',
      'rgba(255, 206, 86, 0.2)',
      'rgba(75, 192, 192, 0.2)',
      'rgba(153, 102, 255, 0.2)',
      'rgba(255, 159, 64, 0.2)',
    ],
    borderColor: [
      'rgba(99, 125, 255, 1)',
      'rgba(255, 99, 132, 1)',
      'rgba(255, 206, 86, 1)',
      'rgba(75, 192, 192, 1)',
      'rgba(153, 102, 255, 1)',
      'rgba(255, 159, 64, 1)',
    ],
  },
  primary: {
    backgroundColor: [
      'rgba(59, 130, 246, 0.2)',
      'rgba(37, 99, 235, 0.2)',
      'rgba(29, 78, 216, 0.2)',
      'rgba(30, 64, 175, 0.2)',
      'rgba(30, 58, 138, 0.2)',
    ],
    borderColor: [
      'rgba(59, 130, 246, 1)',
      'rgba(37, 99, 235, 1)',
      'rgba(29, 78, 216, 1)',
      'rgba(30, 64, 175, 1)',
      'rgba(30, 58, 138, 1)',
    ],
  },
  secondary: {
    backgroundColor: [
      'rgba(107, 114, 128, 0.2)',
      'rgba(75, 85, 99, 0.2)',
      'rgba(55, 65, 81, 0.2)',
      'rgba(31, 41, 55, 0.2)',
      'rgba(17, 24, 39, 0.2)',
    ],
    borderColor: [
      'rgba(107, 114, 128, 1)',
      'rgba(75, 85, 99, 1)',
      'rgba(55, 65, 81, 1)',
      'rgba(31, 41, 55, 1)',
      'rgba(17, 24, 39, 1)',
    ],
  },
  success: {
    backgroundColor: [
      'rgba(16, 185, 129, 0.2)',
      'rgba(5, 150, 105, 0.2)',
      'rgba(4, 120, 87, 0.2)',
      'rgba(6, 95, 70, 0.2)',
      'rgba(6, 78, 59, 0.2)',
    ],
    borderColor: [
      'rgba(16, 185, 129, 1)',
      'rgba(5, 150, 105, 1)',
      'rgba(4, 120, 87, 1)',
      'rgba(6, 95, 70, 1)',
      'rgba(6, 78, 59, 1)',
    ],
  },
  warning: {
    backgroundColor: [
      'rgba(245, 158, 11, 0.2)',
      'rgba(217, 119, 6, 0.2)',
      'rgba(180, 83, 9, 0.2)',
      'rgba(146, 64, 14, 0.2)',
      'rgba(120, 53, 15, 0.2)',
    ],
    borderColor: [
      'rgba(245, 158, 11, 1)',
      'rgba(217, 119, 6, 1)',
      'rgba(180, 83, 9, 1)',
      'rgba(146, 64, 14, 1)',
      'rgba(120, 53, 15, 1)',
    ],
  },
  danger: {
    backgroundColor: [
      'rgba(239, 68, 68, 0.2)',
      'rgba(220, 38, 38, 0.2)',
      'rgba(185, 28, 28, 0.2)',
      'rgba(153, 27, 27, 0.2)',
      'rgba(127, 29, 29, 0.2)',
    ],
    borderColor: [
      'rgba(239, 68, 68, 1)',
      'rgba(220, 38, 38, 1)',
      'rgba(185, 28, 28, 1)',
      'rgba(153, 27, 27, 1)',
      'rgba(127, 29, 29, 1)',
    ],
  },
};

// 图表组件
const ChartComponent: React.FC<ChartProps> = ({
  type,
  data,
  options = {},
  width = '100%',
  height = 300,
  className,
  style,
  loading = false,
  error,
  title,
  description,
  showLegend = true,
  legendPosition = 'top',
  theme = 'default',
  animation = true,
  animationDuration = 1000,
  responsive = true,
  maintainAspectRatio = true,
  onDataPointClick,
}) => {
  const chartRef = useRef<any>(null);
  const [chartLoaded, setChartLoaded] = useState(false);

  // 应用主题颜色
  const applyThemeColors = (chartData: ChartData) => {
    const themeColors = defaultColors[theme];
    
    return {
      ...chartData,
      datasets: chartData.datasets.map((dataset, index) => {
        // 如果已经设置了颜色，则不覆盖
        if (dataset.backgroundColor || dataset.borderColor) {
          return dataset;
        }
        
        // 根据图表类型应用不同的颜色策略
        if (['pie', 'doughnut', 'polarArea'].includes(type)) {
          // 这些图表类型每个数据点都需要一个颜色
          return {
            ...dataset,
            backgroundColor: themeColors.backgroundColor,
            borderColor: themeColors.borderColor,
            borderWidth: 1,
          };
        } else {
          // 其他图表类型每个数据集使用一个颜色
          const colorIndex = index % themeColors.backgroundColor.length;
          return {
            ...dataset,
            backgroundColor: themeColors.backgroundColor[colorIndex],
            borderColor: themeColors.borderColor[colorIndex],
            borderWidth: 1,
          };
        }
      }),
    };
  };

  // 合并选项
  const mergedOptions: ChartOptions = {
    responsive,
    maintainAspectRatio,
    plugins: {
      legend: {
        display: showLegend,
        position: legendPosition,
      },
      title: {
        display: !!title,
        text: title,
        font: {
          size: 16,
          weight: 'bold',
        },
        padding: {
          top: 10,
          bottom: 10,
        },
      },
      tooltip: {
        enabled: true,
      },
      ...options.plugins,
    },
    animation: animation ? {
      duration: animationDuration,
      easing: 'easeOutQuart',
      ...options.animation,
    } : false,
    ...options,
  };

  // 处理点击事件
  useEffect(() => {
    if (!chartRef.current || !onDataPointClick) return;
    
    const chart = chartRef.current;
    
    const handleClick = (event: any) => {
      const points = chart.getElementsAtEventForMode(
        event,
        'nearest',
        { intersect: true },
        false
      );
      
      if (points.length) {
        const firstPoint = points[0];
        const datasetIndex = firstPoint.datasetIndex;
        const index = firstPoint.index;
        const value = data.datasets[datasetIndex].data[index];
        
        onDataPointClick(datasetIndex, index, value);
      }
    };
    
    chart.canvas.addEventListener('click', handleClick);
    
    return () => {
      chart.canvas.removeEventListener('click', handleClick);
    };
  }, [chartRef.current, data, onDataPointClick]);

  // 检查Chart.js是否已加载
  useEffect(() => {
    if (typeof window !== 'undefined' && Chart && LineChart) {
      setChartLoaded(true);
    }
  }, []);

  // 渲染图表
  const renderChart = () => {
    if (!chartLoaded) {
      return (
        <div className="flex items-center justify-center h-full">
          <Loading size="lg" />
        </div>
      );
    }
    
    if (error) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-danger-600">
            <svg
              className="w-12 h-12 mx-auto mb-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <p>{error}</p>
          </div>
        </div>
      );
    }
    
    if (loading) {
      return (
        <div className="flex items-center justify-center h-full">
          <Loading size="lg" />
        </div>
      );
    }
    
    const themedData = applyThemeColors(data);
    
    switch (type) {
      case 'line':
        return <LineChart ref={chartRef} data={themedData} options={mergedOptions} />;
      case 'bar':
        return <BarChart ref={chartRef} data={themedData} options={mergedOptions} />;
      case 'pie':
        return <PieChart ref={chartRef} data={themedData} options={mergedOptions} />;
      case 'doughnut':
        return <DoughnutChart ref={chartRef} data={themedData} options={mergedOptions} />;
      case 'radar':
        return <RadarChart ref={chartRef} data={themedData} options={mergedOptions} />;
      case 'polarArea':
        return <PolarAreaChart ref={chartRef} data={themedData} options={mergedOptions} />;
      case 'scatter':
        return <ScatterChart ref={chartRef} data={themedData} options={mergedOptions} />;
      case 'bubble':
        return <BubbleChart ref={chartRef} data={themedData} options={mergedOptions} />;
      default:
        return <div>Unsupported chart type</div>;
    }
  };

  return (
    <Card className={cn('overflow-hidden', className)} style={style}>
      <div className="p-4">
        {title && !options.plugins?.title?.display && (
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
        )}
        {description && (
          <p className="text-sm text-gray-500 mb-4">{description}</p>
        )}
        <div style={{ width, height }}>
          {renderChart()}
        </div>
      </div>
    </Card>
  );
};

// 导出图表组件
export { ChartComponent as Chart };