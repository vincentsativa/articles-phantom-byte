# PhantomByte Article Deployment - Quick Reference

## 🚀 Deploy New Article

```bash
cd /c/Users/Doter/workspace/articles
./deploy-article.sh your-article-slug.html
```

## 📋 Pre-Deploy Checklist

Article HTML must have:
- ✅ `<meta property="article:published_time" content="2026-04-21">`
- ✅ `<link rel="canonical" href="https://articles.phantom-byte.com/slug.html">`
- ✅ `<meta name="description" content="...">`
- ✅ `<meta property="og:url" content="https://articles.phantom-byte.com/slug.html">`
- ✅ JSON-LD schema (TechArticle)
- ❌ **NO** `<meta name="robots" content="noindex">`

## ✅ Post-Deploy Verification

```bash
# Check sitemap count (should be 44+)
curl -s https://articles.phantom-byte.com/sitemap.xml | grep -c "<loc>"

# Verify article accessible
curl -sI https://articles.phantom-byte.com/slug.html

# Confirm no noindex
curl -s https://articles.phantom-byte.com/slug.html | grep -i noindex
```

## 📊 Current Status

| Metric | Value |
|--------|-------|
| Articles in sitemap | 44 |
| Sitemap URL | https://articles.phantom-byte.com/sitemap.xml |
| Cloud Run service | articles (us-central1) |
| Latest revision | articles-00212-w5h |

## 🛠️ Manual Deploy (If Script Fails)

```bash
# 1. Edit sitemap.xml - add article after terms.html
# 2. Build: docker build -t gcr.io/gen-lang-client-0237860564/articles .
# 3. Push: docker push gcr.io/gen-lang-client-0237860564/articles
# 4. Deploy: gcloud run deploy articles --image gcr.io/gen-lang-client-0237860564/articles --platform managed --region us-central1 --allow-unauthenticated --port 8080
```

## 📝 Backup Location

Sitemap backups: `/c/Users/Doter/workspace/articles/sitemap.xml.backup.*`

## 🔔 Notify Larry After Deploy

Message should include:
- Article URL
- Sitemap update confirmation
- Any errors encountered

---

**Script Location:** `/c/Users/Doter/workspace/articles/deploy-article.sh`  
**Full Documentation:** `DEPLOY-WORKFLOW.md`
