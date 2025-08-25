import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Volume2, 
  VolumeX, 
  Maximize, 
  Minimize, 
  Settings, 
  HelpCircle,
  Zap,
  Trophy,
  Star,
  Gift,
  Bell,
  BellOff
} from 'lucide-react';

import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { cn } from '@/utils/cn';

interface GameEnhancerProps {
  gameName: string;
  children: React.ReactNode;
  showSoundControl?: boolean;
  showFullscreen?: boolean;
  showNotifications?: boolean;
  showHelp?: boolean;
  onSoundToggle?: (enabled: boolean) => void;
  onFullscreenToggle?: (enabled: boolean) => void;
  onNotificationToggle?: (enabled: boolean) => void;
}

interface GameSettings {
  soundEnabled: boolean;
  notificationsEnabled: boolean;
  autoPlay: boolean;
  quickBet: boolean;
  animationsEnabled: boolean;
}

const GameEnhancer: React.FC<GameEnhancerProps> = ({
  gameName,
  children,
  showSoundControl = true,
  showFullscreen = true,
  showNotifications = true,
  showHelp = true,
  onSoundToggle,
  onFullscreenToggle,
  onNotificationToggle,
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [settings, setSettings] = useState<GameSettings>({
    soundEnabled: true,
    notificationsEnabled: true,
    autoPlay: false,
    quickBet: false,
    animationsEnabled: true,
  });

  // 全屏控制
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
    onFullscreenToggle?.(isFullscreen);
  };

  // 监听全屏状态变化
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  // 设置更新
  const updateSetting = (key: keyof GameSettings, value: boolean) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    
    // 触发相应的回调
    if (key === 'soundEnabled') {
      onSoundToggle?.(value);
    } else if (key === 'notificationsEnabled') {
      onNotificationToggle?.(value);
    }
  };

  // 快捷键支持
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'm':
            event.preventDefault();
            updateSetting('soundEnabled', !settings.soundEnabled);
            break;
          case 'f':
            event.preventDefault();
            toggleFullscreen();
            break;
          case 'h':
            event.preventDefault();
            setShowHelpModal(true);
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => {
      document.removeEventListener('keydown', handleKeyPress);
    };
  }, [settings.soundEnabled]);

  return (
    <div className="relative min-h-screen">
      {/* 游戏控制栏 */}
      <div className="fixed top-4 right-4 z-50 flex items-center space-x-2">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white/90 backdrop-blur-sm rounded-lg shadow-medium p-2 flex items-center space-x-2"
        >
          {/* 声音控制 */}
          {showSoundControl && (
            <Button
              variant="ghost"
              size="sm"
              icon={settings.soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
              onClick={() => updateSetting('soundEnabled', !settings.soundEnabled)}
              className={cn(
                'transition-colors',
                settings.soundEnabled ? 'text-primary-600' : 'text-gray-400'
              )}
              title="切换声音 (Ctrl+M)"
            />
          )}

          {/* 通知控制 */}
          {showNotifications && (
            <Button
              variant="ghost"
              size="sm"
              icon={settings.notificationsEnabled ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
              onClick={() => updateSetting('notificationsEnabled', !settings.notificationsEnabled)}
              className={cn(
                'transition-colors',
                settings.notificationsEnabled ? 'text-primary-600' : 'text-gray-400'
              )}
              title="切换通知"
            />
          )}

          {/* 全屏控制 */}
          {showFullscreen && (
            <Button
              variant="ghost"
              size="sm"
              icon={isFullscreen ? <Minimize className="w-4 h-4" /> : <Maximize className="w-4 h-4" />}
              onClick={toggleFullscreen}
              title="切换全屏 (Ctrl+F)"
            />
          )}

          {/* 设置 */}
          <Button
            variant="ghost"
            size="sm"
            icon={<Settings className="w-4 h-4" />}
            onClick={() => setShowSettings(true)}
            title="游戏设置"
          />

          {/* 帮助 */}
          {showHelp && (
            <Button
              variant="ghost"
              size="sm"
              icon={<HelpCircle className="w-4 h-4" />}
              onClick={() => setShowHelpModal(true)}
              title="游戏帮助 (Ctrl+H)"
            />
          )}
        </motion.div>
      </div>

      {/* 游戏内容 */}
      <div className={cn(
        'transition-all duration-300',
        isFullscreen && 'bg-black'
      )}>
        {children}
      </div>

      {/* 设置模态框 */}
      <Modal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        title={`${gameName} - 游戏设置`}
        size="md"
      >
        <div className="p-6 space-y-6">
          {/* 音效设置 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Volume2 className="w-5 h-5 text-gray-600" />
              <div>
                <p className="font-medium text-gray-900">音效</p>
                <p className="text-sm text-gray-500">开启游戏音效和提示音</p>
              </div>
            </div>
            <button
              onClick={() => updateSetting('soundEnabled', !settings.soundEnabled)}
              className={cn(
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                settings.soundEnabled ? 'bg-primary-600' : 'bg-gray-200'
              )}
            >
              <span
                className={cn(
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  settings.soundEnabled ? 'translate-x-6' : 'translate-x-1'
                )}
              />
            </button>
          </div>

          {/* 通知设置 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Bell className="w-5 h-5 text-gray-600" />
              <div>
                <p className="font-medium text-gray-900">通知</p>
                <p className="text-sm text-gray-500">开奖结果和重要消息通知</p>
              </div>
            </div>
            <button
              onClick={() => updateSetting('notificationsEnabled', !settings.notificationsEnabled)}
              className={cn(
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                settings.notificationsEnabled ? 'bg-primary-600' : 'bg-gray-200'
              )}
            >
              <span
                className={cn(
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  settings.notificationsEnabled ? 'translate-x-6' : 'translate-x-1'
                )}
              />
            </button>
          </div>

          {/* 自动投注设置 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Zap className="w-5 h-5 text-gray-600" />
              <div>
                <p className="font-medium text-gray-900">自动投注</p>
                <p className="text-sm text-gray-500">自动重复上次投注</p>
              </div>
            </div>
            <button
              onClick={() => updateSetting('autoPlay', !settings.autoPlay)}
              className={cn(
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                settings.autoPlay ? 'bg-primary-600' : 'bg-gray-200'
              )}
            >
              <span
                className={cn(
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  settings.autoPlay ? 'translate-x-6' : 'translate-x-1'
                )}
              />
            </button>
          </div>

          {/* 快速投注设置 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Star className="w-5 h-5 text-gray-600" />
              <div>
                <p className="font-medium text-gray-900">快速投注</p>
                <p className="text-sm text-gray-500">简化投注流程</p>
              </div>
            </div>
            <button
              onClick={() => updateSetting('quickBet', !settings.quickBet)}
              className={cn(
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                settings.quickBet ? 'bg-primary-600' : 'bg-gray-200'
              )}
            >
              <span
                className={cn(
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  settings.quickBet ? 'translate-x-6' : 'translate-x-1'
                )}
              />
            </button>
          </div>

          {/* 动画设置 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Gift className="w-5 h-5 text-gray-600" />
              <div>
                <p className="font-medium text-gray-900">动画效果</p>
                <p className="text-sm text-gray-500">开启游戏动画和特效</p>
              </div>
            </div>
            <button
              onClick={() => updateSetting('animationsEnabled', !settings.animationsEnabled)}
              className={cn(
                'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                settings.animationsEnabled ? 'bg-primary-600' : 'bg-gray-200'
              )}
            >
              <span
                className={cn(
                  'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                  settings.animationsEnabled ? 'translate-x-6' : 'translate-x-1'
                )}
              />
            </button>
          </div>

          {/* 快捷键说明 */}
          <div className="border-t pt-4">
            <h3 className="font-medium text-gray-900 mb-3">快捷键</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex justify-between">
                <span>切换声音</span>
                <kbd className="px-2 py-1 bg-gray-100 rounded text-xs">Ctrl + M</kbd>
              </div>
              <div className="flex justify-between">
                <span>全屏模式</span>
                <kbd className="px-2 py-1 bg-gray-100 rounded text-xs">Ctrl + F</kbd>
              </div>
              <div className="flex justify-between">
                <span>帮助</span>
                <kbd className="px-2 py-1 bg-gray-100 rounded text-xs">Ctrl + H</kbd>
              </div>
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="flex justify-end space-x-3 pt-4 border-t">
            <Button
              variant="outline"
              onClick={() => {
                setSettings({
                  soundEnabled: true,
                  notificationsEnabled: true,
                  autoPlay: false,
                  quickBet: false,
                  animationsEnabled: true,
                });
              }}
            >
              重置默认
            </Button>
            <Button
              variant="primary"
              onClick={() => setShowSettings(false)}
            >
              确定
            </Button>
          </div>
        </div>
      </Modal>

      {/* 帮助模态框 */}
      <Modal
        isOpen={showHelp}
        onClose={() => setShowHelpModal(false)}
        title={`${gameName} - 游戏帮助`}
        size="lg"
      >
        <div className="p-6">
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-lg mb-3 flex items-center">
                <Trophy className="w-5 h-5 mr-2 text-primary-600" />
                游戏说明
              </h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700">
                  欢迎来到{gameName}！这是一个公平、透明的在线彩票游戏。
                  请仔细阅读游戏规则，理性投注，享受游戏乐趣。
                </p>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-lg mb-3 flex items-center">
                <Star className="w-5 h-5 mr-2 text-secondary-600" />
                操作指南
              </h3>
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-bold">1</div>
                  <p className="text-gray-700">选择您要投注的号码或选项</p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-bold">2</div>
                  <p className="text-gray-700">设置投注金额和倍数</p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-bold">3</div>
                  <p className="text-gray-700">确认投注信息并提交</p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-bold">4</div>
                  <p className="text-gray-700">等待开奖结果，查看中奖情况</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-lg mb-3 flex items-center">
                <Gift className="w-5 h-5 mr-2 text-success-600" />
                注意事项
              </h3>
              <div className="bg-warning-50 border border-warning-200 rounded-lg p-4">
                <ul className="space-y-2 text-sm text-warning-800">
                  <li>• 请确保您已年满18岁</li>
                  <li>• 理性投注，量力而行</li>
                  <li>• 投注前请仔细核对选号和金额</li>
                  <li>• 开奖后请及时查看中奖结果</li>
                  <li>• 如有疑问请联系客服</li>
                </ul>
              </div>
            </div>

            <div className="flex justify-end pt-4 border-t">
              <Button
                variant="primary"
                onClick={() => setShowHelpModal(false)}
              >
                我已了解
              </Button>
            </div>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default GameEnhancer;