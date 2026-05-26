# System Verification Guide

## ✅ Testing Your Integration

Open `verify-systems.html` in your browser to test all systems automatically.

## What's Being Tested:

### 1. Google Analytics ✓
- **Status:** Already working
- **Tracking ID:** G-PDQCZE09E4
- **What it does:** Tracks page views, events, and user behavior
- **Verification:** Check Real-Time view in GA dashboard at https://analytics.google.com

### 2. Email Capture (SendGrid) ✓
- **API Key:** Configured and active
- **Sender Email:** stillinthegame@gmail.com
- **Plan:** 100 emails/day free tier
- **What it does:** Sends welcome email when users subscribe
- **Verification:** Use the test form in verify-systems.html

### 3. Push Notifications (FCM) ✓
- **Service Account:** Configured with your Firebase project
- **Project ID:** gen-lang-client-0237860564
- **What it does:** Enables web push notifications
- **Verification:** Click "Test Push Notification" button

## How to Test:

1. **Open `verify-systems.html`** in Chrome/Firefox/Edge
2. **Wait for automatic tests** to complete (GA check)
3. **Enter your email** in the test form and click "Send Test Email"
   - Check your inbox for the test email
4. **Click "Test Push Notification"**
   - Grant permission when prompted
   - You should see a notification

## Expected Results:

✅ **All Green Checks** = Ready to deploy

❌ **Any Red X's** = Fix needed (see troubleshooting below)

## Troubleshooting:

### Google Analytics Shows Red X:
- Check if you're blocking scripts (ad blockers)
- Verify the GA script tag is in the HTML head
- Wait a few seconds for the script to load

### SendGrid Email Fails:
- Check API key is valid (see TOOLS.md)
- Verify sender email is authenticated in SendGrid
- Check SendGrid dashboard at https://app.sendgrid.com

### Push Notifications Fail:
- Make sure you're using HTTPS (or localhost for testing)
- Check browser supports notifications
- Verify service-worker.js is accessible
- Grant notification permission when prompted

## Integration Points:

### Email Signup Form:
```javascript
// Already configured in email-signup.js
// Uses SendGrid API to send welcome emails
// Stores backup in localStorage
```

### Push Notifications:
```javascript
// Already configured in push-notifications.js
// Uses Firebase Admin SDK for sending
// Service worker handles display
```

### Analytics:
```html
<!-- Already in all HTML files -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-PDQCZE09E4"></script>
```

## After Deployment:

1. **Verify GA:** Check Real-Time view in Google Analytics
2. **Test Email:** Subscribe with a test email
3. **Test Push:** Enable notifications on live site
4. **Monitor:** Check SendGrid activity dashboard

## Files Location:
```
articles/
├── verify-systems.html    ← Test all systems here
├── scripts/
│   ├── email-signup.js    ← SendGrid integration
│   └── push-notifications.js ← FCM integration
├── service-worker.js      ← Push notification handler
└── styles/
    └── main.css           ← Shared styles
```

---

**When all tests pass, you're ready to deploy!** 🚀
