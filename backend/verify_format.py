#!/usr/bin/env python3
"""
Verify exact canonical request format
"""

our_canonical = b"""PUT
/test_image_01.jpg
X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=signed-url%40storied-catwalk-476608-d1.iam.gserviceaccount.com%2F20251116%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251116T044441Z&X-Goog-Expires=900&X-Goog-SignedHeaders=content-type%3Bhost
content-type:image/jpeg
host:sna-bucket-001.storage.googleapis.com

content-type;host
UNSIGNED-PAYLOAD"""

print("Bytes representation:")
print(repr(our_canonical))
print()

print("Split into lines:")
for i, line in enumerate(our_canonical.split(b'\n')):
    print(f"Line {i}: {repr(line)}")
print()

# Check for any non-ASCII characters
print("Hex dump of problematic sections:")
lines = our_canonical.split(b'\n')
for i, line in enumerate(lines):
    if i in [3, 4, 5]:  # Headers and blank line area
        print(f"Line {i}:")
        print(f"  text: {line}")
        print(f"  hex: {line.hex()}")
