import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { Phone, ArrowLeft, Shield, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';

import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { cn } from '@/utils/cn';

// 步骤枚举
enum ResetStep {
  PHONE = 'phone',
  VERIFY = 'verify',
  RESET = 'reset',
}

// 表单验证模式
const phoneSchema = z.object({
  phone: z.string()
    .regex(/^\+234[0-9]{10}$/, '请输入正确的尼日利亚手机号格式: +2348012345678'),
});

const verifySchema = z.object({
  code: z.string().length(6, '验证码必须是6位数字'),
});

const resetSchema = z.object({
  newPassword: z.string()
    .min(8, '密码至少8个字符')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, '密码必须包含大小写字母和数字'),
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "两次输入的密码不一致",
  path: ["confirmPassword"],
});

type PhoneFormData = z.infer<typeof phoneSchema>;
type VerifyFormData = z.infer<typeof verifySchema>;
type ResetFormData = z.infer<typeof resetSchema>;

const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<ResetStep>(ResetStep.PHONE);
  const [phone, setPhone] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // 手机号表单
  const phoneForm = useForm<PhoneFormData>({
    resolver: zodResolver(phoneSchema),
  });

  // 验证码表单
  const verifyForm = useForm<VerifyFormData>({
    resolver: zodResolver(verifySchema),
  });

  // 重置密码表单
  const resetForm = useForm<ResetFormData>({
    resolver: zodResolver(resetSchema),
  });

  // 发送验证码
  const sendVerificationCode = async (data: PhoneFormData) => {
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/v1/auth/password/reset/send/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone: data.phone,
        }),
      });

      const result = await response.json();

      if (result.success) {
        setPhone(data.phone);
        setCurrentStep(ResetStep.VERIFY);
        toast.success('验证码已发送到您的手机');
        
        // 开始倒计时
        setCountdown(60);
        const timer = setInterval(() => {
          setCountdown((prev) => {
            if (prev <= 1) {
              clearInterval(timer);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      } else {
        toast.error(result.message || '发送验证码失败');
      }
    } catch (error) {
      console.error('Send code error:', error);
      toast.error('网络错误，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 验证验证码
  const verifyCode = async (data: VerifyFormData) => {
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/v1/auth/password/reset/verify/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone: phone,
          code: data.code,
        }),
      });

      const result = await response.json();

      if (result.success) {
        setCurrentStep(ResetStep.RESET);
        toast.success('验证码验证成功');
      } else {
        toast.error(result.message || '验证码错误');
      }
    } catch (error) {
      console.error('Verify code error:', error);
      toast.error('网络错误，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 重置密码
  const resetPassword = async (data: ResetFormData) => {
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/v1/auth/password/reset/confirm/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone: phone,
          new_password: data.newPassword,
          confirm_password: data.confirmPassword,
        }),
      });

      const result = await response.json();

      if (result.success) {
        toast.success('密码重置成功！请使用新密码登录');
        navigate('/auth/login');
      } else {
        toast.error(result.message || '密码重置失败');
      }
    } catch (error) {
      console.error('Reset password error:', error);
      toast.error('网络错误，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 重新发送验证码
  const resendCode = async () => {
    if (countdown > 0) return;
    
    await sendVerificationCode({ phone });
  };

  // 渲染步骤指示器
  const renderStepIndicator = () => {
    const steps = [
      { key: ResetStep.PHONE, label: '输入手机号', icon: Phone },
      { key: ResetStep.VERIFY, label: '验证身份', icon: Shield },
      { key: ResetStep.RESET, label: '重置密码', icon: Eye },
    ];

    return (
      <div className="flex items-center justify-center mb-8">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isActive = currentStep === step.key;
          const isCompleted = Object.values(ResetStep).indexOf(currentStep) > index;
          
          return (
            <React.Fragment key={step.key}>
              <div className="flex flex-col items-center">
                <div
                  className={cn(
                    'w-10 h-10 rounded-full flex items-center justify-center mb-2 transition-colors',
                    isActive
                      ? 'bg-primary-500 text-white'
                      : isCompleted
                      ? 'bg-success-500 text-white'
                      : 'bg-gray-200 text-gray-500'
                  )}
                >
                  <Icon className="w-5 h-5" />
                </div>
                <span
                  className={cn(
                    'text-xs font-medium',
                    isActive ? 'text-primary-600' : 'text-gray-500'
                  )}
                >
                  {step.label}
                </span>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={cn(
                    'w-16 h-0.5 mx-4 mt-5 transition-colors',
                    isCompleted ? 'bg-success-500' : 'bg-gray-200'
                  )}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    );
  };

  // 渲染手机号输入步骤
  const renderPhoneStep = () => (
    <form onSubmit={phoneForm.handleSubmit(sendVerificationCode)} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <Phone className="w-4 h-4 inline mr-2" />
          手机号
        </label>
        <Input
          {...phoneForm.register('phone')}
          placeholder="+2348012345678"
          error={phoneForm.formState.errors.phone?.message}
          className={cn(phoneForm.formState.errors.phone && 'border-danger-500')}
        />
        <p className="mt-2 text-sm text-gray-600">
          我们将向您的手机发送验证码
        </p>
      </div>

      <Button
        type="submit"
        variant="primary"
        size="lg"
        fullWidth
        loading={isLoading}
        disabled={isLoading}
      >
        发送验证码
      </Button>
    </form>
  );

  // 渲染验证码输入步骤
  const renderVerifyStep = () => (
    <form onSubmit={verifyForm.handleSubmit(verifyCode)} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <Shield className="w-4 h-4 inline mr-2" />
          验证码
        </label>
        <Input
          {...verifyForm.register('code')}
          placeholder="请输入6位验证码"
          maxLength={6}
          error={verifyForm.formState.errors.code?.message}
          className={cn(verifyForm.formState.errors.code && 'border-danger-500')}
        />
        <div className="mt-2 flex items-center justify-between text-sm">
          <span className="text-gray-600">
            验证码已发送至 {phone}
          </span>
          <button
            type="button"
            onClick={resendCode}
            disabled={countdown > 0}
            className={cn(
              'text-primary-600 hover:text-primary-700 font-medium',
              countdown > 0 && 'text-gray-400 cursor-not-allowed'
            )}
          >
            {countdown > 0 ? `${countdown}s后重发` : '重新发送'}
          </button>
        </div>
      </div>

      <Button
        type="submit"
        variant="primary"
        size="lg"
        fullWidth
        loading={isLoading}
        disabled={isLoading}
      >
        验证
      </Button>
    </form>
  );

  // 渲染密码重置步骤
  const renderResetStep = () => (
    <form onSubmit={resetForm.handleSubmit(resetPassword)} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          新密码
        </label>
        <div className="relative">
          <Input
            {...resetForm.register('newPassword')}
            type={showNewPassword ? 'text' : 'password'}
            placeholder="请输入新密码"
            error={resetForm.formState.errors.newPassword?.message}
            className={cn(resetForm.formState.errors.newPassword && 'border-danger-500', 'pr-12')}
          />
          <button
            type="button"
            onClick={() => setShowNewPassword(!showNewPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
          >
            {showNewPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          确认新密码
        </label>
        <div className="relative">
          <Input
            {...resetForm.register('confirmPassword')}
            type={showConfirmPassword ? 'text' : 'password'}
            placeholder="请再次输入新密码"
            error={resetForm.formState.errors.confirmPassword?.message}
            className={cn(resetForm.formState.errors.confirmPassword && 'border-danger-500', 'pr-12')}
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
          >
            {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>
      </div>

      <Button
        type="submit"
        variant="primary"
        size="lg"
        fullWidth
        loading={isLoading}
        disabled={isLoading}
      >
        重置密码
      </Button>
    </form>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card className="p-8 shadow-heavy">
          {/* 返回按钮 */}
          <div className="mb-6">
            <Link
              to="/auth/login"
              className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              返回登录
            </Link>
          </div>

          {/* Logo和标题 */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-white font-bold text-2xl">L</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">重置密码</h1>
            <p className="text-gray-600">
              {currentStep === ResetStep.PHONE && '输入您的手机号以接收验证码'}
              {currentStep === ResetStep.VERIFY && '请输入发送到您手机的验证码'}
              {currentStep === ResetStep.RESET && '设置您的新密码'}
            </p>
          </div>

          {/* 步骤指示器 */}
          {renderStepIndicator()}

          {/* 表单内容 */}
          <div className="space-y-6">
            {currentStep === ResetStep.PHONE && renderPhoneStep()}
            {currentStep === ResetStep.VERIFY && renderVerifyStep()}
            {currentStep === ResetStep.RESET && renderResetStep()}
          </div>
        </Card>

        {/* 底部信息 */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>© 2024 非洲彩票平台. 保留所有权利.</p>
        </div>
      </motion.div>
    </div>
  );
};

export default ForgotPasswordPage;