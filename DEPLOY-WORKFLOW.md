# PhantomByte Article Deployment Workflow

## Quick Start

```bash
# After creating a new article HTML file:
cd /c/Users/Doter/workspace/articles
./deploy-article.sh your-article-slug.html
```

## What the Script Does

1. **Verifies** article file exists
2. **Extracts** publish date from article metadata
3. **Backs up** current sitemap
4. **Adds** article to sitemap (newest first)
5. **Validates** sitemap (checks HTTPS, XML structure)
6. **Builds** Docker image with updated content
7. **Pushes** to Google Container Registry
8. **Deploys** to Cloud Run
9. **Verifies** deployment succeeded

## Manual Steps (If Script Fails)

### Step 1: Add to Sitemap
Edit `/c/Users/Doter/workspace/articles/sitemap.xml`

Insert new article after `terms.html` entry:
```xml
<url>
  <loc>https://articles.phantom-byte.com/your-article-slug.html</loc>
  <lastmod>2026-04-21</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.8</priority>
</url>
```

### Step 2: Build & Push
```bash
cd /c/Users/Doter/workspace/articles
docker build -t gcr.io/gen-lang-client-0237860564/articles .
docker push gcr.io/gen-lang-client-0237860564/articles
```

### Step 3: Deploy to Cloud Run
```bash
gcloud run deploy articles \
  --image gcr.io/gen-lang-client-0237860564/articles \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

### Step 4: Verify
```bash
# Check sitemap
curl -s https://articles.phantom-byte.com/sitemap.xml | grep -c "<loc>"

# Check article
curl -sI https://articles.phantom-byte.com/your-article-slug.html

# Check for noindex
curl -s https://articles.phantom-byte.com/your-article-slug.html | grep -i noindex
```

## Pre-Deploy Checklist

Before running deploy script, ensure article has:

- [ ] `<meta name="robots" content="index, follow">` (or omit entirely)
- [ ] `<link rel="canonical" href="https://articles.phantom-byte.com/SLUG.html">`
- [ ] `<meta name="description" content="...">`
- [ ] `<meta property="og:url" content="https://articles.phantom-byte.com/SLUG.html">`
- [ ] JSON-LD schema with `@type: "TechArticle"`
- [ ] `property="article:published_time"` with date
- [ ] **NO** `<meta name="robots" content="noindex">`

## Post-Deploy Verification

```bash
# 1. Sitemap has correct URL count (should be 44+ after initial fix)
curl -s https://articles.phantom-byte.com/sitemap.xml | grep -c "<loc>"

# 2. Article is accessible
curl -sI https://articles.phantom-byte.com/SLUG.html | head -1
# Should return: HTTP/2 200

# 3. No noindex directive
curl -s https://articles.phantom-byte.com/SLUG.html | grep -i noindex
# Should return: empty (no output)

# 4. Sitemap contains new article
curl -s https://articles.phantom-byte.com/sitemap.xml | grep "SLUG.html"
# Should return: the URL entry
```

## Updating Main Site (Optional)

For major articles, add to phantom-byte.com homepage:

```bash
cd /c/Users/Doter/workspace/phantom-byte-website
# Edit index.html to add article card in "Latest Articles" section
# Then rebuild and deploy:
docker build -t gcr.io/gen-lang-client-0237860564/phantom-byte-website .
docker push gcr.io/gen-lang-client-0237860564/phantom-byte-website
gcloud run deploy phantom-byte \
  --image gcr.io/gen-lang-client-0237860564/phantom-byte-website \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

## Troubleshooting

### Sitemap not updating
- Check Docker build cache: use `docker build --no-cache`
- Verify sitemap.xml was copied in Dockerfile (it uses `COPY . /usr/share/nginx/html`)

### Cloud Run deployment fails
- Check authentication: `gcloud auth login`
- Configure Docker: `gcloud auth configure-docker gcr.io`

### Article returns 404
- Verify file exists in `/c/Users/Doter/workspace/articles/`
- Check nginx routing: files should be at root, not in subdirectory

## Backup & Restore

Sitemap backups are automatically created:
```
/c/Users/Doter/workspace/articles/sitemap.xml.backup.YYYYMMDD-HHMMSS
```

To restore:
```bash
cp /c/Users/Doter/workspace/articles/sitemap.xml.backup.YYYYMMDD-HHMMSS \
   /c/Users/Doter/workspace/articles/sitemap.xml
# Then rebuild and deploy
```

## Google Search Console

After deployment, Vinny should:
1. Go to https://search.google.com/search-console
2. Select `phantom-byte.com` domain property
3. Navigate to **Sitemaps**
4. Submit: `https://articles.phantom-byte.com/sitemap.xml`
5. Check indexing status after 24-48 hours

---

**Last Updated:** April 21, 2026  
**Sitemap URL Count:** 44 URLs  
**Service:** articles (us-central1)
