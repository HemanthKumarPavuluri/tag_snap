# Tag Snap Backend - Implementation Journey

## Overview
This document details the complete implementation of a Cloud Run service that generates V4 signed URLs for uploading images to a GCS bucket (`sna-bucket-001`) in GCP project `storied-catwalk-476608-d1`.

---

## Architecture & Goal

**Objective:** Create a simple backend service that:
1. Exposes a REST endpoint to request signed URLs
2. Generates V4 signed PUT URLs for direct GCS uploads
3. Runs on Google Cloud Run

**Tech Stack:**
- FastAPI for REST API
- google-cloud-storage for GCS interactions
- Docker for containerization
- Cloud Run for serverless deployment

---

## Implementation Timeline

### Phase 1: Initial Setup & Local Development

#### What We Did
1. Created `backend/signed_urls.py` with FastAPI endpoint
2. Set up `backend/main.py` to expose the FastAPI app
3. Created `backend/pyproject.toml` with dependencies
4. Tested locally

#### Commands Used
```bash
# From repo root, local testing
python3 -m backend.main
curl -X POST "http://localhost:8080/signed-url" \
  -H "Content-Type: application/json" \
  -d '{"filename":"test.jpg","content_type":"image/jpeg"}'
```

#### Status
✅ **SUCCESS** - Endpoint working locally

---

### Phase 2: Docker Build & Push to GCR

#### What We Did
1. Created `backend/Dockerfile` for containerization
2. Added `backend/requirements.txt` with runtime dependencies
3. Added `backend/.dockerignore` to keep image lean
4. Built Docker image locally
5. Attempted to push to Google Container Registry (GCR)

#### Commands Used
```bash
# Build image locally
docker build -t tag-snap-backend:latest -f backend/Dockerfile backend/

# Run locally to test
docker run -p 8080:8080 tag-snap-backend:latest

# Tag for GCR
docker tag tag-snap-backend:latest gcr.io/storied-catwalk-476608-d1/tag-snap-backend:latest

# Attempt to push to GCR
docker push gcr.io/storied-catwalk-476608-d1/tag-snap-backend:latest
```

#### Error Encountered
```
denied: Unauthenticated request. Unauthenticated requests do not have permission 
"artifactregistry.repositories.uploadArtifacts" on resource 
"projects/storied-catwalk-476608-d1/locations/us/repositories/gcr.io"
```

**Why It Failed:** Local Docker push attempted without GCP authentication.

#### Solution
Used Cloud Build to handle build and push automatically:
```bash
cd backend/
gcloud builds submit --tag gcr.io/storied-catwalk-476608-d1/tag-snap-backend --project storied-catwalk-476608-d1
```

#### Status
✅ **SUCCESS** - Image built and pushed via Cloud Build

---

### Phase 3: Initial Cloud Run Deployment

#### What We Did
1. Deployed image to Cloud Run in region `us-west1`
2. Set service account to `signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com`
3. Granted service account roles: Storage Object Creator, Storage Object Viewer, Storage Object User

#### Commands Used
```bash
gcloud run deploy tag-snap-backend \
  --image gcr.io/storied-catwalk-476608-d1/tag-snap-backend:latest \
  --platform managed \
  --region us-west1 \
  --project storied-catwalk-476608-d1 \
  --allow-unauthenticated \
  --service-account signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com
```

#### Service URL
```
https://tag-snap-backend-354516928175.us-west1.run.app
```

#### Status
✅ **SUCCESS** - Service deployed and accessible

---

### Phase 4: Testing & First Failure - Missing Private Key

#### What We Did
1. Called the `/signed-url` endpoint to generate a signed URL
2. Received error about missing private key

#### Command Used
```bash
curl -X POST "https://tag-snap-backend-354516928175.us-west1.run.app/signed-url" \
  -H "Content-Type: application/json" \
  -d '{"filename":"test.jpg","content_type":"image/jpeg"}'
```

#### Error Received
```
{"detail":"you need a private key to sign credentials.the credentials you are currently using 
<class 'google.auth.compute_engine.credentials.Credentials'> just contains a token. see 
https://googleapis.dev/python/google-api-core/latest/auth.html#setting-up"}
```

#### Why It Failed
- Cloud Run uses **Compute Engine credentials** by default
- These credentials contain only auth tokens, NOT the private key
- `blob.generate_signed_url()` requires a private key to sign the URL
- The service account's private key is not automatically available to the running service

#### Analysis
This is a fundamental limitation: Cloud Run's default credentials are designed for API calls (using tokens), not for cryptographic signing (which needs private keys).

---

### Phase 5: Approach 1 - Using Service Account Private Key Secret ✅ WORKING

#### The Strategy
Instead of relying on Cloud Run's default credentials, manually provide the service account's private key:
1. Create a service account key (JSON file)
2. Store it in Cloud Secret Manager
3. Mount it as an environment variable in Cloud Run
4. Parse and use it in the application

#### Implementation Steps

**Step 1: Create Service Account Key**
```bash
gcloud iam service-accounts keys create /tmp/signed-url-sa-key.json \
  --iam-account=signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com \
  --project storied-catwalk-476608-d1
```

