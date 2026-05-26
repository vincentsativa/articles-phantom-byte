#!/bin/bash
#
# Test Google Indexing API Setup
# Run this after completing SETUP-INDEXING-API.md steps
#

set -e

CREDENTIALS_FILE="/c/Users/Doter/workspace/articles/google-indexing-credentials.json"
TEST_URL="https://articles.phantom-byte.com/"

echo "=== Testing Google Indexing API Setup ==="
echo ""

# Check if credentials file exists
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "❌ Credentials file not found: $CREDENTIALS_FILE"
    echo ""
    echo "Please complete SETUP-INDEXING-API.md steps first."
    exit 1
fi

echo "✓ Credentials file found"

# Get access token
echo "Requesting access token..."
TOKEN=$(curl -s -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=$(cat $CREDENTIALS_FILE | jq -r '.private_key' | openssl base64 -d 2>/dev/null || echo "error")" \
  "https://oauth2.googleapis.com/token" 2>/dev/null || echo "failed")

# Simpler approach using gcloud
echo "Using gcloud to get access token..."
ACCESS_TOKEN=$(gcloud auth application-default print-access-token 2>/dev/null || echo "failed")

if [ "$ACCESS_TOKEN" == "failed" ] || [ -z "$ACCESS_TOKEN" ]; then
    echo "⚠️  Could not get access token via gcloud"
    echo ""
    echo "Try this manual test instead:"
    echo ""
    echo "1. Set credentials path:"
    echo "   export GOOGLE_APPLICATION_CREDENTIALS='$CREDENTIALS_FILE'"
    echo ""
    echo "2. Test with curl:"
    echo "   curl -X POST 'https://indexing.googleapis.com/v3/urlNotifications:publish' \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -H 'Authorization: Bearer \$(gcloud auth application-default print-access-token)' \\"
    echo "     -d '{\"url\": \"https://articles.phantom-byte.com/\", \"type\": \"URL_UPDATED\"}'"
    exit 1
fi

echo "✓ Access token obtained"

# Test the API
echo "Testing Indexing API..."
RESPONSE=$(curl -s -X POST \
  "https://indexing.googleapis.com/v3/urlNotifications:publish" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"url\": \"$TEST_URL\",
    \"type\": \"URL_UPDATED\"
  }")

echo ""
echo "Response from Google:"
echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"

# Check if successful
if echo "$RESPONSE" | grep -q "urlNotificationMetadata"; then
    echo ""
    echo "✅ SUCCESS! Indexing API is working!"
    echo ""
    echo "The deploy script will now automatically submit new articles to Google."
else
    echo ""
    echo "⚠️  API returned an error. Check SETUP-INDEXING-API.md troubleshooting."
    echo ""
    echo "Common issues:"
    echo "  - Service account doesn't have Owner permission in GSC"
    echo "  - Indexing API not enabled"
    echo "  - Credentials file is invalid"
fi
