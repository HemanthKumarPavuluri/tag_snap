#!/usr/bin/env python3
"""
Test the full signing process to see where the mismatch is
"""
import os
import sys

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.expanduser('~/.config/gcloud/application_default_credentials.json')

import hashlib
import base64
from datetime import datetime, timezone
from urllib.parse import quote, quote_plus
from google.auth import iam, default
from google.auth.transport.requests import Request

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
        if k != "X-Goog-Signature"
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
        f"\n"
        f"{signed_headers_str}\n"
        f"{payload_hash}"
    )

def _build_string_to_sign(
    timestamp: datetime,
    scope: str,
    canonical_request: str,
) -> str:
    """Build the string to sign for V4 signature."""
    hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    return (
        f"GOOG4-RSA-SHA256\n"
        f"{timestamp.strftime('%Y%m%dT%H%M%SZ')}\n"
        f"{scope}\n"
        f"{hashed_canonical_request}"
    )

try:
    credentials, project = default()
    print(f"Project: {project}")
    print(f"Credentials type: {type(credentials)}")
    print()
    
    service_account_email = "signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com"
    
    # Test parameters
    bucket_name = "sna-bucket-001"
    blob_name = "test_image_01.jpg"
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

    # Build canonical request
    canonical_request = _build_canonical_request(
        "PUT",
        path,
        query_parameters,
        headers,
    )

    # Build string to sign
    string_to_sign = _build_string_to_sign(
        now,
        credential_scope,
        canonical_request,
    )

    print("="*80)
    print("CANONICAL REQUEST:")
    print("="*80)
    print(repr(canonical_request))
    print()

    print("="*80)
    print("STRING TO SIGN:")
    print("="*80)
    print(repr(string_to_sign))
    print()

    # Sign using IAM
    request = Request()
    signer = iam.Signer(request, credentials, service_account_email)
    signature_bytes = signer.sign(string_to_sign.encode('utf-8'))
    
    print("="*80)
    print(f"SIGNATURE (bytes length): {len(signature_bytes)}")
    print(f"SIGNATURE (hex): {signature_bytes.hex()}")
    print()

    # Convert to base64
    signature_b64 = base64.b64encode(signature_bytes).decode('ascii')
    print("="*80)
    print(f"SIGNATURE (base64): {signature_b64}")
    print()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
