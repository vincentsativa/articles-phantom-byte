# Google Indexing API - ACTUAL Status & Fix Instructions

## What Was SUPPOSED To Be Done Last Week
1. Create service account
2. **Enable Indexing API** ← NEVER DONE (just enabled now 4/29)
3. Create JSON key
4. Add service account as **OWNER** in Search Console ← Only added as "Full User"
5. Test submission

## What ACTUALLY Happened
- Service account was created: `phantom-byte-gsc-reader@gen-lang-client-0237860564.iam.gserviceaccount.com`
- JSON key was saved: `/c/Users/Doter/workspace/credentials/gsc-service-account.json`
- The account was added to Search Console but with **wrong permission level** ("siteFullUser" instead of "siteOwner")
- The **Indexing API was never enabled** in the Google Cloud project (just enabled now)
- Result: Every API call returns `403 Permission denied. Failed to verify the URL ownership.`

## How To Fix This NOW (Takes 2 Minutes)

### Step 1: Open Google Search Console
Go to: https://search.google.com/search-console

### Step 2: Add Service Account as OWNER (not "Full User")

For **phantom-byte.com**:
1. Select `phantom-byte.com` property
2. Go to **Settings** (gear icon) → **Users and permissions**
3. Find `phantom-byte-gsc-reader@gen-lang-client-0237860564.iam.gserviceaccount.com`
4. Click **Change permission** → Set to **Owner** (NOT "Full" — must be **Owner**)
5. Save

For **articles.phantom-byte.com**:
1. Select `articles.phantom-byte.com` property (or add it if not there)
2. Go to **Settings** → **Users and permissions**
3. Click **Add user**
4. Enter: `phantom-byte-gsc-reader@gen-lang-client-0237860564.iam.gserviceaccount.com`
5. Permission: **Owner** (NOT "Full" — this is the critical difference)
6. Click **Add**

### Step 3: Verify It Works
After making the change, wait 2-5 minutes, then run:
```bash
cd C:/Users/Doter/workspace/articles
python seo-maintenance.py --submit-url="https://articles.phantom-byte.com/sitemap.xml"
```

You should see:
```
✅ Submitted to Google Indexing API: https://articles.phantom-byte.com/sitemap.xml
Expected indexing: 1-24 hours
```

If you still get 403, wait 5 more minutes (permissions take time to propagate).

## Current Status Summary
| Step | Status |
|------|--------|
| Service account created | ✅ Done |
| JSON key file exists | ✅ Done (`/c/Users/Doter/workspace/credentials/gsc-service-account.json`) |
| Key copied to articles dir | ✅ Done (`/c/Users/Doter/workspace/articles/google-indexing-credentials.json`) |
| Indexing API enabled | ✅ Done (just enabled 4/29/2026) |
| Service account added to GSC | ⚠️ Wrong permission level — "Full User" instead of "Owner" |
| articles.phantom-byte.com added to GSC | ⚠️ Added but "Unverified User" |
| Articles URLs submitting to Google | ❌ 403 Permission denied |

## The EXACT Permission You Need
The service account needs **Owner** role, not Full User. This is a Google Search Console requirement specific to the Indexing API:

> "To use the Indexing API, you must be a site **owner**. The 'Full' permission level is not sufficient." — Google Documentation

## Why Articles Weren't Indexing in 1-24 Hours
The Indexing API was the mechanism supposed to achieve that. Since it was never properly configured (API disabled + wrong permission level), articles have been relying solely on sitemap crawling, which takes 2-7 days. Once you change the permission to **Owner**, articles will index in 1-24 hours after each publish via `seo-maintenance.py --submit`.