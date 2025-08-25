import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    ArrowLeft,
    Filter,
    Search,
    Download,
    Calendar,
    ArrowUpRight,
    ArrowDownLeft,
    Plus,
    Minus,
    TrendingUp,
    RefreshCw,
    Eye,
    CheckCircle,
    Clock,
    AlertCircle,
    XCircle,
    FileText,
    DollarSign
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { Card, CardContent, CardHeader } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Select } from '../../components/ui/Select';
import { Modal } from '../../components/ui/Modal';
import { cn } from '../../utils/cn';
import { formatCurrency, formatDateTime, formatRelativeTime } from '../../utils/format';

interface Transaction {
    id: string;
    type: 'DEPOSIT' | 'WITHDRAW' | 'BET' | 'WIN' | 'REWARD' | 'REFUND' | 'ADJUSTMENT' | 'TRANSFER';
    amount: number;
    fee: number;
    actualAmount: number;
    balanceBefore: number;
    balanceAfter: number;
    status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
    description: string;
    referenceId: string;
    gameType?: string;
    paymentMethod?: string;
    bankAccount?: string;
    createdAt: string;
    updatedAt: string;
    completedAt?: string;
    failureReason?: string;
    metadata?: Record<string, any>;
}

interface FilterOptions {
    type: string;
    status: string;
    dateFrom: string;
    dateTo: string;
    minAmount: string;
    maxAmount: string;
    searchQuery: string;
}

