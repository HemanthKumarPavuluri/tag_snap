# Tag Snap - Complete Implementation Summary

## 🎯 Project Status: ✅ PRODUCTION READY

A FastAPI-based microservice deployed on Google Cloud Run that generates secure V4 signed URLs for direct uploads to Google Cloud Storage.

**Live Endpoint:** https://tag-snap-backend-354516928175.us-west1.run.app/signed-url

---

## 📋 What Was Built

### Service
- **FastAPI REST API** that returns temporary signed URLs
- **Cloud Run deployment** in region `us-west1`
- **Direct GCS uploads** without server intermediary
- **Service-to-service** signing via service account

### Key Features
✅ Generates V4 signed PUT URLs for GCS  
✅ Configurable expiration (default 15 minutes)  
✅ Supports any file type and custom naming  
✅ Secure credential handling via Cloud Secret Manager  
✅ Production-ready error handling  

---

## 📁 Repository Structure

```
tag_snap/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── signed_urls.py             # URL signing logic
│   ├── Dockerfile                 # Container definition
│   ├── requirements.txt           # Python dependencies
│   ├── .dockerignore             # Exclude unneeded files
│   ├── pyproject.toml            # Project metadata
│   ├── README.md                 # User guide
│   ├── IMPLEMENTATION_NOTES.md   # Dev journey & troubleshooting
│   └── ...
├── DEPLOYMENT_GUIDE.md           # Operations guide (this repo root)
└── ...
```

---

## 🚀 Quick Start

### For Users (Requesting Signed URLs)

```bash
# Request a signed URL
curl -X POST "https://tag-snap-backend-354516928175.us-west1.run.app/signed-url" \
  -H "Content-Type: application/json" \
  -d '{"filename":"photo.jpg","content_type":"image/jpeg"}'

# Upload using the returned URL
curl -X PUT "<signed-url>" \
  -H "Content-Type: image/jpeg" \
  --data-binary @photo.jpg
```

### For Operators (Deploying/Maintaining)

```bash
# Deploy new version
cd backend/
gcloud builds submit --tag gcr.io/storied-catwalk-476608-d1/tag-snap-backend \
  --project storied-catwalk-476608-d1

gcloud run deploy tag-snap-backend \
  --image gcr.io/storied-catwalk-476608-d1/tag-snap-backend:latest \
  --platform managed --region us-west1 --project storied-catwalk-476608-d1 \
  --update-secrets=SERVICE_ACCOUNT_KEY_JSON=signed-url-sa-key:latest
```

---

## 🏗️ Architecture Decision: How We Sign URLs

### Problem
Cloud Run's default credentials don't have private keys needed for GCS signing.

### Solution: Two Approaches Explored

| Approach | Status | Why |
|----------|--------|-----|
| **1. Private Key in Secret** | ✅ WORKING | Reliable, uses standard GCS library, easy to implement |
| **2. IAM Keyless Signing** | ❌ FAILED | GCS library doesn't transparently support IAM signing; would need custom implementation |

### Final Implementation
**Approach 1:** Service account key stored in Cloud Secret Manager, mounted as environment variable

**Flow:**
1. Service account key created and stored in Secret Manager
2. Cloud Run mounts secret as `SERVICE_ACCOUNT_KEY_JSON` env var
3. Application parses JSON and creates credentials
4. Uses standard `blob.generate_signed_url()` method
5. Returns signed URL to client

---

## 📚 Documentation

### For Different Audiences

| Document | Audience | Purpose |
|----------|----------|---------|
| `DEPLOYMENT_GUIDE.md` | DevOps/Operators | How to deploy, configure, troubleshoot, monitor |
| `backend/README.md` | Developers | API reference, local development, configuration |
| `backend/IMPLEMENTATION_NOTES.md` | Engineers/Contributors | Full implementation journey, all errors, why solutions work |

---

## 🔍 Implementation Journey

### Phase 1: Local Development ✅
- Built FastAPI endpoint locally
- Tested URL generation
- Set up Docker containerization

### Phase 2: Docker & GCR Push ✅→⚠️→✅
- Built Docker image locally
- Failed: `docker push` without auth → **Solution:** Use `gcloud builds submit`
- Successfully built and pushed image to GCR

### Phase 3: Initial Cloud Run Deployment ✅
- Deployed image to Cloud Run
- Service accessible at endpoint

### Phase 4: First Signing Attempt ❌ (Root Problem Discovered)
- Endpoint returned: "you need a private key"
- **Root Cause:** Cloud Run's Compute Engine credentials are token-based, not key-based
- GCS signing needs private key for cryptographic signature

### Phase 5: Approach 1 - Private Key Secret ✅ (SOLUTION)
**Implementation:**
1. Created service account key
2. Stored in Cloud Secret Manager
3. Mounted as environment variable in Cloud Run
4. Code parses key and creates signing credentials
5. Used standard GCS signing methods

**Result:** ✅ Full end-to-end working

**Test:** Successfully uploaded file to bucket via signed URL

### Phase 6: Approach 2 - Keyless Signing ❌ (Explored)
**Attempted:** Using `google.auth.iam.Signer` for keyless signing via IAM API

**Errors:**
- `Signer.from_service_account_email()` not available in expected form
- Custom `IAMSigner()` constructor failed
- Underlying GCS library still required private key in credentials
- Would need custom signing implementation using IAM API

**Conclusion:** More complex than needed; Approach 1 is better

---

## 🛠️ Technical Stack

