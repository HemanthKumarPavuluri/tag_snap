This small backend exposes a FastAPI endpoint that returns V4 signed PUT URLs for uploading images to a GCS bucket.

## How it works

- Endpoint: `POST /signed-url`
- Request JSON: `{ "filename": "optional-name.jpg", "content_type": "image/jpeg", "expires_minutes": 15 }`
- Response: `{ url, method: "PUT", blob_name, content_type, expires_at }`

## Two Implementation Approaches

### Approach 1: Private Key in Secret (Recommended) ✅ WORKING
Uses the service account's private key mounted as a Cloud Secret. Most reliable and straightforward.

**Setup:**
1. Create a service account key:
   ```bash
   gcloud iam service-accounts keys create sa-key.json \
     --iam-account=signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com
   ```

2. Create Cloud Secret:
   ```bash
   gcloud secrets create signed-url-sa-key --data-file=sa-key.json
   ```

3. Grant service account access to the secret:
   ```bash
   gcloud secrets add-iam-policy-binding signed-url-sa-key \
     --member=serviceAccount:signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com \
     --role=roles/secretmanager.secretAccessor
   ```

4. Deploy with secret:
   ```bash
   gcloud run deploy tag-snap-backend \
     --image gcr.io/storied-catwalk-476608-d1/tag-snap-backend:latest \
     --update-secrets=SERVICE_ACCOUNT_KEY_JSON=signed-url-sa-key:latest
   ```

### Approach 2: IAM-Based Keyless Signing (In Development)
Uses the IAM API to sign URLs without storing a private key. More secure but requires additional setup.

**Status:** Requires further implementation — the `google.auth.iam.Signer` API needs specific authorization patterns that are still being tested.

## IAM Roles Required

Grant the service account:
- `roles/storage.objectCreator` — write objects to bucket
- `roles/storage.objectViewer` — read object metadata
- `roles/iam.serviceAccountTokenCreator` — for IAM-based signing (Approach 2)

## Cloud Run Deployment (Project: storied-catwalk-476608-d1)

1. **Build image** (using Cloud Build):
   ```bash
   gcloud builds submit --tag gcr.io/storied-catwalk-476608-d1/tag-snap-backend backend/
   ```

2. **Deploy to Cloud Run** (with secret for Approach 1):
   ```bash
   gcloud run deploy tag-snap-backend \
     --image gcr.io/storied-catwalk-476608-d1/tag-snap-backend:latest \
     --platform managed \
     --region us-west1 \
     --project storied-catwalk-476608-d1 \
     --allow-unauthenticated \
     --service-account signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com \
     --update-secrets=SERVICE_ACCOUNT_KEY_JSON=signed-url-sa-key:latest
   ```

## Local Development

Set credentials for local testing:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/sa-key.json"
export UPLOAD_BUCKET="sna-bucket-001"

# Run locally
python -m backend.main
```

Test the endpoint:
```bash
curl -X POST "http://localhost:8080/signed-url" \
  -H "Content-Type: application/json" \
  -d '{"filename":"test.jpg","content_type":"image/jpeg"}'
```

## Client Upload Flow

1. **Request signed URL** from backend:
   ```bash
   curl -X POST "https://<cloud-run-url>/signed-url" \
     -H "Content-Type: application/json" \
     -d '{"filename":"image.jpg","content_type":"image/jpeg"}'
   ```

2. **Upload file** using the signed URL:
   ```bash
   curl -X PUT "<signed-url-from-response>" \
     -H "Content-Type: image/jpeg" \
     --data-binary @image.jpg
   ```

The file is now in `gs://sna-bucket-001/image.jpg`!

## Architecture

- **Framework:** FastAPI + Uvicorn
- **Container:** Docker (Python 3.12 slim)
- **Auth:** Google Cloud service account
- **Signing:** V4 signed URLs (RSA-SHA256)
- **Expiry:** Configurable (default 15 minutes)
