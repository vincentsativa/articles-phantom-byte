/**
 * PhantomByte Web Push Notification System
 * Service Worker for handling push notifications
 * 
 * This file must be served from the root of the domain
 * as /firebase-messaging-sw.js
 */

importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js');

// Firebase configuration - matches the main app
const firebaseConfig = {
  apiKey: "AIzaSyAiYUIBqL1GoOr4JBb-uSM32m10x8XCKr4",
  authDomain: "gen-lang-client-0237860564.firebaseapp.com",
  projectId: "gen-lang-client-0237860564",
  storageBucket: "gen-lang-client-0237860564.firebasestorage.app",
  messagingSenderId: "1091380733401",
  appId: "1:1091380733401:web:9b90665032927edfcea5c8"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Initialize messaging
const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message:', payload);
  
  const notificationTitle = payload.notification?.title || 'PhantomByte Update';
  const notificationOptions = {
    body: payload.notification?.body || 'New content available',
    icon: '/images/phantombyte-icon-192.png',
    badge: '/images/phantombyte-badge-72.png',
    tag: payload.data?.articleId || 'default',
    data: payload.data || {},
    requireInteraction: false,
    actions: [
      {
        action: 'open',
        title: 'Read Article'
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ]
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
  console.log('[firebase-messaging-sw.js] Notification clicked:', event);
  
  event.notification.close();
  
  const articleUrl = event.notification.data?.articleUrl || 'https://articles.phantom-byte.com/';
  
  if (event.action === 'open' || event.action === '') {
    event.waitUntil(
      clients.openWindow(articleUrl)
    );
  }
});

// Handle push subscription change
self.addEventListener('pushsubscriptionchange', (event) => {
  console.log('[firebase-messaging-sw.js] Push subscription changed');
  
  // The main app will handle re-subscription
  // This event notifies the app to update the token
  event.waitUntil(
    self.clients.matchAll({ type: 'window' }).then((clientList) => {
      for (const client of clientList) {
        client.postMessage({
          type: 'PUSH_SUBSCRIPTION_CHANGE',
          message: 'Subscription changed, please re-subscribe'
        });
      }
    })
  );
});

// Service worker activation
self.addEventListener('activate', (event) => {
  console.log('[firebase-messaging-sw.js] Service worker activated');
  event.waitUntil(self.clients.claim());
});

console.log('[firebase-messaging-sw.js] Service worker loaded');
