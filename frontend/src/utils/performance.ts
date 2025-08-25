import { useCallback, useRef, useEffect, useMemo } from 'react'

// 防抖函数
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate?: boolean
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      if (!immediate) func(...args)
    }

    const callNow = immediate && !timeout

    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(later, wait)

    if (callNow) func(...args)
  }
}

// 节流函数
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

// React Hook: 防抖
export function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number,
  deps: React.DependencyList = []
): (...args: Parameters<T>) => void {
  const callbackRef = useRef(callback)
  const timeoutRef = useRef<NodeJS.Timeout>()

  // 更新回调引用
  useEffect(() => {
    callbackRef.current = callback
  }, [callback])

  // 清理定时器
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return useCallback((...args: Parameters<T>) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    timeoutRef.current = setTimeout(() => {
      callbackRef.current(...args)
    }, delay)
  }, deps)
}

// React Hook: 节流
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number,
  deps: React.DependencyList = []
): (...args: Parameters<T>) => void {
  const callbackRef = useRef(callback)
  const lastRun = useRef(Date.now())

  useEffect(() => {
    callbackRef.current = callback
  }, [callback])

  return useCallback((...args: Parameters<T>) => {
    if (Date.now() - lastRun.current >= delay) {
      callbackRef.current(...args)
      lastRun.current = Date.now()
    }
  }, deps)
}

// 内存管理Hook
export function useCleanup(cleanup: () => void, deps: React.DependencyList = []) {
  useEffect(() => {
    return cleanup
  }, deps)
}

// 事件监听器清理Hook
export function useEventListener<K extends keyof WindowEventMap>(
  eventName: K,
  handler: (event: WindowEventMap[K]) => void,
  element: Window | Document | HTMLElement = window,
  options?: boolean | AddEventListenerOptions
) {
  const savedHandler = useRef<(event: WindowEventMap[K]) => void>()

  useEffect(() => {
    savedHandler.current = handler
  }, [handler])

  useEffect(() => {
    const isSupported = element && element.addEventListener
    if (!isSupported) return

    const eventListener = (event: Event) => savedHandler.current?.(event as WindowEventMap[K])
    element.addEventListener(eventName, eventListener, options)

    return () => {
      element.removeEventListener(eventName, eventListener, options)
    }
  }, [eventName, element, options])
}

// 定时器清理Hook
export function useInterval(callback: () => void, delay: number | null) {
  const savedCallback = useRef<() => void>()

  useEffect(() => {
    savedCallback.current = callback
  }, [callback])

  useEffect(() => {
    function tick() {
      savedCallback.current?.()
    }

    if (delay !== null) {
      const id = setInterval(tick, delay)
      return () => clearInterval(id)
    }
  }, [delay])
}

// 超时清理Hook
export function useTimeout(callback: () => void, delay: number | null) {
  const savedCallback = useRef<() => void>()

  useEffect(() => {
    savedCallback.current = callback
  }, [callback])

  useEffect(() => {
    if (delay !== null) {
      const id = setTimeout(() => savedCallback.current?.(), delay)
      return () => clearTimeout(id)
    }
  }, [delay])
}

