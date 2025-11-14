# Tag Snap Backend - Deployment & Operations Guide

## Live Service

**Endpoint:** https://tag-snap-backend-354516928175.us-west1.run.app/signed-url

**Status:** ✅ Production Ready

---

## Quick Reference

### Request a Signed URL
```bash
curl -X POST "https://tag-snap-backend-354516928175.us-west1.run.app/signed-url" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "photo.jpg",
    "content_type": "image/jpeg",
    "expires_minutes": 15
  }'
```

### Response
```json
{
  "url": "https://storage.googleapis.com/sna-bucket-001/photo.jpg?X-Goog-Algorithm=GOOG4-RSA-SHA256&...",
  "method": "PUT",
  "blob_name": "photo.jpg",
  "content_type": "image/jpeg",
  "expires_at": "2025-11-14T07:15:00Z"
}
```

### Upload Using Signed URL
```bash
curl -X PUT "<url-from-response>" \
  -H "Content-Type: image/jpeg" \
  --data-binary @photo.jpg
```

---

## Implementation Details

### What This Service Does
- Generates Google Cloud Storage V4 signed PUT URLs
- Allows direct browser/client uploads to GCS without server intermediary
- Handles authentication via service account key

### Architecture
```
Client
  ↓
[1. Request signed URL] → Backend API
  ↓
Backend generates V4 signed URL
  ↓
[2. Return signed URL] → Client
  ↓
Client uploads directly to GCS using signed URL
  ↓
File stored in gs://sna-bucket-001/
```

### Key Components
- **Framework:** FastAPI (Python)
- **Container:** Docker
- **Deployment:** Google Cloud Run (region: us-west1)
- **Storage:** Google Cloud Storage (bucket: sna-bucket-001)
- **Service Account:** signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com

---

## Configuration

### Environment Variables (Cloud Run)
| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `SERVICE_ACCOUNT_KEY_JSON` | Yes | - | Service account private key (mounted from Secret Manager) |
| `UPLOAD_BUCKET` | No | `sna-bucket-001` | GCS bucket name |
| `PORT` | No | `8080` | HTTP port |

### Service Account Roles
The service account needs these IAM roles:
- `roles/storage.objectCreator` — Create objects in bucket
- `roles/storage.objectViewer` — View object metadata
- `roles/secretmanager.secretAccessor` — Read its own secret key

---

## Build & Deploy

### One-Command Deployment

From `backend/` directory:

```bash
# Build and push image
gcloud builds submit --tag gcr.io/storied-catwalk-476608-d1/tag-snap-backend \
  --project storied-catwalk-476608-d1

# Deploy to Cloud Run (update if service exists)
gcloud run deploy tag-snap-backend \
  --image gcr.io/storied-catwalk-476608-d1/tag-snap-backend:latest \
  --platform managed \
  --region us-west1 \
  --project storied-catwalk-476608-d1 \
  --allow-unauthenticated \
  --service-account signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com \
  --update-secrets=SERVICE_ACCOUNT_KEY_JSON=signed-url-sa-key:latest
```

### Step-by-Step Deployment

**Step 1: Build Docker Image**
```bash
cd backend/
gcloud builds submit --tag gcr.io/storied-catwalk-476608-d1/tag-snap-backend \
  --project storied-catwalk-476608-d1
```

**Step 2: Deploy to Cloud Run**
```bash
gcloud run deploy tag-snap-backend \
  --image gcr.io/storied-catwalk-476608-d1/tag-snap-backend:latest \
  --platform managed \
  --region us-west1 \
  --project storied-catwalk-476608-d1 \
  --allow-unauthenticated
```

**Step 3: Set Service Account**
```bash
gcloud run services update-iam-policy tag-snap-backend \
  --project storied-catwalk-476608-d1 \
  --region us-west1 \
  --member=serviceAccount:signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser
```

**Step 4: Mount Secret**
```bash
gcloud run deploy tag-snap-backend \
  --update-secrets=SERVICE_ACCOUNT_KEY_JSON=signed-url-sa-key:latest \
  --platform managed \
  --region us-west1 \
  --project storied-catwalk-476608-d1
```

---

## Local Development

