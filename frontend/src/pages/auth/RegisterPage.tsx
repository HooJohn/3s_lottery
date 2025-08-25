import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { Eye, EyeOff, User, Mail, Phone, MapPin, Gift } from 'lucide-react';
import toast from 'react-hot-toast';

import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { cn } from '@/utils/cn';

// 注册表单验证模式
const registerSchema = z.object({
  fullName: z.string().min(2, '姓名至少2个字符').max(50, '姓名不能超过50个字符'),
  phone: z.string()
    .regex(/^\+234[0-9]{10}$/, '请输入正确的尼日利亚手机号格式: +2348012345678'),
  email: z.string().email('请输入有效的邮箱地址'),
  password: z.string()
    .min(8, '密码至少8个字符')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, '密码必须包含大小写字母和数字'),
  confirmPassword: z.string(),
  country: z.enum(['NG', 'CM'], { errorMap: () => ({ message: '请选择国家' }) }),
  referralCode: z.string().optional(),
  agreeTerms: z.boolean().refine(val => val === true, '请同意服务条款和隐私政策'),
}).refine((data) => data.password === data.confirmPassword, {
  message: "两次输入的密码不一致",
  path: ["confirmPassword"],
});

type RegisterFormData = z.infer<typeof registerSchema>;

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      country: 'NG',
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    
    try {
      // 调用注册API
      const response = await fetch('/api/v1/auth/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          full_name: data.fullName,
          phone: data.phone,
          email: data.email,
          password: data.password,
          password_confirm: data.confirmPassword,
          country: data.country,
          referral_code_input: data.referralCode || '',
        }),
      });

      const result = await response.json();

      if (result.success) {
        // 保存用户信息和token
        localStorage.setItem('access_token', result.data.tokens.access);
        localStorage.setItem('refresh_token', result.data.tokens.refresh);
        localStorage.setItem('user', JSON.stringify(result.data.user));

        toast.success('注册成功！欢迎加入非洲彩票平台！');
        navigate('/dashboard');
      } else {
        // 处理错误信息
        if (result.errors) {
          Object.entries(result.errors).forEach(([field, messages]) => {
            if (Array.isArray(messages)) {
              messages.forEach(message => toast.error(message));
            }
          });
        } else {
          toast.error(result.message || '注册失败，请重试');
        }
      }
    } catch (error) {
      console.error('Registration error:', error);
      toast.error('网络错误，请检查网络连接后重试');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card className="p-8 shadow-heavy">
          {/* Logo和标题 */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-white font-bold text-2xl">L</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">创建账户</h1>
            <p className="text-gray-600">加入数千名玩家，开始您的中奖之旅</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* 姓名 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <User className="w-4 h-4 inline mr-2" />
                姓名
              </label>
              <Input
                {...register('fullName')}
                placeholder="请输入您的姓名"
                error={errors.fullName?.message}
                className={cn(errors.fullName && 'border-danger-500')}
              />
            </div>

            {/* 手机号 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Phone className="w-4 h-4 inline mr-2" />
                手机号
              </label>
              <Input
                {...register('phone')}
                placeholder="+2348012345678"
                error={errors.phone?.message}
                className={cn(errors.phone && 'border-danger-500')}
              />
            </div>

            {/* 邮箱 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Mail className="w-4 h-4 inline mr-2" />
                邮箱地址
              </label>
              <Input
                {...register('email')}
                type="email"
                placeholder="your@email.com"
                error={errors.email?.message}
                className={cn(errors.email && 'border-danger-500')}
              />
            </div>

            {/* 国家 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <MapPin className="w-4 h-4 inline mr-2" />
                国家
              </label>
              <select
                {...register('country')}
                className={cn(
                  'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors',
                  errors.country && 'border-danger-500'
                )}
              >
                <option value="NG">🇳🇬 尼日利亚</option>
                <option value="CM">🇨🇲 喀麦隆</option>
              </select>
              {errors.country && (
                <p className="mt-1 text-sm text-danger-600">{errors.country.message}</p>
              )}
            </div>

            {/* 密码 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                密码
              </label>
              <div className="relative">
                <Input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  placeholder="请输入密码"
                  error={errors.password?.message}
                  className={cn(errors.password && 'border-danger-500', 'pr-12')}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* 确认密码 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                确认密码
              </label>
              <div className="relative">
                <Input
                  {...register('confirmPassword')}
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="请再次输入密码"
                  error={errors.confirmPassword?.message}
                  className={cn(errors.confirmPassword && 'border-danger-500', 'pr-12')}
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

            {/* 推荐码 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Gift className="w-4 h-4 inline mr-2" />
                推荐码 (可选)
              </label>
              <Input
                {...register('referralCode')}
                placeholder="请输入推荐码"
                error={errors.referralCode?.message}
              />
            </div>

            {/* 同意条款 */}
            <div className="flex items-start space-x-3">
              <input
                {...register('agreeTerms')}
                type="checkbox"
                className="mt-1 w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label className="text-sm text-gray-700">
                我同意
                <Link to="/terms" className="text-primary-600 hover:text-primary-700 mx-1">
                  服务条款
                </Link>
                和
                <Link to="/privacy" className="text-primary-600 hover:text-primary-700 mx-1">
                  隐私政策
                </Link>
              </label>
            </div>
            {errors.agreeTerms && (
              <p className="text-sm text-danger-600">{errors.agreeTerms.message}</p>
            )}

            {/* 注册按钮 */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              loading={isLoading}
              disabled={isLoading}
            >
              创建账户
            </Button>
          </form>

          {/* 登录链接 */}
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              已有账户？
              <Link
                to="/auth/login"
                className="text-primary-600 hover:text-primary-700 font-medium ml-1"
              >
                立即登录
              </Link>
            </p>
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

export default RegisterPage;