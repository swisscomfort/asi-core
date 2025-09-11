// ASI-Core PWA Service Worker
// Offline-First Functionality

const CACHE_NAME = 'asi-core-v2.0.0';
const DYNAMIC_CACHE = 'asi-core-dynamic-v1';

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png',
  '/assets/index.css',
  '/assets/index.js'
];

// Install Event - Cache static assets
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[ServiceWorker] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate Event - Clean old caches
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activating...');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME && name !== DYNAMIC_CACHE)
          .map(name => {
            console.log('[ServiceWorker] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event - Network first, fallback to cache
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // API calls - Network only with offline queue
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          // Clone response for cache
          const responseToCache = response.clone();
          
          caches.open(DYNAMIC_CACHE).then(cache => {
            cache.put(request, responseToCache);
          });
          
          return response;
        })
        .catch(error => {
          // Try cache for API calls
          return caches.match(request).then(response => {
            if (response) {
              console.log('[ServiceWorker] Serving API from cache:', request.url);
              return response;
            }
            
            // Return offline response
            return new Response(
              JSON.stringify({
                offline: true,
                message: 'You are offline. Data will sync when connection is restored.'
              }),
              {
                headers: { 'Content-Type': 'application/json' },
                status: 503
              }
            );
          });
        })
    );
    return;
  }
  
  // Static assets - Cache first
  event.respondWith(
    caches.match(request)
      .then(response => {
        if (response) {
          // Update cache in background
          fetch(request).then(fetchResponse => {
            caches.open(CACHE_NAME).then(cache => {
              cache.put(request, fetchResponse);
            });
          });
          return response;
        }
        
        // Not in cache, fetch from network
        return fetch(request).then(fetchResponse => {
          // Cache successful responses
          if (fetchResponse.status === 200) {
            const responseToCache = fetchResponse.clone();
            caches.open(DYNAMIC_CACHE).then(cache => {
              cache.put(request, responseToCache);
            });
          }
          return fetchResponse;
        });
      })
      .catch(error => {
        console.error('[ServiceWorker] Fetch failed:', error);
        
        // Offline fallback page
        if (request.destination === 'document') {
          return caches.match('/offline.html');
        }
      })
  );
});

// Background Sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('[ServiceWorker] Background sync:', event.tag);
  
  if (event.tag === 'sync-reflections') {
    event.waitUntil(syncReflections());
  }
});

// Sync offline reflections when back online
async function syncReflections() {
  try {
    // Get pending reflections from IndexedDB
    const db = await openDB();
    const tx = db.transaction('pending_reflections', 'readonly');
    const store = tx.objectStore('pending_reflections');
    const reflections = await store.getAll();
    
    // Upload each pending reflection
    for (const reflection of reflections) {
      await fetch('/api/reflections', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reflection)
      });
      
      // Remove from pending after successful upload
      const deleteTx = db.transaction('pending_reflections', 'readwrite');
      await deleteTx.objectStore('pending_reflections').delete(reflection.id);
    }
    
    console.log('[ServiceWorker] Synced', reflections.length, 'reflections');
  } catch (error) {
    console.error('[ServiceWorker] Sync failed:', error);
  }
}

// Helper to open IndexedDB
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('ASICore', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('pending_reflections')) {
        db.createObjectStore('pending_reflections', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

// Push Notifications
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'Neue ASI-Core Benachrichtigung',
    icon: '/icon-192.png',
    badge: '/icon-192.png',
    vibrate: [200, 100, 200],
    data: {
      timestamp: new Date().toISOString(),
      url: '/'
    }
  };
  
  event.waitUntil(
    self.registration.showNotification('ASI-Core', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow(event.notification.data.url || '/')
  );
});

console.log('[ServiceWorker] Loaded successfully');
