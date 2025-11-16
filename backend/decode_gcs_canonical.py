#!/usr/bin/env python3
"""
The issue might be that the XML entities (&amp;) need to be decoded!
"""
import hashlib
from html import unescape

# The raw canonical request from the error (with XML entities)
raw_with_entities = """PUT
/test_image_01.jpg
X-Goog-Algorithm=GOOG4-RSA-SHA256&amp;X-Goog-Credential=signed-url%40storied-catwalk-476608-d1.iam.gserviceaccount.com%2F20251116%2Fauto%2Fstorage%2Fgoog4_request&amp;X-Goog-Date=20251116T050034Z&amp;X-Goog-Expires=900&amp;X-Goog-SignedHeaders=content-type%3Bhost
content-type:image/jpeg
host:sna-bucket-001.storage.googleapis.com

content-type;host
UNSIGNED-PAYLOAD"""

# Decode XML entities
decoded = unescape(raw_with_entities)

print("="*80)
print("RAW WITH XML ENTITIES:")
print("="*80)
print(repr(raw_with_entities))
print()

print("="*80)
print("AFTER UNESCAPE:")
print("="*80)
print(repr(decoded))
print()

print(decoded)
print()

hash_val = hashlib.sha256(decoded.encode('utf-8')).hexdigest()
print(f"SHA256: {hash_val}")
print()
print("Expected from StringToSign: b6af122b15121523fc56aa31fa378cfa664052fe2296df06f5635aaaaa08b1cf")
print(f"Match: {hash_val == 'b6af122b15121523fc56aa31fa378cfa664052fe2296df06f5635aaaaa08b1cf'}")
