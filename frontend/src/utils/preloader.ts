// 资源预加载管理器
class ResourcePreloader {
  private preloadedResources = new Set<string>()
  private preloadQueue: Array<() => Promise<any>> = []
  private isPreloading = false

  // 预加载图片
  preloadImage(src: string): Promise<void> {
    if (this.preloadedResources.has(src)) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => {
        this.preloadedResources.add(src)
        resolve()
      }
      img.onerror = reject
      img.src = src
    })
  }

  // 预加载多个图片
  preloadImages(srcs: string[]): Promise<void[]> {
    return Promise.all(srcs.map(src => this.preloadImage(src)))
  }

  // 预加载字体
  preloadFont(fontFamily: string, src: string): Promise<void> {
    if (this.preloadedResources.has(src)) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      const font = new FontFace(fontFamily, `url(${src})`)
      font.load().then(() => {
        document.fonts.add(font)
        this.preloadedResources.add(src)
        resolve()
      }).catch(reject)
    })
  }

  // 预加载CSS
  preloadCSS(href: string): Promise<void> {
    if (this.preloadedResources.has(href)) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      const link = document.createElement('link')
      link.rel = 'preload'
      link.as = 'style'
      link.href = href
      link.onload = () => {
        this.preloadedResources.add(href)
        resolve()
      }
      link.onerror = reject
      document.head.appendChild(link)
    })
  }

  // 预加载JavaScript模块
  preloadModule(src: string): Promise<void> {
    if (this.preloadedResources.has(src)) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      const link = document.createElement('link')
      link.rel = 'modulepreload'
      link.href = src
      link.onload = () => {
        this.preloadedResources.add(src)
        resolve()
      }
      link.onerror = reject
      document.head.appendChild(link)
    })
  }

  // 添加预加载任务到队列
  addToQueue(preloadFunc: () => Promise<any>) {
    this.preloadQueue.push(preloadFunc)
    this.processQueue()
  }

  // 处理预加载队列
  private async processQueue() {
    if (this.isPreloading || this.preloadQueue.length === 0) {
      return
    }

    this.isPreloading = true

    while (this.preloadQueue.length > 0) {
      const preloadFunc = this.preloadQueue.shift()
      if (preloadFunc) {
        try {
          await preloadFunc()
        } catch (error) {
          console.warn('Preload failed:', error)
        }
      }
    }

    this.isPreloading = false
  }

  // 预加载关键资源
  preloadCriticalResources() {
    // 预加载关键图片
    const criticalImages = [
      '/images/logo.png',
      '/images/hero-bg.jpg',
      '/images/game-icons/lottery.png',
      '/images/game-icons/scratch.png',
      '/images/game-icons/sports.png'
    ]

    this.addToQueue(() => this.preloadImages(criticalImages))

    // 预加载关键字体
    this.addToQueue(() => this.preloadFont('Inter', '/fonts/inter-var.woff2'))
  }

  // 基于用户行为的智能预加载
  intelligentPreload(userBehavior: {
    visitedPages: string[]
    gamePreferences: string[]
    timeSpent: Record<string, number>
  }) {
    const { visitedPages, gamePreferences, timeSpent } = userBehavior

    // 根据访问历史预加载
    if (visitedPages.includes('/games')) {
      this.addToQueue(() => import('@/pages/games/GamesPage'))
    }

    // 根据游戏偏好预加载
    if (gamePreferences.includes('lottery11x5')) {
      this.addToQueue(() => import('@/pages/games/Lottery11x5Page'))
    }

    if (gamePreferences.includes('scratch')) {
      this.addToQueue(() => import('@/pages/games/ScratchCardPage'))
    }

    // 根据停留时间预加载相关页面
    const mostVisitedPage = Object.keys(timeSpent).reduce((a, b) => 
      timeSpent[a] > timeSpent[b] ? a : b
    )

    if (mostVisitedPage === '/wallet') {
      this.addToQueue(() => import('@/pages/wallet/DepositPage'))
      this.addToQueue(() => import('@/pages/wallet/WithdrawPage'))
    }
  }

  // 清理预加载资源
  cleanup() {
    this.preloadedResources.clear()
    this.preloadQueue.length = 0
  }
}

// 创建全局实例
export const resourcePreloader = new ResourcePreloader()

// 网络状态感知的预加载
export const networkAwarePreload = (preloadFunc: () => Promise<any>) => {
  // 检查网络连接
  if (!navigator.onLine) {
    return Promise.reject(new Error('No network connection'))
  }

  // 检查网络类型（如果支持）
  const connection = (navigator as any).connection
  if (connection) {
    // 在慢速网络下跳过预加载
    if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
      return Promise.resolve()
    }

    // 在数据节省模式下跳过预加载
    if (connection.saveData) {
      return Promise.resolve()
    }
  }

  return preloadFunc()
}

// 空闲时间预加载
export const idlePreload = (preloadFunc: () => Promise<any>) => {
  if ('requestIdleCallback' in window) {
    return new Promise<void>((resolve) => {
      requestIdleCallback(async () => {
        try {
          await preloadFunc()
        } catch (error) {
          console.warn('Idle preload failed:', error)
        }
        resolve()
      })
    })
  } else {
    // 降级到setTimeout
    return new Promise<void>((resolve) => {
      setTimeout(async () => {
        try {
          await preloadFunc()
        } catch (error) {
          console.warn('Idle preload failed:', error)
        }
        resolve()
      }, 100)
    })
  }
}