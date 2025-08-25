import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  Share2, 
  Copy, 
  QrCode, 
  TrendingUp, 
  DollarSign,
  UserPlus,
  Gift,
  Award,
  Target,
  Calendar,
  CheckCircle,
  Clock,
  ExternalLink
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { cn } from '@/utils/cn';
import { formatCurrency } from '@/utils/format';

interface ReferralLevel {
  level: number;
  name: string;
  commission_rate: number;
  color: string;
  users_count: number;
  total_turnover: number;
  total_commission: number;
}

interface ReferralRecord {
  id: string;
  date: string;
  username: string;
  level: number;
  turnover: number;
  commission_rate: number;
  commission_amount: number;
  status: 'pending' | 'completed';
}

interface ReferralStats {
  total_referrals: number;
  active_referrals: number;
  total_commission: number;
  monthly_commission: number;
  referral_code: string;
  referral_link: string;
}

const ReferralPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [showShareModal, setShowShareModal] = useState(false);
  const [showQRCode, setShowQRCode] = useState(false);

  // 推荐等级配置
  const referralLevels: ReferralLevel[] = [
    {
      level: 1,
      name: '一级推荐',
      commission_rate: 3.0,
      color: 'text-blue-600',
      users_count: 12,
      total_turnover: 450000,
      total_commission: 13500
    },
    {
      level: 2,
      name: '二级推荐',
      commission_rate: 2.0,
      color: 'text-green-600',
      users_count: 35,
      total_turnover: 280000,
      total_commission: 5600
    },
    {
      level: 3,
      name: '三级推荐',
      commission_rate: 1.0,
      color: 'text-yellow-600',
      users_count: 68,
      total_turnover: 180000,
      total_commission: 1800
    },
    {
      level: 4,
      name: '四级推荐',
      commission_rate: 0.7,
      color: 'text-orange-600',
      users_count: 125,
      total_turnover: 120000,
      total_commission: 840
    },
    {
      level: 5,
      name: '五级推荐',
      commission_rate: 0.5,
      color: 'text-red-600',
      users_count: 89,
      total_turnover: 85000,
      total_commission: 425
    },
    {
      level: 6,
      name: '六级推荐',
      commission_rate: 0.3,
      color: 'text-purple-600',
      users_count: 45,
      total_turnover: 60000,
      total_commission: 180
    },
    {
      level: 7,
      name: '七级推荐',
      commission_rate: 0.1,
      color: 'text-gray-600',
      users_count: 23,
      total_turnover: 35000,
      total_commission: 35
    }
  ];

  // 推荐统计数据
  const referralStats: ReferralStats = {
    total_referrals: 397,
    active_referrals: 285,
    total_commission: 22380,
    monthly_commission: 3250,
    referral_code: 'AF8K2M9P',
    referral_link: 'https://lottery.africa/register?ref=AF8K2M9P'
  };

  // 推荐记录
  const referralRecords: ReferralRecord[] = [
    {
      id: '1',
      date: '2024-01-21',
      username: 'user***123',
      level: 1,
      turnover: 5200,
      commission_rate: 3.0,
      commission_amount: 156,
      status: 'completed'
    },
    {
      id: '2',
      date: '2024-01-21',
      username: 'play***456',
      level: 2,
      turnover: 3800,
      commission_rate: 2.0,
      commission_amount: 76,
      status: 'completed'
    },
    {
      id: '3',
      date: '2024-01-20',
      username: 'luck***789',
      level: 1,
      turnover: 8500,
      commission_rate: 3.0,
      commission_amount: 255,
      status: 'pending'
    },
    {
      id: '4',
      date: '2024-01-20',
      username: 'win***012',
      level: 3,
      turnover: 2200,
      commission_rate: 1.0,
      commission_amount: 22,
      status: 'completed'
    }
  ];

  // 复制推荐码
  const copyReferralCode = () => {
    navigator.clipboard.writeText(referralStats.referral_code);
    // 这里可以添加成功提示
  };

  // 复制推荐链接
  const copyReferralLink = () => {
    navigator.clipboard.writeText(referralStats.referral_link);
    // 这里可以添加成功提示
  };

  // 分享推荐链接
  const shareReferralLink = () => {
    if (navigator.share) {
      navigator.share({
        title: '非洲彩票 - 邀请好友',
        text: '加入非洲彩票，享受丰厚奖励！',
        url: referralStats.referral_link,
      });
    } else {
      setShowShareModal(true);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20 lg:pb-0">
      {/* 页面头部 */}
      <div className="bg-gradient-to-r from-success-600 to-primary-600 text-white px-4 py-8 lg:px-6">
        <div className="container-responsive">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2 flex items-center">
                  <Users className="w-8 h-8 mr-3" />
                  推荐奖励
                </h1>
                <p className="text-white text-opacity-80 text-lg">
                  邀请好友，共享收益，最高7级推荐奖励
                </p>
              </div>
              <div className="hidden lg:block">
                <div className="text-right">
                  <p className="text-white text-opacity-80 text-sm">推荐码</p>
                  <div className="flex items-center justify-end">
                    <span className="text-2xl font-bold mr-2">{referralStats.referral_code}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<Copy className="w-4 h-4" />}
                      onClick={copyReferralCode}
                      className="text-white hover:bg-white hover:bg-opacity-20"
                    />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* 推荐统计卡片 */}
      <div className="container-responsive py-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card className="bg-gradient-to-r from-success-50 to-primary-50 border-success-200">
            <CardContent className="p-6">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <UserPlus className="w-6 h-6 text-success-600 mr-2" />
                    <span className="text-sm text-gray-600">总推荐人数</span>
                  </div>
                  <p className="text-2xl font-bold text-success-700">
                    {referralStats.total_referrals}
                  </p>
                  <p className="text-xs text-gray-500">
                    活跃: {referralStats.active_referrals}
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <DollarSign className="w-6 h-6 text-primary-600 mr-2" />
                    <span className="text-sm text-gray-600">累计佣金</span>
                  </div>
                  <p className="text-2xl font-bold text-primary-700">
                    {formatCurrency(referralStats.total_commission)}
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <TrendingUp className="w-6 h-6 text-warning-600 mr-2" />
                    <span className="text-sm text-gray-600">本月佣金</span>
                  </div>
                  <p className="text-2xl font-bold text-warning-700">
                    {formatCurrency(referralStats.monthly_commission)}
                  </p>
                </div>
                
                <div className="text-center">
                  <Button
                    variant="primary"
                    icon={<Share2 className="w-4 h-4" />}
                    onClick={shareReferralLink}
                  >
                    邀请好友
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* 推荐码分享区域 */}
      <div className="container-responsive mb-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold text-gray-900">
                我的推荐码
              </h2>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 推荐码 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    推荐码
                  </label>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg font-mono text-lg font-bold text-center">
                      {referralStats.referral_code}
                    </div>
                    <Button
                      variant="outline"
                      icon={<Copy className="w-4 h-4" />}
                      onClick={copyReferralCode}
                    >
                      复制
                    </Button>
                  </div>
                </div>

                {/* 推荐链接 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    推荐链接
                  </label>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-sm truncate">
                      {referralStats.referral_link}
                    </div>
                    <Button
                      variant="outline"
                      icon={<Copy className="w-4 h-4" />}
                      onClick={copyReferralLink}
                    >
                      复制
                    </Button>
                  </div>
                </div>
              </div>

              {/* 分享按钮 */}
              <div className="flex justify-center space-x-4 mt-6">
                <Button
                  variant="primary"
                  icon={<Share2 className="w-4 h-4" />}
                  onClick={shareReferralLink}
                >
                  分享链接
                </Button>
                <Button
                  variant="outline"
                  icon={<QrCode className="w-4 h-4" />}
                  onClick={() => setShowQRCode(true)}
                >
                  二维码
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* 标签切换 */}
      <div className="container-responsive mb-6">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('overview')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              activeTab === 'overview'
                ? 'bg-white text-primary-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            推荐概览
          </button>
          <button
            onClick={() => setActiveTab('levels')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              activeTab === 'levels'
                ? 'bg-white text-primary-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            推荐层级
          </button>
          <button
            onClick={() => setActiveTab('records')}
            className={cn(
              'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors',
              activeTab === 'records'
                ? 'bg-white text-primary-700 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            佣金记录
          </button>
        </div>
      </div>

      <div className="container-responsive space-y-6">
        {/* 推荐概览 */}
        {activeTab === 'overview' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-6"
          >
            {/* 佣金比例说明 */}
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Award className="w-5 h-5 mr-2 text-primary-600" />
                  佣金比例
                </h3>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {referralLevels.slice(0, 4).map((level) => (
                    <div key={level.level} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className={cn('w-3 h-3 rounded-full', level.color.replace('text-', 'bg-'))} />
                        <span className="text-sm font-medium text-gray-700">
                          {level.name}
                        </span>
                      </div>
                      <span className={cn('font-bold', level.color)}>
                        {level.commission_rate}%
                      </span>
                    </div>
                  ))}
                  <div className="pt-2 border-t">
                    <p className="text-xs text-gray-500">
                      最高7级推荐奖励，总奖励率达7.6%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 推荐规则 */}
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  <Target className="w-5 h-5 mr-2 text-success-600" />
                  推荐规则
                </h3>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-success-500 mt-0.5 flex-shrink-0" />
                    <p className="text-gray-700">
                      好友通过您的推荐码注册并完成首次投注
                    </p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-success-500 mt-0.5 flex-shrink-0" />
                    <p className="text-gray-700">
                      根据好友的有效流水获得相应比例的佣金
                    </p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-success-500 mt-0.5 flex-shrink-0" />
                    <p className="text-gray-700">
                      佣金每日结算，自动发放到您的账户
                    </p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-success-500 mt-0.5 flex-shrink-0" />
                    <p className="text-gray-700">
                      最低有效流水1NGN起计算佣金
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* 推荐层级 */}
        {activeTab === 'levels' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
          >
            {referralLevels.map((level, index) => (
              <motion.div
                key={level.level}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card className="hover:shadow-medium transition-shadow duration-200">
                  <CardContent className="p-6">
                    <div className="text-center mb-4">
                      <div className={cn('w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center', level.color.replace('text-', 'bg-').replace('-600', '-100'))}>
                        <Users className={cn('w-6 h-6', level.color)} />
                      </div>
                      <h3 className="text-lg font-bold text-gray-900 mb-1">
                        {level.name}
                      </h3>
                      <p className={cn('text-2xl font-bold', level.color)}>
                        {level.commission_rate}%
                      </p>
                    </div>
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">推荐人数:</span>
                        <span className="font-medium">{level.users_count}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">总流水:</span>
                        <span className="font-medium">
                          {formatCurrency(level.total_turnover)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">总佣金:</span>
                        <span className={cn('font-bold', level.color)}>
                          {formatCurrency(level.total_commission)}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* 佣金记录 */}
        {activeTab === 'records' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900">
                    佣金记录
                  </h2>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <Calendar className="w-4 h-4" />
                    <span>最近30天</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                {referralRecords.length === 0 ? (
                  <div className="text-center py-8">
                    <Gift className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">暂无佣金记录</p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-200">
                    {referralRecords.map((record) => (
                      <div key={record.id} className="p-4 hover:bg-gray-50 transition-colors">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center">
                              <Users className="w-5 h-5" />
                            </div>
                            <div>
                              <p className="font-medium text-gray-900">
                                {record.level}级推荐佣金
                              </p>
                              <p className="text-sm text-gray-500">
                                {record.date} • {record.username} • 流水: {formatCurrency(record.turnover)}
                              </p>
                            </div>
                          </div>
                          
                          <div className="text-right">
                            <p className="text-lg font-bold text-success-600">
                              +{formatCurrency(record.commission_amount)}
                            </p>
                            <div className="flex items-center">
                              <span className="text-xs text-gray-500 mr-2">
                                {record.commission_rate}% 佣金
                              </span>
                              {record.status === 'completed' ? (
                                <CheckCircle className="w-4 h-4 text-success-500" />
                              ) : (
                                <Clock className="w-4 h-4 text-warning-500" />
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>

      {/* 分享模态框 */}
      <Modal
        isOpen={showShareModal}
        onClose={() => setShowShareModal(false)}
        title="分享推荐链接"
        size="md"
      >
        <div className="p-6">
          <div className="text-center mb-6">
            <Share2 className="w-12 h-12 text-primary-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              邀请好友加入
            </h3>
            <p className="text-gray-600">
              分享您的专属推荐链接，好友注册成功后您将获得丰厚佣金奖励
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                推荐链接
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={referralStats.referral_link}
                  readOnly
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-sm"
                />
                <Button
                  variant="outline"
                  size="sm"
                  icon={<Copy className="w-4 h-4" />}
                  onClick={copyReferralLink}
                >
                  复制
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Button
                variant="outline"
                icon={<ExternalLink className="w-4 h-4" />}
                onClick={() => window.open(`https://wa.me/?text=${encodeURIComponent('加入非洲彩票，享受丰厚奖励！' + referralStats.referral_link)}`, '_blank')}
              >
                WhatsApp
              </Button>
              <Button
                variant="outline"
                icon={<ExternalLink className="w-4 h-4" />}
                onClick={() => window.open(`https://t.me/share/url?url=${encodeURIComponent(referralStats.referral_link)}&text=${encodeURIComponent('加入非洲彩票，享受丰厚奖励！')}`, '_blank')}
              >
                Telegram
              </Button>
            </div>
          </div>
        </div>
      </Modal>

      {/* 二维码模态框 */}
      <Modal
        isOpen={showQRCode}
        onClose={() => setShowQRCode(false)}
        title="推荐二维码"
        size="sm"
      >
        <div className="p-6 text-center">
          <div className="w-48 h-48 bg-gray-100 rounded-lg mx-auto mb-4 flex items-center justify-center">
            <QrCode className="w-24 h-24 text-gray-400" />
          </div>
          <p className="text-gray-600 mb-4">
            扫描二维码或分享给好友注册
          </p>
          <div className="space-y-3">
            <Button
              variant="primary"
              fullWidth
              icon={<Copy className="w-4 h-4" />}
              onClick={copyReferralLink}
            >
              复制推荐链接
            </Button>
            <Button
              variant="outline"
              fullWidth
              icon={<Share2 className="w-4 h-4" />}
              onClick={shareReferralLink}
            >
              分享二维码
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ReferralPage;