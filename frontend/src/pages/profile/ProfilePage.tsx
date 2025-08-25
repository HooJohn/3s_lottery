import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  Settings, 
  Shield, 
  Bell, 
  Globe, 
  Camera,
  Edit3,
  Phone,
  Mail,
  MapPin,
  Calendar,
  Award,
  Eye,
  EyeOff,
  Smartphone,
  Lock,
  LogOut,
  ChevronRight
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Modal } from '../../components/ui/Modal';
import { cn } from '../../utils/cn';
import { formatCurrency, formatDateTime } from '../../utils/format';

const ProfilePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'info' | 'security' | 'preferences'>('info');
  const [showEditModal, setShowEditModal] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [editField, setEditField] = useState<string>('');

  // 模拟用户数据
  const user = {
    id: 'user-123',
    username: 'john_doe',
    email: 'john.doe@example.com',
    phone: '+2348012345678',
    fullName: 'John Doe',
    country: 'NG',
    avatar: null,
    vipLevel: 3,
    totalTurnover: 125000,
    kycStatus: 'APPROVED',
    twoFactorEnabled: true,
    emailNotifications: true,
    smsNotifications: true,
    language: 'en',
    timezone: 'Africa/Lagos',
    createdAt: '2024-01-15T10:30:00Z',
    lastLogin: '2024-01-20T14:25:00Z',
  };

  // VIP等级信息
  const vipInfo = {
    currentLevel: 3,
    nextLevel: 4,
    currentTurnover: 125000,
    requiredTurnover: 200000,
    rebateRate: 0.65,
    withdrawLimit: 100000,
    withdrawTimes: 5,
    withdrawFee: 1.5,
  };

  // 标签页配置
  const tabs = [
    { key: 'info', label: '个人信息', icon: User },
    { key: 'security', label: '安全设置', icon: Shield },
    { key: 'preferences', label: '偏好设置', icon: Settings },
  ];

  // 个人信息字段
  const profileFields = [
    { key: 'fullName', label: '姓名', value: user.fullName, icon: User, editable: true },
    { key: 'username', label: '用户名', value: user.username, icon: User, editable: false },
    { key: 'email', label: '邮箱', value: user.email, icon: Mail, editable: true },
    { key: 'phone', label: '手机号', value: user.phone, icon: Phone, editable: false },
    { key: 'country', label: '国家', value: user.country === 'NG' ? '尼日利亚' : '喀麦隆', icon: MapPin, editable: false },
    { key: 'createdAt', label: '注册时间', value: formatDateTime(user.createdAt), icon: Calendar, editable: false },
  ];

  // 安全设置项
  const securityItems = [
    {
      key: 'password',
      label: '登录密码',
      description: '定期更换密码以保护账户安全',
      icon: Lock,
      action: '修改',
      onClick: () => setShowPasswordModal(true),
    },
    {
      key: 'twoFactor',
      label: '双因子认证',
      description: user.twoFactorEnabled ? '已启用短信验证' : '未启用',
      icon: Smartphone,
      action: user.twoFactorEnabled ? '关闭' : '启用',
      onClick: () => {},
    },
    {
      key: 'kyc',
      label: 'KYC身份验证',
      description: user.kycStatus === 'APPROVED' ? '已通过验证' : '待验证',
      icon: Award,
      action: user.kycStatus === 'APPROVED' ? '已完成' : '去验证',
      onClick: () => {},
    },
  ];

  // 偏好设置项
  const preferenceItems = [
    {
      key: 'language',
      label: '语言设置',
      description: '当前: 中文',
      icon: Globe,
      action: '更改',
      onClick: () => {},
    },
    {
      key: 'notifications',
      label: '通知设置',
      description: '邮件和短信通知',
      icon: Bell,
      action: '设置',
      onClick: () => {},
    },
  ];

  const handleEditField = (field: string) => {
    setEditField(field);
    setShowEditModal(true);
  };

  const calculateVipProgress = () => {
    return ((vipInfo.currentTurnover / vipInfo.requiredTurnover) * 100);
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
      {/* 页面头部 */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 lg:px-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">个人中心</h1>
            <p className="text-sm text-gray-600 mt-1">
              管理您的账户信息和设置
            </p>
          </div>
        </div>
      </div>

      <div className="container-responsive py-6 space-y-6">
        {/* 用户信息卡片 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="bg-gradient-primary text-white overflow-hidden relative">
            {/* 背景装饰 */}
            <div className="absolute top-0 right-0 w-32 h-32 opacity-10">
              <div className="w-full h-full rounded-full border-4 border-white transform translate-x-8 -translate-y-8" />
            </div>

            <CardContent className="relative z-10 p-6">
              <div className="flex items-center space-x-4">
                {/* 头像 */}
                <div className="relative">
                  <div className="w-20 h-20 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                    {user.avatar ? (
                      <img
                        src={user.avatar}
                        alt={user.fullName}
                        className="w-full h-full rounded-full object-cover"
                      />
                    ) : (
                      <span className="text-3xl font-bold text-white">
                        {user.fullName.charAt(0)}
                      </span>
                    )}
                  </div>
                  <button className="absolute -bottom-1 -right-1 w-8 h-8 bg-secondary-500 rounded-full flex items-center justify-center text-gray-900 hover:bg-secondary-600 transition-colors">
                    <Camera className="w-4 h-4" />
                  </button>
                </div>

                {/* 用户信息 */}
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-white mb-1">
                    {user.fullName}
                  </h2>
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="inline-flex items-center px-3 py-1 rounded-full bg-secondary-500 text-gray-900 text-sm font-semibold">
                      VIP{user.vipLevel}
                    </span>
                    <span className="text-white text-opacity-80 text-sm">
                      {user.phone}
                    </span>
                  </div>
                  <p className="text-white text-opacity-60 text-sm">
                    上次登录: {formatDateTime(user.lastLogin, 'MM-dd HH:mm')}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* VIP进度卡片 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">
                  VIP等级进度
                </h2>
                <Button variant="ghost" size="sm">
                  查看详情
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">当前等级</span>
                  <span className="font-semibold">VIP{vipInfo.currentLevel}</span>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">升级进度</span>
                    <span className="font-medium">
                      {formatCurrency(vipInfo.currentTurnover)} / {formatCurrency(vipInfo.requiredTurnover)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-gradient-primary h-2 rounded-full transition-all duration-500"
                      style={{ width: `${calculateVipProgress()}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500">
                    还需 {formatCurrency(vipInfo.requiredTurnover - vipInfo.currentTurnover)} 流水升级到 VIP{vipInfo.nextLevel}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                  <div className="text-center">
                    <p className="text-sm text-gray-600">返水比例</p>
                    <p className="font-bold text-primary-600">{vipInfo.rebateRate}%</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-gray-600">提款手续费</p>
                    <p className="font-bold text-gray-900">{vipInfo.withdrawFee}%</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 标签页导航 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card>
            <CardContent className="p-0">
              <div className="flex border-b border-gray-200">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.key}
                      onClick={() => setActiveTab(tab.key as any)}
                      className={cn(
                        'flex-1 flex items-center justify-center space-x-2 py-4 px-6 text-sm font-medium transition-colors',
                        activeTab === tab.key
                          ? 'text-primary-600 border-b-2 border-primary-600 bg-primary-50'
                          : 'text-gray-500 hover:text-gray-700'
                      )}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{tab.label}</span>
                    </button>
                  );
                })}
              </div>

              {/* 标签页内容 */}
              <div className="p-6">
                {/* 个人信息 */}
                {activeTab === 'info' && (
                  <div className="space-y-4">
                    {profileFields.map((field) => {
                      const Icon = field.icon;
                      return (
                        <div
                          key={field.key}
                          className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0"
                        >
                          <div className="flex items-center space-x-3">
                            <Icon className="w-5 h-5 text-gray-400" />
                            <div>
                              <p className="font-medium text-gray-900">{field.label}</p>
                              <p className="text-sm text-gray-600">{field.value}</p>
                            </div>
                          </div>
                          {field.editable && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEditField(field.key)}
                              icon={<Edit3 className="w-4 h-4" />}
                            >
                              编辑
                            </Button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* 安全设置 */}
                {activeTab === 'security' && (
                  <div className="space-y-4">
                    {securityItems.map((item) => {
                      const Icon = item.icon;
                      return (
                        <div
                          key={item.key}
                          className="flex items-center justify-between py-4 border-b border-gray-100 last:border-b-0"
                        >
                          <div className="flex items-center space-x-3">
                            <Icon className="w-5 h-5 text-gray-400" />
                            <div>
                              <p className="font-medium text-gray-900">{item.label}</p>
                              <p className="text-sm text-gray-600">{item.description}</p>
                            </div>
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={item.onClick}
                            icon={<ChevronRight className="w-4 h-4" />}
                          >
                            {item.action}
                          </Button>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* 偏好设置 */}
                {activeTab === 'preferences' && (
                  <div className="space-y-4">
                    {preferenceItems.map((item) => {
                      const Icon = item.icon;
                      return (
                        <div
                          key={item.key}
                          className="flex items-center justify-between py-4 border-b border-gray-100 last:border-b-0"
                        >
                          <div className="flex items-center space-x-3">
                            <Icon className="w-5 h-5 text-gray-400" />
                            <div>
                              <p className="font-medium text-gray-900">{item.label}</p>
                              <p className="text-sm text-gray-600">{item.description}</p>
                            </div>
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={item.onClick}
                            icon={<ChevronRight className="w-4 h-4" />}
                          >
                            {item.action}
                          </Button>
                        </div>
                      );
                    })}

                    {/* 通知开关 */}
                    <div className="pt-4 space-y-4">
                      <h3 className="font-medium text-gray-900">通知设置</h3>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-900">邮件通知</p>
                          <p className="text-sm text-gray-600">接收重要账户信息和活动通知</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={user.emailNotifications}
                            className="sr-only peer"
                            onChange={() => {}}
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-900">短信通知</p>
                          <p className="text-sm text-gray-600">接收验证码和重要提醒</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={user.smsNotifications}
                            className="sr-only peer"
                            onChange={() => {}}
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 退出登录 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card>
            <CardContent className="p-6">
              <Button
                variant="danger"
                fullWidth
                icon={<LogOut className="w-4 h-4" />}
              >
                退出登录
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* 编辑信息弹窗 */}
      <Modal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        title="编辑信息"
        size="sm"
      >
        <div className="p-6">
          <Input
            label="新值"
            placeholder="请输入新的值"
            variant="outlined"
          />
          <div className="flex space-x-3 mt-6">
            <Button
              variant="outline"
              fullWidth
              onClick={() => setShowEditModal(false)}
            >
              取消
            </Button>
            <Button
              variant="primary"
              fullWidth
              onClick={() => setShowEditModal(false)}
            >
              保存
            </Button>
          </div>
        </div>
      </Modal>

      {/* 修改密码弹窗 */}
      <Modal
        isOpen={showPasswordModal}
        onClose={() => setShowPasswordModal(false)}
        title="修改密码"
        size="sm"
      >
        <div className="p-6 space-y-4">
          <Input
            label="当前密码"
            type="password"
            placeholder="请输入当前密码"
            variant="outlined"
          />
          <Input
            label="新密码"
            type="password"
            placeholder="请输入新密码"
            variant="outlined"
          />
          <Input
            label="确认新密码"
            type="password"
            placeholder="请再次输入新密码"
            variant="outlined"
          />
          <div className="flex space-x-3 mt-6">
            <Button
              variant="outline"
              fullWidth
              onClick={() => setShowPasswordModal(false)}
            >
              取消
            </Button>
            <Button
              variant="primary"
              fullWidth
              onClick={() => setShowPasswordModal(false)}
            >
              确认修改
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ProfilePage;