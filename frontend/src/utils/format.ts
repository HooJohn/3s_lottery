import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { enUS, fr, zhCN } from 'date-fns/locale';

// 语言映射
const localeMap = {
  en: enUS,
  fr: fr,
  zh: zhCN,
};

/**
 * 格式化货币金额
 * @param amount 金额
 * @param currency 货币符号
 * @param locale 语言环境
 */
export function formatCurrency(
  amount: number,
  currency: string = '₦',
  locale: string = 'en'
): string {
  const formatter = new Intl.NumberFormat(locale === 'zh' ? 'zh-CN' : locale, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  
  return `${currency}${formatter.format(amount)}`;
}

/**
 * 格式化数字
 * @param number 数字
 * @param locale 语言环境
 */
export function formatNumber(number: number, locale: string = 'en'): string {
  return new Intl.NumberFormat(locale === 'zh' ? 'zh-CN' : locale).format(number);
}

/**
 * 格式化百分比
 * @param value 数值 (0-1)
 * @param decimals 小数位数
 */
export function formatPercentage(value: number, decimals: number = 2): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * 格式化日期时间
 * @param date 日期字符串或Date对象
 * @param formatStr 格式字符串
 * @param locale 语言环境
 */
export function formatDateTime(
  date: string | Date,
  formatStr: string = 'yyyy-MM-dd HH:mm:ss',
  locale: string = 'en'
): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  const localeObj = localeMap[locale as keyof typeof localeMap] || enUS;
  
  return format(dateObj, formatStr, { locale: localeObj });
}

/**
 * 格式化相对时间
 * @param date 日期字符串或Date对象
 * @param locale 语言环境
 */
export function formatRelativeTime(
  date: string | Date,
  locale: string = 'en'
): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  const localeObj = localeMap[locale as keyof typeof localeMap] || enUS;
  
  return formatDistanceToNow(dateObj, { 
    addSuffix: true, 
    locale: localeObj 
  });
}

/**
 * 格式化手机号
 * @param phone 手机号
 */
export function formatPhone(phone: string): string {
  // 尼日利亚手机号格式: +234 801 234 5678
  if (phone.startsWith('+234')) {
    const number = phone.slice(4);
    return `+234 ${number.slice(0, 3)} ${number.slice(3, 6)} ${number.slice(6)}`;
  }
  
  // 喀麦隆手机号格式: +237 6XX XXX XXX
  if (phone.startsWith('+237')) {
    const number = phone.slice(4);
    return `+237 ${number.slice(0, 3)} ${number.slice(3, 6)} ${number.slice(6)}`;
  }
  
  return phone;
}

/**
 * 格式化银行账号
 * @param accountNumber 银行账号
 */
export function formatBankAccount(accountNumber: string): string {
  // 每4位添加空格
  return accountNumber.replace(/(\d{4})(?=\d)/g, '$1 ');
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 格式化倒计时
 * @param seconds 秒数
 */
export function formatCountdown(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

/**
 * 格式化VIP等级
 * @param level VIP等级数字
 */
export function formatVIPLevel(level: number): string {
  return `VIP${level}`;
}

/**
 * 格式化期次号码
 * @param drawNumber 期次号码
 */
export function formatDrawNumber(drawNumber: string): string {
  // 格式: 20250119-001 -> 2025年01月19日 第001期
  if (drawNumber.includes('-')) {
    const [date, period] = drawNumber.split('-');
    const year = date.slice(0, 4);
    const month = date.slice(4, 6);
    const day = date.slice(6, 8);
    
    return `${year}年${month}月${day}日 第${period}期`;
  }
  
  return drawNumber;
}

/**
 * 格式化彩票号码
 * @param numbers 号码数组
 * @param separator 分隔符
 */
export function formatLotteryNumbers(
  numbers: number[],
  separator: string = ' '
): string {
  return numbers
    .map(num => num.toString().padStart(2, '0'))
    .join(separator);
}

/**
 * 格式化大乐透号码
 * @param frontNumbers 前区号码
 * @param backNumbers 后区号码
 */
export function formatSuperLottoNumbers(
  frontNumbers: number[],
  backNumbers: number[]
): string {
  const front = formatLotteryNumbers(frontNumbers);
  const back = formatLotteryNumbers(backNumbers);
  
  return `${front} + ${back}`;
}

/**
 * 截断文本
 * @param text 文本
 * @param maxLength 最大长度
 * @param suffix 后缀
 */
export function truncateText(
  text: string,
  maxLength: number,
  suffix: string = '...'
): string {
  if (text.length <= maxLength) return text;
  
  return text.slice(0, maxLength - suffix.length) + suffix;
}

/**
 * 格式化交易状态
 * @param status 状态
 * @param locale 语言环境
 */
export function formatTransactionStatus(
  status: string,
  locale: string = 'en'
): { text: string; color: string } {
  const statusMap = {
    en: {
      PENDING: { text: 'Pending', color: 'warning' },
      PROCESSING: { text: 'Processing', color: 'info' },
      COMPLETED: { text: 'Completed', color: 'success' },
      FAILED: { text: 'Failed', color: 'danger' },
      CANCELLED: { text: 'Cancelled', color: 'gray' },
    },
    fr: {
      PENDING: { text: 'En attente', color: 'warning' },
      PROCESSING: { text: 'En cours', color: 'info' },
      COMPLETED: { text: 'Terminé', color: 'success' },
      FAILED: { text: 'Échoué', color: 'danger' },
      CANCELLED: { text: 'Annulé', color: 'gray' },
    },
    zh: {
      PENDING: { text: '待处理', color: 'warning' },
      PROCESSING: { text: '处理中', color: 'info' },
      COMPLETED: { text: '已完成', color: 'success' },
      FAILED: { text: '失败', color: 'danger' },
      CANCELLED: { text: '已取消', color: 'gray' },
    },
  };
  
  const localeMap = statusMap[locale as keyof typeof statusMap] || statusMap.en;
  return localeMap[status as keyof typeof localeMap] || { text: status, color: 'gray' };
}

/**
 * 格式化KYC状态
 * @param status KYC状态
 * @param locale 语言环境
 */
export function formatKYCStatus(
  status: string,
  locale: string = 'en'
): { text: string; color: string } {
  const statusMap = {
    en: {
      PENDING: { text: 'Pending Review', color: 'warning' },
      APPROVED: { text: 'Approved', color: 'success' },
      REJECTED: { text: 'Rejected', color: 'danger' },
      EXPIRED: { text: 'Expired', color: 'gray' },
    },
    fr: {
      PENDING: { text: 'En cours de révision', color: 'warning' },
      APPROVED: { text: 'Approuvé', color: 'success' },
      REJECTED: { text: 'Rejeté', color: 'danger' },
      EXPIRED: { text: 'Expiré', color: 'gray' },
    },
    zh: {
      PENDING: { text: '待审核', color: 'warning' },
      APPROVED: { text: '已通过', color: 'success' },
      REJECTED: { text: '已拒绝', color: 'danger' },
      EXPIRED: { text: '已过期', color: 'gray' },
    },
  };
  
  const localeMap = statusMap[locale as keyof typeof statusMap] || statusMap.en;
  return localeMap[status as keyof typeof localeMap] || { text: status, color: 'gray' };
}