// 性能监控
export class PerformanceMonitor {
  private static instance: PerformanceMonitor
  private metrics: Map<string, number[]> = new Map()

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor()
    }
    return PerformanceMonitor.instance
  }

  // 开始性能测量
  startMeasure(name: string): void {
    performance.mark(`${name}-start`)
  }

  // 结束性能测量
  endMeasure(name: string): number {
    performance.mark(`${name}-end`)
    performance.measure(name, `${name}-start`, `${name}-end`)
    
    const measure = performance.getEntriesByName(name, 'measure')[0]
    const duration = measure.duration

    // 记录到指标中
    if (!this.metrics.has(name)) {
      this.metrics.set(name, [])
    }
    this.metrics.get(name)!.push(duration)

    // 清理性能条目
    performance.clearMarks(`${name}-start`)
    performance.clearMarks(`${name}-end`)
    performance.clearMeasures(name)

    return duration
  }

  // 获取性能统计
  getStats(name: string) {
    const durations = this.metrics.get(name) || []
    if (durations.length === 0) {
      return null
    }

    const sorted = [...durations].sort((a, b) => a - b)
    return {
      count: durations.length,
      min: Math.min(...durations),
      max: Math.max(...durations),
      avg: durations.reduce((a, b) => a + b, 0) / durations.length,
      median: sorted[Math.floor(sorted.length / 2)],
      p95: sorted[Math.floor(sorted.length * 0.95)],
      p99: sorted[Math.floor(sorted.length * 0.99)]
    }
  }

  // 清理指标
  clearMetrics(name?: string): void {
    if (name) {
      this.metrics.delete(name)
    } else {
      this.metrics.clear()
    }
  }

  // 获取所有指标
  getAllStats() {
    const result: Record<string, any> = {}
    for (const [name] of this.metrics) {
      result[name] = this.getStats(name)
    }
    return result
  }
}

// 性能监控装饰器
export function performanceMonitor(name?: string) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value
    const measureName = name || `${target.constructor.name}_${propertyName}`

    descriptor.value = function (...args: any[]) {
      const monitor = PerformanceMonitor.getInstance()
      monitor.startMeasure(measureName)

      try {
        const result = method.apply(this, args)

        if (result instanceof Promise) {
          return result.finally(() => {
            monitor.endMeasure(measureName)
          })
        }

        monitor.endMeasure(measureName)
        return result
      } catch (error) {
        monitor.endMeasure(measureName)
        throw error
      }
    }
  }
}

// React组件性能监控Hook
export function usePerformanceMonitor(name: string) {
  const monitor = PerformanceMonitor.getInstance()

  useEffect(() => {
    monitor.startMeasure(`${name}-render`)
    return () => {
      monitor.endMeasure(`${name}-render`)
    }
  })

  return {
    startMeasure: (measureName: string) => monitor.startMeasure(measureName),
    endMeasure: (measureName: string) => monitor.endMeasure(measureName),
    getStats: (measureName: string) => monitor.getStats(measureName)
  }
}

// 内存使用监控
export function getMemoryUsage() {
  if ('memory' in performance) {
    const memory = (performance as any).memory
    return {
      usedJSHeapSize: memory.usedJSHeapSize,
      totalJSHeapSize: memory.totalJSHeapSize,
      jsHeapSizeLimit: memory.jsHeapSizeLimit,
      usedPercent: (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100
    }
  }
  return null
}

// 长任务监控
export function monitorLongTasks(callback: (entries: PerformanceEntry[]) => void) {
  if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
      callback(list.getEntries())
    })

    try {
      observer.observe({ entryTypes: ['longtask'] })
      return () => observer.disconnect()
    } catch (error) {
      console.warn('Long task monitoring not supported:', error)
    }
  }

  return () => {}
}

// FPS监控
export function monitorFPS(callback: (fps: number) => void) {
  let lastTime = performance.now()
  let frameCount = 0

  function measureFPS() {
    frameCount++
    const currentTime = performance.now()

    if (currentTime >= lastTime + 1000) {
      const fps = Math.round((frameCount * 1000) / (currentTime - lastTime))
      callback(fps)
      frameCount = 0
      lastTime = currentTime
    }

    requestAnimationFrame(measureFPS)
  }

  requestAnimationFrame(measureFPS)
}

// 资源加载监控
export function monitorResourceLoading() {
  const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      if (entry.entryType === 'resource') {
        const resource = entry as PerformanceResourceTiming
        console.log(`Resource: ${resource.name}`)
        console.log(`Duration: ${resource.duration}ms`)
        console.log(`Size: ${resource.transferSize} bytes`)
      }
    }
  })

  observer.observe({ entryTypes: ['resource'] })
  return () => observer.disconnect()
}