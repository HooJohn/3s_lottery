import React, { useEffect, useState, memo } from 'react'
import { PerformanceMonitor, getMemoryUsage, monitorLongTasks, monitorFPS } from '@/utils/performance'

interface PerformanceStats {
  memory?: {
    usedJSHeapSize: number
    totalJSHeapSize: number
    jsHeapSizeLimit: number
    usedPercent: number
  }
  fps: number
  longTasks: number
  renderTime: number
}

interface PerformanceMonitorProps {
  enabled?: boolean
  showOverlay?: boolean
  onStatsUpdate?: (stats: PerformanceStats) => void
}

const PerformanceMonitorComponent = memo<PerformanceMonitorProps>(({
  enabled = __DEV__,
  showOverlay = __DEV__,
  onStatsUpdate
}) => {
  const [stats, setStats] = useState<PerformanceStats>({
    fps: 0,
    longTasks: 0,
    renderTime: 0
  })

  useEffect(() => {
    if (!enabled) return

    const monitor = PerformanceMonitor.getInstance()
    let longTaskCount = 0
    let currentFPS = 0

    // Monitor memory usage
    const updateMemoryStats = () => {
      const memory = getMemoryUsage()
      if (memory) {
        setStats(prev => ({ ...prev, memory }))
      }
    }

    // Monitor FPS
    const fpsCleanup = monitorFPS((fps) => {
      currentFPS = fps
      setStats(prev => ({ ...prev, fps }))
    })

    // Monitor long tasks
    const longTaskCleanup = monitorLongTasks((entries) => {
      longTaskCount += entries.length
      setStats(prev => ({ ...prev, longTasks: longTaskCount }))
    })

    // Update stats periodically
    const interval = setInterval(() => {
      updateMemoryStats()
      
      // Get render performance stats
      const renderStats = monitor.getStats('component-render')
      if (renderStats) {
        setStats(prev => ({ ...prev, renderTime: renderStats.avg }))
      }

      // Notify parent component
      onStatsUpdate?.(stats)
    }, 1000)

    return () => {
      clearInterval(interval)
      fpsCleanup?.()
      longTaskCleanup?.()
    }
  }, [enabled, onStatsUpdate])

  if (!enabled || !showOverlay) {
    return null
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getPerformanceColor = (value: number, thresholds: [number, number]) => {
    if (value < thresholds[0]) return 'text-green-500'
    if (value < thresholds[1]) return 'text-yellow-500'
    return 'text-red-500'
  }

  return (
    <div className="fixed top-4 left-4 z-50 bg-black bg-opacity-80 text-white p-3 rounded-lg text-xs font-mono">
      <div className="space-y-1">
        <div className="font-bold text-blue-400">Performance Monitor</div>
        
        <div className="flex items-center space-x-2">
          <span>FPS:</span>
          <span className={getPerformanceColor(60 - stats.fps, [10, 20])}>
            {stats.fps}
          </span>
        </div>

        {stats.memory && (
          <>
            <div className="flex items-center space-x-2">
              <span>Memory:</span>
              <span className={getPerformanceColor(stats.memory.usedPercent, [70, 85])}>
                {formatBytes(stats.memory.usedJSHeapSize)} / {formatBytes(stats.memory.jsHeapSizeLimit)}
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <span>Usage:</span>
              <span className={getPerformanceColor(stats.memory.usedPercent, [70, 85])}>
                {stats.memory.usedPercent.toFixed(1)}%
              </span>
            </div>
          </>
        )}

        <div className="flex items-center space-x-2">
          <span>Long Tasks:</span>
          <span className={getPerformanceColor(stats.longTasks, [5, 10])}>
            {stats.longTasks}
          </span>
        </div>

        {stats.renderTime > 0 && (
          <div className="flex items-center space-x-2">
            <span>Render:</span>
            <span className={getPerformanceColor(stats.renderTime, [16, 33])}>
              {stats.renderTime.toFixed(2)}ms
            </span>
          </div>
        )}
      </div>
    </div>
  )
})

PerformanceMonitorComponent.displayName = 'PerformanceMonitor'

export default PerformanceMonitorComponent

// Hook for using performance stats in components
export function usePerformanceStats() {
  const [stats, setStats] = useState<PerformanceStats>({
    fps: 0,
    longTasks: 0,
    renderTime: 0
  })

  useEffect(() => {
    const monitor = PerformanceMonitor.getInstance()
    let longTaskCount = 0

    const fpsCleanup = monitorFPS((fps) => {
      setStats(prev => ({ ...prev, fps }))
    })

    const longTaskCleanup = monitorLongTasks((entries) => {
      longTaskCount += entries.length
      setStats(prev => ({ ...prev, longTasks: longTaskCount }))
    })

    const interval = setInterval(() => {
      const memory = getMemoryUsage()
      const renderStats = monitor.getStats('component-render')
      
      setStats(prev => ({
        ...prev,
        memory: memory || prev.memory,
        renderTime: renderStats?.avg || prev.renderTime
      }))
    }, 1000)

    return () => {
      clearInterval(interval)
      fpsCleanup?.()
      longTaskCleanup?.()
    }
  }, [])

  return stats
}

// Performance warning component
interface PerformanceWarningProps {
  threshold?: {
    fps: number
    memory: number
    longTasks: number
  }
  onWarning?: (type: string, value: number) => void
}

export const PerformanceWarning = memo<PerformanceWarningProps>(({
  threshold = { fps: 30, memory: 80, longTasks: 10 },
  onWarning
}) => {
  const stats = usePerformanceStats()
  const [warnings, setWarnings] = useState<string[]>([])

  useEffect(() => {
    const newWarnings: string[] = []

    if (stats.fps > 0 && stats.fps < threshold.fps) {
      newWarnings.push(`Low FPS: ${stats.fps}`)
      onWarning?.('fps', stats.fps)
    }

    if (stats.memory && stats.memory.usedPercent > threshold.memory) {
      newWarnings.push(`High memory usage: ${stats.memory.usedPercent.toFixed(1)}%`)
      onWarning?.('memory', stats.memory.usedPercent)
    }

    if (stats.longTasks > threshold.longTasks) {
      newWarnings.push(`Too many long tasks: ${stats.longTasks}`)
      onWarning?.('longTasks', stats.longTasks)
    }

    setWarnings(newWarnings)
  }, [stats, threshold, onWarning])

  if (warnings.length === 0) {
    return null
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 bg-red-600 text-white p-3 rounded-lg text-sm max-w-xs">
      <div className="font-bold mb-2">Performance Warning</div>
      <ul className="space-y-1">
        {warnings.map((warning, index) => (
          <li key={index} className="flex items-center">
            <span className="w-2 h-2 bg-yellow-400 rounded-full mr-2"></span>
            {warning}
          </li>
        ))}
      </ul>
    </div>
  )
})

PerformanceWarning.displayName = 'PerformanceWarning'