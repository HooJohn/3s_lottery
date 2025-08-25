// Service Worker for caching and performance optimization
const CACHE_NAME = 'africa-lottery-v1'
const STATIC_CACHE = 'static-v1'
const DYNAMIC_CACHE = 'dynamic-v1'
const IMAGE_CACHE = 'images-v1'

// Files to cache immediately
const STATIC_FILES = [
  '/',
  '/index.html',
  '/manifest.json',
  '/offline.html'
]

// API endpoints to cache
const API_CACHE_PATTERNS = [
  /\/api\/games\//,
  /\/api\/user\/profile/,
  /\/api\/finance\/balance/
]

// Image cache patterns
const IMAGE_PATTERNS = [
  /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
  /\/images\//,
  /\/icons\//
]

// Install event - cache static files
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...')
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Caching static files')
        return cache.addAll(STATIC_FILES)
      })
      .then(() => {
        return self.skipWaiting()
      })
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...')
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && 
                cacheName !== DYNAMIC_CACHE && 
                cacheName !== IMAGE_CACHE) {
              console.log('Deleting old cache:', cacheName)
              return caches.delete(cacheName)
            }
          })
        )
      })
      .then(() => {
        return self.clients.claim()
      })
  )
})

// Fetch event - handle requests with caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return
  }

  // Skip chrome-extension and other non-http requests
  if (!request.url.startsWith('http')) {
    return
  }

  // Handle different types of requests
  if (isStaticFile(request)) {
    event.respondWith(handleStaticFile(request))
  } else if (isImageRequest(request)) {
    event.respondWith(handleImageRequest(request))
  } else if (isAPIRequest(request)) {
    event.respondWith(handleAPIRequest(request))
  } else {
    event.respondWith(handleDynamicRequest(request))
  }
})

// Check if request is for static file
function isStaticFile(request) {
  const url = new URL(request.url)
  return STATIC_FILES.some(file => url.pathname === file) ||
         url.pathname.match(/\.(js|css|woff2?|ttf|eot)$/)
}

// Check if request is for image
function isImageRequest(request) {
  return IMAGE_PATTERNS.some(pattern => pattern.test(request.url))
}

// Check if request is for API
function isAPIRequest(request) {
  return API_CACHE_PATTERNS.some(pattern => pattern.test(request.url))
}

// Handle static files - Cache First strategy
async function handleStaticFile(request) {
  try {
    const cache = await caches.open(STATIC_CACHE)
    const cachedResponse = await cache.match(request)
    
    if (cachedResponse) {
      return cachedResponse
    }

    const networkResponse = await fetch(request)
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone())
    }
    
    return networkResponse
  } catch (error) {
    console.error('Static file fetch failed:', error)
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return caches.match('/offline.html')
    }
    
    throw error
  }
}

// Handle images - Cache First with expiration
async function handleImageRequest(request) {
  try {
    const cache = await caches.open(IMAGE_CACHE)
    const cachedResponse = await cache.match(request)
    
    if (cachedResponse) {
      // Check if cached image is still fresh (24 hours)
      const cachedDate = cachedResponse.headers.get('sw-cached-date')
      if (cachedDate) {
        const cacheAge = Date.now() - parseInt(cachedDate)
        const maxAge = 24 * 60 * 60 * 1000 // 24 hours
        
        if (cacheAge < maxAge) {
          return cachedResponse
        }
      }
    }

    const networkResponse = await fetch(request)
    
    if (networkResponse.ok) {
      const responseToCache = networkResponse.clone()
      
      // Add timestamp to cached response
      const headers = new Headers(responseToCache.headers)
      headers.set('sw-cached-date', Date.now().toString())
      
      const cachedResponse = new Response(responseToCache.body, {
        status: responseToCache.status,
        statusText: responseToCache.statusText,
        headers: headers
      })
      
      cache.put(request, cachedResponse)
    }
    
    return networkResponse
  } catch (error) {
    console.error('Image fetch failed:', error)
    
    // Return cached version if available
    const cache = await caches.open(IMAGE_CACHE)
    const cachedResponse = await cache.match(request)
    
    if (cachedResponse) {
      return cachedResponse
    }
    
    throw error
  }
}

// Handle API requests - Network First with cache fallback
async function handleAPIRequest(request) {
  try {
    const networkResponse = await fetch(request)
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE)
      
      // Only cache GET requests
      if (request.method === 'GET') {
        cache.put(request, networkResponse.clone())
      }
    }
    
    return networkResponse
  } catch (error) {
    console.error('API fetch failed:', error)
    
    // Try to return cached version
    const cache = await caches.open(DYNAMIC_CACHE)
    const cachedResponse = await cache.match(request)
    
    if (cachedResponse) {
      return cachedResponse
    }
    
    throw error
  }
}

// Handle other dynamic requests - Network First
async function handleDynamicRequest(request) {
  try {
    const networkResponse = await fetch(request)
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE)
      cache.put(request, networkResponse.clone())
    }
    
    return networkResponse
  } catch (error) {
    console.error('Dynamic request failed:', error)
    
    // Try cached version
    const cache = await caches.open(DYNAMIC_CACHE)
    const cachedResponse = await cache.match(request)
    
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return caches.match('/offline.html')
    }
    
    throw error
  }
}

// Background sync for failed requests
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync())
  }
})

async function doBackgroundSync() {
  // Handle queued requests when back online
  console.log('Background sync triggered')
  
  // You can implement request queuing logic here
  // For example, retry failed API requests
}

// Push notifications
self.addEventListener('push', (event) => {
  if (!event.data) return

  const data = event.data.json()
  const options = {
    body: data.body,
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: data.data,
    actions: data.actions || []
  }

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  )
})

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  event.notification.close()

  if (event.action === 'open') {
    event.waitUntil(
      clients.openWindow(event.notification.data.url || '/')
    )
  }
})

// Message handling from main thread
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }
  
  if (event.data && event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      cacheUrls(event.data.urls)
    )
  }
})

async function cacheUrls(urls) {
  const cache = await caches.open(DYNAMIC_CACHE)
  return Promise.all(
    urls.map(url => {
      return fetch(url).then(response => {
        if (response.ok) {
          return cache.put(url, response)
        }
      }).catch(error => {
        console.warn('Failed to cache URL:', url, error)
      })
    })
  )
}

// Periodic cache cleanup
setInterval(() => {
  cleanupCaches()
}, 60 * 60 * 1000) // Every hour

async function cleanupCaches() {
  const cacheNames = await caches.keys()
  
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName)
    const requests = await cache.keys()
    
    for (const request of requests) {
      const response = await cache.match(request)
      const cachedDate = response.headers.get('sw-cached-date')
      
      if (cachedDate) {
        const cacheAge = Date.now() - parseInt(cachedDate)
        const maxAge = 7 * 24 * 60 * 60 * 1000 // 7 days
        
        if (cacheAge > maxAge) {
          await cache.delete(request)
        }
      }
    }
  }
}