#!/usr/bin/env python3
"""
Compare our canonical request with what GCS expects
"""

# What GCS is showing in the error (from their XML response):
gcs_canonical_from_error = """PUT
/test_image_01.jpg
X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=signed-url%40storied-catwalk-476608-d1.iam.gserviceaccount.com%2F20251116%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251116T043806Z&X-Goog-Expires=900&X-Goog-SignedHeaders=content-type%3Bhost
content-type:image/jpeg
host:sna-bucket-001.storage.googleapis.com

content-type;host
UNSIGNED-PAYLOAD"""

# What we're building
our_canonical = """PUT
/test_image_01.jpg
X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=signed-url%40storied-catwalk-476608-d1.iam.gserviceaccount.com%2F20251116%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20251116T043806Z&X-Goog-Expires=900&X-Goog-SignedHeaders=content-type%3Bhost
content-type:image/jpeg
host:sna-bucket-001.storage.googleapis.com
content-type;host
UNSIGNED-PAYLOAD"""

print("="*80)
print("GCS CANONICAL (from error response):")
print("="*80)
print(repr(gcs_canonical_from_error))
print()
print(gcs_canonical_from_error)
print()

print("="*80)
print("OUR CANONICAL:")
print("="*80)
print(repr(our_canonical))
print()
print(our_canonical)
print()

print("="*80)
print("DIFFERENCES:")
print("="*80)
gcs_lines = gcs_canonical_from_error.split('\n')
our_lines = our_canonical.split('\n')

print(f"GCS has {len(gcs_lines)} lines")
print(f"We have {len(our_lines)} lines")
print()

max_lines = max(len(gcs_lines), len(our_lines))
for i in range(max_lines):
    gcs_line = gcs_lines[i] if i < len(gcs_lines) else "<<MISSING>>"
    our_line = our_lines[i] if i < len(our_lines) else "<<MISSING>>"
    
    if gcs_line != our_line:
        print(f"Line {i}:")
        print(f"  GCS: {repr(gcs_line)}")
        print(f"  US:  {repr(our_line)}")
    else:
        print(f"Line {i}: OK - {repr(gcs_line)}")

print()
print("="*80)
print("KEY OBSERVATION:")
print("="*80)
print("GCS has a blank line after the host header, before the signed headers line")
print("We do NOT have that blank line")
print()
print("In canonical request format:")
print("  1. Method")
print("  2. Path")
print("  3. Query string")
print("  4. Headers (key:value format)")
print("  5. BLANK LINE")
print("  6. Signed headers list")
print("  7. Payload hash")
