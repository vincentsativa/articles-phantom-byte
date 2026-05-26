/**
 * PhantomByte - Share Buttons Handler
 * Handles social sharing functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeShareButtons();
});

function initializeShareButtons() {
    const shareBtn = document.querySelector('.share-btn');
    const twitterBtn = document.querySelector('.share-btn-twitter');
    const facebookBtn = document.querySelector('.share-btn-facebook');
    const linkedinBtn = document.querySelector('.share-btn-linkedin');
    
    if (shareBtn) {
        shareBtn.addEventListener('click', openShareMenu);
    }
    
    if (twitterBtn) {
        twitterBtn.addEventListener('click', shareToTwitter);
    }
    
    if (facebookBtn) {
        facebookBtn.addEventListener('click', shareToFacebook);
    }
    
    if (linkedinBtn) {
        linkedinBtn.addEventListener('click', shareToLinkedIn);
    }
}

function openShareMenu() {
    // Get current page info
    const url = encodeURIComponent(window.location.href);
    const title = encodeURIComponent(document.title);
    
    // Create share menu (simple implementation)
    const shareOptions = [
        { name: 'Twitter', action: () => shareToTwitter() },
        { name: 'Facebook', action: () => shareToFacebook() },
        { name: 'LinkedIn', action: () => shareToLinkedIn() },
        { name: 'Copy Link', action: () => copyLink() }
    ];
    
    // For now, just copy link
    copyLink();
}

function shareToTwitter() {
    const url = encodeURIComponent(window.location.href);
    const title = encodeURIComponent(document.title);
    const text = encodeURIComponent('Check out this article from PhantomByte');
    
    const shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${text}&title=${title}`;
    window.open(shareUrl, '_blank', 'width=600,height=400');
    
    trackShare('twitter');
}

function shareToFacebook() {
    const url = encodeURIComponent(window.location.href);
    
    const shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
    window.open(shareUrl, '_blank', 'width=600,height=400');
    
    trackShare('facebook');
}

function shareToLinkedIn() {
    const url = encodeURIComponent(window.location.href);
    const title = encodeURIComponent(document.title);
    
    const shareUrl = `https://www.linkedin.com/shareArticle?mini=true&url=${url}&title=${title}`;
    window.open(shareUrl, '_blank', 'width=600,height=400');
    
    trackShare('linkedin');
}

function copyLink() {
    const url = window.location.href;
    
    navigator.clipboard.writeText(url).then(() => {
        showNotification('Link copied to clipboard!', 'success');
    }).catch(() => {
        // Fallback for older browsers
        const tempInput = document.createElement('input');
        tempInput.value = url;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        showNotification('Link copied to clipboard!', 'success');
    });
    
    trackShare('copy');
}

function trackShare(platform) {
    // Track share event with analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', 'share', {
            event_category: 'social',
            event_label: platform,
            event_destination: platform
        });
    }
    
    console.log('Share tracked:', platform);
}

function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.querySelector('.share-notification');
    if (existing) existing.remove();
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `share-notification notification-${type}`;
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
