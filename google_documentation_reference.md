# Google Documentation Reference

Complete guide to all essential Google Cloud documentation needed to understand and maintain the tag_snap keyless signing backend.

---

## 📖 Core Documentation by Topic

### 1. Cloud Storage - Signed URLs (Foundation)

**V4 Signed URLs Overview**
- https://cloud.google.com/storage/docs/access-control/signed-urls
- Learn what signed URLs are and when to use them
- Understand the V4 signing process

**Creating Signed URLs Manually** ⭐ **CRITICAL**
- https://cloud.google.com/storage/docs/access-control/signing-urls-manually
- Step-by-step guide to building V4 signed URLs
- How to construct canonical requests
- String-to-sign format
- Signature calculation

**Canonical Requests Format** ⭐ **CRITICAL**
- https://cloud.google.com/storage/docs/authentication/canonical-requests
- Exact format for building canonical requests
- Header formatting rules
- Query parameter ordering
- Blank line requirements

**Creating Signatures** ⭐ **CRITICAL**
- https://cloud.google.com/storage/docs/authentication/creating-signatures
- How to call the IAM signBlob method
- Response format (uses `signedBlob` field)
- Base64 encoding/decoding of payloads
- Hex encoding requirements for URL parameters

**Signatures Overview**
- https://cloud.google.com/storage/docs/authentication/signatures
- Overview of signature types
- Credential scope explained
- String-to-sign components

---

### 2. IAM Credentials API (Keyless Signing)

**IAM Credentials API Documentation** ⭐ **CRITICAL**
- https://cloud.google.com/iam/docs/reference/credentials/rest/v1/projects.serviceAccounts/signBlob
- Complete REST API reference for signBlob
- Request/response format
- Authentication requirements
- Error handling

**signBlob Method Reference** ⭐ **CRITICAL**
- https://cloud.google.com/iam/docs/reference/credentials/rest/v1/projects.serviceAccounts/signBlob
- Endpoint: `https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{email}:signBlob`
- Request body: `{"payload": "base64-encoded-string"}`
- Response body: `{"keyId": "...", "signedBlob": "base64-encoded-signature"}`

**Service Accounts Overview**
- https://cloud.google.com/iam/docs/service-accounts
- What service accounts are
- How to create and manage them
- Service account credentials types

**Service Account Keys**
- https://cloud.google.com/iam/docs/service-account-creds
- Key types (Google-managed vs user-managed)
- Key rotation concepts
- Security best practices

**Using Service Accounts with gcloud**
- https://cloud.google.com/iam/docs/creating-managing-service-accounts
- How to create service accounts
- Grant roles to service accounts
- List and manage service accounts

---

### 3. Cloud Run (Deployment)

**Cloud Run Documentation**
- https://cloud.google.com/run/docs
- Overview of Cloud Run
- How it works
- Pricing and quotas

**Deploying from Source Code** ⭐ **IMPORTANT**
- https://cloud.google.com/run/docs/quickstarts/build-and-deploy
- Deploy directly from repository
- Dockerfile requirements
- Build process

**Service Identity & Access Control** ⭐ **CRITICAL**
- https://cloud.google.com/run/docs/securing/service-identity
- How to configure which service account runs your service
- Identity binding
- Default vs custom service accounts

**Environment Variables** ⭐ **IMPORTANT**
- https://cloud.google.com/run/docs/configuring/environment-variables
- Setting env vars at deployment
- Using Cloud Secrets for sensitive data
- Accessing env vars in code

**IAM for Cloud Run**
- https://cloud.google.com/run/docs/securing/managing-access
- Who can invoke your service
- Public vs authenticated services
- Service account permissions

---

### 4. IAM & Access Control

**Understanding IAM**
- https://cloud.google.com/iam/docs/understanding-custom-roles
- IAM fundamentals
- Roles and permissions
- Service account service identity

**Predefined Roles Reference**
- https://cloud.google.com/iam/docs/understanding-roles
- List of all built-in roles
- Permission descriptions

**Storage IAM Roles** ⭐ **IMPORTANT**
- https://cloud.google.com/storage/docs/access-control/iam-roles

