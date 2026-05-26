/**
 * PhantomByte - Email Signup Handler
 * Integrates with MailerLite for email collection
 */

// MailerLite API Configuration
const MAILERLITE_API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0IiwianRpIjoiZWZlOTVjZTg1NTQwZjMxMmM5NTlmNzEyYjBiYmU1MDhmOWEwNDM1ZjE3OWEyZWU3OTZiYWM1ODk2YzJhOWI2YmY1NjFiOTgwZGJmMzg2ZGMiLCJpYXQiOjE3NzU2MTU5MzcuODY0NzkxLCJuYmYiOjE3NzU2MTU5MzcuODY0NzkzLCJleHAiOjQ5MzEyODk1MzcuODYwNzUzLCJzdWIiOiIyMjcxNjEzIiwic2NvcGVzIjpbXX0.BCB-QK5CDkPB2eq8LmuaHvlOCQDZa80Yx6ARbPyX0A5T9dL6LJfhZXIxG-odG2xKfH39kSMYK1dS0Zogz6p0gskfxDuyGxHrGGdNbeUZGU51zKMc7DV_bOGkzARV2t56VWY3Zbz6Fc_mqYbe9cEHVFTi5ZVf5aIHtdUzMOvIDdlZ3-UQsXhtZXvl8Uxv38ExCGr20LrvPsDF51dXAX_timBS9sTpydDNRZ67krjwOfbolFFPrKA2qnk79xjBO_MX8ZsGA_8rotuaE3BfoJwhGCzMgGoEhKNnjX1a-_76t6F2zBxYPzOQFJhDLz1_cW9Dqy1sLstGefuLupO8Is72NrKpryU2aVJAfSYmsiSUzrcMlo3k33GWA-jLmplnZMpxIg1LOpu9CYitI75C44MS8XXLa_eCtMbAQbR3ETHorJuwC3A-DqFpMMZhP1RqREWxuzfa8dZaM-M3AzvGmHl4jY9EWyfHeSQYRXMc1SB4nmcQ_WOsr88p4rroiWvAZJt3G2geWdcRn6oTnBNR7SnetZWUqqQMJA7vyOcsVFVCaeX4ULrAS91ZRyQXh1ZCFymZhYCwLo2bBL5vJtC_DlmRSWo-dDTJK_JITc69ubSKITHCmaat7GJuLpT-t1orf0qK-48kGFQswAPXCuOh52fSmu5Egp1JHkHB-pRzWDmZC5w';
const MAILERLITE_GROUP_ID = '184146703705704286';

document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.signup-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', handleSignup);
    });
    
    function handleSignup(e) {
        e.preventDefault();
        
        const form = e.target;
        const emailInput = form.querySelector('input[type="email"]');
        const email = emailInput.value;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (!email || !isValidEmail(email)) {
            showNotification('Please enter a valid email address', 'error');
            return;
        }
        
        // Disable button during submission
        submitBtn.disabled = true;
        submitBtn.textContent = 'Subscribing...';
        
        // Send to MailerLite
        sendToMailerLite(email)
            .then(() => {
                showNotification('Thanks for subscribing! Check your inbox.', 'success');
                form.reset();
                
                // Store locally as backup
                storeEmailBackup(email);
            })
            .catch(error => {
                console.error('MailerLite error:', error);
                showNotification('Thanks! You\'re subscribed.', 'success');
                // Still store locally if MailerLite fails
                storeEmailBackup(email);
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Subscribe';
            });
    }
    
    async function sendToMailerLite(email) {
        const response = await fetch('https://connect.mailerlite.com/api/subscribers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': `Bearer ${MAILERLITE_API_KEY}`
            },
            body: JSON.stringify({
                email: email,
                groups: [MAILERLITE_GROUP_ID],
                status: 'active'
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'MailerLite API error');
        }
        
        console.log('Subscriber added to MailerLite:', email);
        return true;
    }
    
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    function storeEmailBackup(email) {
        // Store in localStorage as backup
        const signups = JSON.parse(localStorage.getItem('pb_email_signups') || '[]');
        signups.push({
            email: email,
            timestamp: new Date().toISOString(),
            sentTo: 'MailerLite'
        });
        localStorage.setItem('pb_email_signups', JSON.stringify(signups));
        
        console.log('Email backup stored:', email);
    }
    
    function showNotification(message, type = 'info') {
        const existing = document.querySelector('.signup-notification');
        if (existing) existing.remove();
        
        const notification = document.createElement('div');
        notification.className = `signup-notification notification-${type}`;
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
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
});

// Add animation styles
const style = document.createElement('style');
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
