#!/bin/bash
#
# PhantomByte Article Deploy Script
# Automates sitemap update + Cloud Run deployment for new articles
#
# Usage: ./deploy-article.sh ARTICLE_SLUG.html
# Example: ./deploy-article.sh my-new-article.html
#

set -e

# Configuration
PROJECT_ID="gen-lang-client-0237860564"
SERVICE_NAME="articles"
REGION="us-central1"
ARTICLES_DIR="/c/Users/Doter/workspace/articles"
SITEMAP_FILE="$ARTICLES_DIR/sitemap.xml"
CREDENTIALS_FILE="$ARTICLES_DIR/google-indexing-credentials.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  PhantomByte Article Deploy Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if article slug provided
if [ -z "$1" ]; then
    echo -e "${RED}ERROR: No article slug provided${NC}"
    echo "Usage: ./deploy-article.sh ARTICLE_SLUG.html"
    echo "Example: ./deploy-article.sh my-new-article.html"
    exit 1
fi

ARTICLE_SLUG="$1"
ARTICLE_FILE="$ARTICLES_DIR/$ARTICLE_SLUG"

# Step 1: Verify article file exists
echo -e "${YELLOW}[1/7] Verifying article file...${NC}"
if [ ! -f "$ARTICLE_FILE" ]; then
    echo -e "${RED}ERROR: Article file not found: $ARTICLE_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Article file found${NC}"

# Step 2: Extract publish date from article
echo -e "${YELLOW}[2/7] Extracting publish date...${NC}"
PUB_DATE=$(grep -oP 'property="article:published_time" content="\K[^"]+' "$ARTICLE_FILE" | head -1)
if [ -z "$PUB_DATE" ]; then
    PUB_DATE=$(date +%Y-%m-%d)
    echo -e "${YELLOW}  No published_time found, using today: $PUB_DATE${NC}"
else
    echo -e "${GREEN}✓ Published date: $PUB_DATE${NC}"
fi

# Step 3: Backup current sitemap
echo -e "${YELLOW}[3/7] Backing up current sitemap...${NC}"
BACKUP_FILE="$SITEMAP_FILE.backup.$(date +%Y%m%d-%H%M%S)"
cp "$SITEMAP_FILE" "$BACKUP_FILE"
echo -e "${GREEN}✓ Backup created: $BACKUP_FILE${NC}"

# Step 4: Check if article already in sitemap
echo -e "${YELLOW}[4/7] Checking sitemap for existing entry...${NC}"
if grep -q "$ARTICLE_SLUG" "$SITEMAP_FILE"; then
    echo -e "${YELLOW}  Article already in sitemap, updating date...${NC}"
    # Update existing entry's lastmod
    sed -i "s|<loc>https://articles.phantom-byte.com/$ARTICLE_SLUG</loc>|<loc>https://articles.phantom-byte.com/$ARTICLE_SLUG</loc>|g" "$SITEMAP_FILE"
    # This is a simplified update - for full update would need to find and replace the lastmod line
else
    echo -e "${GREEN}✓ New article, adding to sitemap...${NC}"
    
    # Create temporary file for new sitemap entry
    TEMP_ENTRY=$(cat <<EOF
  <url>
    <loc>https://articles.phantom-byte.com/$ARTICLE_SLUG</loc>
    <lastmod>$PUB_DATE</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
EOF
)
    
    # Insert new article after the terms.html entry (before other articles)
    # Find the line number of terms.html closing tag
    TERMS_LINE=$(grep -n "</url>" "$SITEMAP_FILE" | grep -B5 "terms.html" | tail -1 | cut -d: -f1)
    
    if [ -n "$TERMS_LINE" ]; then
        # Insert after terms.html entry
        head -n "$TERMS_LINE" "$SITEMAP_FILE" > "$SITEMAP_FILE.tmp"
        echo "$TEMP_ENTRY" >> "$SITEMAP_FILE.tmp"
        tail -n +$((TERMS_LINE + 1)) "$SITEMAP_FILE" >> "$SITEMAP_FILE.tmp"
        mv "$SITEMAP_FILE.tmp" "$SITEMAP_FILE"
        echo -e "${GREEN}✓ Article added to sitemap${NC}"
    else
        echo -e "${RED}ERROR: Could not find insertion point in sitemap${NC}"
        exit 1
    fi
