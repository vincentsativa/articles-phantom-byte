# Article Upload Rules - READ FIRST

## DO NOT ADD
- ❌ No outbound links in article body (NYT, BBC, etc. - keep as plain text)
- ❌ No Related Articles section (never add this)
- ❌ No Key Takeaways box unless explicitly in source text
- ❌ No extra sections the user didn't provide

## FOOTER (EXACT - copy from live site)
```html
<footer class="site-footer">
    <div class="container">
        <div class="footer-content">
            <div class="footer-brand">
                <div class="logo">
                    <span class="logo-phantom">Phantom</span><span class="logo-byte">Byte</span>
                </div>
                <p class="tagline">Code from the shadows</p>
                <div class="footer-cta">
                    <a href="https://buymeacoffee.com/DrVincentSativa" target="_blank" class="coffee-btn">☕ Buy Me a Coffee</a>
                </div>
            </div>
            <div class="footer-links">
                <h4>Navigation</h4>
                <ul>
                    <li><a href="../../index.html">Home</a></li>
                    <li><a href="https://phantom-byte.com" target="_blank">Services</a></li>
                </ul>
            </div>
            <div class="footer-social">
                <h4>Social</h4>
                <ul>
                    <li><a href="https://x.com/PhantomByteAI" target="_blank">X / Twitter</a></li>
                    <li><a href="https://www.pinterest.com/PhantomByteAI" target="_blank">Pinterest</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>© 2026 PhantomByte. All rights reserved.</p>
            <p class="privacy-links">
                <a href="privacy.html">Privacy Policy</a> | <a href="terms.html">Terms of Service</a>
            </p>
        </div>
    </div>
</footer>
```

## IMAGE PLACEMENT
- Featured image: After article header (automatic)
- Inside image: **WHERE USER SAYS** - ask if unclear, don't guess

## DEPLOYMENT
1. Build local HTML
2. User verifies
3. User says "YES" or "deploy"
4. Run seo-maintenance.py --all
5. Add article card to index.html (position #1)
6. Git commit + Cloud Run build
7. Verify live
8. Submit to Google

## TITLE/DESCRIPTION
- Title tag: Under 60 chars
- Meta description: 120-160 chars
- H1: Full title (can be longer)
