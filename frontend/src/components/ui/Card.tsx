import React from 'react';
import { cn } from '../../utils/cn';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined' | 'filled';
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  hover?: boolean;
  clickable?: boolean;
}

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  divider?: boolean;
}

export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {}

export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  divider?: boolean;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({
    className,
    variant = 'default',
    padding = 'md',
    hover = false,
    clickable = false,
    children,
    ...props
  }, ref) => {
    const cardStyles = cn(
      // 基础样式
      'bg-white rounded-xl transition-all duration-200',
      
      // 变体样式
      {
        // Default - 轻微阴影
        'shadow-light': variant === 'default',
        
        // Elevated - 明显阴影
        'shadow-medium': variant === 'elevated',
        
        // Outlined - 边框样式
        'border-2 border-gray-200 shadow-none': variant === 'outlined',
        
        // Filled - 填充背景
        'bg-gray-50 shadow-none': variant === 'filled',
      },
      
      // 内边距样式
      {
        'p-0': padding === 'none',
        'p-4': padding === 'sm',
        'p-6': padding === 'md',
        'p-8': padding === 'lg',
        'p-10': padding === 'xl',
      },
      
      // 悬停效果
      {
        'hover:shadow-heavy hover:-translate-y-1': hover,
      },
      
      // 可点击样式
      {
        'cursor-pointer select-none': clickable,
        'hover:shadow-heavy hover:-translate-y-1': clickable,
        'active:translate-y-0 active:shadow-medium': clickable,
      },
      
      className
    );

    return (
      <div
        ref={ref}
        className={cardStyles}
        role={clickable ? 'button' : undefined}
        tabIndex={clickable ? 0 : undefined}
        {...props}
      >
        {children}
      </div>
    );
  }
);

const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, divider = false, children, ...props }, ref) => {
    const headerStyles = cn(
      'flex items-center justify-between',
      {
        'pb-4 mb-4 border-b border-gray-200': divider,
      },
      className
    );

    return (
      <div ref={ref} className={headerStyles} {...props}>
        {children}
      </div>
    );
  }
);

const CardContent = React.forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, children, ...props }, ref) => {
    const contentStyles = cn('flex-1', className);

    return (
      <div ref={ref} className={contentStyles} {...props}>
        {children}
      </div>
    );
  }
);

const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className, divider = false, children, ...props }, ref) => {
    const footerStyles = cn(
      'flex items-center justify-between',
      {
        'pt-4 mt-4 border-t border-gray-200': divider,
      },
      className
    );

    return (
      <div ref={ref} className={footerStyles} {...props}>
        {children}
      </div>
    );
  }
);

// 特殊卡片组件

export interface GameCardProps extends CardProps {
  title: string;
  description?: string;
  image?: string;
  badge?: string;
  status?: 'active' | 'maintenance' | 'inactive';
  onPlay?: () => void;
}

const GameCard = React.forwardRef<HTMLDivElement, GameCardProps>(
  ({
    className,
    title,
    description,
    image,
    badge,
    status = 'active',
    onPlay,
    ...props
  }, ref) => {
    const gameCardStyles = cn(
      'overflow-hidden cursor-pointer group',
      'hover:shadow-heavy hover:-translate-y-2',
      'transition-all duration-300',
      className
    );

    const statusColors = {
      active: 'bg-success-500',
      maintenance: 'bg-warning-500',
      inactive: 'bg-gray-500',
    };

    const statusTexts = {
      active: '可用',
      maintenance: '维护中',
      inactive: '暂停',
    };

    return (
      <Card
        ref={ref}
        className={gameCardStyles}
        padding="none"
        onClick={status === 'active' ? onPlay : undefined}
        {...props}
      >
        {/* 游戏图片/图标区域 */}
        <div className="relative h-40 bg-gradient-primary flex items-center justify-center overflow-hidden">
          {image ? (
            <img
              src={image}
              alt={title}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
            />
          ) : (
            <div className="text-white text-4xl font-bold">
              {title.charAt(0)}
            </div>
          )}
          
          {/* 状态徽章 */}
          {status !== 'active' && (
            <div className={cn(
              'absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-semibold text-white',
              statusColors[status]
            )}>
              {statusTexts[status]}
            </div>
          )}
          
          {/* 自定义徽章 */}
          {badge && status === 'active' && (
            <div className="absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-semibold bg-secondary-500 text-gray-900">
              {badge}
            </div>
          )}
          
          {/* 悬停遮罩 */}
          <div className="absolute inset-0 bg-black opacity-0 group-hover:opacity-20 transition-opacity duration-300" />
        </div>
        
        {/* 游戏信息 */}
        <div className="p-4">
          <h3 className="font-semibold text-lg text-gray-900 mb-1 group-hover:text-primary-600 transition-colors">
            {title}
          </h3>
          {description && (
            <p className="text-sm text-gray-600 line-clamp-2">
              {description}
            </p>
          )}
        </div>
      </Card>
    );
  }
);

export interface UserCardProps extends CardProps {
  user: {
    name: string;
    avatar?: string;
    vipLevel: number;
    balance: number;
  };
  showBalance?: boolean;
}

const UserCard = React.forwardRef<HTMLDivElement, UserCardProps>(
  ({
    className,
    user,
    showBalance = true,
    ...props
  }, ref) => {
    const userCardStyles = cn(
      'bg-gradient-primary text-white relative overflow-hidden',
      className
    );

    return (
      <Card
        ref={ref}
        className={userCardStyles}
        padding="lg"
        {...props}
      >
        {/* 背景装饰 */}
        <div className="absolute top-0 right-0 w-32 h-32 opacity-10">
          <div className="w-full h-full rounded-full border-4 border-white transform translate-x-8 -translate-y-8" />
        </div>
        
        <div className="relative z-10">
          {/* 用户头像和基本信息 */}
          <div className="flex items-center mb-4">
            <div className="w-16 h-16 rounded-full bg-white bg-opacity-20 flex items-center justify-center mr-4">
              {user.avatar ? (
                <img
                  src={user.avatar}
                  alt={user.name}
                  className="w-full h-full rounded-full object-cover"
                />
              ) : (
                <span className="text-2xl font-bold text-white">
                  {user.name.charAt(0).toUpperCase()}
                </span>
              )}
            </div>
            
            <div>
              <h2 className="text-xl font-bold text-white mb-1">
                {user.name}
              </h2>
              <div className="inline-flex items-center px-2 py-1 rounded-full bg-secondary-500 text-gray-900 text-xs font-semibold">
                VIP{user.vipLevel}
              </div>
            </div>
          </div>
          
          {/* 余额信息 */}
          {showBalance && (
            <div>
              <p className="text-white text-opacity-80 text-sm mb-1">
                账户余额
              </p>
              <p className="text-2xl font-bold text-white">
                ₦{user.balance.toLocaleString()}
              </p>
            </div>
          )}
        </div>
      </Card>
    );
  }
);

Card.displayName = 'Card';
CardHeader.displayName = 'CardHeader';
CardContent.displayName = 'CardContent';
CardFooter.displayName = 'CardFooter';
GameCard.displayName = 'GameCard';
UserCard.displayName = 'UserCard';

export { 
  Card, 
  CardHeader, 
  CardContent, 
  CardFooter,
  GameCard,
  UserCard
};