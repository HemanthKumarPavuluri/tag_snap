#!/usr/bin/env python3
"""Debug script to test signed URL generation logic"""
import hashlib
from datetime import datetime, timezone
from urllib.parse import quote, quote_plus

def _build_canonical_request(
    method: str,
    path: str,
    query_parameters: dict,
    headers: dict,
) -> str:
    """Build canonical request string per Google V4 signing spec."""
    # 1. Canonical Query String
    canonical_params = {
        k: v for k, v in query_parameters.items() 
        if k not in ("X-Goog-Signature", "X-Goog-SignedHeaders")
    }
    canonical_query = "&".join(
        f"{quote(k, safe='')}={quote(str(v), safe='')}" for k, v in sorted(canonical_params.items())
    )

    # 2. Canonical Headers (lowercase keys, sorted)
    header_lines = []
    signed_headers = []
    for k in sorted(headers.keys()):
        v = headers[k].strip()
        k_lower = k.lower()
        signed_headers.append(k_lower)
        header_lines.append(f"{k_lower}:{v}")

    canonical_headers = "\n".join(header_lines)
    signed_headers_str = ";".join(signed_headers)

    # 3. Payload Hash
    payload_hash = "UNSIGNED-PAYLOAD"

    return (
        f"{method}\n"
        f"{path}\n"
        f"{canonical_query}\n"
        f"{canonical_headers}\n"
        f"\n"  # ← BLANK LINE AFTER HEADERS
        f"{signed_headers_str}\n"
        f"{payload_hash}"
    )

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
    print(f"{k}")
    print(f"  value: {v}")
    print(f"  encoded: {encoded_k}={encoded_v}")
    print()

print("=" * 80)
print("FINAL QUERY STRING (for URL):")
print("-" * 80)
# This is how it should be built for the final URL
final_query_parts = []
for k, v in sorted(query_parameters.items()):
    # Note: NOT including X-Goog-Signature yet
    if k != "X-Goog-Signature":
        # For final URL, use quote_plus for safety
        encoded_k = quote(k, safe='')
        encoded_v = quote_plus(str(v), safe='')
        final_query_parts.append(f"{encoded_k}={encoded_v}")
        
final_query = "&".join(final_query_parts)
print(final_query)
