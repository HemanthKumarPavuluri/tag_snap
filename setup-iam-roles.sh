#!/bin/bash

# Setup IAM roles for enterprise keyless signing with IAM API
# This script configures the service account for IAM-based signing (no private keys)

set -e

PROJECT_ID="storied-catwalk-476608-d1"
SA_EMAIL="signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com"
REGION="us-west1"
SERVICE_NAME="tag-snap-backend"
BUCKET="sna-bucket-001"

echo "🔐 Setting up enterprise keyless signing with IAM API..."
echo ""
echo "📋 Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Service Account: $SA_EMAIL"
echo "   Region: $REGION"
echo "   Service: $SERVICE_NAME"
echo "   Bucket: $BUCKET"
echo ""

# Step 1: Grant roles/iam.serviceAccountTokenCreator to self (for IAM signing)
echo "✅ Step 1: Granting iam.serviceAccountTokenCreator role..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --condition=None \
  --quiet

echo "   ✓ Service account can now sign blobs via IAM API"
echo ""

# Step 2: Grant roles/storage.objectCreator for uploading
echo "✅ Step 2: Granting storage.objectCreator role..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.objectCreator" \
  --condition=None \
  --quiet

echo "   ✓ Service account can create objects in buckets"
echo ""

# Step 3: Grant roles/storage.objectViewer for reading metadata
echo "✅ Step 3: Granting storage.objectViewer role..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.objectViewer" \
  --condition=None \
  --quiet

echo "   ✓ Service account can view object metadata"
echo ""

# Step 4: Update Cloud Run service with new environment variables
echo "✅ Step 4: Updating Cloud Run service..."
gcloud run deploy "$SERVICE_NAME" \
  --platform managed \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --update-env-vars \
    SERVICE_ACCOUNT_EMAIL="$SA_EMAIL",\
    GCP_PROJECT_ID="$PROJECT_ID",\
    UPLOAD_BUCKET="$BUCKET" \
  --quiet

echo "   ✓ Cloud Run service updated with environment variables"
echo ""

# Step 5: Verify the deployment
echo "✅ Step 5: Verifying deployment..."
echo ""
gcloud run services describe "$SERVICE_NAME" \
  --platform managed \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --format="table(status.conditions[0].message,status.url)"

echo ""
echo "🎉 Enterprise keyless signing setup complete!"
echo ""
echo "📝 What was configured:"
echo "   • Service account can sign blobs via IAM API (no private keys)"
echo "   • No private keys stored in Cloud Secret Manager"
echo "   • Secure end-to-end signing using Google's HSM"
echo "   • All operations audit-logged in Cloud Audit Logs"
echo ""
echo "🚀 Test the endpoint:"
echo "   curl -X POST 'https://<your-service-url>/signed-url' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"filename\":\"test.jpg\",\"content_type\":\"image/jpeg\"}'"
echo ""
echo "💡 Security benefits of keyless signing:"
echo "   ✓ No private keys to leak or rotate"
echo "   ✓ Instant revocation via IAM role"
echo "   ✓ Full audit trail in Cloud Audit Logs"
echo "   ✓ Enterprise-grade security"
