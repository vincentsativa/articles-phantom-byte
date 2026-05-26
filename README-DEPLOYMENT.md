# PhantomByte Article Deployment - Complete Setup

## 🎯 What You Have Now

1. **Automated deploy script** - One command deploys everything
2. **Google Indexing API integration** - Articles indexed in 1-24 hours instead of 2-7 days
3. **Automatic sitemap updates** - Every deploy adds the article to sitemap
4. **Verification built-in** - Script confirms everything worked

---

## 📋 Setup Checklist (Do This Once)

### Step 1: Enable Google Indexing API

Follow the guide: **`SETUP-INDEXING-API.md`**

Quick version:
1. Create service account in Google Cloud Console
2. Download JSON key → rename to `google-indexing-credentials.json`
3. Place it in: `/c/Users/Doter/workspace/articles/google-indexing-credentials.json`
4. Enable Indexing API
5. Add service account as Owner in Search Console

### Step 2: Test Setup

```bash
cd /c/Users/Doter/workspace/articles
./test-indexing-api.sh
```

Should see: `✅ SUCCESS! Indexing API is working!`

---

## 🚀 Deploy New Article (Every Time)

```bash
cd /c/Users/Doter/workspace/articles
./deploy-article.sh your-article-slug.html
```

**That's it.** The script will:
- ✅ Update sitemap
- ✅ Build & deploy to Cloud Run
- ✅ **Submit to Google Indexing API** (if credentials exist)
- ✅ Verify everything works

---

## ⏱️ Indexing Timeline

| Method | Time to Index |
|--------|---------------|
| **Indexing API** (with credentials) | **1-24 hours** |
| Sitemap crawl (no credentials) | 2-7 days |

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `deploy-article.sh` | Main deployment script |
| `test-indexing-api.sh` | Test Indexing API setup |
| `SETUP-INDEXING-API.md` | Step-by-step setup guide |
| `DEPLOY-WORKFLOW.md` | Full documentation |
| `QUICK-REFERENCE.md` | Quick cheat sheet |
| `.gitignore` | Prevents committing credentials |

---

## 🔧 Troubleshooting

### Script says "credentials not found"
That's OK! Article will still be indexed via sitemap, just takes longer (2-7 days instead of 1-24 hours).

To enable fast indexing, complete `SETUP-INDEXING-API.md`.

### Google API returns error
- Check service account has **Owner** permission in GSC
- Wait 5 minutes after adding permissions
- Verify Indexing API is enabled

### Article not showing in Google after 24 hours
- Check GSC → URL Inspection tool
- Manually request indexing if needed
- Sometimes takes up to 48 hours

---

## 📊 Current Status

- **Sitemap:** 44 articles
- **Service:** articles (us-central1)
- **Domain:** articles.phantom-byte.com
- **Indexing:** Fast (API) + Slow (sitemap) fallback

---

**Questions?** Check `DEPLOY-WORKFLOW.md` for detailed docs.
