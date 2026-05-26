/**
 * PhantomByte - Service Worker for Push Notifications
 * Handles push events and notifications display
 */

// Service Worker version
const SW_VERSION = '1.0.0';

// Install event
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Install v' + SW_VERSION);
  self.skipWaiting();
});

// Activate event
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activate');
  event.waitUntil(self.clients.claim());
});

// Push event handler
self.addEventListener('push', (event) => {
  console.log('[ServiceWorker] Push received');
  
  let data = {};
  
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = {
        title: 'PhantomByte',
        body: event.data.text(),
        icon: '/images/logo-icon.png',
        badge: '/images/badge-icon.png'
      };
    }
  }
  
  const title = data.title || 'PhantomByte';
  const options = {
    body: data.body || 'New update from PhantomByte',
    icon: data.icon || '/images/logo-icon.png',
    badge: data.badge || '/images/badge-icon.png',
    vibrate: [200, 100, 200],
    tag: data.tag || 'phantombyte-notification',
    requireInteraction: data.requireInteraction || false,
    actions: data.actions || [
      {
        action: 'open',
        title: 'Read Article',
        icon: '/images/open-icon.png'
      },
      {
        action: 'close',
        title: 'Dismiss'
      }
    ],
    data: {
      url: data.url || '/',
      timestamp: Date.now()
    }
  };
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('[ServiceWorker] Notification click received');
  
  event.notification.close();
  
  if (event.action === 'close') {
    return;
  }
  
  // Default action (click on notification body or 'open' action)
  const urlToOpen = event.notification.data?.url || '/';
  
  event.waitUntil(
    self.clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    }).then((clientList) => {
      // Check if there's already a window open
      for (const client of clientList) {
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }
      // Open new window
      if (self.clients.openWindow) {
        return self.clients.openWindow(urlToOpen);
      }
    })
  );
});

// Background sync for offline support (optional)
self.addEventListener('sync', (event) => {
  console.log('[ServiceWorker] Sync event:', event.tag);
  
  if (event.tag === 'sync-email-signup') {
    event.waitUntil(syncEmailSignups());
  }
});

async function syncEmailSignups() {
  // Get pending signups from IndexedDB
  const signups = await getPendingSignups();
  
  for (const signup of signups) {
    try {
      await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(signup)
      });
      await removePendingSignup(signup.id);
    } catch (error) {
      console.error('Failed to sync signup:', error);
    }
  }
}

// IndexedDB helpers for offline support
function getPendingSignups() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('PhantomByteDB', 1);
    
    request.onerror = () => reject(request.error);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('pendingSignups')) {
        db.createObjectStore('pendingSignups', { keyPath: 'id', autoIncrement: true });
      }
    };
    
    request.onsuccess = (event) => {
      const db = event.target.result;
      const transaction = db.transaction('pendingSignups', 'readonly');
      const store = transaction.objectStore('pendingSignups');
      const getAllRequest = store.getAll();
      
      getAllRequest.onsuccess = () => resolve(getAllRequest.result || []);
      getAllRequest.onerror = () => reject(getAllRequest.error);
    };
  });
}

function removePendingSignup(id) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('PhantomByteDB', 1);
    
    request.onsuccess = (event) => {
      const db = event.target.result;
      const transaction = db.transaction('pendingSignups', 'readwrite');
      const store = transaction.objectStore('pendingSignups');
      store.delete(id);
      transaction.oncomplete = () => resolve();
    };
    
    request.onerror = () => reject(request.error);
  });
}
