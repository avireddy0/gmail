#!/bin/bash
# Gmail Scraper Cloud Run Deployment Script
set -e

# Configuration
PROJECT_ID="claude-mcp-457317"
SERVICE_NAME="gmail-scraper"
REGION="us-central1"
SERVICE_ACCOUNT_EMAIL="claude-service-account@claude-mcp-457317.iam.gserviceaccount.com"
SERVICE_ACCOUNT_KEY_FILE="$HOME/claude-mcp-457317-069a2a199017.json"
ADMIN_EMAIL="avi@envsn.com"

echo "=== Gmail Scraper Cloud Run Deployment ==="
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Step 1: Copy service account key to project directory
echo "Step 1: Copying service account key..."
cp "$SERVICE_ACCOUNT_KEY_FILE" ./service-account-key.json

# Step 2: Build and deploy
echo "Step 2: Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --project=$PROJECT_ID \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --service-account=$SERVICE_ACCOUNT_EMAIL \
  --set-env-vars="PROJECT_ID=$PROJECT_ID,DATASET_ID=gmail_analytics,TABLE_ID=messages,ADMIN_EMAIL=$ADMIN_EMAIL" \
  --timeout=3600 \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=1

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Service URL will be displayed above."
echo ""
echo "To trigger a scrape, use:"
echo "curl -X POST https://YOUR-SERVICE-URL/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"query\": \"after:2024/12/01\", \"max_per_user\": 100}'"
echo ""
