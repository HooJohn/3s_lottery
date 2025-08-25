import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { Eye, EyeOff, User, Lock, Smartphone } from 'lucide-react';
import { motion } from 'framer-motion';

import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { cn } from '@/utils/cn';

// 表单验证模式
const loginSchema = z.object({
  username: z.string().min(1, '请输入用户名、邮箱或手机号'),
  password: z.string().min(6, '密码至少6位字符'),
  rememberMe: z.boolean().optional(),
});

type LoginFormData = z.infer<typeof loginSchema>;

const LoginPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      rememberMe: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000));
      console.log('Login data:', data);
      // 这里会调用实际的登录API
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-primary-100 opacity-20" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full bg-secondary-100 opacity-20" />
      </div>

      <div className="relative w-full max-w-md space-y-8">
        {/* Logo和标题 */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <div className="mx-auto h-16 w-16 bg-gradient-primary rounded-2xl flex items-center justify-center mb-6">
            <span className="text-2xl font-bold text-white">L</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            欢迎回来
          </h1>
          <p className="text-gray-600">
            登录您的账户继续游戏
          </p>
        </motion.div>

        {/* 登录表单 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card className="shadow-heavy">
            <CardHeader>
              <div className="text-center">
                <h2 className="text-xl font-semibold text-gray-900">
                  登录账户
                </h2>
              </div>
            </CardHeader>
            
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {/* 用户名输入 */}
                <div>
                  <Input
                    {...register('username')}
                    type="text"
                    label="用户名 / 邮箱 / 手机号"
                    placeholder="请输入用户名、邮箱或手机号"
                    leftIcon={<User className="w-5 h-5" />}
                    error={errors.username?.message}
                    variant="outlined"
                    inputSize="lg"
                  />
                </div>

                {/* 密码输入 */}
                <div>
                  <Input
                    {...register('password')}
                    type="password"
                    label="密码"
                    placeholder="请输入密码"
                    leftIcon={<Lock className="w-5 h-5" />}
                    error={errors.password?.message}
                    variant="outlined"
                    inputSize="lg"
                    showPasswordToggle
                  />
                </div>

                {/* 记住我和忘记密码 */}
                <div className="flex items-center justify-between">
                  <label className="flex items-center">
                    <input
                      {...register('rememberMe')}
                      type="checkbox"
                      className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    />
                    <span className="ml-2 text-sm text-gray-600">
                      记住我
                    </span>
                  </label>
                  
                  <Link
                    to="/auth/forgot-password"
                    className="text-sm text-primary-600 hover:text-primary-500 font-medium"
                  >
                    忘记密码？
                  </Link>
                </div>

                {/* 登录按钮 */}
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  fullWidth
                  loading={isLoading}
                  className="mt-6"
                >
                  {isLoading ? '登录中...' : '登录'}
                </Button>

                {/* 分割线 */}
                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">
                      或者
                    </span>
                  </div>
                </div>

                {/* 快速登录选项 */}
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    size="md"
                    icon={<Smartphone className="w-4 h-4" />}
                    className="justify-center"
                  >
                    短信登录
                  </Button>
                  
                  <Button
                    type="button"
                    variant="ghost"
                    size="md"
                    className="justify-center"
                  >
                    游客试玩
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </motion.div>

        {/* 注册链接 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-center"
        >
          <p className="text-sm text-gray-600">
            还没有账户？{' '}
            <Link
              to="/auth/register"
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              立即注册
            </Link>
          </p>
        </motion.div>

        {/* 语言切换 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex justify-center space-x-4"
        >
          <button className="flex items-center space-x-1 text-sm text-gray-500 hover:text-gray-700">
            <span className="text-lg">🇳🇬</span>
            <span>English</span>
          </button>
          <button className="flex items-center space-x-1 text-sm text-gray-500 hover:text-gray-700">
            <span className="text-lg">🇨🇲</span>
            <span>Français</span>
          </button>
          <button className="flex items-center space-x-1 text-sm text-primary-600 font-medium">
            <span className="text-lg">🇨🇳</span>
            <span>中文</span>
          </button>
        </motion.div>

        {/* 底部信息 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="text-center text-xs text-gray-500 space-y-2"
        >
          <p>
            登录即表示您同意我们的{' '}
            <Link to="/terms" className="text-primary-600 hover:underline">
              服务条款
            </Link>{' '}
            和{' '}
            <Link to="/privacy" className="text-primary-600 hover:underline">
              隐私政策
            </Link>
          </p>
          <p>© 2024 非洲彩票平台. 保留所有权利.</p>
        </motion.div>
      </div>
    </div>
  );
};

export default LoginPage;