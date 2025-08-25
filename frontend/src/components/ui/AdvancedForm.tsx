import React from 'react';
import { Card } from './Card';
import { Button } from './Button';
import { Input } from './Input';
import FormField from './FormField';
import { Select } from './Select';
import Checkbox from './Checkbox';
import Radio, { RadioGroup } from './Radio';
import DatePicker from './DatePicker';
import { 
  useFormValidation, 
  commonRules, 
  combineRules, 
  createRule,
  ValidationSchema 
} from '@/utils/validation';

interface UserFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
  phone: string;
  country: string;
  birthDate: Date | null;
  gender: string;
  agreeTerms: boolean;
  newsletter: boolean;
}

const AdvancedForm: React.FC = () => {
  const initialData: UserFormData = {
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    phone: '',
    country: '',
    birthDate: null,
    gender: '',
    agreeTerms: false,
    newsletter: false,
  };

  // 验证规则
  const validationSchema: ValidationSchema = {
    username: combineRules(
      commonRules.required,
      commonRules.username
    ),
    email: combineRules(
      commonRules.required,
      commonRules.email
    ),
    password: combineRules(
      commonRules.required,
      commonRules.password
    ),
    confirmPassword: combineRules(
      commonRules.required,
      createRule({
        custom: (value) => {
          if (value !== data.password) {
            return '两次输入的密码不一致';
          }
          return null;
        }
      })
    ),
    fullName: combineRules(
      commonRules.required,
      createRule({ minLength: 2, message: '姓名至少需要2个字符' })
    ),
    phone: combineRules(
      commonRules.required,
      commonRules.phone
    ),
    country: commonRules.required,
    gender: commonRules.required,
    agreeTerms: createRule({
      custom: (value) => {
        if (!value) {
          return '请同意服务条款';
        }
        return null;
      }
    }),
  };

  const {
    data,
    errors,
    touched,
    updateField,
    touchField,
    validateAllFields,
    reset,
    isValid
  } = useFormValidation(initialData, validationSchema);

  // 选项数据
  const countryOptions = [
    { value: 'NG', label: '尼日利亚', icon: '🇳🇬' },
    { value: 'CM', label: '喀麦隆', icon: '🇨🇲' },
    { value: 'GH', label: '加纳', icon: '🇬🇭' },
    { value: 'KE', label: '肯尼亚', icon: '🇰🇪' },
    { value: 'ZA', label: '南非', icon: '🇿🇦' },
  ];

  const genderOptions = [
    { value: 'male', label: '男性' },
    { value: 'female', label: '女性' },
    { value: 'other', label: '其他' },
  ];

  // 提交处理
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateAllFields()) {
      console.log('表单提交成功:', data);
      alert('注册成功！请查看控制台输出。');
      reset();
    } else {
      console.log('表单验证失败:', errors);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <Card>
        <div className="p-6">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">用户注册</h1>
            <p className="text-gray-600">使用高级表单验证的注册表单示例</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 账户信息 */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">账户信息</h3>
              
              <FormField
                label="用户名"
                required
                error={touched.username ? errors.username : ''}
                hint="3-20位字符，只能包含字母、数字和下划线"
              >
                <Input
                  value={data.username}
                  onChange={(e) => updateField('username', e.target.value)}
                  onBlur={() => touchField('username')}
                  placeholder="请输入用户名"
                />
              </FormField>

              <FormField
                label="邮箱地址"
                required
                error={touched.email ? errors.email : ''}
                hint="用于登录和接收重要通知"
              >
                <Input
                  type="email"
                  value={data.email}
                  onChange={(e) => updateField('email', e.target.value)}
                  onBlur={() => touchField('email')}
                  placeholder="请输入邮箱地址"
                />
              </FormField>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  label="密码"
                  required
                  error={touched.password ? errors.password : ''}
                  hint="至少8位，包含大小写字母和数字"
                >
                  <Input
                    type="password"
                    value={data.password}
                    onChange={(e) => updateField('password', e.target.value)}
                    onBlur={() => touchField('password')}
                    placeholder="请输入密码"
                  />
                </FormField>

                <FormField
                  label="确认密码"
                  required
                  error={touched.confirmPassword ? errors.confirmPassword : ''}
                >
                  <Input
                    type="password"
                    value={data.confirmPassword}
                    onChange={(e) => updateField('confirmPassword', e.target.value)}
                    onBlur={() => touchField('confirmPassword')}
                    placeholder="请再次输入密码"
                  />
                </FormField>
              </div>
            </div>

            {/* 个人信息 */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">个人信息</h3>
              
              <FormField
                label="姓名"
                required
                error={touched.fullName ? errors.fullName : ''}
              >
                <Input
                  value={data.fullName}
                  onChange={(e) => updateField('fullName', e.target.value)}
                  onBlur={() => touchField('fullName')}
                  placeholder="请输入真实姓名"
                />
              </FormField>

              <FormField
                label="手机号"
                required
                error={touched.phone ? errors.phone : ''}
                hint="用于接收验证码和重要通知"
              >
                <Input
                  type="tel"
                  value={data.phone}
                  onChange={(e) => updateField('phone', e.target.value)}
                  onBlur={() => touchField('phone')}
                  placeholder="请输入手机号"
                />
              </FormField>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  label="国家"
                  required
                  error={touched.country ? errors.country : ''}
                >
                  <Select
                    options={countryOptions}
                    value={data.country}
                    onChange={(value) => {
                      updateField('country', value as string);
                      touchField('country');
                    }}
                    placeholder="请选择国家"
                    searchable
                  />
                </FormField>

                <FormField
                  label="出生日期"
                  hint="可选填"
                >
                  <DatePicker
                    value={data.birthDate}
                    onChange={(date) => updateField('birthDate', date)}
                    placeholder="请选择出生日期"
                    maxDate={new Date()}
                  />
                </FormField>
              </div>

              <FormField
                label="性别"
                required
                error={touched.gender ? errors.gender : ''}
              >
                <RadioGroup
                  options={genderOptions}
                  value={data.gender}
                  onChange={(value) => {
                    updateField('gender', value);
                    touchField('gender');
                  }}
                  name="gender"
                  direction="horizontal"
                />
              </FormField>
            </div>

            {/* 协议和设置 */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">协议和设置</h3>
              
              <FormField error={touched.agreeTerms ? errors.agreeTerms : ''}>
                <Checkbox
                  checked={data.agreeTerms}
                  onChange={(checked) => {
                    updateField('agreeTerms', checked);
                    touchField('agreeTerms');
                  }}
                  label="我已阅读并同意服务条款和隐私政策"
                  color="primary"
                />
              </FormField>

              <Checkbox
                checked={data.newsletter}
                onChange={(checked) => updateField('newsletter', checked)}
                label="订阅邮件通知"
                description="接收产品更新、优惠活动等信息"
              />
            </div>

            {/* 提交按钮 */}
            <div className="flex flex-col sm:flex-row gap-4 pt-6">
              <Button
                type="button"
                variant="outline"
                onClick={reset}
                className="flex-1"
              >
                重置表单
              </Button>
              <Button
                type="submit"
                disabled={!isValid}
                className="flex-1"
              >
                注册账户
              </Button>
            </div>

            {/* 表单状态显示 */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">表单状态</h4>
              <div className="text-sm space-y-1">
                <p>表单有效性: <span className={isValid ? 'text-green-600' : 'text-red-600'}>
                  {isValid ? '✓ 有效' : '✗ 无效'}
                </span></p>
                <p>错误数量: {Object.keys(errors).filter(key => errors[key]).length}</p>
                <p>已触摸字段: {Object.keys(touched).filter(key => touched[key]).length}</p>
              </div>
            </div>
          </form>
        </div>
      </Card>
    </div>
  );
};

export default AdvancedForm;