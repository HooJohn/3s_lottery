import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * 合并Tailwind CSS类名的工具函数
 * 使用clsx处理条件类名，使用twMerge处理Tailwind冲突
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}