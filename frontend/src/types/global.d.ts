// 全局类型定义
declare const __DEV__: boolean
declare const __PROD__: boolean
declare const __VERSION__: string

// 扩展Window接口
interface Window {
  // Service Worker相关
  workbox?: any
  
  // 性能监控相关
  performance: Performance & {
    memory?: {
      usedJSHeapSize: number
      totalJSHeapSize: number
      jsHeapSizeLimit: number
    }
  }
  
  // 网络信息API
  navigator: Navigator & {
    connection?: {
      effectiveType: string
      downlink: number
      rtt: number
      saveData: boolean
    }
  }
}

// 模块声明
declare module '*.svg' {
  const content: string
  export default content
}

declare module '*.png' {
  const content: string
  export default content
}

declare module '*.jpg' {
  const content: string
  export default content
}

declare module '*.jpeg' {
  const content: string
  export default content
}

declare module '*.gif' {
  const content: string
  export default content
}

declare module '*.webp' {
  const content: string
  export default content
}

declare module '*.ico' {
  const content: string
  export default content
}

declare module '*.bmp' {
  const content: string
  export default content
}

declare module '*.css' {
  const classes: { [key: string]: string }
  export default classes
}

declare module '*.scss' {
  const classes: { [key: string]: string }
  export default classes
}

declare module '*.sass' {
  const classes: { [key: string]: string }
  export default classes
}

declare module '*.less' {
  const classes: { [key: string]: string }
  export default classes
}

// Vite环境变量
interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_WS_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_VERSION: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}