#!/bin/bash
#
# PhantomByte Deploy with SEO Automation
# This script does EVERYTHING: SEO maintenance + build + deploy + verification
#
# Usage: ./deploy-with-seo.sh [article-slug.html]
#   With slug: Deploys a specific article (also runs SEO maintenance)
#   Without slug: Just runs SEO maintenance and deploys site updates
#
# This replaces the manual deploy process. Every deploy now includes:
#   1. SEO maintenance (sitemap, RSS, llms.txt regeneration)
#   2. SEO validation
#   3. Git commit
#   4. Docker build + push
#   5. Cloud Run deploy
#   6. Live verification
#   7. Google Indexing API submission (if configured)
#

set -e

# ─── Configuration ──────────────────────────────────────────────────────────
PROJECT_ID="gen-lang-client-0237860564"
SERVICE_NAME="articles"
REGION="us-central1"
ARTICLES_DIR="/c/Users/Doter/workspace/articles"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors (no unicode to avoid encoding issues)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "============================================================"
echo "  PhantomByte Deploy with SEO Automation"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# ─── Step 1: Run SEO Maintenance ─────────────────────────────────────────
echo ""
echo ">>> [1/7] Running SEO maintenance..."
cd "$ARTICLES_DIR"
python seo-maintenance.py --all

if [ $? -ne 0 ]; then
    echo "!!! SEO maintenance failed! Aborting deploy."
    exit 1
fi

# ─── Step 2: Validate SEO (stop on critical errors) ──────────────────────
echo ""
echo ">>> [2/7] Validating SEO..."

# Check that sitemap was updated
SITEMAP_DATE=$(grep '<lastmod>' sitemap.xml | head -1 | sed 's/.*<lastmod>//;s/<\/lastmod>.*//')
TODAY=$(date +%Y-%m-%d)

if [ "$SITEMAP_DATE" != "$TODAY" ]; then
    echo "!!! WARNING: Sitemap lastmod date ($SITEMAP_DATE) is not today ($TODAY)"
fi

# Count articles in sitemap
SITEMAP_COUNT=$(grep -c '<loc>' sitemap.xml)
echo "    Sitemap contains $SITEMAP_COUNT URLs"

# Verify no articles are missing from sitemap by checking index.html links
MISSING=0
while IFS= read -r link; do
    slug=$(echo "$link" | sed 's/href="//;s/"//')
    case "$slug" in
        *.html)
            if ! grep -q "$slug" sitemap.xml 2>/dev/null; then
                if [ "$slug" != "index.html" ] && [ "$slug" != "privacy.html" ] && [ "$slug" != "terms.html" ]; then
                    echo "    !!! MISSING from sitemap: $slug"
                    MISSING=$((MISSING + 1))
                fi
            fi
            ;;
    esac
done < <(grep -o 'href="[^"]*\.html"' "$ARTICLES_DIR/index.html")

if [ $MISSING -gt 0 ]; then
    echo "!!! $MISSING articles in index.html but NOT in sitemap!"
    echo "    Re-running SEO maintenance..."
    python seo-maintenance.py --sitemap
fi

# ─── Step 3: Check for missing OG images ──────────────────────────────────
echo ""
echo ">>> [3/7] Checking required assets..."

MISSING_ASSETS=0
for img in "og-featured.jpg" "twitter-featured.jpg" "phantombyte-logo.png"; do
    if [ ! -f "$ARTICLES_DIR/images/$img" ]; then
        echo "    !!! Missing: images/$img"
        MISSING_ASSETS=$((MISSING_ASSETS + 1))
    fi
done

if [ $MISSING_ASSETS -gt 0 ]; then
    echo "!!! $MISSING_ASSETS required images are missing!"
    echo "    Run seo-maintenance.py to create them, or create manually."
fi

# ─── Step 4: Git commit ──────────────────────────────────────────────────
echo ""
echo ">>> [4/7] Committing changes to git..."
cd "$ARTICLES_DIR"

