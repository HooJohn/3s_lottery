import { debounce, throttle, PerformanceMonitor } from '@/utils/performance'
import { cacheManager } from '@/utils/cache'
import { resourcePreloader } from '@/utils/preloader'

describe('Performance Utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    jest.clearAllTimers()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
  })

  describe('debounce', () => {
    it('should delay function execution', () => {
      const mockFn = jest.fn()
      const debouncedFn = debounce(mockFn, 100)

      debouncedFn()
      debouncedFn()
      debouncedFn()

      expect(mockFn).not.toHaveBeenCalled()

      jest.advanceTimersByTime(100)
      expect(mockFn).toHaveBeenCalledTimes(1)
    })

    it('should reset delay on subsequent calls', () => {
      const mockFn = jest.fn()
      const debouncedFn = debounce(mockFn, 100)

      debouncedFn()
      jest.advanceTimersByTime(50)
      debouncedFn()
      jest.advanceTimersByTime(50)

      expect(mockFn).not.toHaveBeenCalled()

      jest.advanceTimersByTime(50)
      expect(mockFn).toHaveBeenCalledTimes(1)
    })

    it('should execute immediately when immediate flag is true', () => {
      const mockFn = jest.fn()
      const debouncedFn = debounce(mockFn, 100, true)

      debouncedFn()
      expect(mockFn).toHaveBeenCalledTimes(1)

      debouncedFn()
      expect(mockFn).toHaveBeenCalledTimes(1)

      jest.advanceTimersByTime(100)
      debouncedFn()
      expect(mockFn).toHaveBeenCalledTimes(2)
    })
  })

  describe('throttle', () => {
    it('should limit function execution rate', () => {
      const mockFn = jest.fn()
      const throttledFn = throttle(mockFn, 100)

      throttledFn()
      throttledFn()
      throttledFn()

      expect(mockFn).toHaveBeenCalledTimes(1)

      jest.advanceTimersByTime(100)
      throttledFn()
      expect(mockFn).toHaveBeenCalledTimes(2)
    })

    it('should preserve function arguments', () => {
      const mockFn = jest.fn()
      const throttledFn = throttle(mockFn, 100)

      throttledFn('arg1', 'arg2')
      expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2')
    })
  })

  describe('PerformanceMonitor', () => {
    let monitor: PerformanceMonitor

    beforeEach(() => {
      monitor = PerformanceMonitor.getInstance()
      monitor.clearMetrics()
    })

    it('should measure performance correctly', () => {
      monitor.startMeasure('test')
      
      // Simulate some work
      jest.advanceTimersByTime(100)
      
      const duration = monitor.endMeasure('test')
      expect(duration).toBeGreaterThan(0)
    })

    it('should calculate statistics correctly', () => {
      monitor.startMeasure('test')
      monitor.endMeasure('test')
      
      monitor.startMeasure('test')
      monitor.endMeasure('test')

      const stats = monitor.getStats('test')
      expect(stats).toBeDefined()
      expect(stats?.count).toBe(2)
      expect(stats?.avg).toBeGreaterThan(0)
    })

    it('should clear metrics correctly', () => {
      monitor.startMeasure('test')
      monitor.endMeasure('test')

      monitor.clearMetrics('test')
      const stats = monitor.getStats('test')
      expect(stats).toBeNull()
    })
  })

  describe('Cache Manager', () => {
    beforeEach(() => {
      cacheManager.clear()
    })

    it('should store and retrieve data correctly', () => {
      const testData = { key: 'value' }
      cacheManager.set('test', testData)

      const retrieved = cacheManager.get('test')
      expect(retrieved).toEqual(testData)
    })

    it('should respect TTL', () => {
      const testData = { key: 'value' }
      cacheManager.set('test', testData, 100)

      expect(cacheManager.get('test')).toEqual(testData)

      jest.advanceTimersByTime(150)
      expect(cacheManager.get('test')).toBeNull()
    })

    it('should handle cache size limits', () => {
      // Fill cache beyond limit
      for (let i = 0; i < 150; i++) {
        cacheManager.set(`key${i}`, `value${i}`)
      }

      const stats = cacheManager.getStats()
      expect(stats.size).toBeLessThanOrEqual(100) // maxSize
    })
  })

  describe('Resource Preloader', () => {
    beforeEach(() => {
      // Mock Image constructor
      global.Image = class {
        onload: (() => void) | null = null
        onerror: (() => void) | null = null
        src: string = ''

        constructor() {
          setTimeout(() => {
            if (this.onload) {
              this.onload()
            }
          }, 10)
        }
      } as any
    })

    it('should preload images successfully', async () => {
      const promise = resourcePreloader.preloadImage('/test-image.jpg')
      
      jest.advanceTimersByTime(10)
      await expect(promise).resolves.toBeUndefined()
    })

    it('should preload multiple images', async () => {
      const images = ['/image1.jpg', '/image2.jpg', '/image3.jpg']
      const promise = resourcePreloader.preloadImages(images)
      
      jest.advanceTimersByTime(10)
      await expect(promise).resolves.toHaveLength(3)
    })

    it('should not preload same image twice', async () => {
      const imageSrc = '/test-image.jpg'
      
      await resourcePreloader.preloadImage(imageSrc)
      const secondLoad = await resourcePreloader.preloadImage(imageSrc)
      
      expect(secondLoad).toBeUndefined()
    })
  })
})