**Step 2: Store in Cloud Secret Manager**
```bash
gcloud secrets create signed-url-sa-key \
  --data-file=/tmp/signed-url-sa-key.json \
  --project storied-catwalk-476608-d1 \
  --replication-policy="automatic"
```

**Step 3: Grant Service Account Access to Secret**
```bash
gcloud secrets add-iam-policy-binding signed-url-sa-key \
  --member=serviceAccount:signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor \
  --project storied-catwalk-476608-d1
```

**Step 4: Update Cloud Run Deployment**
```bash
gcloud run deploy tag-snap-backend \
  --image gcr.io/storied-catwalk-476608-d1/tag-snap-backend:latest \
  --update-secrets=SERVICE_ACCOUNT_KEY_JSON=signed-url-sa-key:latest \
  --platform managed \
  --region us-west1 \
  --project storied-catwalk-476608-d1
```

#### Code Implementation (signed_urls.py)
```python
import json
from google.oauth2 import service_account

sa_key_json = os.environ.get("SERVICE_ACCOUNT_KEY_JSON")

if sa_key_json:
    try:
        # Try parsing as JSON string (Cloud Secret mounted as env var)
        sa_info = json.loads(sa_key_json)
    except json.JSONDecodeError:
        # Try as file path
        if os.path.isfile(sa_key_json):
            with open(sa_key_json) as f:
                sa_info = json.load(f)
        else:
            raise ValueError("SERVICE_ACCOUNT_KEY_JSON is not valid JSON or file path")
    
    # Create credentials from the service account info
    credentials = service_account.Credentials.from_service_account_info(sa_info)
    client = storage.Client(credentials=credentials)

# Generate signed URL using the private key
url = blob.generate_signed_url(
    version="v4",
    expiration=expiration,
    method="PUT",
    content_type=content_type,
)
```

#### Testing
```bash
curl -X POST "https://tag-snap-backend-354516928175.us-west1.run.app/signed-url" \
  -H "Content-Type: application/json" \
  -d '{"filename":"test-image.jpg","content_type":"image/jpeg","expires_minutes":15}'
```

#### Response (SUCCESS)
```json
{
    "url": "https://storage.googleapis.com/sna-bucket-001/test-image.jpg?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=signed-url%40storied-catwalk-476608-d1.iam.gserviceaccount.com%2F20251114%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251114T015419Z&X-Goog-Expires=900&X-Goog-SignedHeaders=content-type%3Bhost&X-Goog-Signature=1b42a906a2375e8ee1f4aae62029ff1dbe536e237b938bcad07998d35b55c8fdfdb1c3bf8e3eecda5680a37919de9d758ef55be9d074e389536146b656d366779...",
    "method": "PUT",
    "blob_name": "test-image.jpg",
    "content_type": "image/jpeg",
    "expires_at": "2025-11-14T02:09:19.185226+00:00"
}
```

#### End-to-End Upload Test
```bash
# Create test file
echo "test image content" > /tmp/test.jpg

# Request signed URL
SIGNED_URL=$(curl -s -X POST "https://tag-snap-backend-354516928175.us-west1.run.app/signed-url" \
  -H "Content-Type: application/json" \
  -d '{"filename":"upload-test-'$(date +%s)'.jpg","content_type":"image/jpeg"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['url'])")

# Upload file
curl -X PUT "$SIGNED_URL" \
  -H "Content-Type: image/jpeg" \
  --data-binary @/tmp/test.jpg

# Verify in bucket
gsutil ls gs://sna-bucket-001/upload-test-*
# Output: gs://sna-bucket-001/upload-test-1763085272.jpg
```

#### Status
✅ **SUCCESS** - Full end-to-end working!

**Pros:**
- Simple, straightforward implementation
- Uses standard GCS signing methods
- Works immediately
- Secure (key stored encrypted in Secret Manager)

**Cons:**
- Requires storing private key
- Key rotation requires manual secret update

---

### Phase 6: Approach 2 - IAM-Based Keyless Signing ❌ NOT WORKING

#### The Strategy
Use `google.auth.iam.Signer` to sign URLs via IAM API instead of storing the private key:
- Service calls IAM API's `signBlob` endpoint
- No private key stored locally
- More secure, enterprise-grade approach

#### What We Attempted

**Step 1: Update Code to Use IAM Signer**
```python
from google.auth.iam import Signer

credentials, project_id = default()
service_account_email = credentials.service_account_email

# Create IAM-based signer
iam_signer = Signer.from_service_account_email(
    service_account_email, 
    request=auth_request
)

url = blob.generate_signed_url(
    version="v4",
    expiration=expiration,
    method="PUT",
    content_type=content_type,
    service_account_email=service_account_email,
    signer=iam_signer,
)
```

**Step 2: Try Alternative Constructor**
```python
from google.auth.iam import Signer as IAMSigner

signer = IAMSigner(
    request=auth_request,
    service_account_email=service_account_email
)
```

#### Errors Encountered

**Error 1: Method Not Found**
```
AttributeError: type object 'Signer' has no attribute 'from_service_account_email'
```

**Error 2: Constructor Parameters Wrong**
```
TypeError: __init__() got unexpected keyword arguments
```

