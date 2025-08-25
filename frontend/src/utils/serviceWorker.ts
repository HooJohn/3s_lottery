// Service Worker registration and management
const isLocalhost = Boolean(
  window.location.hostname === 'localhost' ||
  window.location.hostname === '[::1]' ||
  window.location.hostname.match(
    /^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/
  )
)

interface ServiceWorkerConfig {
  onSuccess?: (registration: ServiceWorkerRegistration) => void
  onUpdate?: (registration: ServiceWorkerRegistration) => void
  onOffline?: () => void
  onOnline?: () => void
}

export function register(config?: ServiceWorkerConfig) {
  if ('serviceWorker' in navigator) {
    // The URL constructor is available in all browsers that support SW.
    const publicUrl = new URL(process.env.PUBLIC_URL || '', window.location.href)
    if (publicUrl.origin !== window.location.origin) {
      // Our service worker won't work if PUBLIC_URL is on a different origin
      return
    }

    window.addEventListener('load', () => {
      const swUrl = `${process.env.PUBLIC_URL}/sw.js`

      if (isLocalhost) {
        // This is running on localhost. Let's check if a service worker still exists or not.
        checkValidServiceWorker(swUrl, config)

        // Add some additional logging to localhost, pointing developers to the
        // service worker/PWA documentation.
        navigator.serviceWorker.ready.then(() => {
          console.log(
            'This web app is being served cache-first by a service ' +
            'worker. To learn more, visit https://cra.link/PWA'
          )
        })
      } else {
        // Is not localhost. Just register service worker
        registerValidSW(swUrl, config)
      }
    })

    // Listen for network status changes
    window.addEventListener('online', () => {
      console.log('App is online')
      config?.onOnline?.()
    })

    window.addEventListener('offline', () => {
      console.log('App is offline')
      config?.onOffline?.()
    })
  }
}

function registerValidSW(swUrl: string, config?: ServiceWorkerConfig) {
  navigator.serviceWorker
    .register(swUrl)
    .then((registration) => {
      registration.onupdatefound = () => {
        const installingWorker = registration.installing
        if (installingWorker == null) {
          return
        }
        installingWorker.onstatechange = () => {
          if (installingWorker.state === 'installed') {
            if (navigator.serviceWorker.controller) {
              // At this point, the updated precached content has been fetched,
              // but the previous service worker will still serve the older
              // content until all client tabs are closed.
              console.log(
                'New content is available and will be used when all ' +
                'tabs for this page are closed. See https://cra.link/PWA.'
              )

              // Execute callback
              if (config && config.onUpdate) {
                config.onUpdate(registration)
              }
            } else {
              // At this point, everything has been precached.
              // It's the perfect time to display a
              // "Content is cached for offline use." message.
              console.log('Content is cached for offline use.')

              // Execute callback
              if (config && config.onSuccess) {
                config.onSuccess(registration)
              }
            }
          }
        }
      }
    })
    .catch((error) => {
      console.error('Error during service worker registration:', error)
    })
}

function checkValidServiceWorker(swUrl: string, config?: ServiceWorkerConfig) {
  // Check if the service worker can be found. If it can't reload the page.
  fetch(swUrl, {
    headers: { 'Service-Worker': 'script' },
  })
    .then((response) => {
      // Ensure service worker exists, and that we really are getting a JS file.
      const contentType = response.headers.get('content-type')
      if (
        response.status === 404 ||
        (contentType != null && contentType.indexOf('javascript') === -1)
      ) {
        // No service worker found. Probably a different app. Reload the page.
        navigator.serviceWorker.ready.then((registration) => {
          registration.unregister().then(() => {
            window.location.reload()
          })
        })
      } else {
        // Service worker found. Proceed as normal.
        registerValidSW(swUrl, config)
      }
    })
    .catch(() => {
      console.log(
        'No internet connection found. App is running in offline mode.'
      )
    })
}

