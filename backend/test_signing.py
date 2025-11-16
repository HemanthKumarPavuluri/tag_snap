#!/usr/bin/env python3
"""Debug script to test signed URL generation"""
import os
import sys
import hashlib
import base64
from datetime import datetime, timezone
from urllib.parse import quote, quote_plus

# Set credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/user/.config/gcloud/application_default_credentials.json'

from signed_urls import _build_canonical_request, _build_string_to_sign

# Test parameters
bucket_name = "sna-bucket-001"
blob_name = "test_image_01.jpg"
service_account_email = "signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com"
content_type = "image/jpeg"
expiration_minutes = 15

now = datetime.now(timezone.utc)
timestamp = now.strftime("%Y%m%dT%H%M%SZ")
datestamp = now.strftime("%Y%m%d")

credential_scope = f"{datestamp}/auto/storage/goog4_request"
expiration_seconds = expiration_minutes * 60

query_parameters = {
    "X-Goog-Algorithm": "GOOG4-RSA-SHA256",
    "X-Goog-Credential": f"{service_account_email}/{credential_scope}",
    "X-Goog-Date": timestamp,
    "X-Goog-Expires": str(expiration_seconds),
    "X-Goog-SignedHeaders": "content-type;host",
}

path = f"/{blob_name}"
headers = {
    "content-type": content_type,
    "host": f"{bucket_name}.storage.googleapis.com",
}

print("=" * 80)
print("DEBUG: Signed URL Generation")
print("=" * 80)
print(f"Timestamp: {timestamp}")
print(f"Credential Scope: {credential_scope}")
print()

# Build canonical request
canonical_request = _build_canonical_request(
    "PUT",
    path,
    query_parameters,
    headers,
)

print("CANONICAL REQUEST:")
print("-" * 80)
print(repr(canonical_request))
print()
print("CANONICAL REQUEST (formatted):")
print("-" * 80)
print(canonical_request)
print()

# Build string to sign
string_to_sign = _build_string_to_sign(
    now,
    credential_scope,
    canonical_request,
)

print("STRING TO SIGN:")
print("-" * 80)
print(repr(string_to_sign))
print()
print("STRING TO SIGN (formatted):")
print("-" * 80)
print(string_to_sign)
print()

# Show hash of canonical request
hashed_canonical = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
print(f"SHA256 of Canonical Request: {hashed_canonical}")
print()

# Show query parameter encoding
print("QUERY PARAMETER ENCODING:")
print("-" * 80)
canonical_params = {
    k: v for k, v in query_parameters.items() 
    if k not in ("X-Goog-Signature", "X-Goog-SignedHeaders")
}
for k, v in sorted(canonical_params.items()):
    encoded_k = quote(k, safe='')
    encoded_v = quote(str(v), safe='')
    print(f"{k} = {v}")
    print(f"  quote(k, safe='') = {encoded_k}")
    print(f"  quote(v, safe='') = {encoded_v}")
    print()
