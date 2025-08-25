import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowLeft,
  Building,
  Plus,
  Edit,
  Trash2,
  Star,
  AlertCircle,
  CheckCircle,
  Clock,
  Eye,
  EyeOff,
  Shield,
  Info,
  CreditCard,
  User,
  Calendar,
  DollarSign
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { Card, CardContent, CardHeader } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import { Select } from '../../components/ui/Select';
import { cn } from '../../utils/cn';
import { formatCurrency, formatDateTime, formatRelativeTime } from '../../utils/format';

interface BankAccount {
  id: string;
  bankName: string;
  bankCode: string;
  accountNumber: string;
  accountName: string;
  isDefault: boolean;
  isVerified: boolean;
  createdAt: string;
}

interface WithdrawRequest {
  id: string;
  amount: number;
  fee: number;
  netAmount: number;
  bankAccount: BankAccount;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  reference: string;
  createdAt: string;
  processedAt?: string;
  estimatedArrival?: string;
  reason?: string;
}

interface VIPLimits {
  level: number;
  dailyLimit: number;
  remainingDaily: number;
  dailyTimes: number;
  remainingTimes: number;
  minAmount: number;
  maxAmount: number;
  feeRate: number;
}

const WithdrawPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'withdraw' | 'accounts' | 'history'>('withdraw');
  const [selectedBankId, setSelectedBankId] = useState<string>('');
  const [amount, setAmount] = useState<string>('');
  const [withdrawPassword, setWithdrawPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showAddBankModal, setShowAddBankModal] = useState(false);
  const [showEditBankModal, setShowEditBankModal] = useState(false);
  const [editingBank, setEditingBank] = useState<BankAccount | null>(null);

  // 新增银行账户表单
  const [newBankForm, setNewBankForm] = useState({
    bankCode: '',
    accountNumber: '',
    accountName: '',
  });

  // 模拟用户余额和VIP信息
  const userBalance = {
    availableBalance: 15420.50,
    mainBalance: 18270.50,
    bonusBalance: 2850.00,
    frozenBalance: 500.00,
  };

  const vipLimits: VIPLimits = {
    level: 2,
    dailyLimit: 50000,
    remainingDaily: 35000,
    dailyTimes: 5,
    remainingTimes: 3,
    minAmount: 100,
    maxAmount: 50000,
    feeRate: 0.01, // 1.0%
  };

  // 模拟银行账户数据
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([
    {
      id: '1',
      bankName: 'Access Bank',
      bankCode: '044',
      accountNumber: '0123456789',
      accountName: 'John Doe',
      isDefault: true,
      isVerified: true,
      createdAt: '2024-01-15T10:00:00Z',
    },
    {
      id: '2',
      bankName: 'GTBank',
      bankCode: '058',
      accountNumber: '0987654321',
      accountName: 'John Doe',
      isDefault: false,
      isVerified: true,
      createdAt: '2024-01-10T14:30:00Z',
    },
  ]);

  // 模拟提款记录
  const withdrawHistory: WithdrawRequest[] = [
    {
      id: '1',
      amount: 5000,
      fee: 50,
      netAmount: 4950,
      bankAccount: bankAccounts[0],
      status: 'COMPLETED',
      reference: 'WTH-20240120-001',
      createdAt: '2024-01-20T10:30:00Z',
      processedAt: '2024-01-20T11:45:00Z',
      estimatedArrival: '2024-01-20T16:00:00Z',
    },
    {
      id: '2',
      amount: 3000,
      fee: 30,
      netAmount: 2970,
      bankAccount: bankAccounts[1],
      status: 'PROCESSING',
      reference: 'WTH-20240119-002',
      createdAt: '2024-01-19T16:45:00Z',
      estimatedArrival: '2024-01-20T10:00:00Z',
    },
    {
      id: '3',
      amount: 2000,
      fee: 20,
      netAmount: 1980,
      bankAccount: bankAccounts[0],
      status: 'PENDING',
      reference: 'WTH-20240119-003',
      createdAt: '2024-01-19T14:20:00Z',
      estimatedArrival: '2024-01-20T08:00:00Z',
    },
  ];

  // 尼日利亚主要银行列表
  const nigerianBanks = [
    { code: '044', name: 'Access Bank' },
    { code: '014', name: 'Afribank Nigeria Plc' },
    { code: '023', name: 'Citibank Nigeria Limited' },
    { code: '050', name: 'Ecobank Nigeria Plc' },
    { code: '084', name: 'Enterprise Bank Limited' },
    { code: '070', name: 'Fidelity Bank Plc' },
    { code: '011', name: 'First Bank of Nigeria Limited' },
    { code: '214', name: 'First City Monument Bank Plc' },
    { code: '058', name: 'Guaranty Trust Bank Plc' },
    { code: '030', name: 'Heritage Banking Company Ltd' },
    { code: '082', name: 'Keystone Bank Limited' },
    { code: '076', name: 'Skye Bank Plc' },
    { code: '068', name: 'Standard Chartered Bank Nigeria Limited' },
    { code: '232', name: 'Sterling Bank Plc' },
    { code: '032', name: 'Union Bank of Nigeria Plc' },
    { code: '033', name: 'United Bank for Africa Plc' },
    { code: '215', name: 'Unity Bank Plc' },
    { code: '035', name: 'Wema Bank Plc' },
    { code: '057', name: 'Zenith Bank Plc' },
  ];

  const withdrawAmount = parseFloat(amount) || 0;
  const calculatedFee = withdrawAmount * vipLimits.feeRate;
  const netAmount = withdrawAmount - calculatedFee;
  const selectedBank = bankAccounts.find(bank => bank.id === selectedBankId);

  // 状态配置
  const statusConfig = {
    PENDING: {
      icon: Clock,
      color: 'text-warning-600',
      bgColor: 'bg-warning-100',
      label: '待处理',
    },
    PROCESSING: {
      icon: AlertCircle,
      color: 'text-info-600',
      bgColor: 'bg-info-100',
      label: '处理中',
    },
    COMPLETED: {
      icon: CheckCircle,
      color: 'text-success-600',
      bgColor: 'bg-success-100',
      label: '已完成',
    },
    FAILED: {
      icon: AlertCircle,
      color: 'text-danger-600',
      bgColor: 'bg-danger-100',
      label: '失败',
    },
    CANCELLED: {
      icon: AlertCircle,
      color: 'text-gray-600',
      bgColor: 'bg-gray-100',
      label: '已取消',
    },
  };

  const handleAmountChange = (value: string) => {
    const numericValue = value.replace(/[^0-9.]/g, '');
    setAmount(numericValue);
  };

  const handleWithdraw = () => {
    if (!selectedBankId || !amount || !withdrawPassword || withdrawAmount < vipLimits.minAmount) {
      return;
    }
    setShowConfirmModal(true);
  };

  const handleConfirmWithdraw = async () => {
    try {
      // 调用提款API
      const response = await fetch('/api/v1/finance/withdraw/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          bank_account_id: selectedBankId,
          amount: withdrawAmount,
          withdraw_password: withdrawPassword,
        }),
      });

      if (response.ok) {
        setShowConfirmModal(false);
        setAmount('');
        setWithdrawPassword('');
        setActiveTab('history');
        // 显示成功消息
      }
    } catch (error) {
      console.error('Withdraw error:', error);
    }
  };

  const handleAddBank = async () => {
    try {
      const response = await fetch('/api/v1/finance/bank-accounts/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(newBankForm),
      });

      if (response.ok) {
        const newBank = await response.json();
        setBankAccounts([...bankAccounts, newBank]);
        setShowAddBankModal(false);
        setNewBankForm({ bankCode: '', accountNumber: '', accountName: '' });
      }
    } catch (error) {
      console.error('Add bank error:', error);
    }
  };

  const handleEditBank = async () => {
    if (!editingBank) return;

    try {
      const response = await fetch(`/api/v1/finance/bank-accounts/${editingBank.id}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(newBankForm),
      });

      if (response.ok) {
        const updatedBank = await response.json();
        setBankAccounts(bankAccounts.map(bank => 
          bank.id === editingBank.id ? updatedBank : bank
        ));
        setShowEditBankModal(false);
        setEditingBank(null);
        setNewBankForm({ bankCode: '', accountNumber: '', accountName: '' });
      }
    } catch (error) {
      console.error('Edit bank error:', error);
    }
  };

  const handleDeleteBank = async (bankId: string) => {
    if (window.confirm('确定要删除这个银行账户吗？')) {
      try {
        const response = await fetch(`/api/v1/finance/bank-accounts/${bankId}/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        });

        if (response.ok) {
          setBankAccounts(bankAccounts.filter(bank => bank.id !== bankId));
        }
      } catch (error) {
        console.error('Delete bank error:', error);
      }
    }
  };

  const handleSetDefaultBank = async (bankId: string) => {
    try {
      const response = await fetch(`/api/v1/finance/bank-accounts/${bankId}/set-default/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        setBankAccounts(bankAccounts.map(bank => ({
          ...bank,
          isDefault: bank.id === bankId,
        })));
      }
    } catch (error) {
      console.error('Set default bank error:', error);
    }
  };

  const openEditModal = (bank: BankAccount) => {
    setEditingBank(bank);
    setNewBankForm({
      bankCode: bank.bankCode,
      accountNumber: bank.accountNumber,
      accountName: bank.accountName,
    });
    setShowEditBankModal(true);
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
      {/* 页面头部 */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 lg:px-6">
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
            <h1 className="text-2xl font-bold text-gray-900">提款</h1>
            <p className="text-sm text-gray-600 mt-1">
              安全快捷地提取您的资金
            </p>
          </div>
        </div>
      </div>

      {/* 标签页导航 */}
      <div className="bg-white border-b border-gray-200">
        <div className="container-responsive">
          <div className="flex space-x-8">
            {[
              { key: 'withdraw', label: '申请提款', icon: DollarSign },
              { key: 'accounts', label: '银行账户', icon: Building },
              { key: 'history', label: '提款记录', icon: Calendar },
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={cn(
                    'flex items-center space-x-2 py-4 border-b-2 transition-colors',
                    activeTab === tab.key
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <div className="container-responsive py-6">
        {/* 申请提款标签页 */}
        {activeTab === 'withdraw' && (
          <div className="space-y-6">
            {/* 余额和限额信息 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card>
                <CardHeader>
                  <h2 className="text-lg font-semibold text-gray-900">账户信息</h2>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* 余额信息 */}
                    <div className="space-y-4">
                      <h3 className="font-medium text-gray-900">可用余额</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center p-3 bg-success-50 rounded-lg">
                          <span className="text-sm text-gray-600">可提款余额</span>
                          <span className="text-lg font-bold text-success-600">
                            {formatCurrency(userBalance.availableBalance)}
                          </span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">主余额</span>
                          <span className="font-semibold">{formatCurrency(userBalance.mainBalance)}</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">奖金余额</span>
                          <span className="font-semibold">{formatCurrency(userBalance.bonusBalance)}</span>
                        </div>
                      </div>
                    </div>

                    {/* VIP限额信息 */}
                    <div className="space-y-4">
                      <h3 className="font-medium text-gray-900">VIP{vipLimits.level} 提款权益</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center p-3 bg-primary-50 rounded-lg">
                          <span className="text-sm text-gray-600">今日剩余额度</span>
                          <span className="font-bold text-primary-600">
                            {formatCurrency(vipLimits.remainingDaily)}
                          </span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">今日剩余次数</span>
                          <span className="font-semibold">{vipLimits.remainingTimes} 次</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">手续费率</span>
                          <span className="font-semibold">{(vipLimits.feeRate * 100).toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">单笔限额</span>
                          <span className="font-semibold text-xs">
                            {formatCurrency(vipLimits.minAmount)} - {formatCurrency(vipLimits.maxAmount)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* 提款表单 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <Card>
                <CardHeader>
                  <h2 className="text-lg font-semibold text-gray-900">提款申请</h2>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* 银行账户选择 */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        选择银行账户
                      </label>
                      <Select
                        value={selectedBankId}
                        onChange={setSelectedBankId}
                        placeholder="请选择银行账户"
                        options={bankAccounts.map(bank => ({
                          value: bank.id,
                          label: `${bank.bankName} - ${bank.accountNumber} ${bank.isDefault ? '(默认)' : ''}`,
                        }))}
                      />
                      {bankAccounts.length === 0 && (
                        <p className="text-sm text-gray-500 mt-2">
                          您还没有添加银行账户，请先
                          <button
                            onClick={() => setActiveTab('accounts')}
                            className="text-primary-600 hover:text-primary-700 font-medium"
                          >
                            添加银行账户
                          </button>
                        </p>
                      )}
                    </div>

                    {/* 提款金额 */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        提款金额 (₦)
                      </label>
                      <Input
                        value={amount}
                        onChange={(e) => handleAmountChange(e.target.value)}
                        placeholder="请输入提款金额"
                        variant="outlined"
                        inputSize="lg"
                        className="text-center text-xl font-semibold"
                      />
                      
                      {/* 金额验证提示 */}
                      {withdrawAmount > 0 && (
                        <div className="mt-2 text-sm">
                          {withdrawAmount < vipLimits.minAmount ? (
                            <p className="text-danger-600 flex items-center">
                              <AlertCircle className="w-4 h-4 mr-1" />
                              最小提款金额: {formatCurrency(vipLimits.minAmount)}
                            </p>
                          ) : withdrawAmount > vipLimits.maxAmount ? (
                            <p className="text-danger-600 flex items-center">
                              <AlertCircle className="w-4 h-4 mr-1" />
                              最大提款金额: {formatCurrency(vipLimits.maxAmount)}
                            </p>
                          ) : withdrawAmount > vipLimits.remainingDaily ? (
                            <p className="text-danger-600 flex items-center">
                              <AlertCircle className="w-4 h-4 mr-1" />
                              超出今日剩余额度: {formatCurrency(vipLimits.remainingDaily)}
                            </p>
                          ) : withdrawAmount > userBalance.availableBalance ? (
                            <p className="text-danger-600 flex items-center">
                              <AlertCircle className="w-4 h-4 mr-1" />
                              余额不足
                            </p>
                          ) : (
                            <p className="text-success-600 flex items-center">
                              <CheckCircle className="w-4 h-4 mr-1" />
                              金额有效
                            </p>
                          )}
                        </div>
                      )}

                      {/* 费用计算 */}
                      {withdrawAmount > 0 && withdrawAmount >= vipLimits.minAmount && (
                        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">提款金额</span>
                              <span className="font-semibold">{formatCurrency(withdrawAmount)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">手续费 ({(vipLimits.feeRate * 100).toFixed(1)}%)</span>
                              <span className="font-semibold text-warning-600">-{formatCurrency(calculatedFee)}</span>
                            </div>
                            <div className="flex justify-between border-t border-gray-200 pt-2">
                              <span className="text-gray-900 font-semibold">实际到账</span>
                              <span className="font-bold text-success-600">{formatCurrency(netAmount)}</span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* 提款密码 */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        提款密码
                      </label>
                      <div className="relative">
                        <Input
                          type={showPassword ? 'text' : 'password'}
                          value={withdrawPassword}
                          onChange={(e) => setWithdrawPassword(e.target.value)}
                          placeholder="请输入提款密码"
                          variant="outlined"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        >
                          {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        为了您的资金安全，请输入6位数字提款密码
                      </p>
                    </div>

                    {/* 安全提示 */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="flex items-start space-x-2">
                        <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
                        <div className="text-sm text-blue-800">
                          <p className="font-semibold mb-1">安全提示：</p>
                          <ul className="space-y-1">
                            <li>• 提款将转入您绑定的银行账户</li>
                            <li>• 工作日通常2-4小时内到账</li>
                            <li>• 周末和节假日可能延迟到账</li>
                            <li>• 请确保银行账户信息准确无误</li>
                          </ul>
                        </div>
                      </div>
                    </div>

                    {/* 提交按钮 */}
                    <Button
                      variant="primary"
                      size="lg"
                      fullWidth
                      onClick={handleWithdraw}
                      disabled={
                        !selectedBankId || 
                        !amount || 
                        !withdrawPassword ||
                        withdrawAmount < vipLimits.minAmount ||
                        withdrawAmount > vipLimits.maxAmount ||
                        withdrawAmount > vipLimits.remainingDaily ||
                        withdrawAmount > userBalance.availableBalance ||
                        vipLimits.remainingTimes <= 0
                      }
                      className="h-14 text-lg"
                    >
                      申请提款 {withdrawAmount > 0 && `${formatCurrency(netAmount)}`}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        )}

        {/* 银行账户管理标签页 */}
        {activeTab === 'accounts' && (
          <div className="space-y-6">
            {/* 添加银行账户按钮 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Button
                variant="primary"
                icon={<Plus className="w-4 h-4" />}
                onClick={() => setShowAddBankModal(true)}
              >
                添加银行账户
              </Button>
            </motion.div>

            {/* 银行账户列表 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <Card>
                <CardHeader>
                  <h2 className="text-lg font-semibold text-gray-900">我的银行账户</h2>
                </CardHeader>
                <CardContent className="p-0">
                  {bankAccounts.length === 0 ? (
                    <div className="p-8 text-center">
                      <Building className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600 mb-4">您还没有添加银行账户</p>
                      <Button
                        variant="primary"
                        onClick={() => setShowAddBankModal(true)}
                      >
                        添加第一个银行账户
                      </Button>
                    </div>
                  ) : (
                    <div className="divide-y divide-gray-200">
                      {bankAccounts.map((bank, index) => (
                        <motion.div
                          key={bank.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.1 }}
                          className="p-4 hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                                <Building className="w-6 h-6 text-primary-600" />
                              </div>
                              
                              <div>
                                <div className="flex items-center space-x-2">
                                  <h3 className="font-semibold text-gray-900">{bank.bankName}</h3>
                                  {bank.isDefault && (
                                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                                      <Star className="w-3 h-3 mr-1" />
                                      默认
                                    </span>
                                  )}
                                  {bank.isVerified && (
                                    <CheckCircle className="w-4 h-4 text-success-600" />
                                  )}
                                </div>
                                <p className="text-sm text-gray-600 mt-1">
                                  {bank.accountNumber} - {bank.accountName}
                                </p>
                                <p className="text-xs text-gray-500">
                                  添加于 {formatDateTime(bank.createdAt, 'YYYY-MM-DD')}
                                </p>
                              </div>
                            </div>

                            <div className="flex items-center space-x-2">
                              {!bank.isDefault && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleSetDefaultBank(bank.id)}
                                  className="text-xs"
                                >
                                  设为默认
                                </Button>
                              )}
                              <Button
                                variant="ghost"
                                size="sm"
                                icon={<Edit className="w-3 h-3" />}
                                onClick={() => openEditModal(bank)}
                              />
                              <Button
                                variant="ghost"
                                size="sm"
                                icon={<Trash2 className="w-3 h-3" />}
                                onClick={() => handleDeleteBank(bank.id)}
                                className="text-danger-600 hover:text-danger-700"
                              />
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </div>
        )}

        {/* 提款记录标签页 */}
        {activeTab === 'history' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold text-gray-900">提款记录</h2>
              </CardHeader>
              <CardContent className="p-0">
                {withdrawHistory.length === 0 ? (
                  <div className="p-8 text-center">
                    <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">暂无提款记录</p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-200">
                    {withdrawHistory.map((withdraw, index) => {
                      const statusConfig_ = statusConfig[withdraw.status];
                      const StatusIcon = statusConfig_.icon;

                      return (
                        <motion.div
                          key={withdraw.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.1 }}
                          className="p-4 hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                              <div className={cn(
                                'w-12 h-12 rounded-full flex items-center justify-center',
                                statusConfig_.bgColor
                              )}>
                                <StatusIcon className={cn('w-6 h-6', statusConfig_.color)} />
                              </div>
                              
                              <div>
                                <div className="flex items-center space-x-2">
                                  <h3 className="font-semibold text-gray-900">
                                    {withdraw.bankAccount.bankName}
                                  </h3>
                                  <span className={cn(
                                    'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                                    statusConfig_.bgColor,
                                    statusConfig_.color
                                  )}>
                                    {statusConfig_.label}
                                  </span>
                                </div>
                                <p className="text-sm text-gray-600 mt-1">
                                  {withdraw.bankAccount.accountNumber} - {withdraw.bankAccount.accountName}
                                </p>
                                <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                                  <span>{formatDateTime(withdraw.createdAt, 'MM-dd HH:mm')}</span>
                                  <span>{withdraw.reference}</span>
                                  {withdraw.estimatedArrival && (
                                    <span>预计到账: {formatDateTime(withdraw.estimatedArrival, 'MM-dd HH:mm')}</span>
                                  )}
                                </div>
                              </div>
                            </div>

                            <div className="text-right">
                              <p className="font-bold text-lg text-gray-900">
                                -{formatCurrency(withdraw.amount)}
                              </p>
                              <p className="text-sm text-gray-600">
                                手续费: {formatCurrency(withdraw.fee)}
                              </p>
                              <p className="text-sm font-semibold text-success-600">
                                实际到账: {formatCurrency(withdraw.netAmount)}
                              </p>
                            </div>
                          </div>
                          
                          {withdraw.reason && (
                            <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                              <p className="text-sm text-yellow-800">
                                <Info className="w-4 h-4 inline mr-1" />
                                {withdraw.reason}
                              </p>
                            </div>
                          )}
                        </motion.div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>

      {/* 确认提款弹窗 */}
      <Modal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        title="确认提款"
        size="sm"
      >
        <div className="p-6">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-warning-100 rounded-full flex items-center justify-center mx-auto">
              <DollarSign className="w-8 h-8 text-warning-600" />
            </div>
            
            <div>
              <p className="text-lg font-semibold text-gray-900">
                {formatCurrency(netAmount)}
              </p>
              <p className="text-sm text-gray-600">
                提款到 {selectedBank?.bankName} ({selectedBank?.accountNumber})
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 text-left">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">提款金额</span>
                  <span className="font-semibold">{formatCurrency(withdrawAmount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">手续费</span>
                  <span className="font-semibold text-warning-600">-{formatCurrency(calculatedFee)}</span>
                </div>
                <div className="flex justify-between border-t border-gray-200 pt-2">
                  <span className="text-gray-900 font-semibold">实际到账</span>
                  <span className="font-bold text-success-600">{formatCurrency(netAmount)}</span>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-left">
              <p className="text-xs text-blue-800">
                <Clock className="w-3 h-3 inline mr-1" />
                预计2-4小时内到账，周末可能延迟
              </p>
            </div>
          </div>

          <div className="flex space-x-3 mt-6">
            <Button
              variant="outline"
              fullWidth
              onClick={() => setShowConfirmModal(false)}
            >
              取消
            </Button>
            <Button
              variant="primary"
              fullWidth
              onClick={handleConfirmWithdraw}
            >
              确认提款
            </Button>
          </div>
        </div>
      </Modal>

      {/* 添加银行账户弹窗 */}
      <Modal
        isOpen={showAddBankModal}
        onClose={() => setShowAddBankModal(false)}
        title="添加银行账户"
        size="md"
      >
        <div className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                选择银行
              </label>
              <Select
                value={newBankForm.bankCode}
                onChange={(value) => setNewBankForm({ ...newBankForm, bankCode: value })}
                placeholder="请选择银行"
                options={nigerianBanks.map(bank => ({
                  value: bank.code,
                  label: bank.name,
                }))}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                账户号码
              </label>
              <Input
                value={newBankForm.accountNumber}
                onChange={(e) => setNewBankForm({ ...newBankForm, accountNumber: e.target.value })}
                placeholder="请输入银行账户号码"
                variant="outlined"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                账户名称
              </label>
              <Input
                value={newBankForm.accountName}
                onChange={(e) => setNewBankForm({ ...newBankForm, accountName: e.target.value })}
                placeholder="请输入账户持有人姓名"
                variant="outlined"
              />
              <p className="text-xs text-gray-500 mt-1">
                必须与注册姓名一致
              </p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start space-x-2">
                <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div className="text-sm text-yellow-800">
                  <p className="font-semibold mb-1">重要提醒：</p>
                  <ul className="space-y-1">
                    <li>• 账户名称必须与您的注册姓名完全一致</li>
                    <li>• 请确保银行账户信息准确无误</li>
                    <li>• 错误信息可能导致提款失败</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div className="flex space-x-3 mt-6">
            <Button
              variant="outline"
              fullWidth
              onClick={() => setShowAddBankModal(false)}
            >
              取消
            </Button>
            <Button
              variant="primary"
              fullWidth
              onClick={handleAddBank}
              disabled={!newBankForm.bankCode || !newBankForm.accountNumber || !newBankForm.accountName}
            >
              添加账户
            </Button>
          </div>
        </div>
      </Modal>

      {/* 编辑银行账户弹窗 */}
      <Modal
        isOpen={showEditBankModal}
        onClose={() => setShowEditBankModal(false)}
        title="编辑银行账户"
        size="md"
      >
        <div className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                选择银行
              </label>
              <Select
                value={newBankForm.bankCode}
                onChange={(value) => setNewBankForm({ ...newBankForm, bankCode: value })}
                placeholder="请选择银行"
                options={nigerianBanks.map(bank => ({
                  value: bank.code,
                  label: bank.name,
                }))}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                账户号码
              </label>
              <Input
                value={newBankForm.accountNumber}
                onChange={(e) => setNewBankForm({ ...newBankForm, accountNumber: e.target.value })}
                placeholder="请输入银行账户号码"
                variant="outlined"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                账户名称
              </label>
              <Input
                value={newBankForm.accountName}
                onChange={(e) => setNewBankForm({ ...newBankForm, accountName: e.target.value })}
                placeholder="请输入账户持有人姓名"
                variant="outlined"
              />
            </div>
          </div>

          <div className="flex space-x-3 mt-6">
            <Button
              variant="outline"
              fullWidth
              onClick={() => setShowEditBankModal(false)}
            >
              取消
            </Button>
            <Button
              variant="primary"
              fullWidth
              onClick={handleEditBank}
              disabled={!newBankForm.bankCode || !newBankForm.accountNumber || !newBankForm.accountName}
            >
              保存修改
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default WithdrawPage;