| Role | Purpose | Used For |
|------|---------|----------|
| `roles/iam.serviceAccountTokenCreator` | Call IAM signBlob API | Keyless signing permission |
| `roles/storage.objectCreator` | Write objects to bucket | Upload/PUT operations |
| `roles/storage.objectViewer` | Read object metadata | Query object details |
| `roles/storage.admin` | Full bucket access | Administrative operations |

**Granting IAM Roles**
- https://cloud.google.com/iam/docs/granting-changing-revoking-access
- How to grant roles to service accounts
- Using gcloud commands
- Policy binding syntax

**Service Account Impersonation**
- https://cloud.google.com/iam/docs/impersonating-service-accounts
- How one account can act as another
- Delegation patterns

---

### 5. Google Cloud Client Libraries

**google-auth Library (Python)** ⭐ **USED IN PROJECT**
- https://google-auth.readthedocs.io/
- Authentication and credentials
- Application Default Credentials (ADC)
- Creating access tokens
- Refreshing credentials

**google-cloud-storage Library**
- https://cloud.google.com/python/docs/reference/storage/latest
- Python client for Cloud Storage
- Upload/download objects
- Bucket management

**google-cloud-iam Library**
- https://cloud.google.com/python/docs/reference/google-cloud-iam/latest
- IAM management in Python
- Service account operations

**Using HTTP Requests to IAM API**
- https://cloud.google.com/iam/docs/reference/credentials/rest
- Direct REST API calls
- Manual HTTP request examples
- Authentication headers

---

### 6. Cryptography & Security Standards

**V4 Signing Algorithm** ⭐ **CRITICAL**
- https://cloud.google.com/storage/docs/authentication/signatures#signature-algorithm
- RSA-2048-SHA256 explained
- Key size requirements
- Hash algorithm specifications

**RFC 3986 - URI Generic Syntax**
- https://tools.ietf.org/html/rfc3986
- URL encoding rules
- Reserved characters
- Percent-encoding requirements

**Understanding HMAC Keys (Alternative)**
- https://cloud.google.com/storage/docs/authentication/hmackeys
- Alternative to service accounts
- Use cases
- Not recommended for new projects

---

### 7. Cloud Audit Logs (Debugging)

**Cloud Audit Logs Overview** ⭐ **IMPORTANT FOR DEBUGGING**
- https://cloud.google.com/logging/docs/audit
- What operations are logged
- Log entry structure
- How to access audit logs

**Querying Audit Logs** ⭐ **IMPORTANT FOR DEBUGGING**
- https://cloud.google.com/logging/docs/audit/query-examples
- Query syntax
- Filtering examples
- Finding specific operations

**IAM Activity Logging**
- https://cloud.google.com/iam/docs/audit-logging
- Service account activity
- SignBlob operation logs
- Role grant/revoke logs

**Cloud Logging Query Language**
- https://cloud.google.com/logging/docs/logging-query-language
- Advanced query syntax
- Filtering and aggregation
- Time-based searches

---

### 8. Google Cloud CLI (gcloud)

**gcloud CLI Overview**
- https://cloud.google.com/cli/docs
- Installation and setup
- Configuration
- Authentication

**gcloud run deploy** ⭐ **USED IN DEPLOYMENT**
- https://cloud.google.com/run/docs/gcloud-reference/run-deploy
- Deploy services to Cloud Run
- Environment variables
- Service account configuration
- Region selection

**gcloud iam service-accounts** ⭐ **USED IN SETUP**
- https://cloud.google.com/cli/docs/gcloud-reference/iam/service-accounts
- Create service accounts: `gcloud iam service-accounts create`
- Add IAM binding: `gcloud iam service-accounts add-iam-policy-binding`
- List accounts: `gcloud iam service-accounts list`

**gcloud logging read** ⭐ **USED IN DEBUGGING**
- https://cloud.google.com/cli/docs/gcloud-reference/logging/read
- Query Cloud Logs
- Filter options
- Output formatting

**gsutil** ⭐ **USED FOR STORAGE**
- https://cloud.google.com/storage/docs/gsutil
- `gsutil ls` - list buckets/objects
- `gsutil cp` - copy objects
- `gsutil iam` - manage IAM on buckets

---

## 🎯 Documentation by Use Case

### "I want to understand how V4 signed URLs work"
1. Read: https://cloud.google.com/storage/docs/access-control/signed-urls
2. Deep dive: https://cloud.google.com/storage/docs/access-control/signing-urls-manually
3. Reference: https://cloud.google.com/storage/docs/authentication/canonical-requests

