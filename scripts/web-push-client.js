/**
 * PhantomByte Web Push Notification System
 * Client-side JavaScript for subscription management
 * 
 * Include this in your article template to enable push notifications
 */

(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    // Firebase config - should match your project
    firebase: {
      apiKey: "AIzaSyAiYUIBqL1GoOr4JBb-uSM32m10x8XCKr4",
      authDomain: "gen-lang-client-0237860564.firebaseapp.com",
      projectId: "gen-lang-client-0237860564",
      storageBucket: "gen-lang-client-0237860564.firebasestorage.app",
      messagingSenderId: "1091380733401",
      appId: "1:1091380733401:web:9b90665032927edfcea5c8"
    },
    // VAPID key for web push (from Firebase Console > Cloud Messaging > Web Push certificates)
    vapidKey: "BMTYT68726UTSESVn8eEaYd2mEXXzplgc0OkmDj40Q3sX2kD89IUw63AL7qb8pawqLZZwy6__ne9qRn_G2J1-Vs",
    // API endpoint for saving tokens
    apiEndpoint: "https://capture-api-sendgrid-1091380733401.us-central1.run.app/api/capture-push-token",
    // LocalStorage key
    storageKey: 'phantombyte_push_status'
  };

  // State
  let firebaseApp = null;
  let messaging = null;
  let isSubscribed = false;

  /**
   * Initialize the push notification system
   */
  async function init() {
    // Check if browser supports notifications
    if (!('Notification' in window)) {
      console.log('Push notifications not supported');
      return;
    }

    // Check if service workers are supported
    if (!('serviceWorker' in navigator)) {
      console.log('Service workers not supported');
      return;
    }

    // Load Firebase SDK dynamically
    await loadFirebaseSDK();
    
    // Initialize Firebase
    if (!firebase.apps.length) {
      firebaseApp = firebase.initializeApp(CONFIG.firebase);
    } else {
      firebaseApp = firebase.app();
    }
    
    messaging = firebase.messaging();

    // Register service worker
    await registerServiceWorker();
    
    // Check current subscription status
    await checkSubscriptionStatus();
    
    // Render the subscribe button
    renderSubscribeButton();
  }

  /**
   * Load Firebase SDK dynamically
   */
  function loadFirebaseSDK() {
    return new Promise((resolve, reject) => {
      if (window.firebase) {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js';
      script.onload = () => {
        const messagingScript = document.createElement('script');
        messagingScript.src = 'https://www.gstatic.com/firebasejs/10.8.0/firebase-messaging-compat.js';
        messagingScript.onload = resolve;
        messagingScript.onerror = reject;
        document.head.appendChild(messagingScript);
      };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  /**
   * Register the service worker
   */
  async function registerServiceWorker() {
    try {
      const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
      console.log('Service Worker registered:', registration);
      
      // Wait for the service worker to be ready
      await navigator.serviceWorker.ready;
      
      return registration;
    } catch (error) {
      console.error('Service Worker registration failed:', error);
      throw error;
    }
  }

  /**
   * Check if user is already subscribed
   */
  async function checkSubscriptionStatus() {
    const status = localStorage.getItem(CONFIG.storageKey);
    if (status) {
      const parsed = JSON.parse(status);
      isSubscribed = parsed.subscribed || false;
    }
    
    // Also check notification permission
    if (Notification.permission === 'granted') {
      // Try to get existing token
      try {
        const token = await messaging.getToken({ vapidKey: CONFIG.vapidKey });
        if (token) {
          isSubscribed = true;
          saveStatus({ subscribed: true, token: token });
        }
      } catch (error) {
        console.log('No existing token found');
      }
    }
  }

  /**
   * Subscribe to push notifications
   */
  async function subscribe() {
    try {
      // Request permission
      const permission = await Notification.requestPermission();
      
      if (permission !== 'granted') {
        console.log('Notification permission denied');
        showMessage('Notifications blocked. You can enable them in browser settings.');
        return false;
      }

      // Get FCM token
      const token = await messaging.getToken({ 
        vapidKey: CONFIG.vapidKey,
        serviceWorkerRegistration: await navigator.serviceWorker.ready
      });

      if (!token) {
        console.log('No registration token available');
        return false;
      }

      console.log('FCM Token:', token);

      // Save token to server
      await saveTokenToServer(token);
      
      // Update status
      isSubscribed = true;
      saveStatus({ subscribed: true, token: token });
      
      // Update UI
      updateButtonState();
      showMessage('✅ You\'ll get notified when new articles drop!');
      
      return true;
    } catch (error) {
      console.error('Error subscribing:', error);
      const msg = error.code 
        ? `Firebase error: ${error.code} - ${error.message}` 
        : error.message 
        || 'Something went wrong. Try again later.';
      showMessage(msg);
      return false;
    }
  }

  /**
   * Unsubscribe from push notifications
   */
  async function unsubscribe() {
    try {
      const token = await messaging.getToken({ vapidKey: CONFIG.vapidKey });
      
      if (token) {
        // Delete token from server
        await deleteTokenFromServer(token);
        
        // Delete token from FCM
        await messaging.deleteToken();
      }
      
      // Update status
      isSubscribed = false;
      localStorage.removeItem(CONFIG.storageKey);
      
      // Update UI
      updateButtonState();
      showMessage('Unsubscribed. You won\'t receive notifications anymore.');
      
      return true;
    } catch (error) {
      console.error('Error unsubscribing:', error);
      return false;
    }
  }

  /**
   * Save token to server (Firestore via Capture API)
   */
  async function saveTokenToServer(token) {
    try {
      const response = await fetch(CONFIG.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          userId: token,
          token: token,
          platform: 'web',
          subscribedAt: new Date().toISOString(),
          userAgent: navigator.userAgent
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      console.log('Token saved to server');
    } catch (error) {
      console.error('Error saving token:', error);
      // Still consider subscribed even if server save fails
      // The token is valid, we can retry later
    }
  }

  /**
   * Delete token from server
   */
  async function deleteTokenFromServer(token) {
    // Note: capture-api doesn't have an unsubscribe endpoint yet.
    // The FCM token will be invalidated locally via messaging.deleteToken() above.
    console.log('Token removed locally (no server unsubscribe endpoint)');
  }

  /**
   * Save subscription status to localStorage
   */
  function saveStatus(status) {
    localStorage.setItem(CONFIG.storageKey, JSON.stringify(status));
  }

  /**
   * Render the subscribe button (or wire up server-rendered button)
   */
  function renderSubscribeButton() {
    // Add styles first (idempotent)
    addStyles();

    // Check if button was server-rendered (common case: HTML includes the button)
    const existingBtn = document.getElementById('phantombyte-push-btn');
    if (existingBtn) {
      // Wire up the existing server-rendered button
      existingBtn.addEventListener('click', handleButtonClick);
      updateButtonState();
      return;
    }

    // Create button container from scratch
    const container = document.createElement('div');
    container.id = 'phantombyte-push-container';
    container.innerHTML = `
      <button id="phantombyte-push-btn" class="phantombyte-push-btn" aria-label="Subscribe to notifications">
        <span class="phantombyte-push-icon">🔔</span>
        <span class="phantombyte-push-text">Get Article Alerts</span>
      </button>
      <div id="phantombyte-push-message" class="phantombyte-push-message"></div>
    `;

    // Insert into page (after header or in footer)
    const insertTarget = document.querySelector('header') || document.querySelector('nav') || document.body;
    insertTarget.appendChild(container);

    // Add click handler
    document.getElementById('phantombyte-push-btn').addEventListener('click', handleButtonClick);

    // Set initial state
    updateButtonState();
  }

  /**
   * Handle button click
   */
  async function handleButtonClick() {
    const btn = document.getElementById('phantombyte-push-btn');
    btn.disabled = true;
    btn.classList.add('phantombyte-push-loading');

    if (isSubscribed) {
      await unsubscribe();
    } else {
      await subscribe();
    }

    btn.disabled = false;
    btn.classList.remove('phantombyte-push-loading');
  }

  /**
   * Update button state based on subscription
   */
  function updateButtonState() {
    const btn = document.getElementById('phantombyte-push-btn');
    const text = btn?.querySelector('.phantombyte-push-text');
    const icon = btn?.querySelector('.phantombyte-push-icon');
    
    if (!btn) return;

    if (isSubscribed) {
      text.textContent = 'Notifications On';
      icon.textContent = '🔔';
      btn.classList.add('phantombyte-push-active');
    } else {
      text.textContent = 'Get Article Alerts';
      icon.textContent = '🔔';
      btn.classList.remove('phantombyte-push-active');
    }
  }

  /**
   * Show message to user
   */
  function showMessage(text) {
    const msgEl = document.getElementById('phantombyte-push-message');
    if (msgEl) {
      msgEl.textContent = text;
      msgEl.classList.add('phantombyte-push-message-visible');
      
      setTimeout(() => {
        msgEl.classList.remove('phantombyte-push-message-visible');
      }, 5000);
    }
  }

  /**
   * Add CSS styles
   */
  function addStyles() {
    if (document.getElementById('phantombyte-push-styles')) {
      return;
    }

    const styles = document.createElement('style');
    styles.id = 'phantombyte-push-styles';
    styles.textContent = `
      #phantombyte-push-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }

      .phantombyte-push-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 20px;
        background: linear-gradient(135deg, #9D4EDD 0%, #7B2CBF 100%);
        color: white;
        border: none;
        border-radius: 50px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(157, 78, 221, 0.4);
        transition: all 0.3s ease;
      }

      .phantombyte-push-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(157, 78, 221, 0.5);
      }

      .phantombyte-push-btn:active {
        transform: translateY(0);
      }

      .phantombyte-push-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
      }

      .phantombyte-push-active {
        background: linear-gradient(135deg, #00FF88 0%, #00CC6A 100%) !important;
        box-shadow: 0 4px 15px rgba(0, 255, 136, 0.4) !important;
      }

      .phantombyte-push-loading {
        animation: phantombyte-pulse 1s infinite;
      }

      @keyframes phantombyte-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }

      .phantombyte-push-icon {
        font-size: 16px;
      }

      .phantombyte-push-message {
        position: absolute;
        bottom: 100%;
        right: 0;
        margin-bottom: 10px;
        padding: 10px 15px;
        background: #1a1a2e;
        color: white;
        border-radius: 8px;
        font-size: 13px;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transform: translateY(10px);
        transition: all 0.3s ease;
      }

      .phantombyte-push-message-visible {
        opacity: 1;
        visibility: visible;
        transform: translateY(0);
      }

      @media (max-width: 640px) {
        #phantombyte-push-container {
          bottom: 10px;
          right: 10px;
          left: 10px;
        }

        .phantombyte-push-btn {
          width: 100%;
          justify-content: center;
        }

        .phantombyte-push-message {
          left: 0;
          right: 0;
          white-space: normal;
          text-align: center;
        }
      }
    `;
    document.head.appendChild(styles);
  }

  // Handle foreground messages
  function setupForegroundMessaging() {
    if (!messaging) return;
    
    messaging.onMessage((payload) => {
      console.log('Foreground message received:', payload);
      
      // Show custom notification or banner
      showMessage(`📢 ${payload.notification?.title}: ${payload.notification?.body}`);
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose API for manual control
  window.PhantomBytePush = {
    subscribe,
    unsubscribe,
    get isSubscribed() { return isSubscribed; }
  };

  /* Relocate the push container out of <header> so position:fixed anchors to the viewport
     instead of the header's sticky containing block (which breaks header gradient on mobile). */
  (function relocatePushContainer(){
    function relocate(){
      var c=document.getElementById('phantombyte-push-container');
      if(c && c.parentNode!==document.body){ document.body.appendChild(c); }
    }
    if(document.readyState!=='loading'){ relocate(); }
    else { document.addEventListener('DOMContentLoaded',relocate); }
    window.addEventListener('load',function(){ relocate(); setTimeout(relocate,300); setTimeout(relocate,1200); });
    var h=document.querySelector('header');
    if(h && window.MutationObserver){
      var mo=new MutationObserver(function(){ relocate(); });
      mo.observe(h,{childList:true,subtree:true});
      setTimeout(function(){ mo.disconnect(); },6000);
    }
  })();

})();