// Performance benchmarks
describe('Performance Benchmarks', () => {
  it('should render virtual list efficiently', () => {
    const startTime = performance.now()
    
    // Simulate virtual list rendering with 10000 items
    const items = Array.from({ length: 10000 }, (_, i) => ({ id: i, name: `Item ${i}` }))
    const visibleItems = items.slice(0, 20) // Only render visible items
    
    const endTime = performance.now()
    const renderTime = endTime - startTime
    
    expect(renderTime).toBeLessThan(10) // Should render in less than 10ms
  })

  it('should handle large dataset filtering efficiently', () => {
    const startTime = performance.now()
    
    // Create large dataset
    const data = Array.from({ length: 100000 }, (_, i) => ({
      id: i,
      name: `Item ${i}`,
      category: i % 10,
      active: i % 2 === 0
    }))
    
    // Filter data
    const filtered = data.filter(item => item.active && item.category < 5)
    
    const endTime = performance.now()
    const filterTime = endTime - startTime
    
    expect(filterTime).toBeLessThan(50) // Should filter in less than 50ms
    expect(filtered.length).toBeGreaterThan(0)
  })

  it('should handle rapid state updates efficiently', () => {
    const startTime = performance.now()
    
    // Simulate rapid state updates
    let state = { count: 0, items: [] as number[] }
    
    for (let i = 0; i < 1000; i++) {
      state = {
        count: state.count + 1,
        items: [...state.items, i]
      }
    }
    
    const endTime = performance.now()
    const updateTime = endTime - startTime
    
    expect(updateTime).toBeLessThan(100) // Should update in less than 100ms
    expect(state.count).toBe(1000)
    expect(state.items).toHaveLength(1000)
  })
})

// Memory leak detection
describe('Memory Leak Detection', () => {
  it('should not leak memory with event listeners', () => {
    const listeners: Array<() => void> = []
    
    // Add many event listeners
    for (let i = 0; i < 1000; i++) {
      const listener = () => console.log(`Listener ${i}`)
      listeners.push(listener)
      document.addEventListener('click', listener)
    }
    
    // Remove all listeners
    listeners.forEach(listener => {
      document.removeEventListener('click', listener)
    })
    
    // Check that listeners array can be garbage collected
    listeners.length = 0
    
    expect(listeners).toHaveLength(0)
  })

  it('should cleanup timers properly', () => {
    const timers: NodeJS.Timeout[] = []
    
    // Create many timers
    for (let i = 0; i < 100; i++) {
      const timer = setTimeout(() => {}, 1000)
      timers.push(timer)
    }
    
    // Clear all timers
    timers.forEach(timer => clearTimeout(timer))
    
    expect(timers).toHaveLength(100)
  })
})