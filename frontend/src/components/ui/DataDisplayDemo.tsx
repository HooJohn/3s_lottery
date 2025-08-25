import React, { useState } from 'react';
import { Table } from './Table';
import { List } from './List';
import { Chart } from './Chart';
import { Statistics, StatisticsGroup, Counter } from './Statistics';
import { Card } from './Card';
import { Button } from './Button';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Users, 
  ShoppingCart, 
  Activity,
  ChevronRight,
  Star
} from 'lucide-react';

const DataDisplayDemo: React.FC = () => {
  // 表格演示数据
  const tableData = [
    { id: 1, name: '张三', age: 28, city: '北京', status: 'active', score: 85 },
    { id: 2, name: '李四', age: 32, city: '上海', status: 'inactive', score: 72 },
    { id: 3, name: '王五', age: 24, city: '广州', status: 'active', score: 91 },
    { id: 4, name: '赵六', age: 35, city: '深圳', status: 'active', score: 68 },
    { id: 5, name: '钱七', age: 29, city: '杭州', status: 'inactive', score: 76 },
    { id: 6, name: '孙八', age: 31, city: '成都', status: 'active', score: 88 },
    { id: 7, name: '周九', age: 27, city: '武汉', status: 'active', score: 79 },
    { id: 8, name: '吴十', age: 33, city: '南京', status: 'inactive', score: 84 },
  ];

  const tableColumns = [
    {
      key: 'id',
      title: 'ID',
      dataIndex: 'id',
      width: 80,
      sorter: true,
    },
    {
      key: 'name',
      title: '姓名',
      dataIndex: 'name',
      sorter: true,
    },
    {
      key: 'age',
      title: '年龄',
      dataIndex: 'age',
      sorter: true,
    },
    {
      key: 'city',
      title: '城市',
      dataIndex: 'city',
      sorter: true,
      filterable: true,
    },
    {
      key: 'status',
      title: '状态',
      dataIndex: 'status',
      render: (value: string) => (
        <span className={`px-2 py-1 rounded-full text-xs ${
          value === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
        }`}>
          {value === 'active' ? '活跃' : '非活跃'}
        </span>
      ),
      filterable: true,
    },
    {
      key: 'score',
      title: '得分',
      dataIndex: 'score',
      sorter: true,
      render: (value: number) => (
        <div className="flex items-center">
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className="bg-blue-600 h-2.5 rounded-full" 
              style={{ width: `${value}%` }}
            ></div>
          </div>
          <span className="ml-2">{value}</span>
        </div>
      ),
    },
    {
      key: 'action',
      title: '操作',
      render: (_: any, record: any) => (
        <div className="flex space-x-2">
          <Button size="sm" variant="outline">查看</Button>
          <Button size="sm" variant="outline" color="danger">删除</Button>
        </div>
      ),
    },
  ];

  // 列表演示数据
  const listData = [
    { id: 1, title: '非洲彩票平台上线', description: '全新的彩票平台正式上线，提供多种彩票游戏', date: '2023-10-15' },
    { id: 2, title: '11选5彩票新增玩法', description: '11选5彩票新增多种玩法，中奖机会更多', date: '2023-10-12' },
    { id: 3, title: '首充优惠活动', description: '新用户首次充值享受100%充值奖励', date: '2023-10-10' },
    { id: 4, title: 'VIP会员系统升级', description: 'VIP会员系统全面升级，特权更丰富', date: '2023-10-08' },
    { id: 5, title: '推荐好友得奖励', description: '推荐好友注册，双方都可获得奖励', date: '2023-10-05' },
  ];

  // 图表演示数据
  const lineChartData = {
    labels: ['一月', '二月', '三月', '四月', '五月', '六月'],
    datasets: [
      {
        label: '用户增长',
        data: [12, 19, 3, 5, 2, 3],
        fill: false,
        tension: 0.4,
      },
      {
        label: '投注金额',
        data: [5, 10, 15, 12, 18, 14],
        fill: false,
        tension: 0.4,
      },
    ],
  };

  const barChartData = {
    labels: ['11选5', '刮刮乐', '大乐透', '体育博彩', '其他'],
    datasets: [
      {
        label: '投注金额',
        data: [12000, 19000, 3000, 5000, 2000],
      },
    ],
  };

  const pieChartData = {
    labels: ['存款', '提款', '投注', '中奖', '奖励'],
    datasets: [
      {
        data: [30, 20, 25, 15, 10],
      },
    ],
  };

  // 统计数据
  const statisticsData = [
    { title: '总用户数', value: 12345, trend: 'up', trendPercentage: 15, icon: <Users className="w-10 h-10 text-blue-500" /> },
    { title: '今日投注', value: 54321, trend: 'up', trendPercentage: 8, icon: <ShoppingCart className="w-10 h-10 text-green-500" /> },
    { title: '总奖金池', value: 987654, trend: 'up', trendPercentage: 12, icon: <DollarSign className="w-10 h-10 text-yellow-500" /> },
    { title: '活跃用户', value: 7890, trend: 'down', trendPercentage: 3, icon: <Activity className="w-10 h-10 text-red-500" /> },
  ];

  // 虚拟列表数据
  const virtualListData = Array.from({ length: 1000 }, (_, index) => ({
    id: index + 1,
    title: `项目 ${index + 1}`,
    description: `这是项目 ${index + 1} 的描述信息`,
  }));

  // 状态管理
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [infiniteData, setInfiniteData] = useState(listData.slice(0, 3));

  // 加载更多数据
  const loadMoreData = () => {
    setLoading(true);
    
    // 模拟异步加载
    setTimeout(() => {
      if (infiniteData.length >= listData.length) {
        setHasMore(false);
      } else {
        setInfiniteData([...infiniteData, ...listData.slice(infiniteData.length, infiniteData.length + 1)]);
      }
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-12">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">数据展示组件演示</h1>
        <p className="text-gray-600">展示表格、列表、图表和统计数据组件的功能和用法</p>
      </div>

      {/* 统计数据展示 */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">统计数据</h2>
        
        <StatisticsGroup columns={4} title="核心指标">
          {statisticsData.map((stat, index) => (
            <Statistics
              key={index}
              title={stat.title}
              value={stat.value}
              trend={stat.trend as 'up' | 'down'}
              trendPercentage={stat.trendPercentage}
              prefix={stat.title === '总奖金池' ? <DollarSign className="w-4 h-4" /> : undefined}
              icon={stat.icon}
              animation
            />
          ))}
        </StatisticsGroup>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">数字动画</h3>
            <div className="space-y-6">
              <div>
                <p className="text-sm text-gray-500 mb-1">基本计数器</p>
                <div className="text-3xl font-bold text-gray-900">
                  <Counter start={0} end={12345} duration={2000} />
                </div>
              </div>
              
              <div>
                <p className="text-sm text-gray-500 mb-1">带前缀和后缀</p>
                <div className="text-3xl font-bold text-gray-900">
                  <Counter 
                    start={0} 
                    end={9876} 
                    duration={2000} 
                    prefix={<DollarSign className="inline w-6 h-6 mr-1" />} 
                    suffix=" 元"
                  />
                </div>
              </div>
              
              <div>
                <p className="text-sm text-gray-500 mb-1">小数点和分隔符</p>
                <div className="text-3xl font-bold text-gray-900">
                  <Counter 
                    start={0} 
                    end={1234.56} 
                    duration={2000} 
                    decimals={2}
                    separator="," 
                  />
                </div>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">统计卡片变体</h3>
            <div className="space-y-4">
              <Statistics
                title="总收入"
                value={123456.78}
                precision={2}
                prefix={<DollarSign className="w-4 h-4" />}
                trend="up"
                trendPercentage={12.5}
                description="较上月"
                size="large"
              />
              
              <Statistics
                title="转化率"
                value={25.8}
                suffix="%"
                trend="down"
                trendPercentage={3.2}
                description="较上周"
                status="danger"
              />
              
              <Statistics
                title="活跃用户"
                value={8642}
                trend="neutral"
                description="过去30天"
                layout="horizontal"
                icon={<Users className="w-8 h-8 text-blue-500" />}
              />
            </div>
          </Card>
        </div>
      </section>

      {/* 图表展示 */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">图表</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Chart
            type="line"
            data={lineChartData}
            title="用户增长和投注趋势"
            description="过去6个月的数据"
            theme="primary"
          />
          
          <Chart
            type="bar"
            data={barChartData}
            title="各游戏投注金额"
            description="按游戏类型统计"
            theme="success"
          />
          
          <Chart
            type="pie"
            data={pieChartData}
            title="资金流向分布"
            description="按交易类型统计"
            theme="warning"
          />
          
          <Chart
            type="doughnut"
            data={pieChartData}
            title="资金流向分布"
            description="环形图展示"
            theme="danger"
          />
        </div>
      </section>

      {/* 表格展示 */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">表格</h2>
        
        <Card>
          <Table
            columns={tableColumns}
            dataSource={tableData}
            rowKey="id"
            pagination={{
              pageSize: 5,
              showSizeChanger: true,
              showTotal: (total, range) => `显示 ${range[0]}-${range[1]}，共 ${total} 条`,
            }}
            bordered
            title={() => <h3 className="text-lg font-semibold">用户数据表格</h3>}
            expandable={{
              expandedRowRender: (record) => (
                <div className="p-4 bg-gray-50">
                  <p className="mb-2"><strong>详细信息：</strong></p>
                  <p>ID: {record.id}</p>
                  <p>姓名: {record.name}</p>
                  <p>年龄: {record.age}</p>
                  <p>城市: {record.city}</p>
                  <p>状态: {record.status === 'active' ? '活跃' : '非活跃'}</p>
                  <p>得分: {record.score}</p>
                </div>
              ),
              rowExpandable: (record) => record.status === 'active',
            }}
          />
        </Card>
      </section>

      {/* 列表展示 */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">列表</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <List
              header={<h3 className="text-lg font-semibold">基础列表</h3>}
              dataSource={listData}
              rowKey="id"
              renderItem={(item) => (
                <List.Item
                  title={item.title}
                  description={item.description}
                  extra={<span className="text-gray-500 text-sm">{item.date}</span>}
                  actions={[
                    <Button key="view" size="sm" variant="outline">查看</Button>,
                    <Button key="edit" size="sm" variant="outline">编辑</Button>,
                  ]}
                />
              )}
              bordered
              split
            />
          </Card>
          
          <Card>
            <List
              header={<h3 className="text-lg font-semibold">网格列表</h3>}
              dataSource={listData}
              rowKey="id"
              grid={{ column: 2, gutter: 16 }}
              renderItem={(item) => (
                <Card className="h-full">
                  <div className="p-4">
                    <h4 className="font-medium text-gray-900 mb-2">{item.title}</h4>
                    <p className="text-sm text-gray-500 mb-4">{item.description}</p>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-400">{item.date}</span>
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    </div>
                  </div>
                </Card>
              )}
            />
          </Card>
          
          <Card>
            <List
              header={<h3 className="text-lg font-semibold">虚拟滚动列表</h3>}
              dataSource={virtualListData}
              rowKey="id"
              renderItem={(item) => (
                <List.Item
                  title={item.title}
                  description={item.description}
                />
              )}
              virtual
              height={300}
              itemHeight={80}
              bordered
            />
          </Card>
          
          <Card>
            <List
              header={<h3 className="text-lg font-semibold">无限滚动列表</h3>}
              dataSource={infiniteData}
              rowKey="id"
              renderItem={(item) => (
                <List.Item
                  title={item.title}
                  description={item.description}
                  extra={<span className="text-gray-500 text-sm">{item.date}</span>}
                />
              )}
              infiniteScroll
              hasMore={hasMore}
              loadMore={loadMoreData}
              loadingMore={loading}
              height={300}
              bordered
            />
          </Card>
        </div>
      </section>

      {/* 组合使用示例 */}
      <section>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">组合使用示例</h2>
        
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">游戏数据分析面板</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
              <Statistics
                title="总投注额"
                value={1234567}
                prefix={<DollarSign className="w-4 h-4" />}
                trend="up"
                trendPercentage={8.5}
              />
              
              <Statistics
                title="总中奖额"
                value={876543}
                prefix={<DollarSign className="w-4 h-4" />}
                trend="up"
                trendPercentage={5.2}
              />
              
              <Statistics
                title="投注人次"
                value={9876}
                trend="up"
                trendPercentage={12.3}
              />
              
              <Statistics
                title="中奖率"
                value={32.5}
                suffix="%"
                trend="down"
                trendPercentage={2.1}
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <Chart
                type="line"
                data={lineChartData}
                title="投注趋势"
                height={250}
              />
              
              <Chart
                type="pie"
                data={pieChartData}
                title="游戏分布"
                height={250}
              />
            </div>
            
            <Table
              columns={[
                { key: 'id', title: 'ID', dataIndex: 'id', width: 80 },
                { key: 'name', title: '游戏名称', dataIndex: 'name' },
                { key: 'betAmount', title: '投注金额', dataIndex: 'score', sorter: true },
                { key: 'winAmount', title: '中奖金额', dataIndex: 'age', sorter: true },
                { key: 'ratio', title: '返奖率', 
                  render: (_, record) => `${((record.age / record.score) * 100).toFixed(2)}%` 
                },
                { key: 'popularity', title: '热度', 
                  render: (_, record) => (
                    <div className="flex items-center">
                      {Array.from({ length: Math.ceil(record.score / 20) }).map((_, i) => (
                        <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                      ))}
                    </div>
                  )
                },
              ]}
              dataSource={tableData}
              rowKey="id"
              pagination={{ pageSize: 5 }}
              size="small"
            />
          </div>
        </Card>
      </section>
    </div>
  );
};

export default DataDisplayDemo;