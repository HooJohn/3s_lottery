import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// 导入语言包
import enTranslations from '@/locales/en.json';
import frTranslations from '@/locales/fr.json';
import zhTranslations from '@/locales/zh.json';

// 语言资源
const resources = {
  en: {
    translation: enTranslations,
  },
  fr: {
    translation: frTranslations,
  },
  zh: {
    translation: zhTranslations,
  },
};

// 支持的语言列表
export const supportedLanguages = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'zh', name: '中文', flag: '🇨🇳' },
];

// 获取当前环境
const isDevelopment = process.env.NODE_ENV === 'development';

// 根据环境过滤语言
export const availableLanguages = isDevelopment 
  ? supportedLanguages 
  : supportedLanguages.filter(lang => lang.code !== 'zh');

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: isDevelopment,
    
    // 语言检测配置
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
    },

    interpolation: {
      escapeValue: false, // React已经处理了XSS
    },

    // 命名空间
    defaultNS: 'translation',
    ns: ['translation'],

    // 加载配置
    load: 'languageOnly',
    preload: isDevelopment ? ['en', 'fr', 'zh'] : ['en', 'fr'],

    // 键分隔符
    keySeparator: '.',
    nsSeparator: ':',

    // 复数规则
    pluralSeparator: '_',
    contextSeparator: '_',

    // 后备配置
    saveMissing: isDevelopment,
    missingKeyHandler: isDevelopment ? (lng, ns, key) => {
      console.warn(`Missing translation key: ${key} for language: ${lng}`);
    } : undefined,
  });

// 导出i18n实例
export default i18n;

// 工具函数：获取当前语言的区域设置
export const getCurrentLocale = (): string => {
  switch (i18n.language) {
    case 'fr':
      return 'fr-CM'; // 喀麦隆法语
    case 'zh':
      return 'zh-CN'; // 简体中文
    case 'en':
    default:
      return 'en-NG'; // 尼日利亚英语
  }
};

// 工具函数：格式化货币
export const formatCurrency = (amount: number, currency = 'NGN'): string => {
  const locale = getCurrentLocale();
  
  // 根据语言调整货币符号显示
  const currencyDisplay = i18n.language === 'zh' ? 'code' : 'symbol';
  
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
    currencyDisplay,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

// 工具函数：格式化数字
export const formatNumber = (number: number, options?: Intl.NumberFormatOptions): string => {
  const locale = getCurrentLocale();
  
  return new Intl.NumberFormat(locale, options).format(number);
};

// 工具函数：格式化百分比
export const formatPercentage = (value: number, minimumFractionDigits = 1): string => {
  const locale = getCurrentLocale();
  
  return new Intl.NumberFormat(locale, {
    style: 'percent',
    minimumFractionDigits,
    maximumFractionDigits: 2,
  }).format(value / 100);
};

// 工具函数：格式化日期
export const formatDate = (date: Date | string, options?: Intl.DateTimeFormatOptions): string => {
  const locale = getCurrentLocale();
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  };
  
  return new Intl.DateTimeFormat(locale, { ...defaultOptions, ...options }).format(dateObj);
};

// 工具函数：格式化时间
export const formatTime = (date: Date | string): string => {
  const locale = getCurrentLocale();
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  return new Intl.DateTimeFormat(locale, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(dateObj);
};

// 工具函数：格式化相对时间
export const formatRelativeTime = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);
  
  const rtf = new Intl.RelativeTimeFormat(i18n.language, { numeric: 'auto' });
  
  if (diffInSeconds < 60) {
    return rtf.format(-diffInSeconds, 'second');
  } else if (diffInSeconds < 3600) {
    return rtf.format(-Math.floor(diffInSeconds / 60), 'minute');
  } else if (diffInSeconds < 86400) {
    return rtf.format(-Math.floor(diffInSeconds / 3600), 'hour');
  } else if (diffInSeconds < 2592000) { // 30 days
    return rtf.format(-Math.floor(diffInSeconds / 86400), 'day');
  } else {
    return formatDate(dateObj, { month: 'short', day: 'numeric' });
  }
};

// 工具函数：格式化文件大小
export const formatFileSize = (bytes: number): string => {
  const locale = getCurrentLocale();
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  const formattedSize = new Intl.NumberFormat(locale, {
    minimumFractionDigits: unitIndex === 0 ? 0 : 1,
    maximumFractionDigits: unitIndex === 0 ? 0 : 1,
  }).format(size);
  
  return `${formattedSize} ${units[unitIndex]}`;
};

// 工具函数：格式化电话号码
export const formatPhoneNumber = (phone: string, country = 'NG'): string => {
  // 移除所有非数字字符
  const cleaned = phone.replace(/\D/g, '');
  
  if (country === 'NG') {
    // 尼日利亚电话号码格式：+234 XXX XXX XXXX
    if (cleaned.length === 11 && cleaned.startsWith('0')) {
      const number = cleaned.substring(1);
      return `+234 ${number.substring(0, 3)} ${number.substring(3, 6)} ${number.substring(6)}`;
    } else if (cleaned.length === 10) {
      return `+234 ${cleaned.substring(0, 3)} ${cleaned.substring(3, 6)} ${cleaned.substring(6)}`;
    }
  } else if (country === 'CM') {
    // 喀麦隆电话号码格式：+237 X XXX XX XX
    if (cleaned.length === 9) {
      return `+237 ${cleaned.substring(0, 1)} ${cleaned.substring(1, 4)} ${cleaned.substring(4, 6)} ${cleaned.substring(6)}`;
    }
  }
  
  return phone; // 返回原始格式如果无法格式化
};

// 工具函数：切换语言
export const changeLanguage = async (language: string): Promise<void> => {
  await i18n.changeLanguage(language);
};

// 工具函数：获取当前语言信息
export const getCurrentLanguage = () => {
  return availableLanguages.find(lang => lang.code === i18n.language) || availableLanguages[0];
};