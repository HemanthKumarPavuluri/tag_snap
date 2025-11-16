# Signature Verification Fix - Final Solution

## Problem
The backend was generating signed URLs that GCS rejected with **"SignatureDoesNotMatch" 403 errors**.

## Root Cause Analysis
After extensive debugging and reviewing the Google Cloud documentation, the issue was **not** with:
- ✓ Canonical request format (verified correct)
- ✓ String-to-sign encoding (verified correct)
- ✓ IAM signBlob API functionality (working correctly)
- ✓ URL encoding of query parameters (RFC 3986 compliant)
- ✓ Service account permissions (all correct roles assigned)

The actual problem was a combination of **TWO issues**:

### Issue 1: Wrong Signature Encoding Format
**The Bug:** Signatures were being base64-encoded for the URL parameter.
```python
signature_b64 = base64.b64encode(signature_bytes).decode('ascii')
```

**The Fix:** Per Google V4 signing specification, signatures must be **hex-encoded** in the URL.
```python
signature_hex = signature_bytes.hex()
```

Reference from Google docs: "To complete the signature, ensure the message digest is base64 decoded, and then **hex-encode the message digest**."

### Issue 2: Wrong Response Field Name
**The Bug:** Code was looking for a `signature` field in the signBlob API response.
```python
signature_b64 = result.get('signature', '')  # ← Wrong field name
```

**The Fix:** The signBlob API returns the signature in a field called `signedBlob`.
```python
signature_b64 = result.get('signedBlob', '')  # ← Correct field name
```

Actual response from signBlob API:
```json
{
  "keyId": "19b224fa788558c0e251...",
  "signedBlob": "RaAVSTj5U1qYXkb5wSiCfHhEN7IHixbu..."
}
```

### Issue 3: Cloud Run Service Account Configuration
**The Bug:** The Cloud Run service was running as the default Compute Engine service account, which didn't have permission to call signBlob as the `signed-url` service account.

**The Fix:** Configure the Cloud Run service to run as the `signed-url` service account:
```bash
gcloud run services update signed-url-service \
  --service-account=signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com
```

## Verification
Successfully uploaded multiple test files to GCS using signed URLs:
- test-final-upload.jpg (200 OK)
- test-image-real.jpg (200 OK)
- test-image-with-content.jpg (200 OK)
- test-image-with-text.jpg (200 OK)

All files now appear in the bucket without signature errors.

## Code Changes
- Changed signature encoding from base64 to hex: `base64.b64encode()` → `.hex()`
- Fixed response field name: `result.get('signature')` → `result.get('signedBlob')`
- Configured Cloud Run service account for keyless signing capability

## Lessons Learned
1. Google's documentation specifically states signatures should be hex-encoded in V4 URLs
2. The IAM signBlob API response uses the field name `signedBlob`, not `signature`
3. When using keyless signing (IAM signBlob), the calling service must have the correct IAM role
4. Audit logs are invaluable for debugging - they show the exact payload being signed