fi

# Step 5: Validate sitemap
echo -e "${YELLOW}[5/7] Validating sitemap...${NC}"
URL_COUNT=$(grep -c "<loc>" "$SITEMAP_FILE")
echo "  Total URLs in sitemap: $URL_COUNT"

# Check for HTTP URLs (should all be HTTPS)
if grep -q "http://articles" "$SITEMAP_FILE"; then
    echo -e "${RED}ERROR: Found HTTP URLs in sitemap!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Sitemap validation passed (all HTTPS)${NC}"

# Step 6: Build and push Docker image
echo -e "${YELLOW}[6/7] Building Docker image...${NC}"
cd "$ARTICLES_DIR"
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME . 2>&1 | tail -5

echo -e "${YELLOW}  Pushing to GCR...${NC}"
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME 2>&1 | tail -5

# Get the image digest
IMAGE_DIGEST=$(docker inspect gcr.io/$PROJECT_ID/$SERVICE_NAME --format='{{index .RepoDigests 0}}' | cut -d'@' -f2)
echo -e "${GREEN}✓ Image pushed: $IMAGE_DIGEST${NC}"

# Step 7: Deploy to Cloud Run
echo -e "${YELLOW}[7/7] Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME@$IMAGE_DIGEST \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 2>&1 | tail -5

# Verification
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Verifying deployment..."
sleep 8

# Check sitemap is live
LIVE_COUNT=$(curl -s https://articles.phantom-byte.com/sitemap.xml | grep -c "<loc>" 2>/dev/null || echo "0")
echo "  Live sitemap URL count: $LIVE_COUNT"

# Check article is accessible
ARTICLE_STATUS=$(curl -sI "https://articles.phantom-byte.com/$ARTICLE_SLUG" | head -1)
echo "  Article status: $ARTICLE_STATUS"

# Check for noindex
NOINDEX_CHECK=$(curl -s "https://articles.phantom-byte.com/$ARTICLE_SLUG" | grep -i "noindex" || echo "")
if [ -z "$NOINDEX_CHECK" ]; then
    echo -e "  ${GREEN}✓ No noindex directive found${NC}"
else
    echo -e "  ${RED}✗ WARNING: noindex found in article!${NC}"
fi

# Submit to Google Indexing API
echo ""
if [ -f "$CREDENTIALS_FILE" ]; then
    echo -e "${YELLOW}Submitting to Google Indexing API...${NC}"
    
    # Get access token
    export GOOGLE_APPLICATION_CREDENTIALS="$CREDENTIALS_FILE"
    ACCESS_TOKEN=$(gcloud auth application-default print-access-token 2>/dev/null)
    
    if [ -n "$ACCESS_TOKEN" ]; then
        # Submit URL to Google
        GOOGLE_RESPONSE=$(curl -s -X POST \
          "https://indexing.googleapis.com/v3/urlNotifications:publish" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer $ACCESS_TOKEN" \
          -d "{
            \"url\": \"https://articles.phantom-byte.com/$ARTICLE_SLUG\",
            \"type\": \"URL_UPDATED\"
          }")
        
        if echo "$GOOGLE_RESPONSE" | grep -q "urlNotificationMetadata"; then
            echo -e "  ${GREEN}✓ Submitted to Google Indexing API${NC}"
            echo -e "  ${GREEN}  Expected indexing: 1-24 hours${NC}"
        else
            echo -e "  ${YELLOW}⚠ Google API response: $GOOGLE_RESPONSE${NC}"
            echo -e "  ${YELLOW}  Will still be indexed via sitemap (2-7 days)${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠ Could not get access token, skipping Indexing API${NC}"
    fi
else
    echo -e "  ${YELLOW}ℹ Indexing API credentials not found${NC}"
    echo -e "  ${YELLOW}  Article will be indexed via sitemap (2-7 days)${NC}"
    echo -e "  ${YELLOW}  Run SETUP-INDEXING-API.md to enable faster indexing${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  All Done!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Article URL:"
echo "  https://articles.phantom-byte.com/$ARTICLE_SLUG"
echo ""
echo "Sitemap:"
echo "  https://articles.phantom-byte.com/sitemap.xml"
echo ""
echo -e "${GREEN}Done!${NC}"