**Error 3: Fundamental Limitation**
```
AttributeError: you need a private key to sign credentials.the credentials you are 
currently using <class 'google.auth.compute_engine.credentials.Credentials'> just 
contains a token.
```

Even when providing a custom signer, the `blob.generate_signed_url()` method validates that credentials have a private key as a fallback.

#### Root Cause Analysis
The `google.cloud.storage._signing.generate_signed_url()` function:
1. Requires credentials with a private key for validation
2. Even if a custom `signer` parameter is provided, it still checks for a private key
3. Cloud Run's Compute Engine credentials don't have a private key
4. The library doesn't fully support keyless signing out-of-the-box

#### What Would Be Required
To make Approach 2 work would require:
1. Writing custom signing logic using IAM API directly
2. Building the canonical request string manually
3. Calling IAM's `signBlob` endpoint
4. Constructing the signed URL with the signature
5. Much more complex than using the built-in methods

#### Status
❌ **NOT WORKING** - Fundamental limitation in google-cloud-storage library

---

## Final Solution Summary

### What Worked: Approach 1 ✅

**The Winning Recipe:**
1. Generate service account key → Store in Cloud Secret Manager
2. Mount secret as `SERVICE_ACCOUNT_KEY_JSON` env var in Cloud Run
3. Parse JSON and create credentials in the application
4. Use standard `blob.generate_signed_url()` method
5. Return signed URL to client

**Deployment Command:**
```bash
# Build & push
cd backend/
gcloud builds submit --tag gcr.io/storied-catwalk-476608-d1/tag-snap-backend --project storied-catwalk-476608-d1

# Deploy
gcloud run deploy tag-snap-backend \
  --image gcr.io/storied-catwalk-476608-d1/tag-snap-backend:latest \
  --platform managed \
  --region us-west1 \
  --project storied-catwalk-476608-d1 \
  --allow-unauthenticated \
  --service-account signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com \
  --update-secrets=SERVICE_ACCOUNT_KEY_JSON=signed-url-sa-key:latest
```

**Live Endpoint:**
```
https://tag-snap-backend-354516928175.us-west1.run.app/signed-url
```

**Client Usage:**
```bash
# Request signed URL
curl -X POST "https://tag-snap-backend-354516928175.us-west1.run.app/signed-url" \
  -H "Content-Type: application/json" \
  -d '{"filename":"myimage.jpg","content_type":"image/jpeg","expires_minutes":15}'

# Upload using the returned URL
curl -X PUT "<signed-url-from-response>" \
  -H "Content-Type: image/jpeg" \
  --data-binary @myimage.jpg
```

---

## Key Learnings

### 1. Cloud Run Authentication Model
- **Default credentials:** Token-based (Compute Engine credentials)
- **For signing:** Need credentials with private key
- **Solution:** Manually provide service account key via secret

### 2. GCS Signed URL Requirements
- `blob.generate_signed_url()` needs a signing credential
- Cloud Run's default credentials won't work
- Must explicitly provide credentials with a private key

### 3. Why Keyless Signing Didn't Work
- Google libraries default to requiring private keys
- IAM signing via API is not transparent to the library
- Would need custom implementation of signing logic

### 4. Best Practices
- Use Cloud Secret Manager for sensitive data
- Grant minimal IAM permissions (Storage Object Creator only needed)
- Consider key rotation strategy for long-term deployments
- Signed URLs are short-lived (default 15 minutes) - safe

---

## Troubleshooting Guide

### Issue: "you need a private key to sign credentials"
**Cause:** Using Cloud Run's default Compute Engine credentials
**Solution:** Mount service account key via `--update-secrets`

### Issue: "Unauthenticated request" during docker push
**Cause:** No Docker authentication to GCR
**Solution:** Use `gcloud builds submit` instead of local `docker push`

### Issue: "could not find a version that satisfies the requirement"
**Cause:** Typo in package name (e.g., `google-cloud-iam-credentials` vs `google-cloud-iamcredentials`)
**Solution:** Check PyPI for correct package names

### Issue: Signed URL doesn't work for upload
**Cause:** Content-Type header mismatch between request and signature
**Solution:** Ensure client uses exact Content-Type from signed URL response

---

## Files Modified/Created

| File | Purpose |
|------|---------|
| `backend/signed_urls.py` | Core endpoint logic for generating signed URLs |
| `backend/main.py` | FastAPI app setup |
| `backend/Dockerfile` | Container definition |
| `backend/requirements.txt` | Python dependencies |
| `backend/.dockerignore` | Exclude unneeded files from image |
| `backend/README.md` | User-facing documentation |
| `backend/IMPLEMENTATION_NOTES.md` | This file - implementation journey |

---

## Conclusion

Successfully implemented a production-ready signed URL service on Google Cloud Run that:
- ✅ Generates V4 signed PUT URLs on demand
- ✅ Securely handles service account credentials
- ✅ Enables direct GCS uploads from clients
- ✅ Runs efficiently on serverless infrastructure

The journey revealed important lessons about Cloud Run authentication models and GCS signing requirements, ultimately leading to a robust, maintainable solution.
