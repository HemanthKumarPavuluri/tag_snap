#!/usr/bin/env python3
"""
Extract and verify canonical request from GCS error response.
This script lets us capture the exact CanonicalRequest that GCS computed,
then compare it with what we're generating.
"""

import re
import base64
import hashlib
from xml.etree import ElementTree as ET

# GCS Error Response from the last 403 (captured manually)
gcs_error_response = '''<?xml version='1.0' encoding='UTF-8'?><Error><Code>SignatureDoesNotMatch</Code><Message>Access denied.</Message><Details>The request signature we calculated does not match the signature you provided. Check your Google secret key and signing method.</Details><StringToSign>GOOG4-RSA-SHA256
20251116T050034Z
20251116/auto/storage/goog4_request
b6af122b15121523fc56aa31fa378cfa664052fe2296df06f5635aaaaa08b1cf</StringToSign><CanonicalRequest>PUT
/test_image_01.jpg
X-Goog-Algorithm=GOOG4-RSA-SHA256&amp;X-Goog-Credential=signed-url%40storied-catwalk-476608-d1.iam.gserviceaccount.com%2F20251116%2Fauto%2Fstorage%2Fgoog4_request&amp;X-Goog-Date=20251116T050034Z&amp;X-Goog-Expires=900&amp;X-Goog-SignedHeaders=content-type%3Bhost
content-type:image/jpeg
host:sna-bucket-001.storage.googleapis.com

content-type;host
UNSIGNED-PAYLOAD</CanonicalRequest></Error>'''

print("="*80)
print("PARSING GCS ERROR RESPONSE")
print("="*80)

# Parse XML
root = ET.fromstring(gcs_error_response)

# Extract CanonicalRequest
canonical_request_elem = root.find('CanonicalRequest')
if canonical_request_elem is not None:
    gcs_canonical = canonical_request_elem.text
    print("✓ Found CanonicalRequest in error response")
else:
    print("✗ Could not find CanonicalRequest in error response")
    exit(1)

# Extract StringToSign
string_to_sign_elem = root.find('StringToSign')
if string_to_sign_elem is not None:
    gcs_string_to_sign = string_to_sign_elem.text
    print("✓ Found StringToSign in error response")
else:
    print("✗ Could not find StringToSign in error response")
    exit(1)

print()
print("="*80)
print("GCS CANONICAL REQUEST:")
print("="*80)
print(repr(gcs_canonical))
print()
print(gcs_canonical)
print()

print("="*80)
print("GCS STRING TO SIGN:")
print("="*80)
print(repr(gcs_string_to_sign))
print()
print(gcs_string_to_sign)
print()

# Verify hash
canonical_hash = hashlib.sha256(gcs_canonical.encode('utf-8')).hexdigest()
print("="*80)
print("VERIFICATION:")
print("="*80)
print(f"SHA256 of canonical request: {canonical_hash}")
print()

# Extract hash from StringToSign
lines = gcs_string_to_sign.split('\n')
if len(lines) >= 4:
    expected_hash = lines[3]
    print(f"Hash from StringToSign:      {expected_hash}")
    print(f"Match: {canonical_hash == expected_hash}")
else:
    print("Could not extract hash from StringToSign")

print()
print("="*80)
print("IMPORTANT FINDINGS:")
print("="*80)

# Check for key differences
print()
print("1. Query parameters in canonical request:")
lines = gcs_canonical.split('\n')
if len(lines) > 2:
    query_line = lines[2]
    print(f"   {query_line}")
    print()
    params = query_line.split('&')
    for param in params:
        print(f"   - {param}")

print()
print("2. Headers in canonical request:")
for i, line in enumerate(lines):
    if i >= 3 and i <= 4:  # Header lines
        print(f"   Line {i}: {repr(line)}")

print()
print("3. Blank line present:")
for i, line in enumerate(lines):
    if line == '':
        print(f"   ✓ Blank line at line {i}")

print()
print("KEY OBSERVATION:")
print("- Notice the query parameters include X-Goog-SignedHeaders")
print("- This is what GCS used to build THEIR canonical request")
print("- We might NOT need to include it in OUR canonical request for signing")
print("- The query string in the URL that GCS validates might be different")
