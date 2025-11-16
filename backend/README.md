This small backend exposes a FastAPI endpoint that returns V4 signed PUT URLs for uploading images to a GCS bucket.

## How it works

- Endpoint: `POST /signed-url`
- Request JSON: `{ "filename": "optional-name.jpg", "content_type": "image/jpeg", "expires_minutes": 15 }`
- Response: `{ url, method: "PUT", blob_name, content_type, expires_at }`

## Implementation: Enterprise Keyless Signing ✅ WORKING

The current implementation uses **enterprise-grade keyless signing** via Google's IAM Credentials API:

**Security Benefits:**
- ✓ No private keys in memory or on disk
- ✓ Keys remain in Google's Hardware Security Modules (HSM)
- ✓ Full audit trail of all signing operations
- ✓ Instant revocation via IAM role changes
- ✓ Zero key rotation overhead

**How It Works:**
1. Backend calls IAM Credentials `signBlob` API
2. Payload (string-to-sign) is sent base64-encoded
3. Google signs the payload with the service account's key (never exposed)
4. Signature returned as base64, decoded to bytes, then hex-encoded for URL
5. Final signed URL ready for client uploads

**Setup:**
1. Create service account for signing:
   ```bash
   gcloud iam service-accounts create signed-url
   ```

2. Grant necessary roles:
   ```bash
   # Allow signing operations
   gcloud iam service-accounts add-iam-policy-binding \
     signed-url@PROJECT_ID.iam.gserviceaccount.com \
     --member=serviceAccount:signed-url@PROJECT_ID.iam.gserviceaccount.com \
     --role=roles/iam.serviceAccountTokenCreator
   
   # Allow bucket operations
   gsutil iam ch serviceAccount:signed-url@PROJECT_ID.iam.gserviceaccount.com:objectCreator,objectViewer gs://YOUR_BUCKET
   ```

3. Configure Cloud Run service identity:
   ```bash
   gcloud run services update signed-url-service \
     --region us-west1 \
     --service-account=signed-url@PROJECT_ID.iam.gserviceaccount.com
   ```

4. Deploy:
   ```bash
   gcloud run deploy signed-url-service --source . \
     --region us-west1 \
     --set-env-vars SERVICE_ACCOUNT_EMAIL=signed-url@PROJECT_ID.iam.gserviceaccount.com,UPLOAD_BUCKET=your-bucket
   ```

## Critical Implementation Details

1. **Signature Encoding:** Signatures must be **hex-encoded** (not base64) in the X-Goog-Signature URL parameter
   ```python
   signature_hex = signature_bytes.hex()  # Correct
   ```

2. **signBlob Response Field:** The IAM API returns signatures in the `signedBlob` field (not `signature`)
   ```python
   signature_b64 = response.json()['signedBlob']  # Correct
   ```

3. **Cloud Run Identity:** The Cloud Run service MUST run as a service account with permission to call signBlob on the target service account

## IAM Roles Required

- `roles/iam.serviceAccountTokenCreator` — to call IAM signBlob API
- `roles/storage.objectCreator` — to write objects to bucket
- `roles/storage.objectViewer` — to read object metadata


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
