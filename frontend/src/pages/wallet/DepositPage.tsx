import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowLeft,
  CreditCard,
  Smartphone,
  Building,
  Copy,
  CheckCircle,
  AlertCircle,
  Clock,
  Upload,
  Camera
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { Card, CardContent, CardHeader } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import { cn } from '../../utils/cn';
import { formatCurrency } from '../../utils/format';

interface PaymentMethod {
  id: string;
  name: string;
  type: 'gateway' | 'bank' | 'mobile';
  icon: React.ComponentType<any>;
  description: string;
  minAmount: number;
  maxAmount: number;
  processingTime: string;
  fee: number;
  isActive: boolean;
}

const DepositPage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedMethod, setSelectedMethod] = useState<string>('');
  const [amount, setAmount] = useState<string>('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showReceiptModal, setShowReceiptModal] = useState(false);
  const [uploadedReceipt, setUploadedReceipt] = useState<File | null>(null);

  // 支付方式配置
  const paymentMethods: PaymentMethod[] = [
    {
      id: 'paystack',
      name: 'Paystack',
      type: 'gateway',
      icon: CreditCard,
      description: '支持银行卡、银行转账等多种支付方式',
      minAmount: 100,
      maxAmount: 500000,
      processingTime: '即时到账',
      fee: 0,
      isActive: true,
    },
    {
      id: 'flutterwave',
      name: 'Flutterwave',
      type: 'gateway',
      icon: CreditCard,
      description: '安全快捷的在线支付平台',
      minAmount: 100,
      maxAmount: 500000,
      processingTime: '即时到账',
      fee: 0,
      isActive: true,
    },
    {
      id: 'bank_transfer',
      name: '银行转账',
      type: 'bank',
      icon: Building,
      description: '直接转账到我们的银行账户',
      minAmount: 500,
      maxAmount: 1000000,
      processingTime: '1-24小时',
      fee: 0,
      isActive: true,
    },
    {
      id: 'opay',
      name: 'OPay',
      type: 'mobile',
      icon: Smartphone,
      description: '使用OPay移动钱包快速支付',
      minAmount: 100,
      maxAmount: 200000,
      processingTime: '即时到账',
      fee: 0,
      isActive: true,
    },
    {
      id: 'palmpay',
      name: 'PalmPay',
      type: 'mobile',
      icon: Smartphone,
      description: '使用PalmPay移动钱包快速支付',
      minAmount: 100,
      maxAmount: 200000,
      processingTime: '即时到账',
      fee: 0,
      isActive: true,
    },
  ];

  // 快捷金额选项
  const quickAmounts = [100, 500, 1000, 2000, 5000, 10000];

  // 银行信息（用于银行转账）
  const bankInfo = {
    bankName: 'Access Bank',
    accountName: 'Africa Lottery Platform Ltd',
    accountNumber: '0123456789',
    sortCode: '044150149',
  };

  const selectedPaymentMethod = paymentMethods.find(method => method.id === selectedMethod);
  const depositAmount = parseFloat(amount) || 0;

  const handleAmountChange = (value: string) => {
    // 只允许数字和小数点
    const numericValue = value.replace(/[^0-9.]/g, '');
    setAmount(numericValue);
  };

  const handleQuickAmount = (quickAmount: number) => {
    setAmount(quickAmount.toString());
  };

  const handleDeposit = () => {
    if (!selectedMethod || !amount || depositAmount < (selectedPaymentMethod?.minAmount || 0)) {
      return;
    }

    if (selectedMethod === 'bank_transfer') {
      setShowReceiptModal(true);
    } else {
      setShowConfirmModal(true);
    }
  };

  const handleConfirmDeposit = async () => {
    try {
      // 这里调用实际的支付API
      console.log('Processing deposit:', {
        method: selectedMethod,
        amount: depositAmount,
      });

      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000));

      setShowConfirmModal(false);
      
      // 跳转到支付页面或显示成功消息
      if (selectedMethod === 'paystack' || selectedMethod === 'flutterwave') {
        // 跳转到第三方支付页面
        window.location.href = `https://checkout.${selectedMethod}.com/...`;
      } else {
        // 显示成功消息并返回钱包页面
        navigate('/wallet', { 
          state: { message: '存款申请已提交，请等待处理' }
        });
      }
    } catch (error) {
      console.error('Deposit error:', error);
    }
  };

  const handleReceiptUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedReceipt(file);
    }
  };

  const handleSubmitBankTransfer = async () => {
    if (!uploadedReceipt) return;

    try {
      const formData = new FormData();
      formData.append('amount', amount);
      formData.append('payment_method', selectedMethod);
      formData.append('receipt', uploadedReceipt);

      // 调用API提交银行转账凭证
      const response = await fetch('/api/v1/finance/deposit/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: formData,
      });

      if (response.ok) {
        setShowReceiptModal(false);
        navigate('/wallet', { 
          state: { message: '转账凭证已提交，我们将在24小时内处理' }
        });
      }
    } catch (error) {
      console.error('Bank transfer submission error:', error);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // 这里可以显示复制成功的提示
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
            <h1 className="text-2xl font-bold text-gray-900">存款</h1>
            <p className="text-sm text-gray-600 mt-1">
              选择支付方式并完成存款
            </p>
          </div>
        </div>
      </div>

      <div className="container-responsive py-6 space-y-6">
        {/* 存款金额 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold text-gray-900">存款金额</h2>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Input
                  label="存款金额 (₦)"
                  value={amount}
                  onChange={(e) => handleAmountChange(e.target.value)}
                  placeholder="请输入存款金额"
                  variant="outlined"
                  inputSize="lg"
                  className="text-center text-2xl font-bold"
                />

                {/* 快捷金额 */}
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-3">快捷金额</p>
                  <div className="grid grid-cols-3 gap-3">
                    {quickAmounts.map((quickAmount) => (
                      <Button
                        key={quickAmount}
                        variant={amount === quickAmount.toString() ? 'primary' : 'outline'}
                        size="sm"
                        onClick={() => handleQuickAmount(quickAmount)}
                        className="text-sm"
                      >
                        ₦{quickAmount.toLocaleString()}
                      </Button>
                    ))}
                  </div>
                </div>

                {/* 金额验证提示 */}
                {selectedPaymentMethod && depositAmount > 0 && (
                  <div className="text-sm">
                    {depositAmount < selectedPaymentMethod.minAmount ? (
                      <p className="text-danger-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        最小存款金额: {formatCurrency(selectedPaymentMethod.minAmount)}
                      </p>
                    ) : depositAmount > selectedPaymentMethod.maxAmount ? (
                      <p className="text-danger-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        最大存款金额: {formatCurrency(selectedPaymentMethod.maxAmount)}
                      </p>
                    ) : (
                      <p className="text-success-600 flex items-center">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        金额有效
                      </p>
                    )}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 支付方式选择 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold text-gray-900">选择支付方式</h2>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-gray-200">
                {paymentMethods.map((method) => {
                  const Icon = method.icon;
                  const isSelected = selectedMethod === method.id;
                  
                  return (
                    <button
                      key={method.id}
                      onClick={() => setSelectedMethod(method.id)}
                      disabled={!method.isActive}
                      className={cn(
                        'w-full p-4 text-left transition-colors hover:bg-gray-50',
                        isSelected && 'bg-primary-50 border-r-4 border-primary-500',
                        !method.isActive && 'opacity-50 cursor-not-allowed'
                      )}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={cn(
                          'w-12 h-12 rounded-lg flex items-center justify-center',
                          isSelected ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-600'
                        )}>
                          <Icon className="w-6 h-6" />
                        </div>
                        
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <h3 className="font-semibold text-gray-900">{method.name}</h3>
                            {method.fee === 0 && (
                              <span className="text-xs bg-success-100 text-success-800 px-2 py-1 rounded-full">
                                免费
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mt-1">{method.description}</p>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            <span>限额: {formatCurrency(method.minAmount)} - {formatCurrency(method.maxAmount)}</span>
                            <span>到账: {method.processingTime}</span>
                          </div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 银行转账信息 */}
        {selectedMethod === 'bank_transfer' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold text-gray-900">银行转账信息</h2>
              </CardHeader>
              <CardContent>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                  <div className="flex items-start space-x-2">
                    <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
                    <div className="text-sm text-yellow-800">
                      <p className="font-semibold mb-1">重要提醒：</p>
                      <ul className="space-y-1">
                        <li>• 请确保转账金额与填写金额一致</li>
                        <li>• 转账后请上传转账凭证</li>
                        <li>• 我们将在24小时内处理您的存款</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm text-gray-600">银行名称</span>
                        <div className="flex items-center space-x-2">
                          <span className="font-semibold">{bankInfo.bankName}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={<Copy className="w-3 h-3" />}
                            onClick={() => copyToClipboard(bankInfo.bankName)}
                          />
                        </div>
                      </div>
                      
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm text-gray-600">账户名称</span>
                        <div className="flex items-center space-x-2">
                          <span className="font-semibold">{bankInfo.accountName}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={<Copy className="w-3 h-3" />}
                            onClick={() => copyToClipboard(bankInfo.accountName)}
                          />
                        </div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm text-gray-600">账户号码</span>
                        <div className="flex items-center space-x-2">
                          <span className="font-semibold font-mono">{bankInfo.accountNumber}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={<Copy className="w-3 h-3" />}
                            onClick={() => copyToClipboard(bankInfo.accountNumber)}
                          />
                        </div>
                      </div>
                      
                      <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm text-gray-600">Sort Code</span>
                        <div className="flex items-center space-x-2">
                          <span className="font-semibold font-mono">{bankInfo.sortCode}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={<Copy className="w-3 h-3" />}
                            onClick={() => copyToClipboard(bankInfo.sortCode)}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* 提交按钮 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Button
            variant="primary"
            size="lg"
            fullWidth
            onClick={handleDeposit}
            disabled={
              !selectedMethod || 
              !amount || 
              depositAmount < (selectedPaymentMethod?.minAmount || 0) ||
              depositAmount > (selectedPaymentMethod?.maxAmount || 0)
            }
            className="h-14 text-lg"
          >
            {selectedMethod === 'bank_transfer' ? '上传转账凭证' : `存款 ${formatCurrency(depositAmount)}`}
          </Button>
        </motion.div>
      </div>

      {/* 确认存款弹窗 */}
      <Modal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        title="确认存款"
        size="sm"
      >
        <div className="p-6">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto">
              <CreditCard className="w-8 h-8 text-primary-600" />
            </div>
            
            <div>
              <p className="text-lg font-semibold text-gray-900">
                {formatCurrency(depositAmount)}
              </p>
              <p className="text-sm text-gray-600">
                通过 {selectedPaymentMethod?.name} 存款
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 text-left">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">存款金额</span>
                  <span className="font-semibold">{formatCurrency(depositAmount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">手续费</span>
                  <span className="font-semibold">{formatCurrency(selectedPaymentMethod?.fee || 0)}</span>
                </div>
                <div className="flex justify-between border-t border-gray-200 pt-2">
                  <span className="text-gray-900 font-semibold">总计</span>
                  <span className="font-bold">{formatCurrency(depositAmount + (selectedPaymentMethod?.fee || 0))}</span>
                </div>
              </div>
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
              onClick={handleConfirmDeposit}
            >
              确认存款
            </Button>
          </div>
        </div>
      </Modal>

      {/* 银行转账凭证上传弹窗 */}
      <Modal
        isOpen={showReceiptModal}
        onClose={() => setShowReceiptModal(false)}
        title="上传转账凭证"
        size="sm"
      >
        <div className="p-6">
          <div className="space-y-4">
            <div className="text-center">
              <p className="text-lg font-semibold text-gray-900 mb-2">
                存款金额: {formatCurrency(depositAmount)}
              </p>
              <p className="text-sm text-gray-600">
                请上传您的转账凭证以便我们快速处理
              </p>
            </div>

            {/* 文件上传区域 */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              {uploadedReceipt ? (
                <div className="space-y-3">
                  <CheckCircle className="w-12 h-12 text-success-600 mx-auto" />
                  <p className="text-sm font-medium text-gray-900">
                    {uploadedReceipt.name}
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setUploadedReceipt(null)}
                  >
                    重新选择
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto" />
                  <div>
                    <p className="text-gray-600 mb-2">点击上传或拖拽文件到此处</p>
                    <p className="text-xs text-gray-500">支持 JPG、PNG 格式，最大 5MB</p>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleReceiptUpload}
                    className="hidden"
                    id="receipt-upload"
                  />
                  <label htmlFor="receipt-upload">
                    <Button variant="outline" size="sm" as="span">
                      选择文件
                    </Button>
                  </label>
                </div>
              )}
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start space-x-2">
                <Clock className="w-5 h-5 text-blue-600 mt-0.5" />
                <div className="text-sm text-blue-800">
                  <p className="font-semibold mb-1">处理时间：</p>
                  <p>我们将在收到凭证后24小时内处理您的存款申请</p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex space-x-3 mt-6">
            <Button
              variant="outline"
              fullWidth
              onClick={() => setShowReceiptModal(false)}
            >
              取消
            </Button>
            <Button
              variant="primary"
              fullWidth
              onClick={handleSubmitBankTransfer}
              disabled={!uploadedReceipt}
            >
              提交凭证
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default DepositPage;