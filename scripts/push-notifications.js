/**
 * PhantomByte - Web Push Notifications
 * Handles push notification subscription and management
 */

// VAPID public key from Firebase Console > Cloud Messaging > Web Push certificates
const VAPID_PUBLIC_KEY = 'BMTYT68726UTSESVn8eEaYd2mEXXzplgc0OkmDj40Q3sX2kD89IUw63AL7qb8pawqLZZwy6__ne9qRn_G2J1-Vs';

document.addEventListener('DOMContentLoaded', function() {
    const pushBtn = document.getElementById('enablePushBtn');
    
    if (pushBtn) {
        pushBtn.addEventListener('click', handlePushEnable);
        checkPushSupport();
    }
});

async function checkPushSupport() {
    const pushBtn = document.getElementById('enablePushBtn');
    
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        if (pushBtn) {
            pushBtn.textContent = 'Push Not Supported';
            pushBtn.disabled = true;
            pushBtn.style.background = '#666';
        }
        console.log('Push notifications not supported');
        return;
    }
    
    // Check if already subscribed
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    
    if (subscription) {
        if (pushBtn) {
            pushBtn.textContent = 'Notifications Enabled ✓';
            pushBtn.disabled = true;
            pushBtn.style.background = '#00CC6A';
        }
    }
}

async function handlePushEnable() {
    const pushBtn = document.getElementById('enablePushBtn');
    
    if (!('serviceWorker' in navigator)) {
        showNotification('Push notifications not supported in your browser', 'error');
        return;
    }
    
    try {
        // Request permission
        const permission = await Notification.requestPermission();
        
        if (permission !== 'granted') {
            showNotification('Notification permission denied', 'error');
            pushBtn.textContent = 'Notifications Disabled';
            pushBtn.disabled = true;
            return;
        }
        
        // Register service worker
        const registration = await navigator.serviceWorker.register('/service-worker.js');
        
        // Subscribe to push
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
        });
        
        // Send subscription to your server
        await sendSubscriptionToServer(subscription);
        
        showNotification('Push notifications enabled! You\'ll get updates.', 'success');
        pushBtn.textContent = 'Notifications Enabled ✓';
        pushBtn.disabled = true;
        pushBtn.style.background = '#00CC6A';
        
        console.log('Push subscription:', subscription);
        
    } catch (error) {
        console.error('Push subscription error:', error);
        showNotification('Failed to enable notifications', 'error');
    }
}

async function sendSubscriptionToServer(subscription) {
    // TODO: Send to your backend server
    // This will store the subscription for sending push notifications later
    
    // Store locally for now
    const subscriptions = JSON.parse(localStorage.getItem('pb_push_subscriptions') || '[]');
    subscriptions.push({
        subscription: subscription,
        timestamp: new Date().toISOString()
    });
    localStorage.setItem('pb_push_subscriptions', JSON.stringify(subscriptions));
    
    console.log('Subscription stored:', subscription);
    
    // Example: Send to your backend
    /*
    await fetch('/api/subscribe-push', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subscription)
    });
    */
}

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    
    return outputArray;
}

function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.querySelector('.push-notification');
    if (existing) existing.remove();
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `push-notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#00CC6A' : type === 'error' ? '#ff4444' : '#9D4EDD'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Add animation styles if not already present
if (!document.getElementById('push-anim-styles')) {
    const style = document.createElement('style');
    style.id = 'push-anim-styles';
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(400px); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}
