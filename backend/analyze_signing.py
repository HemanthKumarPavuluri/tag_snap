#!/usr/bin/env python3
"""
Test signing the same StringToSign with different methods to debug the issue.
This will help us understand if iam.Signer is the problem.
"""

import base64
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

string_to_sign = """GOOG4-RSA-SHA256
20251116T081637Z
20251116/auto/storage/goog4_request
f434deab8c513bd05d53dd125ef5b6d0b3a187ffab603fb3e01fc050b8cd2df7"""

print("="*80)
print("STRING TO SIGN:")
print("="*80)
print(repr(string_to_sign))
print()
print(string_to_sign)
print()

print("="*80)
print("ANALYSIS:")
print("="*80)
print(f"Length: {len(string_to_sign)} bytes")
print(f"Bytes: {string_to_sign.encode('utf-8')[:50]}...")
print()

print("="*80)
print("WHAT WE KNOW:")
print("="*80)
print("""
1. The canonical request format IS correct (verified against GCS errors)
2. The hash computation IS correct (verified against GCS StringToSign)
3. So we're passing the right string to the signer

4. The problem MUST be one of:
   a) iam.Signer is not using RSA-SHA256
   b) iam.Signer is using a different key than expected
   c) There's an encoding issue in how we pass the data to iam.Signer
   d) The service account doesn't have permission to sign

5. Key facts about iam.Signer:
   - It calls the IAM signBlob API
   - The signBlob API uses the service account's private key (in HSM)
   - It should return a 256-byte RSA-2048-SHA256 signature

6. Testing strategy:
   - We can't directly access the private key to test locally
   - But we CAN verify that the signature FORMAT is correct (256 bytes)
   - We CAN check IAM permissions
   - We CAN try a different signing approach if needed
""")

print()
print("="*80)
print("NEXT STEPS:")
print("="*80)
print("""
1. Verify IAM service account has correct roles
2. Check if there's an issue with how iam.Signer is being called
3. Consider using the IAM signBlob API directly instead of iam.Signer
4. Look at Cloud Run service account IAM configuration
""")
