#!/usr/bin/env python3

# GCS canonical request from the latest 403 error (need to grab from cloud run logs)
# Let me compute what we SHOULD be sending

import hashlib
from urllib.parse import quote

canonical_request = """PUT
/test_image_01.jpg
X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=signed-url%40storied-catwalk-476608-d1.iam.gserviceaccount.com%2F20251116%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251116T045045Z&X-Goog-Expires=900
content-type:image/jpeg
host:sna-bucket-001.storage.googleapis.com

content-type;host
UNSIGNED-PAYLOAD"""

print("="*80)
print("CANONICAL REQUEST (without X-Goog-SignedHeaders):")
print("="*80)
print(canonical_request)
print()

hash_value = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
print(f"SHA256 Hash: {hash_value}")
print()

string_to_sign = f"""GOOG4-RSA-SHA256
20251116T045045Z
20251116/auto/storage/goog4_request
{hash_value}"""

print("="*80)
print("STRING TO SIGN:")
print("="*80)
print(string_to_sign)
