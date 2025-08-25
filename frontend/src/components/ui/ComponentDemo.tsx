import React, { useState } from 'react';
import { Button } from './Button';
import { Input } from './Input';
import { Card, CardHeader, CardContent, CardFooter, GameCard, UserCard } from './Card';
import { Modal, Drawer, Dialog } from './Modal';
import { Select, SelectOption } from './Select';
import { Loading, Skeleton } from './Loading';
import { Badge, BadgeWrapper } from './Badge';
import { ToastProvider, useToast } from './Toast';
import { Search, User, Mail, Phone, Bell, Star, Heart, Settings } from 'lucide-react';

// 内部组件，使用Toast上下文
const ComponentDemoContent: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectValue, setSelectValue] = useState<string>('');
  const [multiSelectValue, setMultiSelectValue] = useState<string[]>([]);
  const [showLoading, setShowLoading] = useState(false);
  
  const { addToast } = useToast();

  const handleButtonClick = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setIsModalOpen(true);
    }, 2000);
  };

  const handleShowLoading = () => {
    setShowLoading(true);
    setTimeout(() => {
      setShowLoading(false);
    }, 3000);
  };

  const mockUser = {
    name: 'John Doe',
    vipLevel: 3,
    balance: 125000,
  };

  const selectOptions: SelectOption[] = [
    { value: 'option1', label: '选项一', icon: <Star className="w-4 h-4" /> },
    { value: 'option2', label: '选项二', icon: <Heart className="w-4 h-4" /> },
    { value: 'option3', label: '选项三', icon: <Settings className="w-4 h-4" /> },
    { value: 'option4', label: '禁用选项', disabled: true },
    { value: 'option5', label: '带描述的选项', description: '这是一个带有详细描述的选项' },
  ];

  return (
    <div className="p-8 space-y-8 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">基础组件演示</h1>

      {/* Button 组件演示 */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">Button 组件</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Button variant="primary" onClick={handleButtonClick} loading={loading}>
            主要按钮
          </Button>
          <Button variant="secondary">
            次要按钮
          </Button>
          <Button variant="danger">
            危险按钮
          </Button>
          <Button variant="success">
            成功按钮
          </Button>
          <Button variant="outline">
            边框按钮
          </Button>
          <Button variant="ghost">
            透明按钮
          </Button>
          <Button disabled>
            禁用按钮
          </Button>
          <Button loading>
            加载中
          </Button>
        </div>
        
        <div className="space-y-2">
          <h3 className="text-lg font-medium">不同尺寸</h3>
          <div className="flex items-center gap-4">
            <Button size="sm">小按钮</Button>
            <Button size="md">中按钮</Button>
            <Button size="lg">大按钮</Button>
            <Button size="xl">超大按钮</Button>
          </div>
        </div>

        <div className="space-y-2">
          <h3 className="text-lg font-medium">带图标</h3>
          <div className="flex items-center gap-4">
            <Button icon={<User />} iconPosition="left">
              左图标
            </Button>
            <Button icon={<Search />} iconPosition="right">
              右图标
            </Button>
          </div>
        </div>
      </section>

      {/* Input 组件演示 */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">Input 组件</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input
            label="用户名"
            placeholder="请输入用户名"
            leftIcon={<User />}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
          />
          <Input
            label="邮箱"
            type="email"
            placeholder="请输入邮箱"
            leftIcon={<Mail />}
            success="邮箱格式正确"
          />
          <Input
            label="手机号"
            type="tel"
            placeholder="请输入手机号"
            leftIcon={<Phone />}
            error="手机号格式不正确"
          />
          <Input
            label="密码"
            type="password"
            placeholder="请输入密码"
            showPasswordToggle
            helperText="密码至少8位字符"
          />
          <Input
            label="搜索"
            type="search"
            placeholder="搜索内容..."
            leftIcon={<Search />}
            variant="filled"
          />
          <Input
            label="禁用输入"
            placeholder="禁用状态"
            disabled
          />
        </div>
      </section>

      {/* Card 组件演示 */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">Card 组件</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card variant="default">
            <CardHeader divider>
              <h3 className="font-semibold">默认卡片</h3>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">这是一个默认样式的卡片</p>
            </CardContent>
          </Card>

          <Card variant="elevated" hover>
            <CardHeader>
              <h3 className="font-semibold">悬浮卡片</h3>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">带有悬停效果的卡片</p>
            </CardContent>
          </Card>

          <Card variant="outlined" clickable>
            <CardHeader>
              <h3 className="font-semibold">边框卡片</h3>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">可点击的边框卡片</p>
            </CardContent>
          </Card>

          <Card variant="filled">
            <CardHeader divider>
              <h3 className="font-semibold">填充卡片</h3>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">填充背景的卡片</p>
            </CardContent>
            <CardFooter divider>
              <Button size="sm">操作</Button>
            </CardFooter>
          </Card>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <GameCard
            title="11选5彩票"
            description="每日7期开奖，简单易玩，中奖率高"
            badge="热门"
            status="active"
            onPlay={() => alert('进入11选5游戏')}
          />
          
          <UserCard user={mockUser} />
        </div>
      </section>

      {/* Modal 组件演示 */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">Modal 组件</h2>
        <div className="flex gap-4">
          <Button onClick={() => setIsModalOpen(true)}>
            打开弹窗
          </Button>
          <Button onClick={() => setIsDrawerOpen(true)}>
            打开抽屉
          </Button>
          <Button onClick={() => setIsDialogOpen(true)}>
            打开确认对话框
          </Button>
        </div>
      </section>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="演示弹窗"
        size="md"
      >
        <div className="p-6">
          <p className="text-gray-600 mb-4">
            这是一个演示弹窗，展示了Modal组件的基本功能。支持动画过渡效果。
          </p>
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>
              取消
            </Button>
            <Button onClick={() => setIsModalOpen(false)}>
              确认
            </Button>
          </div>
        </div>
      </Modal>

      {/* Drawer */}
      <Drawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        title="侧边抽屉"
        position="right"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            这是一个从右侧滑出的抽屉组件，适合用于导航菜单或详细信息展示。
          </p>
          <div className="space-y-3">
            <Button fullWidth variant="outline">
              菜单项 1
            </Button>
            <Button fullWidth variant="outline">
              菜单项 2
            </Button>
            <Button fullWidth variant="outline">
              菜单项 3
            </Button>
          </div>
        </div>
      </Drawer>

      {/* Select 组件演示 */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">Select 组件</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">基础选择器</label>
            <Select
              options={selectOptions}
              value={selectValue}
              onChange={(value) => setSelectValue(value as string)}
              placeholder="请选择一个选项"
            />
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">可搜索选择器</label>
            <Select
              options={selectOptions}
              searchable
              placeholder="搜索并选择"
            />
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">多选选择器</label>
            <Select
              options={selectOptions}
              multiple
              value={multiSelectValue}
              onChange={(value) => setMultiSelectValue(value as string[])}
              placeholder="可选择多个选项"
            />
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">可清空选择器</label>
            <Select
              options={selectOptions}
              clearable
              placeholder="可清空的选择器"
            />
          </div>
        </div>
      </section>

      {/* Loading 组件演示 */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">Loading 组件</h2>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <h3 className="text-lg font-medium">不同类型的加载动画</h3>
            <div className="flex items-center gap-8 p-6 bg-white rounded-lg">
              <div className="text-center space-y-2">
                <Loading variant="spinner" />
                <p className="text-sm text-gray-600">旋转器</p>
              </div>
              <div className="text-center space-y-2">
                <Loading variant="dots" />
                <p className="text-sm text-gray-600">点状</p>
              </div>
              <div className="text-center space-y-2">
                <Loading variant="pulse" />
                <p className="text-sm text-gray-600">脉冲</p>
              </div>
            </div>
          </div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-medium">不同尺寸</h3>
            <div className="flex items-center gap-8 p-6 bg-white rounded-lg">
              <Loading size="sm" text="小" />
              <Loading size="md" text="中" />
              <Loading size="lg" text="大" />
              <Loading size="xl" text="超大" />
            </div>
          </div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-medium">骨架屏</h3>
            <div className="p-6 bg-white rounded-lg space-y-4">
              <div className="flex items-center space-x-4">
                <Skeleton variant="circular" width={40} height={40} />
                <div className="space-y-2 flex-1">
                  <Skeleton variant="text" width="60%" />
                  <Skeleton variant="text" width="40%" />
                </div>
              </div>
              <Skeleton variant="rectangular" height={200} />
            </div>
          </div>
          
          <div className="space-y-2">
            <Button onClick={handleShowLoading}>
              显示全屏加载
            </Button>
          </div>
        </div>
      </section>

      {/* Badge 组件演示 */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">Badge 组件</h2>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <h3 className="text-lg font-medium">基础徽章</h3>
            <div className="flex items-center gap-4 p-6 bg-white rounded-lg">
              <Badge>默认</Badge>
              <Badge variant="primary">主要</Badge>
              <Badge variant="secondary">次要</Badge>
              <Badge variant="success">成功</Badge>
              <Badge variant="warning">警告</Badge>
              <Badge variant="danger">危险</Badge>
              <Badge variant="info">信息</Badge>
            </div>
          </div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-medium">不同尺寸</h3>
            <div className="flex items-center gap-4 p-6 bg-white rounded-lg">
              <Badge size="sm" variant="primary">小</Badge>
              <Badge size="md" variant="primary">中</Badge>
              <Badge size="lg" variant="primary">大</Badge>
            </div>
          </div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-medium">带图标和可关闭</h3>
            <div className="flex items-center gap-4 p-6 bg-white rounded-lg">
              <Badge icon={<Star />} variant="primary">收藏</Badge>
              <Badge closable variant="success" onClose={() => alert('关闭徽章')}>
                可关闭
              </Badge>
            </div>
          </div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-medium">数字徽章</h3>
            <div className="flex items-center gap-6 p-6 bg-white rounded-lg">
              <BadgeWrapper badge={{ count: 5, variant: 'danger' }}>
                <Bell className="w-6 h-6 text-gray-600" />
              </BadgeWrapper>
              <BadgeWrapper badge={{ count: 99, variant: 'primary', maxCount: 99 }}>
                <Mail className="w-6 h-6 text-gray-600" />
              </BadgeWrapper>
              <BadgeWrapper badge={{ count: 1000, variant: 'success', maxCount: 999 }}>
                <User className="w-6 h-6 text-gray-600" />
              </BadgeWrapper>
              <BadgeWrapper badge={{ dot: true, variant: 'danger' }}>
                <Settings className="w-6 h-6 text-gray-600" />
              </BadgeWrapper>
            </div>
          </div>
        </div>
      </section>

      {/* Toast 组件演示 */}
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-800">Toast 组件</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Button 
            variant="success" 
            onClick={() => addToast({
              type: 'success',
              title: '操作成功',
              message: '您的操作已成功完成！',
              duration: 3000
            })}
          >
            成功提示
          </Button>
          <Button 
            variant="danger" 
            onClick={() => addToast({
              type: 'error',
              title: '操作失败',
              message: '抱歉，操作失败，请重试。',
              duration: 5000
            })}
          >
            错误提示
          </Button>
          <Button 
            variant="secondary" 
            onClick={() => addToast({
              type: 'warning',
              title: '注意',
              message: '请注意检查您的输入信息。',
              duration: 4000
            })}
          >
            警告提示
          </Button>
          <Button 
            variant="outline" 
            onClick={() => addToast({
              type: 'info',
              message: '这是一条普通的信息提示。',
              duration: 3000
            })}
          >
            信息提示
          </Button>
        </div>
        
        <div className="flex gap-4">
          <Button 
            onClick={() => addToast({
              type: 'success',
              title: '带操作的提示',
              message: '点击右侧按钮执行操作。',
              action: {
                label: '立即查看',
                onClick: () => alert('执行操作')
              },
              duration: 0 // 不自动关闭
            })}
          >
            带操作按钮
          </Button>
          <Button 
            variant="outline"
            onClick={() => addToast({
              type: 'info',
              message: '这是一个不可关闭的持久提示。',
              closable: false,
              duration: 0
            })}
          >
            持久提示
          </Button>
        </div>
      </section>

      {/* Dialog */}
      <Dialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        title="确认操作"
        type="confirm"
        onConfirm={() => alert('已确认')}
        onCancel={() => alert('已取消')}
      >
        <p className="text-gray-700">
          您确定要执行此操作吗？此操作不可撤销。
        </p>
      </Dialog>

      {/* 全屏加载 */}
      {showLoading && (
        <Loading
          fullScreen
          text="正在加载中..."
          size="lg"
        />
      )}
    </div>
  );
};

// 主组件，提供Toast上下文
const ComponentDemo: React.FC = () => {
  return (
    <ToastProvider>
      <ComponentDemoContent />
    </ToastProvider>
  );
};

export default ComponentDemo;