### "I want to implement keyless signing"
1. Start: https://cloud.google.com/iam/docs/service-accounts
2. API docs: https://cloud.google.com/iam/docs/reference/credentials/rest/v1/projects.serviceAccounts/signBlob
3. Implementation: https://cloud.google.com/storage/docs/authentication/creating-signatures

### "I want to deploy to Cloud Run"
1. Basics: https://cloud.google.com/run/docs/quickstarts/build-and-deploy
2. Identity: https://cloud.google.com/run/docs/securing/service-identity
3. Environment: https://cloud.google.com/run/docs/configuring/environment-variables

### "I need to set up IAM permissions"
1. Overview: https://cloud.google.com/iam/docs/understanding-custom-roles
2. Roles: https://cloud.google.com/storage/docs/access-control/iam-roles
3. Grant: https://cloud.google.com/iam/docs/granting-changing-revoking-access

### "I need to debug signature issues"
1. Canonical requests: https://cloud.google.com/storage/docs/authentication/canonical-requests
2. Creating signatures: https://cloud.google.com/storage/docs/authentication/creating-signatures
3. Audit logs: https://cloud.google.com/logging/docs/audit/query-examples

### "I need to check Cloud Run logs"
1. Read logs: https://cloud.google.com/cli/docs/gcloud-reference/logging/read
2. Query syntax: https://cloud.google.com/logging/docs/logging-query-language
3. Audit logs: https://cloud.google.com/logging/docs/audit

---

## 📋 Critical Implementation Details from Docs

### From Canonical Requests Doc
- Headers must be lowercase
- Query parameters must be sorted alphabetically
- Blank line required after headers
- Payload hash format (UNSIGNED-PAYLOAD for object uploads)

### From Creating Signatures Doc
- Response field is `signedBlob` (not `signature`)
- Payload must be base64-encoded when sent to API
- Signature returned as base64-encoded
- **Signature must be hex-encoded in URL** (critical fix!)

### From Service Identity Doc
- Cloud Run service needs explicit service account assignment
- Without it, uses default Compute Engine service account
- Service account must have `iam.serviceAccountTokenCreator` role

### From RFC 3986
- Reserved characters: `:/?#[]@!$&'()*+,;=`
- Percent-encode all reserved characters in query params
- Use `quote(safe='')` for strict encoding

---

## 🔗 Quick Reference URLs

| Component | URL |
|-----------|-----|
| V4 Signed URLs | https://cloud.google.com/storage/docs/access-control/signed-urls |
| Canonical Requests | https://cloud.google.com/storage/docs/authentication/canonical-requests |
| Creating Signatures | https://cloud.google.com/storage/docs/authentication/creating-signatures |
| IAM signBlob API | https://cloud.google.com/iam/docs/reference/credentials/rest/v1/projects.serviceAccounts/signBlob |
| Cloud Run Service Identity | https://cloud.google.com/run/docs/securing/service-identity |
| Storage IAM Roles | https://cloud.google.com/storage/docs/access-control/iam-roles |
| gcloud run deploy | https://cloud.google.com/run/docs/gcloud-reference/run-deploy |
| Cloud Audit Logs | https://cloud.google.com/logging/docs/audit |
| RFC 3986 | https://tools.ietf.org/html/rfc3986 |

---

## ✅ Documentation Checklist

Before deploying to production, review:
- [ ] V4 Signed URLs overview and format
- [ ] Canonical request construction (exact format)
- [ ] Creating signatures via IAM API
- [ ] Service account creation and management
- [ ] Cloud Run service identity configuration
- [ ] IAM roles and permissions
- [ ] Cloud Audit Logs for verification
- [ ] Error handling and troubleshooting

---

## 📝 Notes for Implementation

1. **Always refer to Creating Signatures doc** when debugging signature issues
2. **Service Identity is critical** - Cloud Run must run as correct service account
3. **Canonical format matters** - Even one extra space breaks signatures
4. **Hex encoding is required** - Not base64 for URL parameters
5. **Audit logs are your friend** - Check them when uploads fail
6. **Keep references handy** - Bookmark the 3 critical docs (Canonical, Creating Signatures, Service Identity)
