// 表单验证工具函数

export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => string | null;
  message?: string;
}

export interface ValidationSchema {
  [key: string]: ValidationRule | ValidationRule[];
}

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

// 验证单个字段
export const validateField = (value: any, rules: ValidationRule | ValidationRule[]): string | null => {
  const ruleArray = Array.isArray(rules) ? rules : [rules];
  
  for (const rule of ruleArray) {
    // 必填验证
    if (rule.required && (value === null || value === undefined || value === '' || 
        (Array.isArray(value) && value.length === 0))) {
      return rule.message || '此字段为必填项';
    }
    
    // 如果值为空且不是必填，跳过其他验证
    if (!rule.required && (value === null || value === undefined || value === '')) {
      continue;
    }
    
    // 最小长度验证
    if (rule.minLength && typeof value === 'string' && value.length < rule.minLength) {
      return rule.message || `最少需要${rule.minLength}个字符`;
    }
    
    // 最大长度验证
    if (rule.maxLength && typeof value === 'string' && value.length > rule.maxLength) {
      return rule.message || `最多允许${rule.maxLength}个字符`;
    }
    
    // 正则表达式验证
    if (rule.pattern && typeof value === 'string' && !rule.pattern.test(value)) {
      return rule.message || '格式不正确';
    }
    
    // 自定义验证
    if (rule.custom) {
      const customError = rule.custom(value);
      if (customError) {
        return customError;
      }
    }
  }
  
  return null;
};

// 验证整个表单
export const validateForm = (data: Record<string, any>, schema: ValidationSchema): ValidationResult => {
  const errors: Record<string, string> = {};
  
  for (const [field, rules] of Object.entries(schema)) {
    const error = validateField(data[field], rules);
    if (error) {
      errors[field] = error;
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// 常用验证规则
export const commonRules = {
  required: { required: true },
  email: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message: '请输入有效的邮箱地址',
  },
  phone: {
    pattern: /^[\+]?[1-9][\d]{0,15}$/,
    message: '请输入有效的手机号码',
  },
  password: {
    minLength: 8,
    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
    message: '密码至少8位，包含大小写字母和数字',
  },
  username: {
    minLength: 3,
    maxLength: 20,
    pattern: /^[a-zA-Z0-9_]+$/,
    message: '用户名只能包含字母、数字和下划线，长度3-20位',
  },
  url: {
    pattern: /^https?:\/\/.+/,
    message: '请输入有效的URL地址',
  },
  number: {
    custom: (value: any) => {
      if (isNaN(Number(value))) {
        return '请输入有效的数字';
      }
      return null;
    },
  },
  positiveNumber: {
    custom: (value: any) => {
      const num = Number(value);
      if (isNaN(num)) {
        return '请输入有效的数字';
      }
      if (num <= 0) {
        return '请输入大于0的数字';
      }
      return null;
    },
  },
  age: {
    custom: (value: any) => {
      const age = Number(value);
      if (isNaN(age)) {
        return '请输入有效的年龄';
      }
      if (age < 0 || age > 150) {
        return '请输入有效的年龄范围';
      }
      return null;
    },
  },
};

// 创建验证规则的辅助函数
export const createRule = (rule: ValidationRule): ValidationRule => rule;

export const combineRules = (...rules: ValidationRule[]): ValidationRule[] => rules;

// 异步验证支持
export interface AsyncValidationRule {
  validator: (value: any) => Promise<string | null>;
  message?: string;
}

export const validateFieldAsync = async (
  value: any, 
  rules: (ValidationRule | AsyncValidationRule)[]
): Promise<string | null> => {
  // 先执行同步验证
  const syncRules = rules.filter(rule => !('validator' in rule)) as ValidationRule[];
  const syncError = validateField(value, syncRules);
  if (syncError) {
    return syncError;
  }
  
  // 再执行异步验证
  const asyncRules = rules.filter(rule => 'validator' in rule) as AsyncValidationRule[];
  for (const rule of asyncRules) {
    try {
      const error = await rule.validator(value);
      if (error) {
        return error;
      }
    } catch (err) {
      return rule.message || '验证失败';
    }
  }
  
  return null;
};

// 防抖验证 Hook
export const useDebounceValidation = (
  value: any,
  rules: ValidationRule | ValidationRule[],
  delay: number = 300
) => {
  const [error, setError] = React.useState<string | null>(null);
  const [isValidating, setIsValidating] = React.useState(false);
  
  React.useEffect(() => {
    setIsValidating(true);
    const timer = setTimeout(() => {
      const validationError = validateField(value, rules);
      setError(validationError);
      setIsValidating(false);
    }, delay);
    
    return () => clearTimeout(timer);
  }, [value, rules, delay]);
  
  return { error, isValidating };
};

// 表单状态管理 Hook
export const useFormValidation = <T extends Record<string, any>>(
  initialData: T,
  schema: ValidationSchema
) => {
  const [data, setData] = React.useState<T>(initialData);
  const [errors, setErrors] = React.useState<Record<string, string>>({});
  const [touched, setTouched] = React.useState<Record<string, boolean>>({});
  
  const validateSingleField = (field: string, value: any) => {
    if (schema[field]) {
      const error = validateField(value, schema[field]);
      setErrors(prev => ({
        ...prev,
        [field]: error || '',
      }));
      return !error;
    }
    return true;
  };
  
  const validateAllFields = () => {
    const result = validateForm(data, schema);
    setErrors(result.errors);
    return result.isValid;
  };
  
  const updateField = (field: string, value: any) => {
    setData(prev => ({ ...prev, [field]: value }));
    
    // 如果字段已经被触摸过，立即验证
    if (touched[field]) {
      validateSingleField(field, value);
    }
  };
  
  const touchField = (field: string) => {
    setTouched(prev => ({ ...prev, [field]: true }));
    validateSingleField(field, data[field]);
  };
  
  const reset = () => {
    setData(initialData);
    setErrors({});
    setTouched({});
  };
  
  return {
    data,
    errors,
    touched,
    updateField,
    touchField,
    validateAllFields,
    reset,
    isValid: Object.keys(errors).length === 0,
  };
};

// React import for hooks
import React from 'react';