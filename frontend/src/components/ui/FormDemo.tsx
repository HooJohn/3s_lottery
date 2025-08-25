import React, { useState } from 'react';
import { Card } from './Card';
import { Button } from './Button';
import { Input } from './Input';
import FormField from './FormField';
import { Select } from './Select';
import Checkbox, { CheckboxGroup } from './Checkbox';
import Radio, { RadioGroup } from './Radio';
import DatePicker, { DateRangePicker } from './DatePicker';

const FormDemo: React.FC = () => {
  // 表单状态
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    country: '',
    hobbies: [] as string[],
    gender: '',
    birthDate: null as Date | null,
    workPeriod: [null, null] as [Date | null, Date | null],
    newsletter: false,
    terms: false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // 国家选项
  const countryOptions = [
    { value: 'NG', label: '尼日利亚', icon: '🇳🇬' },
    { value: 'CM', label: '喀麦隆', icon: '🇨🇲' },
    { value: 'GH', label: '加纳', icon: '🇬🇭' },
    { value: 'KE', label: '肯尼亚', icon: '🇰🇪' },
    { value: 'ZA', label: '南非', icon: '🇿🇦' },
  ];

  // 爱好选项
  const hobbyOptions = [
    { value: 'sports', label: '体育运动', description: '足球、篮球、网球等' },
    { value: 'music', label: '音乐', description: '听音乐、演奏乐器' },
    { value: 'reading', label: '阅读', description: '小说、杂志、新闻' },
    { value: 'travel', label: '旅行', description: '探索新地方' },
    { value: 'cooking', label: '烹饪', description: '制作美食' },
  ];

  // 性别选项
  const genderOptions = [
    { value: 'male', label: '男性' },
    { value: 'female', label: '女性' },
    { value: 'other', label: '其他' },
    { value: 'prefer-not-to-say', label: '不愿透露' },
  ];

  // 表单验证
  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = '请输入姓名';
    }

    if (!formData.email.trim()) {
      newErrors.email = '请输入邮箱地址';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = '请输入有效的邮箱地址';
    }

    if (!formData.country) {
      newErrors.country = '请选择国家';
    }

    if (!formData.gender) {
      newErrors.gender = '请选择性别';
    }

    if (!formData.terms) {
      newErrors.terms = '请同意服务条款';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // 提交表单
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      console.log('表单数据:', formData);
      alert('表单提交成功！请查看控制台输出。');
    }
  };

  // 重置表单
  const handleReset = () => {
    setFormData({
      name: '',
      email: '',
      country: '',
      hobbies: [],
      gender: '',
      birthDate: null,
      workPeriod: [null, null],
      newsletter: false,
      terms: false,
    });
    setErrors({});
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">表单组件演示</h1>
        <p className="text-gray-600">展示所有表单组件的功能和用法</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* 基础输入字段 */}
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">基础输入字段</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormField
                label="姓名"
                required
                error={errors.name}
                hint="请输入您的真实姓名"
              >
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="请输入姓名"
                />
              </FormField>

              <FormField
                label="邮箱地址"
                required
                error={errors.email}
                hint="用于接收重要通知"
              >
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="请输入邮箱地址"
                />
              </FormField>
            </div>
          </div>
        </Card>

        {/* 选择器组件 */}
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">选择器组件</h2>
            
            <div className="space-y-6">
              <FormField
                label="国家"
                required
                error={errors.country}
                hint="选择您所在的国家"
              >
                <Select
                  options={countryOptions}
                  value={formData.country}
                  onChange={(value) => setFormData({ ...formData, country: value as string })}
                  placeholder="请选择国家"
                  searchable
                  clearable
                />
              </FormField>

              <FormField
                label="兴趣爱好"
                hint="可以选择多个选项"
              >
                <Select
                  options={hobbyOptions}
                  value={formData.hobbies}
                  onChange={(value) => setFormData({ ...formData, hobbies: value as string[] })}
                  placeholder="请选择兴趣爱好"
                  multiple
                  searchable
                  clearable
                />
              </FormField>
            </div>
          </div>
        </Card>

        {/* 复选框和单选框 */}
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">复选框和单选框</h2>
            
            <div className="space-y-6">
              <FormField
                label="性别"
                required
                error={errors.gender}
              >
                <RadioGroup
                  options={genderOptions}
                  value={formData.gender}
                  onChange={(value) => setFormData({ ...formData, gender: value })}
                  name="gender"
                  direction="horizontal"
                />
              </FormField>

              <FormField label="兴趣爱好（复选框版本）">
                <CheckboxGroup
                  options={hobbyOptions}
                  value={formData.hobbies}
                  onChange={(value) => setFormData({ ...formData, hobbies: value })}
                  name="hobbies"
                />
              </FormField>

              <div className="space-y-3">
                <Checkbox
                  checked={formData.newsletter}
                  onChange={(checked) => setFormData({ ...formData, newsletter: checked })}
                  label="订阅邮件通知"
                  description="接收产品更新和优惠信息"
                />

                <FormField error={errors.terms}>
                  <Checkbox
                    checked={formData.terms}
                    onChange={(checked) => setFormData({ ...formData, terms: checked })}
                    label="我同意服务条款和隐私政策"
                    color="primary"
                  />
                </FormField>
              </div>
            </div>
          </div>
        </Card>

        {/* 日期选择器 */}
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">日期选择器</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormField
                label="出生日期"
                hint="选择您的出生日期"
              >
                <DatePicker
                  value={formData.birthDate}
                  onChange={(date) => setFormData({ ...formData, birthDate: date })}
                  placeholder="请选择出生日期"
                  maxDate={new Date()}
                />
              </FormField>

              <FormField
                label="工作时间段"
                hint="选择工作的起止时间"
              >
                <DateRangePicker
                  value={formData.workPeriod}
                  onChange={(dates) => setFormData({ ...formData, workPeriod: dates })}
                  placeholder="请选择工作时间段"
                />
              </FormField>
            </div>
          </div>
        </Card>

        {/* 表单操作按钮 */}
        <Card>
          <div className="p-6">
            <div className="flex flex-col sm:flex-row gap-4 justify-end">
              <Button
                type="button"
                variant="outline"
                onClick={handleReset}
                className="sm:w-auto"
              >
                重置表单
              </Button>
              <Button
                type="submit"
                className="sm:w-auto"
              >
                提交表单
              </Button>
            </div>
          </div>
        </Card>

        {/* 表单数据预览 */}
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">表单数据预览</h2>
            <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-auto">
              {JSON.stringify(formData, null, 2)}
            </pre>
          </div>
        </Card>
      </form>
    </div>
  );
};

export default FormDemo;