### Setup
```bash
cd backend/

# Create virtualenv
python3 -m venv .venv
source .venv/bin/activate  # or on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Locally
```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/sa-key.json"

# Run server
python -m backend.main

# Server runs on http://localhost:8080
```

### Test Locally
```bash
curl -X POST "http://localhost:8080/signed-url" \
  -H "Content-Type: application/json" \
  -d '{"filename":"test.jpg","content_type":"image/jpeg"}'
```

---

## Troubleshooting

### 1. Service Returns "you need a private key"
**Cause:** `SERVICE_ACCOUNT_KEY_JSON` secret not mounted

**Solution:**
```bash
gcloud run deploy tag-snap-backend \
  --update-secrets=SERVICE_ACCOUNT_KEY_JSON=signed-url-sa-key:latest \
  --platform managed --region us-west1 --project storied-catwalk-476608-d1
```

### 2. Upload Returns 403 Forbidden
**Cause:** Service account missing Storage Object Creator role

**Solution:**
```bash
gcloud projects add-iam-policy-binding storied-catwalk-476608-d1 \
  --member=serviceAccount:signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com \
  --role=roles/storage.objectCreator
```

### 3. "Credential not found" Locally
**Cause:** `GOOGLE_APPLICATION_CREDENTIALS` not set or path wrong

**Solution:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/sa-key.json"
# Verify file exists
cat $GOOGLE_APPLICATION_CREDENTIALS
```

### 4. Signed URL Upload Fails (403 or 500)
**Cause:** Content-Type mismatch

**Solution:** Ensure the `Content-Type` header in the curl command matches the `content_type` returned in the signed URL response:

```bash
# If response has "content_type": "image/jpeg"
curl -X PUT "<signed-url>" -H "Content-Type: image/jpeg" --data-binary @file.jpg

# Not this:
curl -X PUT "<signed-url>" --data-binary @file.jpg  # Missing Content-Type header
```

### 5. Check Uploaded Files
```bash
# List files in bucket
gsutil ls gs://sna-bucket-001/

# View file details
gsutil stat gs://sna-bucket-001/myfile.jpg

# Download a file
gsutil cp gs://sna-bucket-001/myfile.jpg ./
```

---

## Monitoring & Logs

### View Cloud Run Logs
```bash
# Recent logs
gcloud run services describe tag-snap-backend \
  --platform managed --region us-west1 --project storied-catwalk-476608-d1

# Stream logs
gcloud run services logs read tag-snap-backend \
  --platform managed --region us-west1 --project storied-catwalk-476608-d1 --limit 50 --follow
```

### Check Service Status
```bash
gcloud run services describe tag-snap-backend \
  --platform managed --region us-west1 --project storied-catwalk-476608-d1
```

---

## API Reference

### Endpoint: `POST /signed-url`

**Request Body:**
```json
{
  "filename": "optional.jpg",
  "content_type": "image/jpeg",
  "expires_minutes": 15
}
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `filename` | string | `uuid.hex` + `.jpg` | Object name in bucket |
| `content_type` | string | `image/jpeg` | MIME type for upload |
| `expires_minutes` | number | `15` | URL expiration time |

**Response:**
```json
{
  "url": "https://storage.googleapis.com/...",
  "method": "PUT",
  "blob_name": "optional.jpg",
  "content_type": "image/jpeg",
  "expires_at": "2025-11-14T07:00:00Z"
}
```

**Error Response:**
```json
{
  "detail": "Error description"
}
```

---

## Security Best Practices

1. **Service Account Key:** Stored encrypted in Cloud Secret Manager
   - Rotated periodically (create new key, update secret, delete old key)
   - Only accessible to Cloud Run service

2. **Signed URLs:** Time-limited (default 15 minutes)
   - Cannot be reused after expiration
   - Specific to object and operation (PUT only)

3. **Bucket Permissions:** Least privilege
   - Service account has only Storage Object Creator role
   - Cannot list, delete, or modify other objects

4. **API Access:** Public endpoint but requires valid signature
   - Clients can't forge signatures without the private key
   - Bucket is private; objects are inaccessible without signed URL

---

## For Detailed Implementation History

See `IMPLEMENTATION_NOTES.md` for:
- Complete troubleshooting journey
- Why different approaches failed
- All errors and solutions
- Lessons learned