const TransactionHistoryPage: React.FC = () => {
    const navigate = useNavigate();
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [filteredTransactions, setFilteredTransactions] = useState<Transaction[]>([]);
    const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
    const [showDetailModal, setShowDetailModal] = useState(false);
    const [showFilterModal, setShowFilterModal] = useState(false);
    const [showExportModal, setShowExportModal] = useState(false);
    const [loading, setLoading] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [pageSize] = useState(20);

    // 筛选条件
    const [filters, setFilters] = useState<FilterOptions>({
        type: '',
        status: '',
        dateFrom: '',
        dateTo: '',
        minAmount: '',
        maxAmount: '',
        searchQuery: '',
    });

    // 模拟交易数据
    const mockTransactions: Transaction[] = [
        {
            id: 'TXN-20240120-001',
            type: 'DEPOSIT',
            amount: 5000,
            fee: 0,
            actualAmount: 5000,
            balanceBefore: 10000,
            balanceAfter: 15000,
            status: 'COMPLETED',
            description: '通过Paystack存款',
            referenceId: 'DEP-20240120-001',
            paymentMethod: 'Paystack',
            createdAt: '2024-01-20T10:30:00Z',
            updatedAt: '2024-01-20T10:35:00Z',
            completedAt: '2024-01-20T10:35:00Z',
        },
        {
            id: 'TXN-20240120-002',
            type: 'BET',
            amount: -200,
            fee: 0,
            actualAmount: -200,
            balanceBefore: 15000,
            balanceAfter: 14800,
            status: 'COMPLETED',
            description: '11选5投注 - 第20240120001期',
            referenceId: 'BET-20240120-002',
            gameType: '11选5',
            createdAt: '2024-01-20T09:15:00Z',
            updatedAt: '2024-01-20T09:15:00Z',
            completedAt: '2024-01-20T09:15:00Z',
            metadata: {
                drawNumber: '20240120001',
                betNumbers: [1, 3, 5, 7, 9],
                betType: '任选五',
                odds: 540,
            },
        },
        {
            id: 'TXN-20240120-003',
            type: 'WIN',
            amount: 1500,
            fee: 0,
            actualAmount: 1500,
            balanceBefore: 14800,
            balanceAfter: 16300,
            status: 'COMPLETED',
            description: '11选5中奖 - 第20240120001期',
            referenceId: 'WIN-20240120-003',
            gameType: '11选5',
            createdAt: '2024-01-20T09:20:00Z',
            updatedAt: '2024-01-20T09:20:00Z',
            completedAt: '2024-01-20T09:20:00Z',
            metadata: {
                drawNumber: '20240120001',
                winningNumbers: [1, 3, 5, 7, 9],
                prizeLevel: '五等奖',
                odds: 540,
            },
        },
        {
            id: 'TXN-20240119-004',
            type: 'WITHDRAW',
            amount: -3000,
            fee: -30,
            actualAmount: -3030,
            balanceBefore: 16300,
            balanceAfter: 13270,
            status: 'PROCESSING',
            description: '提款到Access Bank',
            referenceId: 'WTH-20240119-004',
            bankAccount: 'Access Bank - ****6789',
            createdAt: '2024-01-19T16:45:00Z',
            updatedAt: '2024-01-19T17:00:00Z',
        },
        {
            id: 'TXN-20240119-005',
            type: 'REWARD',
            amount: 150,
            fee: 0,
            actualAmount: 150,
            balanceBefore: 13270,
            balanceAfter: 13420,
            status: 'COMPLETED',
            description: 'VIP返水奖励',
            referenceId: 'RWD-20240119-005',
            createdAt: '2024-01-19T00:00:00Z',
            updatedAt: '2024-01-19T00:00:00Z',
            completedAt: '2024-01-19T00:00:00Z',
            metadata: {
                vipLevel: 2,
                rebateRate: 0.008,
                validTurnover: 18750,
            },
        },
        {
            id: 'TXN-20240118-006',
            type: 'DEPOSIT',
            amount: 2000,
            fee: 0,
            actualAmount: 2000,
            balanceBefore: 11270,
            balanceAfter: 13270,
            status: 'FAILED',
            description: '银行转账存款',
            referenceId: 'DEP-20240118-006',
            paymentMethod: '银行转账',
            createdAt: '2024-01-18T14:20:00Z',
            updatedAt: '2024-01-18T15:30:00Z',
            failureReason: '银行账户信息不匹配',
        },
    ];

    // 交易类型配置
    const transactionConfig = {
        DEPOSIT: {
            icon: ArrowDownLeft,
            color: 'text-success-600',
            bgColor: 'bg-success-100',
            label: '存款',
        },
        WITHDRAW: {
            icon: ArrowUpRight,
            color: 'text-warning-600',
            bgColor: 'bg-warning-100',
            label: '提款',
        },
        BET: {
            icon: Minus,
            color: 'text-danger-600',
            bgColor: 'bg-danger-100',
            label: '投注',
        },
        WIN: {
            icon: Plus,
            color: 'text-success-600',
            bgColor: 'bg-success-100',
            label: '中奖',
        },
        REWARD: {
            icon: TrendingUp,
            color: 'text-secondary-600',
            bgColor: 'bg-secondary-100',
            label: '奖励',
        },
        REFUND: {
            icon: RefreshCw,
            color: 'text-info-600',
            bgColor: 'bg-info-100',
            label: '退款',
        },
        ADJUSTMENT: {
            icon: DollarSign,
            color: 'text-gray-600',
            bgColor: 'bg-gray-100',
            label: '调整',
        },
        TRANSFER: {
            icon: ArrowUpRight,
            color: 'text-primary-600',
            bgColor: 'bg-primary-100',
            label: '转账',
        },
    };

    // 状态配置
    const statusConfig = {
        COMPLETED: {
            icon: CheckCircle,
            color: 'text-success-600',
            bgColor: 'bg-success-100',
            label: '已完成',
        },
        PROCESSING: {
            icon: Clock,
            color: 'text-warning-600',
            bgColor: 'bg-warning-100',
            label: '处理中',
        },
        PENDING: {
            icon: AlertCircle,
            color: 'text-info-600',
            bgColor: 'bg-info-100',
            label: '待处理',
        },
        FAILED: {
            icon: XCircle,
            color: 'text-danger-600',
            bgColor: 'bg-danger-100',
            label: '失败',
        },
        CANCELLED: {
            icon: XCircle,
            color: 'text-gray-600',
            bgColor: 'bg-gray-100',
            label: '已取消',
        },
    };

    // 筛选选项
    const typeOptions = [
        { value: '', label: '全部类型' },
        { value: 'DEPOSIT', label: '存款' },
        { value: 'WITHDRAW', label: '提款' },
        { value: 'BET', label: '投注' },
        { value: 'WIN', label: '中奖' },
        { value: 'REWARD', label: '奖励' },
        { value: 'REFUND', label: '退款' },
        { value: 'ADJUSTMENT', label: '调整' },
        { value: 'TRANSFER', label: '转账' },
    ];

    const statusOptions = [
        { value: '', label: '全部状态' },
        { value: 'COMPLETED', label: '已完成' },
        { value: 'PROCESSING', label: '处理中' },
        { value: 'PENDING', label: '待处理' },
        { value: 'FAILED', label: '失败' },
        { value: 'CANCELLED', label: '已取消' },
    ];

    // 快捷时间范围
    const quickDateRanges = [
        { label: '今天', days: 0 },
        { label: '最近7天', days: 7 },
        { label: '最近30天', days: 30 },
        { label: '最近90天', days: 90 },
    ];

    useEffect(() => {
        loadTransactions();
    }, [currentPage, filters]);

    useEffect(() => {
        applyFilters();
    }, [transactions, filters]);

    const loadTransactions = async () => {
        setLoading(true);
        try {
            // 模拟API调用
            await new Promise(resolve => setTimeout(resolve, 500));
            setTransactions(mockTransactions);
            setTotalPages(Math.ceil(mockTransactions.length / pageSize));
        } catch (error) {
            console.error('Load transactions error:', error);
        } finally {
            setLoading(false);
        }
    };

    const applyFilters = () => {
        let filtered = [...transactions];

        // 类型筛选
        if (filters.type) {
            filtered = filtered.filter(t => t.type === filters.type);
        }

        // 状态筛选
        if (filters.status) {
            filtered = filtered.filter(t => t.status === filters.status);
        }

        // 日期范围筛选
        if (filters.dateFrom) {
            filtered = filtered.filter(t => new Date(t.createdAt) >= new Date(filters.dateFrom));
        }
        if (filters.dateTo) {
            filtered = filtered.filter(t => new Date(t.createdAt) <= new Date(filters.dateTo));
        }

        // 金额范围筛选
        if (filters.minAmount) {
            filtered = filtered.filter(t => Math.abs(t.amount) >= parseFloat(filters.minAmount));
        }
        if (filters.maxAmount) {
            filtered = filtered.filter(t => Math.abs(t.amount) <= parseFloat(filters.maxAmount));
        }

        // 搜索筛选
        if (filters.searchQuery) {
            const query = filters.searchQuery.toLowerCase();
            filtered = filtered.filter(t =>
                t.id.toLowerCase().includes(query) ||
                t.referenceId.toLowerCase().includes(query) ||
                t.description.toLowerCase().includes(query)
            );
        }

        setFilteredTransactions(filtered);
    };

    const handleFilterChange = (key: keyof FilterOptions, value: string) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const handleQuickDateRange = (days: number) => {
        const today = new Date();
        const fromDate = new Date(today);
        fromDate.setDate(today.getDate() - days);

        setFilters(prev => ({
            ...prev,
            dateFrom: days === 0 ? today.toISOString().split('T')[0] : fromDate.toISOString().split('T')[0],
            dateTo: today.toISOString().split('T')[0],
        }));
    };

    const clearFilters = () => {
        setFilters({
            type: '',
            status: '',
            dateFrom: '',
            dateTo: '',
            minAmount: '',
            maxAmount: '',
            searchQuery: '',
        });
    };

    const handleViewDetails = (transaction: Transaction) => {
        setSelectedTransaction(transaction);
        setShowDetailModal(true);
    };

    const handleExport = async (format: 'pdf' | 'excel') => {
        try {
            const response = await fetch('/api/v1/finance/transactions/export/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                body: JSON.stringify({
                    format,
                    filters,
                    transactions: filteredTransactions.map(t => t.id),
                }),
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `transactions_${new Date().toISOString().split('T')[0]}.${format === 'pdf' ? 'pdf' : 'xlsx'}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                setShowExportModal(false);
            }
        } catch (error) {
            console.error('Export error:', error);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
            {/* 页面头部 */}
            <div className="bg-white border-b border-gray-200 px-4 py-4 lg:px-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <Button
                            variant="ghost"
                            size="sm"
                            icon={<ArrowLeft className="w-4 h-4" />}
                            onClick={() => navigate('/wallet')}
                        >
                            返回
                        </Button>
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">交易记录</h1>
                            <p className="text-sm text-gray-600 mt-1">
                                查看您的所有交易记录和详细信息
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center space-x-2">
                        <Button
                            variant="ghost"
                            size="sm"
                            icon={<RefreshCw className="w-4 h-4" />}
                            onClick={loadTransactions}
                            disabled={loading}
                        >
                            刷新
                        </Button>
                        <Button
                            variant="ghost"
                            size="sm"
                            icon={<Download className="w-4 h-4" />}
                            onClick={() => setShowExportModal(true)}
                        >
                            导出
                        </Button>
                    </div>
                </div>
            </div>

            <div className="container-responsive py-6 space-y-6">
                {/* 筛选和搜索 */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <Card>
                        <CardContent className="p-4">
                            <div className="space-y-4">
                                {/* 搜索框 */}
                                <div className="relative">
                                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                                    <Input
                                        value={filters.searchQuery}
                                        onChange={(e) => handleFilterChange('searchQuery', e.target.value)}
                                        placeholder="搜索交易ID、参考号或描述..."
                                        className="pl-10"
                                    />
                                </div>

                                {/* 快捷筛选 */}
                                <div className="flex flex-wrap gap-2">
                                    {quickDateRanges.map((range) => (
                                        <Button
                                            key={range.label}
                                            variant="outline"
                                            size="sm"
                                            onClick={() => handleQuickDateRange(range.days)}
                                            className="text-xs"
                                        >
                                            {range.label}
                                        </Button>
                                    ))}
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        icon={<Filter className="w-3 h-3" />}
                                        onClick={() => setShowFilterModal(true)}
                                        className="text-xs"
                                    >
                                        高级筛选
                                    </Button>
                                    {(filters.type || filters.status || filters.dateFrom || filters.dateTo || filters.minAmount || filters.maxAmount) && (
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={clearFilters}
                                            className="text-xs text-danger-600"
                                        >
                                            清除筛选
                                        </Button>
                                    )}
                                </div>

                                {/* 基础筛选 */}
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                    <Select
                                        value={filters.type}
                                        onChange={(value) => handleFilterChange('type', value)}
                                        placeholder="交易类型"
                                        options={typeOptions}
                                    />
                                    <Select
                                        value={filters.status}
                                        onChange={(value) => handleFilterChange('status', value)}
                                        placeholder="交易状态"
                                        options={statusOptions}
                                    />
                                    <Input
                                        type="date"
                                        value={filters.dateFrom}
                                        onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                                        placeholder="开始日期"
                                    />
                                    <Input
                                        type="date"
                                        value={filters.dateTo}
                                        onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                                        placeholder="结束日期"
                                    />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                {/* 交易统计 */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                    className="grid grid-cols-1 md:grid-cols-4 gap-4"
                >
                    <Card className="text-center">
                        <CardContent className="p-4">
                            <div className="text-2xl font-bold text-gray-900 mb-1">
                                {filteredTransactions.length}
                            </div>
                            <div className="text-sm text-gray-600">总交易数</div>
                        </CardContent>
                    </Card>
                    <Card className="text-center">
                        <CardContent className="p-4">
                            <div className="text-2xl font-bold text-success-600 mb-1">
                                {formatCurrency(
                                    filteredTransactions
                                        .filter(t => t.amount > 0 && t.status === 'COMPLETED')
                                        .reduce((sum, t) => sum + t.amount, 0)
                                )}
                            </div>
                            <div className="text-sm text-gray-600">总收入</div>
                        </CardContent>
                    </Card>
                    <Card className="text-center">
                        <CardContent className="p-4">
                            <div className="text-2xl font-bold text-danger-600 mb-1">
                                {formatCurrency(
                                    Math.abs(filteredTransactions
                                        .filter(t => t.amount < 0 && t.status === 'COMPLETED')
                                        .reduce((sum, t) => sum + t.amount, 0))
                                )}
                            </div>
                            <div className="text-sm text-gray-600">总支出</div>
                        </CardContent>
                    </Card>
                    <Card className="text-center">
                        <CardContent className="p-4">
                            <div className="text-2xl font-bold text-primary-600 mb-1">
                                {formatCurrency(
                                    filteredTransactions
                                        .filter(t => t.status === 'COMPLETED')
                                        .reduce((sum, t) => sum + t.amount, 0)
                                )}
                            </div>
                            <div className="text-sm text-gray-600">净收益</div>
                        </CardContent>
                    </Card>
                </motion.div>

                {/* 交易记录列表 */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                >
                    <Card>
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <h2 className="text-lg font-semibold text-gray-900">
                                    交易记录 ({filteredTransactions.length})
                                </h2>
                            </div>
                        </CardHeader>
                        <CardContent className="p-0">
                            {loading ? (
                                <div className="p-8 text-center">
                                    <RefreshCw className="w-8 h-8 text-gray-400 mx-auto mb-4 animate-spin" />
                                    <p className="text-gray-600">加载中...</p>
                                </div>
                            ) : filteredTransactions.length === 0 ? (
                                <div className="p-8 text-center">
                                    <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                                    <p className="text-gray-600 mb-2">暂无交易记录</p>
                                    <p className="text-sm text-gray-500">尝试调整筛选条件或时间范围</p>
                                </div>
                            ) : (
                                <div className="divide-y divide-gray-200">
                                    {filteredTransactions.map((transaction, index) => {
                                        const typeConfig = transactionConfig[transaction.type];
                                        const statusConfig_ = statusConfig[transaction.status];
                                        const TypeIcon = typeConfig.icon;
                                        const StatusIcon = statusConfig_.icon;

                                        return (
                                            <motion.div
                                                key={transaction.id}
                                                initial={{ opacity: 0, x: -20 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ duration: 0.3, delay: index * 0.05 }}
                                                className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                                                onClick={() => handleViewDetails(transaction)}
                                            >
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center space-x-4">
                                                        {/* 交易类型图标 */}
                                                        <div className={cn(
                                                            'w-12 h-12 rounded-full flex items-center justify-center',
                                                            typeConfig.bgColor
                                                        )}>
                                                            <TypeIcon className={cn('w-6 h-6', typeConfig.color)} />
                                                        </div>

                                                        {/* 交易信息 */}
                                                        <div className="flex-1 min-w-0">
                                                            <div className="flex items-center space-x-2 mb-1">
                                                                <h3 className="font-medium text-gray-900 truncate">
                                                                    {transaction.description}
                                                                </h3>
                                                                <span className={cn(
                                                                    'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                                                                    statusConfig_.bgColor,
                                                                    statusConfig_.color
                                                                )}>
                                                                    <StatusIcon className="w-3 h-3 mr-1" />
                                                                    {statusConfig_.label}
                                                                </span>
                                                            </div>

                                                            <div className="flex items-center space-x-4 text-sm text-gray-500">
                                                                <span>{formatDateTime(transaction.createdAt, 'MM-dd HH:mm')}</span>
                                                                <span>{transaction.referenceId}</span>
                                                                {transaction.gameType && (
                                                                    <span className="text-primary-600">{transaction.gameType}</span>
                                                                )}
                                                                {transaction.paymentMethod && (
                                                                    <span>{transaction.paymentMethod}</span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* 金额和余额变化 */}
                                                    <div className="text-right">
                                                        <p className={cn(
                                                            'font-bold text-lg',
                                                            transaction.amount > 0 ? 'text-success-600' : 'text-gray-900'
                                                        )}>
                                                            {transaction.amount > 0 ? '+' : ''}
                                                            {formatCurrency(transaction.amount)}
                                                        </p>
                                                        {transaction.fee !== 0 && (
                                                            <p className="text-xs text-gray-500">
                                                                手续费: {formatCurrency(Math.abs(transaction.fee))}
                                                            </p>
                                                        )}
                                                        <p className="text-xs text-gray-500 mt-1">
                                                            余额: {formatCurrency(transaction.balanceAfter)}
                                                        </p>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        );
                                    })}
                                </div>
                            )}

                            {/* 分页 */}
                            {filteredTransactions.length > 0 && totalPages > 1 && (
                                <div className="p-4 border-t border-gray-200">
                                    <div className="flex items-center justify-between">
                                        <p className="text-sm text-gray-600">
                                            显示 {(currentPage - 1) * pageSize + 1} - {Math.min(currentPage * pageSize, filteredTransactions.length)} 条，
                                            共 {filteredTransactions.length} 条记录
                                        </p>
                                        <div className="flex items-center space-x-2">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                                                disabled={currentPage === 1}
                                            >
                                                上一页
                                            </Button>
                                            <span className="text-sm text-gray-600">
                                                {currentPage} / {totalPages}
                                            </span>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                                                disabled={currentPage === totalPages}
                                            >
                                                下一页
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </motion.div>
            </div>

            {/* 交易详情弹窗 */}
            <Modal
                isOpen={showDetailModal}
                onClose={() => setShowDetailModal(false)}
                title="交易详情"
                size="md"
            >
                {selectedTransaction && (
                    <div className="p-6">
                        <div className="space-y-6">
                            {/* 基本信息 */}
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">基本信息</h3>
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <span className="text-gray-600">交易ID:</span>
                                        <p className="font-mono text-gray-900">{selectedTransaction.id}</p>
                                    </div>
                                    <div>
                                        <span className="text-gray-600">参考号:</span>
                                        <p className="font-mono text-gray-900">{selectedTransaction.referenceId}</p>
                                    </div>
                                    <div>
                                        <span className="text-gray-600">交易类型:</span>
                                        <p className="text-gray-900">{transactionConfig[selectedTransaction.type].label}</p>
                                    </div>
                                    <div>
                                        <span className="text-gray-600">交易状态:</span>
                                        <span className={cn(
                                            'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                                            statusConfig[selectedTransaction.status].bgColor,
                                            statusConfig[selectedTransaction.status].color
                                        )}>
                                            {statusConfig[selectedTransaction.status].label}
                                        </span>
                                    </div>
                                    <div>
                                        <span className="text-gray-600">创建时间:</span>
                                        <p className="text-gray-900">{formatDateTime(selectedTransaction.createdAt)}</p>
                                    </div>
                                    {selectedTransaction.completedAt && (
                                        <div>
                                            <span className="text-gray-600">完成时间:</span>
                                            <p className="text-gray-900">{formatDateTime(selectedTransaction.completedAt)}</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* 金额信息 */}
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">金额信息</h3>
                                <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">交易金额:</span>
                                        <span className={cn(
                                            'font-bold',
                                            selectedTransaction.amount > 0 ? 'text-success-600' : 'text-gray-900'
                                        )}>
                                            {selectedTransaction.amount > 0 ? '+' : ''}
                                            {formatCurrency(selectedTransaction.amount)}
                                        </span>
                                    </div>
                                    {selectedTransaction.fee !== 0 && (
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">手续费:</span>
                                            <span className="text-warning-600">
                                                {formatCurrency(Math.abs(selectedTransaction.fee))}
                                            </span>
                                        </div>
                                    )}
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">实际金额:</span>
                                        <span className="font-bold text-gray-900">
                                            {selectedTransaction.actualAmount > 0 ? '+' : ''}
                                            {formatCurrency(selectedTransaction.actualAmount)}
                                        </span>
                                    </div>
                                    <div className="border-t border-gray-200 pt-3">
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">交易前余额:</span>
                                            <span className="text-gray-900">{formatCurrency(selectedTransaction.balanceBefore)}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">交易后余额:</span>
                                            <span className="font-bold text-gray-900">{formatCurrency(selectedTransaction.balanceAfter)}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* 附加信息 */}
                            {(selectedTransaction.gameType || selectedTransaction.paymentMethod || selectedTransaction.bankAccount) && (
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">附加信息</h3>
                                    <div className="grid grid-cols-1 gap-3 text-sm">
                                        {selectedTransaction.gameType && (
                                            <div>
                                                <span className="text-gray-600">游戏类型:</span>
                                                <p className="text-gray-900">{selectedTransaction.gameType}</p>
                                            </div>
                                        )}
                                        {selectedTransaction.paymentMethod && (
                                            <div>
                                                <span className="text-gray-600">支付方式:</span>
                                                <p className="text-gray-900">{selectedTransaction.paymentMethod}</p>
                                            </div>
                                        )}
                                        {selectedTransaction.bankAccount && (
                                            <div>
                                                <span className="text-gray-600">银行账户:</span>
                                                <p className="text-gray-900">{selectedTransaction.bankAccount}</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* 游戏详情 */}
                            {selectedTransaction.metadata && (
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">详细信息</h3>
                                    <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                                        {Object.entries(selectedTransaction.metadata).map(([key, value]) => (
                                            <div key={key} className="flex justify-between">
                                                <span className="text-gray-600 capitalize">{key.replace(/([A-Z])/g, ' $1')}:</span>
                                                <span className="text-gray-900">
                                                    {Array.isArray(value) ? value.join(', ') : String(value)}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* 失败原因 */}
                            {selectedTransaction.failureReason && (
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">失败原因</h3>
                                    <div className="bg-danger-50 border border-danger-200 rounded-lg p-4">
                                        <p className="text-danger-800 text-sm">{selectedTransaction.failureReason}</p>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="flex justify-end mt-6">
                            <Button
                                variant="outline"
                                onClick={() => setShowDetailModal(false)}
                            >
                                关闭
                            </Button>
                        </div>
                    </div>
                )}
            </Modal>

            {/* 高级筛选弹窗 */}
            <Modal
                isOpen={showFilterModal}
                onClose={() => setShowFilterModal(false)}
                title="高级筛选"
                size="md"
            >
                <div className="p-6">
                    <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    最小金额
                                </label>
                                <Input
                                    type="number"
                                    value={filters.minAmount}
                                    onChange={(e) => handleFilterChange('minAmount', e.target.value)}
                                    placeholder="0"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    最大金额
                                </label>
                                <Input
                                    type="number"
                                    value={filters.maxAmount}
                                    onChange={(e) => handleFilterChange('maxAmount', e.target.value)}
                                    placeholder="无限制"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="flex space-x-3 mt-6">
                        <Button
                            variant="outline"
                            fullWidth
                            onClick={() => setShowFilterModal(false)}
                        >
                            取消
                        </Button>
                        <Button
                            variant="primary"
                            fullWidth
                            onClick={() => setShowFilterModal(false)}
                        >
                            应用筛选
                        </Button>
                    </div>
                </div>
            </Modal>

            {/* 导出弹窗 */}
            <Modal
                isOpen={showExportModal}
                onClose={() => setShowExportModal(false)}
                title="导出交易记录"
                size="sm"
            >
                <div className="p-6">
                    <div className="space-y-4">
                        <p className="text-gray-600 text-sm">
                            选择导出格式，将导出当前筛选条件下的所有交易记录
                        </p>

                        <div className="space-y-3">
                            <Button
                                variant="outline"
                                fullWidth
                                icon={<FileText className="w-4 h-4" />}
                                onClick={() => handleExport('pdf')}
                                className="justify-start"
                            >
                                导出为 PDF
                            </Button>
                            <Button
                                variant="outline"
                                fullWidth
                                icon={<FileText className="w-4 h-4" />}
                                onClick={() => handleExport('excel')}
                                className="justify-start"
                            >
                                导出为 Excel
                            </Button>
                        </div>

                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                            <p className="text-xs text-blue-800">
                                <AlertCircle className="w-3 h-3 inline mr-1" />
                                导出文件将包含当前筛选的 {filteredTransactions.length} 条记录
                            </p>
                        </div>
                    </div>

                    <div className="flex space-x-3 mt-6">
                        <Button
                            variant="outline"
                            fullWidth
                            onClick={() => setShowExportModal(false)}
                        >
                            取消
                        </Button>
                    </div>
                </div>
            </Modal>
        </div>
    );
};

export default TransactionHistoryPage;