```
FastAPI
├── HTTP API Framework
├── Async request handling
└── Data validation (Pydantic)

Google Cloud Libraries
├── google-cloud-storage
├── google-oauth2
└── google-auth

Deployment
├── Docker (containerization)
├── Cloud Build (build & push)
├── Cloud Run (serverless)
├── Cloud Secret Manager (credentials)
└── Cloud Storage (data)

Infrastructure (GCP)
├── Project: storied-catwalk-476608-d1
├── Region: us-west1
├── Bucket: sna-bucket-001
└── Service Account: signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com
```

---

## 📊 Performance & Costs

**Response Time:** ~200-500ms (GCP → GCS API call)

**Monthly Costs (Estimate):**
- Cloud Run: ~$5-20 (very low traffic, generous free tier)
- Cloud Storage: ~$0.05-2 (depends on storage size)
- Cloud Secret Manager: Free for ≤6 secrets
- **Total:** ~$5-22/month

---

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────┐
│         Client Application                  │
│  Requests signed URL → Uploads file        │
└──────────────┬──────────────────────────────┘
               │
               ├─ Req: POST /signed-url
               │
┌──────────────▼──────────────────────────────┐
│     Cloud Run Service                       │
│  • Runs as service account                 │
│  • Reads private key from secret           │
│  • Generates V4 signed URL                │
│  • Returns URL to client                  │
└──────────────┬──────────────────────────────┘
               │
               ├─ Resp: {"url": "...", ...}
               │
┌──────────────▼──────────────────────────────┐
│     Google Cloud Storage                    │
│  • Validates signature in URL              │
│  • Allows PUT upload                        │
│  • Stores file                             │
└─────────────────────────────────────────────┘

Credential Flow:
┌──────────────────────┐
│ Service Account      │
│   private_key.json  │
└──────────┬───────────┘
           │
           ├─ Store encrypted in Secret Manager
           │
┌──────────▼───────────┐
│ Cloud Secret Manager │
│ signed-url-sa-key   │
└──────────┬───────────┘
           │
           ├─ Mount as env var in Cloud Run
           │
┌──────────▼──────────────────┐
│ Cloud Run Service           │
│ SERVICE_ACCOUNT_KEY_JSON    │
│ ↓ (parsed by app)          │
│ Google OAuth2 Credentials   │
│ ↓ (used for signing)        │
│ generate_signed_url()       │
└─────────────────────────────┘
```

---

## 🐛 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "you need a private key" | Secret not mounted | Check `--update-secrets` flag in deployment |
| 403 Forbidden on upload | Wrong Content-Type | Ensure header matches signature |
| Service account missing role | IAM not configured | Grant `storage.objectCreator` role |
| Build fails: package not found | Wrong pip package name | Verify in `requirements.txt` |

---

## ✅ What Worked

1. **Approach 1:** Private key in Cloud Secret Manager ✅
2. **Docker Build:** Using `gcloud builds submit` ✅
3. **Cloud Run Deployment:** Standard deployment with secrets ✅
4. **End-to-End Upload:** Client → Signed URL → GCS ✅
5. **Error Handling:** Proper HTTP error responses ✅

---

## ❌ What Didn't Work

1. **Local docker push to GCR:** Needed `gcloud auth configure-docker` + proper auth
2. **IAM Keyless Signing:** GCS library doesn't support transparent IAM signing
3. **Default Cloud Run Credentials:** Insufficient for cryptographic signing

---

## 📖 For Different Users

### I want to upload files
→ See: `DEPLOYMENT_GUIDE.md` (Quick Reference section)

### I'm deploying this service
→ See: `DEPLOYMENT_GUIDE.md` (Build & Deploy section)

### I'm developing/extending this
→ See: `backend/README.md` (Local Development) + `backend/IMPLEMENTATION_NOTES.md`

### I need to troubleshoot something
→ See: `DEPLOYMENT_GUIDE.md` (Troubleshooting) or `backend/IMPLEMENTATION_NOTES.md`

---

## 🎓 Key Learnings

1. **Cloud Run Credentials:** Token-based by default; signing requires explicit private keys
2. **GCS Signing:** Requires cryptographic keys, not just authorization
3. **Secrets Management:** Cloud Secret Manager is the right place for credentials
4. **Error Messages:** GCS library errors clearly indicate the root cause (missing key)
5. **Cloud Build vs Docker:** Cloud Build handles auth transparently; recommended for GCP

---

## 📞 Support & Maintenance

**Deployment Changes:**
1. Update code in `backend/signed_urls.py`
2. Rebuild: `gcloud builds submit --tag gcr.io/storied-catwalk-476608-d1/tag-snap-backend`
3. Redeploy: Same command as above

**Credentials Rotation:**
1. Create new service account key
2. Update Secret Manager: `gcloud secrets versions add signed-url-sa-key --data-file=new-key.json`
3. Cloud Run automatically uses latest secret version (no redeploy needed!)
4. Delete old key: `gcloud iam service-accounts keys delete <KEY-ID>`

**Monitoring:**
- Check logs: `gcloud run services logs read tag-snap-backend --project storied-catwalk-476608-d1`
- View metrics: Cloud Console → Cloud Run → tag-snap-backend

---

## 🎉 Conclusion

Successfully built and deployed a production-ready signed URL service on Google Cloud Run that securely handles credential management and enables direct GCS uploads from client applications.

**Status:** ✅ **Ready for Production Use**