# Stage all changes (sitemap, RSS, llms.txt, nginx.conf, any new articles)
git add sitemap.xml rss.xml llms.txt nginx.conf images/ 2>/dev/null || true
git add -A 2>/dev/null || true

# Check if there are changes to commit
if git diff --staged --quiet 2>/dev/null; then
    echo "    No git changes to commit"
else
    git commit -m "seo: auto-maintained sitemap, RSS, llms.txt, and security headers $(date +%Y-%m-%d)"
    echo "    Git commit created"
fi

# ─── Step 5: Build & Push Docker Image ────────────────────────────────────
echo ""
echo ">>> [5/7] Building Docker image..."
cd "$ARTICLES_DIR"

docker build --no-cache -t gcr.io/$PROJECT_ID/$SERVICE_NAME . 2>&1 | tail -5

echo "    Pushing to GCR..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME 2>&1 | tail -3

# ─── Step 6: Deploy to Cloud Run ──────────────────────────────────────────
echo ""
echo ">>> [6/7] Deploying to Cloud Run..."

gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 2>&1 | tail -5

echo "    Waiting for deployment to propagate..."
sleep 10

# ─── Step 7: Verify live & submit to Google ──────────────────────────────
echo ""
echo ">>> [7/7] Verifying live deployment..."

# Verify sitemap is live
LIVE_COUNT=$(curl -s https://articles.phantom-byte.com/sitemap.xml | grep -c '<loc>' 2>/dev/null || echo "0")
echo "    Live sitemap URLs: $LIVE_COUNT"

# Verify RSS is live
RSS_CHECK=$(curl -s https://articles.phantom-byte.com/rss.xml | grep -c '<item>' 2>/dev/null || echo "0")
echo "    Live RSS articles: $RSS_CHECK"

# Verify robots.txt references sitemap
ROBOTS_SITEMAP=$(curl -s https://articles.phantom-byte.com/robots.txt | grep -c "Sitemap:" 2>/dev/null || echo "0")
echo "    robots.txt sitemap reference: $ROBOTS_SITEMAP"

# Check HSTS header
HSTS_HEADER=$(curl -sI https://articles.phantom-byte.com/ | grep -i "strict-transport" | head -1 || echo "MISSING")
echo "    HSTS header: $HSTS_HEADER"

# If a specific article was provided, verify it loads
if [ -n "$1" ]; then
    ARTICLE_STATUS=$(curl -sI "https://articles.phantom-byte.com/$1" | head -1 || echo "000")
    echo "    Article $1 status: $ARTICLE_STATUS"
fi

# Submit to Google Indexing API
if [ -f "$ARTICLES_DIR/google-indexing-credentials.json" ]; then
    echo ""
    echo "    Submitting updated sitemap to Google Indexing API..."
    python seo-maintenance.py --submit-url="https://articles.phantom-byte.com/sitemap.xml"
    
    # Submit homepage sitemap too
    if [ -f "$ARTICLES_DIR/../phantom-byte-website/google-indexing-credentials.json" ]; then
        echo "    Submitting main site sitemap to Google..."
        python seo-maintenance.py --submit-url="https://phantom-byte.com/sitemap.xml"
    fi
else
    echo ""
    echo "    [!] Google Indexing API not configured."
    echo "    [!] Set up credentials per SETUP-INDEXING-API.md for faster indexing."
fi

echo ""
echo "============================================================"
echo "  DEPLOY COMPLETE"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
echo ""
echo "  Sitemap: https://articles.phantom-byte.com/sitemap.xml"
echo "  RSS:     https://articles.phantom-byte.com/rss.xml"
echo "  llms.txt: https://articles.phantom-byte.com/llms.txt"
echo "  Articles: $LIVE_COUNT live URLs"
echo ""
echo "  NEXT STEPS:"
echo "  1. Check Google Search Console for indexing status"
echo "  2. Monitor: https://search.google.com/search-console"
echo ""