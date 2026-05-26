# Setup Google Indexing API - Quick Guide

## Why Use This?

Without this: Google finds your articles in **2-7 days** (when they recrawl sitemap)  
With this: Google indexes in **1-24 hours** (you tell them directly)

---

## Step 1: Create Service Account

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **"+ CREATE CREDENTIALS"** → **"Service account"**
3. Fill in:
   - **Service account name:** `indexing-api`
   - **Service account ID:** `indexing-api@gen-lang-client-0237860564.iam.gserviceaccount.com`
   - **Description:** `Auto-submit articles to Google Indexing API`
4. Click **"Create and continue"**
5. Skip optional fields, click **"Continue"**
6. Click **"Done"**

---

## Step 2: Create JSON Key

1. In the service account list, click on `indexing-api`
2. Go to **"Keys"** tab
3. Click **"Add key"** → **"Create new key"**
4. Select **JSON** format
5. Click **"Create"**
6. **Download the JSON file** (it downloads automatically)
7. **IMPORTANT:** Rename it to `google-indexing-credentials.json`
8. Move it to: `/c/Users/Doter/workspace/articles/google-indexing-credentials.json`

---

## Step 3: Enable Indexing API

1. Go to: https://console.cloud.google.com/apis/library/indexing.googleapis.com
2. Click **"ENABLE"**
3. Wait for it to finish (about 30 seconds)

---

## Step 4: Add to Google Search Console

1. Go to: https://search.google.com/search-console
2. Select `phantom-byte.com` property
3. Go to **Settings** (gear icon) → **Users and permissions**
4. Click **"Add user"**
5. Enter the service account email:
   ```
   indexing-api@gen-lang-client-0237860564.iam.gserviceaccount.com
   ```
6. Select permission: **"Owner"** (required for Indexing API)
7. Click **"Add"**

---

## Step 5: Verify Setup

```bash
cd /c/Users/Doter/workspace/articles
./test-indexing-api.sh
```

If you see `"Notification sent successfully"` - you're good to go!

---

## Security Notes

- The JSON key file has full access to submit URLs to Google
- **Never commit it to Git** (it's in .gitignore)
- **Never share it publicly**
- Store it only on your local machine

---

## Troubleshooting

### "Permission denied" error
- Make sure service account has **Owner** permission in GSC
- Wait 5 minutes after adding permissions (propagation delay)

### "API not enabled" error
- Go to https://console.cloud.google.com/apis/library/indexing.googleapis.com
- Click ENABLE

### "Invalid credentials" error
- Re-download the JSON key
- Make sure file is at: `/c/Users/Doter/workspace/articles/google-indexing-credentials.json`

---

**Once set up, the deploy script will automatically submit each new article to Google!**