export function unregister() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready
      .then((registration) => {
        registration.unregister()
      })
      .catch((error) => {
        console.error(error.message)
      })
  }
}

// Service Worker utilities
export class ServiceWorkerManager {
  private registration: ServiceWorkerRegistration | null = null

  constructor() {
    this.init()
  }

  private async init() {
    if ('serviceWorker' in navigator) {
      try {
        this.registration = await navigator.serviceWorker.ready
        this.setupMessageListener()
      } catch (error) {
        console.error('Service Worker initialization failed:', error)
      }
    }
  }

  private setupMessageListener() {
    if (!this.registration) return

    navigator.serviceWorker.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'CACHE_UPDATED') {
        console.log('Cache updated:', event.data.url)
      }
    })
  }

  // Send message to service worker
  async sendMessage(message: any): Promise<void> {
    if (!this.registration || !this.registration.active) {
      console.warn('Service Worker not available')
      return
    }

    this.registration.active.postMessage(message)
  }

  // Skip waiting for new service worker
  async skipWaiting(): Promise<void> {
    await this.sendMessage({ type: 'SKIP_WAITING' })
  }

  // Cache specific URLs
  async cacheUrls(urls: string[]): Promise<void> {
    await this.sendMessage({ type: 'CACHE_URLS', urls })
  }

  // Check if app is running in standalone mode (PWA)
  isStandalone(): boolean {
    return window.matchMedia('(display-mode: standalone)').matches ||
           (window.navigator as any).standalone === true
  }

  // Get cache size
  async getCacheSize(): Promise<number> {
    if (!('storage' in navigator)) {
      return 0
    }

    try {
      const estimate = await navigator.storage.estimate()
      return estimate.usage || 0
    } catch (error) {
      console.error('Failed to get cache size:', error)
      return 0
    }
  }

  // Clear all caches
  async clearCaches(): Promise<void> {
    if (!('caches' in window)) {
      return
    }

    try {
      const cacheNames = await caches.keys()
      await Promise.all(
        cacheNames.map(cacheName => caches.delete(cacheName))
      )
      console.log('All caches cleared')
    } catch (error) {
      console.error('Failed to clear caches:', error)
    }
  }

  // Update service worker
  async updateServiceWorker(): Promise<void> {
    if (!this.registration) {
      return
    }

    try {
      await this.registration.update()
      console.log('Service Worker update check completed')
    } catch (error) {
      console.error('Service Worker update failed:', error)
    }
  }
}

// Create global instance
export const serviceWorkerManager = new ServiceWorkerManager()

// Network status utilities
export class NetworkManager {
  private listeners: Array<(online: boolean) => void> = []

  constructor() {
    this.setupEventListeners()
  }

  private setupEventListeners() {
    window.addEventListener('online', () => {
      this.notifyListeners(true)
    })

    window.addEventListener('offline', () => {
      this.notifyListeners(false)
    })
  }

  private notifyListeners(online: boolean) {
    this.listeners.forEach(listener => listener(online))
  }

  // Add network status listener
  addListener(listener: (online: boolean) => void): () => void {
    this.listeners.push(listener)
    
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(listener)
      if (index > -1) {
        this.listeners.splice(index, 1)
      }
    }
  }

  // Check if online
  isOnline(): boolean {
    return navigator.onLine
  }

  // Get connection info (if supported)
  getConnectionInfo(): any {
    const connection = (navigator as any).connection || 
                      (navigator as any).mozConnection || 
                      (navigator as any).webkitConnection

    if (connection) {
      return {
        effectiveType: connection.effectiveType,
        downlink: connection.downlink,
        rtt: connection.rtt,
        saveData: connection.saveData
      }
    }

    return null
  }

  // Check if connection is slow
  isSlowConnection(): boolean {
    const connection = this.getConnectionInfo()
    if (!connection) return false

    return connection.effectiveType === 'slow-2g' || 
           connection.effectiveType === '2g' ||
           connection.saveData === true
  }
}

export const networkManager = new NetworkManager()