#!/usr/bin/env python3
"""
Test if iam.Signer is working correctly by logging what we get back.
Run this in Cloud Run context to debug the actual signing.
"""

# This would be run inside Cloud Run where default credentials are available
code = '''
import os
import base64
from google.auth import iam, default
from google.auth.transport.requests import Request

service_account_email = os.environ.get(
    "SERVICE_ACCOUNT_EMAIL",
    "signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com"
)

# Test string
test_message = b"This is a test message"

print(f"Service Account: {service_account_email}")
print(f"Message: {test_message}")
print(f"Message length: {len(test_message)}")
print()

try:
    # Get credentials
    credentials, _ = default()
    request = Request()
    
    # Create signer
    signer = iam.Signer(request, credentials, service_account_email)
    
    # Sign
    print("Calling iam.Signer.sign()...")
    signature = signer.sign(test_message)
    
    # Inspect result
    print(f"Signature type: {type(signature)}")
    print(f"Signature length: {len(signature)}")
    print(f"Signature (first 50 bytes): {signature[:50]}")
    print()
    
    if isinstance(signature, bytes):
        # Try to decode as base64
        try:
            decoded = base64.b64decode(signature)
            print(f"Decoded as base64 length: {len(decoded)}")
        except:
            print("Could not decode as base64 - likely raw bytes")
    
    # Base64 encode for inspection
    if isinstance(signature, bytes):
        b64 = base64.b64encode(signature).decode('ascii')
    else:
        b64 = signature
    
    print(f"Base64 encoded: {b64[:100]}...")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
'''

print("Code to test iam.Signer:")
print("="*80)
print(code)
print("="*80)
print()
print("This code needs to run in Cloud Run or in an environment with google.auth credentials.")
print("We'll add it to the backend for debugging purposes.")
