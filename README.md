# PhantomByte Article Templates

Clean, responsive article templates inspired by DigitalTrends with PhantomByte branding.

## 🎨 Brand Colors
- **Purple Primary:** `#9D4EDD`
- **Neon Green:** `#00FF88`
- **Background:** Dark/Black theme

## 📁 File Structure

```
articles/
├── index.html              # Articles listing page (homepage style)
├── article-template.html   # Single article template
├── styles/
│   ├── main.css           # Core styles + branding
│   ├── articles.css       # Listing page styles
│   └── article.css        # Single article styles
├── scripts/
│   ├── email-signup.js    # Newsletter subscription
│   ├── push-notifications.js  # Web push notifications
│   ├── ad-manager.js      # Ad slot management (PerformCB ready)
│   └── share-buttons.js   # Social sharing
└── images/
    ├── placeholder-*.jpg  # Placeholder images
    └── author-vinny.jpg   # Author avatar
```

## 🚀 Quick Start

### 1. To Create a New Article:
1. Copy `article-template.html` to `article-your-title.html`
2. Edit the content:
   - Update `<title>` tag
   - Update `article-title` heading
   - Update `article-category` 
   - Update author info and date
   - Replace featured image
   - Write your article content in `article-body`
   - Update ad slots with PerformCB or AdSense code
3. Add article card to `index.html` grid

### 2. Customization Points:

**Ad Integration:**
- Top ad slot: `.ad-slot-article-top`
- Bottom ad slot: `.ad-slot-article-bottom`
- Listing page: `.ad-slot-horizontal`
- Edit `scripts/ad-manager.js` for PerformCB API integration

**Email Signup:**
- Forms are already integrated
- Edit `scripts/email-signup.js` to connect to SendGrid/Mailchimp
- API endpoint ready for integration

**Push Notifications:**
- Edit `scripts/push-notifications.js`
- Add your VAPID public key (Firebase/OneSignal)
- Service worker needed: create `service-worker.js` in root

**Buy Me a Coffee:**
- Links updated to: `https://buymeacoffee.com/DrVincentSativa`
- Saved in memory/vinny-preferences.md

## 📊 Analytics
- Google Analytics ID: `G-PDQCZE09E4`
- Already integrated on all pages
- Tracks page views, shares, and events

## 🎯 Key Features

✅ **Clean Reading Experience**
- Minimal distractions
- Good typography and spacing
- Readable on all devices

✅ **Monetization Ready**
- Ad slots (top/bottom of articles)
- Buy Me a Coffee CTAs
- Email collection forms
- Push notification prompts

✅ **Responsive Design**
- Mobile-first approach
- Adapts to all screen sizes
- Touch-friendly navigation

✅ **PhantomByte Branding**
- Purple/neon green color scheme
- Logo in header/footer
- Footer links to phantom-byte.com

✅ **SEO Optimized**
- Proper heading hierarchy
- Meta descriptions
- Semantic HTML5
- Fast loading

## 🔧 Deployment Checklist

### Before Deploy:
1. [ ] Replace placeholder images with real ones
2. [ ] Add PerformCB API key to `ad-manager.js`
3. [ ] Add VAPID key to `push-notifications.js`
4. [ ] Connect email signup to SendGrid API
5. [ ] Create `service-worker.js` for push notifications
6. [ ] Update author avatar image
7. [ ] Test locally in browser
8. [ ] Verify all links work

### Lessons from Past Deployments:
- Use `.Replace()` in PowerShell (not `-replace` with regex chars)
- Use HTML entities for emojis (e.g., `&#9749;` for ☕)
- Always test live URLs after deploy (Cloud Run caching issues)
- Verify DNS provider is IONOS before making changes

## 📝 Adding Articles Workflow

1. **Write Article:**
   ```powershell
   Copy-Item article-template.html article-my-new-post.html
   ```

2. **Edit Content:**
   - Title, category, date
   - Featured image
   - Article body content
   - Ad placements

3. **Update Listing Page:**
   - Add new card to `index.html`
   - Make it featured if needed
   - Update grid order

4. **Test Locally:**
   ```powershell
   # Open in browser
   Start-Process "C:\Users\Doter\workspace\articles\index.html"
   ```

5. **Deploy:**
   - Use cloud-run-batch-deploy skill
   - Map domain (e.g., `articles.phantom-byte.com`)
   - Verify live

## 🔗 Integration with phantom-byte.com

All templates include footer navigation back to main site:
- **Home** → `../../index.html` (adjust path based on deployment)
- **Services** → `../../index.html#services`
- **Articles** → Links to this articles section

## 📞 Support

Refer to:
- `SOUL.md` - Agent persona and rules
- `TOOLS.md` - Local credentials and setup
- `MEMORY.md` - Important lessons and context

---

**Built by PhantomByte** - Code from the shadows 👻
