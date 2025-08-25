import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Bell, 
  Volume2, 
  VolumeX, 
  Smartphone, 
  Monitor,
  Trophy,
  DollarSign,
  Gift,
  Megaphone,
  Settings,
  Save,
  RotateCcw
} from 'lucide-react';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { pushNotificationService, PushNotificationConfig } from '@/services/pushNotifications';
import { cn } from '@/utils/cn';

interface NotificationSettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

const NotificationSettings: React.FC<NotificationSettingsProps> = ({ isOpen, onClose }) => {
  const [config, setConfig] = useState<PushNotificationConfig>(pushNotificationService.getConfig());
  const [hasChanges, setHasChanges] = useState(false);

  // 监听配置变化
  useEffect(() => {
    const currentConfig = pushNotificationService.getConfig();
    setHasChanges(JSON.stringify(config) !== JSON.stringify(currentConfig));
  }, [config]);

  // 更新配置项
  const updateConfig = (key: keyof PushNotificationConfig, value: boolean) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  // 保存配置
  const saveConfig = () => {
    pushNotificationService.updateConfig(config);
    setHasChanges(false);
    
    // 保存到localStorage
    localStorage.setItem('notification_config', JSON.stringify(config));
    
    onClose();
  };

  // 重置配置
  const resetConfig = () => {
    const defaultConfig: PushNotificationConfig = {
      enableSound: true,
      enableVibration: true,
      enableDesktopNotifications: true,
      enableDrawResults: true,
      enableBalanceUpdates: true,
      enableRewardUpdates: true,
      enableSystemAnnouncements: true,
    };
    setConfig(defaultConfig);
  };

  // 测试通知
  const testNotification = () => {
    // 模拟一个测试通知
    const testMessage = {
      type: 'test',
      data: {
        title: '测试通知',
        content: '这是一个测试通知，用于验证您的通知设置。',
        priority: 'normal'
      },
      timestamp: Date.now()
    };

    // 这里应该调用推送服务的测试方法
    console.log('发送测试通知:', testMessage);
  };

  if (!isOpen) return null;

  const settingGroups = [
    {
      title: '通知方式',
      icon: Bell,
      settings: [
        {
          key: 'enableSound' as keyof PushNotificationConfig,
          label: '声音提醒',
          description: '播放通知声音',
          icon: config.enableSound ? Volume2 : VolumeX
        },
        {
          key: 'enableVibration' as keyof PushNotificationConfig,
          label: '振动提醒',
          description: '设备振动反馈',
          icon: Smartphone
        },
        {
          key: 'enableDesktopNotifications' as keyof PushNotificationConfig,
          label: '桌面通知',
          description: '显示系统桌面通知',
          icon: Monitor
        }
      ]
    },
    {
      title: '通知内容',
      icon: Settings,
      settings: [
        {
          key: 'enableDrawResults' as keyof PushNotificationConfig,
          label: '开奖结果',
          description: '11选5、大乐透开奖通知',
          icon: Trophy
        },
        {
          key: 'enableBalanceUpdates' as keyof PushNotificationConfig,
          label: '余额变动',
          description: '存款、提款、余额变动通知',
          icon: DollarSign
        },
        {
          key: 'enableRewardUpdates' as keyof PushNotificationConfig,
          label: '奖励通知',
          description: 'VIP返水、推荐佣金通知',
          icon: Gift
        },
        {
          key: 'enableSystemAnnouncements' as keyof PushNotificationConfig,
          label: '系统公告',
          description: '系统维护、安全警报等通知',
          icon: Megaphone
        }
      ]
    }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="w-full max-w-2xl mx-4 bg-white rounded-2xl shadow-2xl max-h-[90vh] overflow-hidden"
      >
        {/* 头部 */}
        <div className="bg-gradient-to-r from-primary-600 to-secondary-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Bell className="w-6 h-6" />
              <h2 className="text-xl font-bold">通知设置</h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p className="text-white text-opacity-80 mt-2">
            自定义您的通知偏好，获得最佳体验
          </p>
        </div>

        {/* 内容区域 */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          <div className="space-y-6">
            {settingGroups.map((group, groupIndex) => {
              const GroupIcon = group.icon;
              return (
                <motion.div
                  key={group.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: groupIndex * 0.1 }}
                >
                  <Card>
                    <CardHeader>
                      <h3 className="text-lg font-semibold flex items-center">
                        <GroupIcon className="w-5 h-5 mr-2 text-primary-600" />
                        {group.title}
                      </h3>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {group.settings.map((setting, settingIndex) => {
                          const SettingIcon = setting.icon;
                          const isEnabled = config[setting.key];
                          
                          return (
                            <motion.div
                              key={setting.key}
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ duration: 0.3, delay: (groupIndex * group.settings.length + settingIndex) * 0.05 }}
                              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                            >
                              <div className="flex items-center space-x-3">
                                <SettingIcon className={cn(
                                  'w-5 h-5',
                                  isEnabled ? 'text-primary-600' : 'text-gray-400'
                                )} />
                                <div>
                                  <p className="font-medium text-gray-900">
                                    {setting.label}
                                  </p>
                                  <p className="text-sm text-gray-600">
                                    {setting.description}
                                  </p>
                                </div>
                              </div>
                              
                              <button
                                onClick={() => updateConfig(setting.key, !isEnabled)}
                                className={cn(
                                  'relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
                                  isEnabled ? 'bg-primary-600' : 'bg-gray-300'
                                )}
                              >
                                <span
                                  className={cn(
                                    'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                                    isEnabled ? 'translate-x-6' : 'translate-x-1'
                                  )}
                                />
                              </button>
                            </motion.div>
                          );
                        })}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}

            {/* 测试通知 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold">测试通知</h3>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 mb-4">
                    发送一个测试通知来验证您的设置是否正常工作
                  </p>
                  <Button
                    variant="outline"
                    icon={<Bell className="w-4 h-4" />}
                    onClick={testNotification}
                  >
                    发送测试通知
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>

        {/* 底部操作栏 */}
        <div className="border-t border-gray-200 p-6 bg-gray-50">
          <div className="flex items-center justify-between">
            <Button
              variant="outline"
              icon={<RotateCcw className="w-4 h-4" />}
              onClick={resetConfig}
            >
              重置默认
            </Button>
            
            <div className="flex space-x-3">
              <Button
                variant="outline"
                onClick={onClose}
              >
                取消
              </Button>
              <Button
                variant="primary"
                icon={<Save className="w-4 h-4" />}
                onClick={saveConfig}
                disabled={!hasChanges}
              >
                保存设置
              </Button>
            </div>
          </div>
          
          {hasChanges && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm text-warning-600 mt-2"
            >
              您有未保存的更改
            </motion.p>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default NotificationSettings;