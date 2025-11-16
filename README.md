# tag_snap - GCS V4 Signed URL Backend

Enterprise-grade backend for generating Google Cloud Storage V4 signed URLs using keyless signing via IAM Credentials API.

---

## 📚 Documentation Journey

### Phase 1: Foundation & Architecture
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Overview of the project objectives and architecture
- **[KEYLESS_SIGNING_QUICK_REFERENCE.md](KEYLESS_SIGNING_QUICK_REFERENCE.md)** - Quick start guide for developers

### Phase 2: Implementation Details
- **[KEYLESS_SIGNING_GUIDE.md](KEYLESS_SIGNING_GUIDE.md)** - Complete technical implementation guide
  - How keyless signing works
  - IAM Credentials API integration
  - V4 signed URL generation process
  - Security architecture

### Phase 3: Debugging & Problem Resolution
- **[SIGNATURE_FIX_NOTES.md](SIGNATURE_FIX_NOTES.md)** - Root cause analysis and fixes for signature validation
  - Issue #1: Signature encoding format (base64 vs hex)
  - Issue #2: IAM response field name (`signedBlob` vs `signature`)
  - Issue #3: Cloud Run service account identity configuration
  - Critical implementation details discovered

### Phase 4: Deployment & Verification
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Final implementation status and test results
  - ✅ All tests passing
  - ✅ Files successfully uploaded to GCS
  - ✅ Production-ready status

### Phase 5: Operational Guides
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Step-by-step deployment instructions
- **[backend/README.md](backend/README.md)** - API endpoint documentation

---

## 🔑 Key Concepts

### Keyless Signing (Current Implementation)
Private keys **never leave Google's Hardware Security Modules**. All signing happens remotely via IAM API.

**Benefits:**
- Zero private key exposure
- Full audit trail of all operations
- Instant revocation via IAM roles
- Zero key rotation overhead

**Architecture:**
```
Client Request
    ↓
Backend (/signed-url endpoint)
    ↓
IAM Credentials API (signBlob)
    ↓
Google's HSM (signs with service account key)
    ↓
Backend receives signature (never touches key)
    ↓
V4 Signed URL returned
    ↓
Client uploads directly to GCS
```

---

## 🚀 Quick Start

### Generate a Signed URL
```bash
curl -X POST "https://signed-url-service-354516928175.us-west1.run.app/signed-url" \
  -H "Content-Type: application/json" \
  -d '{"filename":"image.jpg","content_type":"image/jpeg","expires_minutes":15}' | jq .
```

### Upload a File
```bash
# Get signed URL
SIGNED_URL=$(curl -s -X POST "https://signed-url-service-354516928175.us-west1.run.app/signed-url" \
  -H "Content-Type: application/json" \
  -d '{"filename":"image.jpg","content_type":"image/jpeg"}' | jq -r '.url')

# Upload file
curl -X PUT "$SIGNED_URL" \
  -H "Content-Type: image/jpeg" \
  --data-binary @image.jpg
```

---

## 📋 Critical Implementation Details

### Three Critical Fixes Applied

1. **Signature Encoding** → Must be hex-encoded (not base64) in URL
2. **IAM Response Field** → Use `signedBlob` (not `signature`)
3. **Cloud Run Identity** → Service must run as the signing service account

See [SIGNATURE_FIX_NOTES.md](SIGNATURE_FIX_NOTES.md) for details.

---

## 📂 Project Structure

```
tag_snap/
├── README.md (this file)
├── PROJECT_SUMMARY.md - High-level overview
├── KEYLESS_SIGNING_GUIDE.md - Technical deep dive
├── KEYLESS_SIGNING_QUICK_REFERENCE.md - Developer quick start
├── SIGNATURE_FIX_NOTES.md - Bug fixes & solutions
├── IMPLEMENTATION_COMPLETE.md - Final status
├── DEPLOYMENT_GUIDE.md - Deployment instructions
├── setup-iam-roles.sh - IAM configuration automation
└── backend/
    ├── signed_urls.py - Main implementation
    ├── main.py - FastAPI app
    ├── README.md - API documentation
    ├── Dockerfile - Container config
    └── requirements.txt - Dependencies
```

---

## ✅ Verification Status

**All systems operational:**
- ✅ Signed URL generation working
- ✅ Signature validation passing
- ✅ Direct GCS uploads successful (HTTP 200)
- ✅ Files verified in bucket
- ✅ Enterprise security posture achieved

**Files successfully uploaded:**
- test-final-upload.jpg
- test-image-real.jpg
- test-image-with-content.jpg
- test-image-with-text.jpg
- test-final-validation.txt

---

## 🔗 Services Deployed

| Service | URL | Status |
|---------|-----|--------|
| signed-url-service | https://signed-url-service-354516928175.us-west1.run.app | ✅ Working |
| tag-snap-backend | https://tag-snap-backend-354516928175.us-west1.run.app | ⚠️ Old code |

**Note:** Use `signed-url-service` (has all fixes). `tag-snap-backend` has older buggy code.

---

## 📖 Where to Start

1. **First time?** → Read [KEYLESS_SIGNING_QUICK_REFERENCE.md](KEYLESS_SIGNING_QUICK_REFERENCE.md)
2. **Need details?** → Read [KEYLESS_SIGNING_GUIDE.md](KEYLESS_SIGNING_GUIDE.md)
3. **Deploying?** → Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
4. **Troubleshooting?** → Read [SIGNATURE_FIX_NOTES.md](SIGNATURE_FIX_NOTES.md)
5. **Using the API?** → Read [backend/README.md](backend/README.md)

---

## 🛠️ Technologies

- **Framework**: FastAPI (Python)
- **Signing**: Google IAM Credentials API (keyless)
- **Storage**: Google Cloud Storage
- **Deployment**: Cloud Run
- **Protocol**: V4 Signed URLs (RFC-compliant)
- **Cryptography**: RSA-2048-SHA256
