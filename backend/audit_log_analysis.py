#!/usr/bin/env python3
"""
Check the signBlob API documentation to see if we need to specify the hash algorithm.

From Google IAM Credentials API docs:
https://cloud.google.com/docs/authentication/client-libraries

The signBlob API actually supports specifying the algorithm!
"""

print("""
KEY INSIGHT FROM AUDIT LOG:
The request shows we're calling:
  iamcredentials.googleapis.com/SignBlob

The API endpoint supports specifying which algorithm to use.

For Google Cloud Storage V4 signed URLs, we MUST use:
- Algorithm: RSA_SIGN_PKCS1_4096_SHA512 or RSA_SIGN_PKCS1_2048_SHA256
- For V4: Typically RSA_SIGN_PKCS1_2048_SHA256

Let's check if we're specifying the algorithm in our signBlob call...
""")

print("""
Looking at the request in the audit log:
{
  "payload": "...",
  "@type": "type.googleapis.com/google.iam.credentials.v1.SignBlobRequest",
  "name": "projects/-/serviceAccounts/signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com"
}

There's NO "algorithm" field specified!
This means signBlob might be using a DEFAULT algorithm, not necessarily SHA256!

POTENTIAL FIX:
We might need to specify the algorithm in the request body when calling signBlob.
""")

print("""
Let's check what the actual SignBlobRequest proto looks like:

message SignBlobRequest {
  string name = 1;
  bytes payload = 2;
  // Note: There might be additional fields for algorithm/hash algorithm
}

The solution might be to look at what fields are available in the v1 API.
""")
