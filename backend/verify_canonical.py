#!/usr/bin/env python3
"""
Verify that our canonical request computation produces the hash shown in the audit log.

Audit log shows:
  StringToSign payload (decoded): GOOG4-RSA-SHA256\n20251116T083431Z\n20251116/auto/storage/goog4_request\n73ba499f2b93d4906d452503297e736406027c02f5ce875688f6c984dad875fd

The last part (73ba499f...) is the SHA256 hash of the canonical request.

Let's verify we compute the same hash.
"""

import hashlib

# From the audit log, we know the string-to-sign was:
string_to_sign = """GOOG4-RSA-SHA256
20251116T083431Z
20251116/auto/storage/goog4_request
73ba499f2b93d4906d452503297e736406027c02f5ce875688f6c984dad875fd"""

# The hash (73ba499f...) is the SHA256 of the canonical request.
# So let's work backward: we need to find what canonical request produces that hash.

# Let's trace through what we know:
# 1. Timestamp: 20251116T083431Z
# 2. Credential scope: 20251116/auto/storage/goog4_request
# 3. Hash: 73ba499f2b93d4906d452503297e736406027c02f5ce875688f6c984dad875fd

# From a typical signed URL generation:
# - Bucket: sna-bucket-001
# - Method: PUT
# - Object path: /uploads/... (some filename)
# - Content-Type: image/jpeg
# - Host header: sna-bucket-001.storage.googleapis.com
# - Signed headers: content-type;host

# Let's test various canonical request constructions to find which one produces
# the hash 73ba499f2b93d4906d452503297e736406027c02f5ce875688f6c984dad875fd

test_canonical_requests = [
    # Test 1: Simple without parameters
    """PUT
/file.jpg

host:sna-bucket-001.storage.googleapis.com

host
UNSIGNED-PAYLOAD""",
    
    # Test 2: With content-type and host
    """PUT
/file.jpg

content-type:image/jpeg
host:sna-bucket-001.storage.googleapis.com

content-type;host
UNSIGNED-PAYLOAD""",
]

target_hash = "73ba499f2b93d4906d452503297e736406027c02f5ce875688f6c984dad875fd"

for i, canonical in enumerate(test_canonical_requests):
    computed_hash = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    print(f"Test {i+1}:")
    print(f"  Computed: {computed_hash}")
    print(f"  Target:   {target_hash}")
    print(f"  Match: {computed_hash == target_hash}")
    print()

# Let's also check: what if we DON'T include UNSIGNED-PAYLOAD?
canonical_no_payload = """PUT
/file.jpg

content-type:image/jpeg
host:sna-bucket-001.storage.googleapis.com

content-type;host"""

computed_hash = hashlib.sha256(canonical_no_payload.encode('utf-8')).hexdigest()
print("Test (no payload hash):")
print(f"  Computed: {computed_hash}")
print(f"  Target:   {target_hash}")
print(f"  Match: {computed_hash == target_hash}")
