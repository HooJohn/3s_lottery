// 缓存管理器
interface CacheItem<T> {
  data: T
  timestamp: number
  ttl: number
}

class CacheManager {
  private cache = new Map<string, CacheItem<any>>()
  private maxSize = 100 // 最大缓存项数
  private defaultTTL = 5 * 60 * 1000 // 默认5分钟过期

  // 设置缓存
  set<T>(key: string, data: T, ttl: number = this.defaultTTL): void {
    // 如果缓存已满，删除最旧的项
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value
      this.cache.delete(oldestKey)
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    })
  }

  // 获取缓存
  get<T>(key: string): T | null {
    const item = this.cache.get(key)
    
    if (!item) {
      return null
    }

    // 检查是否过期
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key)
      return null
    }

    return item.data
  }

  // 删除缓存
  delete(key: string): boolean {
    return this.cache.delete(key)
  }

  // 清空缓存
  clear(): void {
    this.cache.clear()
  }

  // 清理过期缓存
  cleanup(): void {
    const now = Date.now()
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > item.ttl) {
        this.cache.delete(key)
      }
    }
  }

  // 获取缓存统计
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      keys: Array.from(this.cache.keys())
    }
  }
}

// 创建全局缓存实例
export const cacheManager = new CacheManager()

// 定期清理过期缓存
setInterval(() => {
  cacheManager.cleanup()
}, 60000) // 每分钟清理一次

// LocalStorage缓存管理
class LocalStorageCache {
  private prefix = 'africa_lottery_'

  set<T>(key: string, data: T, ttl: number = 24 * 60 * 60 * 1000): void {
    try {
      const item = {
        data,
        timestamp: Date.now(),
        ttl
      }
      localStorage.setItem(this.prefix + key, JSON.stringify(item))
    } catch (error) {
      console.warn('LocalStorage cache set failed:', error)
    }
  }

  get<T>(key: string): T | null {
    try {
      const itemStr = localStorage.getItem(this.prefix + key)
      if (!itemStr) {
        return null
      }

      const item = JSON.parse(itemStr)
      
      // 检查是否过期
      if (Date.now() - item.timestamp > item.ttl) {
        this.delete(key)
        return null
      }

      return item.data
    } catch (error) {
      console.warn('LocalStorage cache get failed:', error)
      return null
    }
  }

  delete(key: string): void {
    try {
      localStorage.removeItem(this.prefix + key)
    } catch (error) {
      console.warn('LocalStorage cache delete failed:', error)
    }
  }

  clear(): void {
    try {
      const keys = Object.keys(localStorage)
      keys.forEach(key => {
        if (key.startsWith(this.prefix)) {
          localStorage.removeItem(key)
        }
      })
    } catch (error) {
      console.warn('LocalStorage cache clear failed:', error)
    }
  }

  cleanup(): void {
    try {
      const keys = Object.keys(localStorage)
      const now = Date.now()
      
      keys.forEach(key => {
        if (key.startsWith(this.prefix)) {
          const itemStr = localStorage.getItem(key)
          if (itemStr) {
            try {
              const item = JSON.parse(itemStr)
              if (now - item.timestamp > item.ttl) {
                localStorage.removeItem(key)
              }
            } catch {
              // 如果解析失败，删除该项
              localStorage.removeItem(key)
            }
          }
        }
      })
    } catch (error) {
      console.warn('LocalStorage cache cleanup failed:', error)
    }
  }
}

export const localStorageCache = new LocalStorageCache()

// SessionStorage缓存管理
class SessionStorageCache {
  private prefix = 'africa_lottery_session_'

  set<T>(key: string, data: T): void {
    try {
      const item = {
        data,
        timestamp: Date.now()
      }
      sessionStorage.setItem(this.prefix + key, JSON.stringify(item))
    } catch (error) {
      console.warn('SessionStorage cache set failed:', error)
    }
  }

  get<T>(key: string): T | null {
    try {
      const itemStr = sessionStorage.getItem(this.prefix + key)
      if (!itemStr) {
        return null
      }

      const item = JSON.parse(itemStr)
      return item.data
    } catch (error) {
      console.warn('SessionStorage cache get failed:', error)
      return null
    }
  }

  delete(key: string): void {
    try {
      sessionStorage.removeItem(this.prefix + key)
    } catch (error) {
      console.warn('SessionStorage cache delete failed:', error)
    }
  }

  clear(): void {
    try {
      const keys = Object.keys(sessionStorage)
      keys.forEach(key => {
        if (key.startsWith(this.prefix)) {
          sessionStorage.removeItem(key)
        }
      })
    } catch (error) {
      console.warn('SessionStorage cache clear failed:', error)
    }
  }
}

export const sessionStorageCache = new SessionStorageCache()

// 缓存装饰器
export function cached<T extends (...args: any[]) => any>(
  ttl: number = 5 * 60 * 1000,
  keyGenerator?: (...args: Parameters<T>) => string
) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value

    descriptor.value = function (...args: Parameters<T>) {
      const key = keyGenerator 
        ? keyGenerator(...args)
        : `${target.constructor.name}_${propertyName}_${JSON.stringify(args)}`

      // 尝试从缓存获取
      const cached = cacheManager.get<ReturnType<T>>(key)
      if (cached !== null) {
        return cached
      }

      // 执行原方法
      const result = method.apply(this, args)

      // 如果是Promise，缓存resolved值
      if (result instanceof Promise) {
        return result.then((resolvedValue: ReturnType<T>) => {
          cacheManager.set(key, resolvedValue, ttl)
          return resolvedValue
        })
      }

      // 缓存同步结果
      cacheManager.set(key, result, ttl)
      return result
    }
  }
}

// 清理所有缓存
export const clearAllCaches = () => {
  cacheManager.clear()
  localStorageCache.clear()
  sessionStorageCache.clear()
}

// 定期清理LocalStorage缓存
setInterval(() => {
  localStorageCache.cleanup()
}, 5 * 60 * 1000) // 每5分钟清理一次