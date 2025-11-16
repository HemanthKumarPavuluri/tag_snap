# backend/signed_urls.py - Enterprise Keyless Signing using google.auth.iam
import os
import hashlib
import base64
from datetime import timedelta, datetime, timezone
import uuid
from typing import Optional
from urllib.parse import quote_plus, quote

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.auth import iam, default
from google.auth.transport.requests import Request

router = APIRouter()


class SignedURLRequest(BaseModel):
    filename: Optional[str] = None
    content_type: Optional[str] = "image/jpeg"
    expires_minutes: Optional[int] = 15


class IAMSigner:
    """Enterprise-grade signer using IAM API for keyless signing.
    
    This implementation uses Google's IAM API to sign requests without storing
    private keys. Keys remain in Google's HSM and are never exposed to the application.
    
    Security benefits:
    - No private keys in memory or on disk
    - Audit trail of all signing operations
    - Instant revocation via IAM role changes
    - Zero key rotation overhead
    """
    
    def __init__(self, service_account_email: str):
        self.service_account_email = service_account_email
        # Get the credentials for making IAM API calls
        self.credentials, _ = default()
        self.request = Request()
    
    def sign_bytes(self, message: bytes) -> bytes:
        """Sign bytes using IAM API signBlob endpoint.
        
        Args:
            message: Bytes to sign
            
        Returns:
            Signature bytes
            
        Raises:
            HTTPException: If signing fails
        """
        try:
            signer = iam.Signer(self.request, self.credentials, self.service_account_email)
            signature = signer.sign(message)
            return signature
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"IAM signing failed: {str(e)}"
            )
    
    @property
    def signer_email(self) -> str:
        return self.service_account_email


def _build_canonical_request(
    method: str,
    path: str,
    query_parameters: dict,
    headers: dict,
) -> str:
    """Build canonical request string per Google V4 signing spec.
    
    All header names must be lowercase in the canonical request.
    """
    # 1. Canonical Query String
    # Exclude X-Goog-Signature from canonical query (it's added after signing)
    # Also exclude X-Goog-SignedHeaders as per V4 spec
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
        # Format: lowercase_key:value (no space after colon, value stripped)
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
        f"{signed_headers_str}\n"
        f"{payload_hash}"
    )


def _build_string_to_sign(
    timestamp: datetime,
    scope: str,
    canonical_request: str,
) -> str:
    """Build the string to sign for V4 signature."""
    credential_scope = scope
    hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    return (
        f"GOOG4-RSA-SHA256\n"
        f"{timestamp.strftime('%Y%m%dT%H%M%SZ')}\n"
        f"{credential_scope}\n"
        f"{hashed_canonical_request}"
    )


def generate_signed_url_iam(
    bucket_name: str,
    blob_name: str,
    service_account_email: str,
    content_type: str,
    expiration_minutes: int = 15,
) -> dict:
    """Generate a V4 signed URL using IAM API (keyless signing).
    
    Enterprise-secure: No private keys stored. Signing via IAM signBlob.
    """
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")
    
    # Credential scope for V4 signing
    credential_scope = f"{datestamp}/auto/storage/goog4_request"
    
    # Query parameters for the signed URL
    expiration_seconds = expiration_minutes * 60
    query_parameters = {
        "X-Goog-Algorithm": "GOOG4-RSA-SHA256",
        "X-Goog-Credential": f"{service_account_email}/{credential_scope}",
        "X-Goog-Date": timestamp,
        "X-Goog-Expires": str(expiration_seconds),
        "X-Goog-SignedHeaders": "content-type;host",  # ← LOWERCASE!
    }
    
    # Canonical request
    # Note: Headers must be lowercase for canonical request
    path = f"/{blob_name}"
    headers = {
        "content-type": content_type,
        "host": f"{bucket_name}.storage.googleapis.com",
    }
    
    canonical_request = _build_canonical_request(
        "PUT",
        path,
        query_parameters,
        headers,
    )
    
    # String to sign
    string_to_sign = _build_string_to_sign(
        now,
        credential_scope,
        canonical_request,
    )

    # Sign using IAM (keyless)
    signature_bytes = IAMSigner(service_account_email).sign_bytes(string_to_sign.encode('utf-8'))
    signature_b64 = base64.b64encode(signature_bytes).decode('ascii')

    # Add signature to query params
    query_parameters["X-Goog-Signature"] = signature_b64

    # Build final URL
    query_string = "&".join(
        f"{quote(k)}={quote_plus(str(v))}"
        for k, v in sorted(query_parameters.items())
    )
    
    signed_url = f"https://{bucket_name}.storage.googleapis.com{path}?{query_string}"
    
    expires_at = now + timedelta(minutes=expiration_minutes)
    
    return {
        "url": signed_url,
        "method": "PUT",
        "blob_name": blob_name,
        "content_type": content_type,
        "expires_at": expires_at.isoformat(),
    }


@router.post("/signed-url")
async def create_upload_signed_url(req: SignedURLRequest):
    """Return a V4 signed URL for uploading an object to GCS.

    Enterprise-grade keyless implementation using IAM API.
    
    Security model:
    - No private keys stored, transmitted, or kept in memory
    - All cryptographic signing done via Google IAM API
    - Keys remain in Google's hardware security modules (HSM)
    - Full audit trail of signing operations
    - Instant revocation via IAM role management
    
    Required IAM Roles:
    - roles/iam.serviceAccountTokenCreator → on target SA
    - roles/storage.objectCreator → on bucket
    """
    bucket_name = os.environ.get("UPLOAD_BUCKET", "sna-bucket-001")
    service_account_email = os.environ.get(
        "SERVICE_ACCOUNT_EMAIL",
        "signed-url@storied-catwalk-476608-d1.iam.gserviceaccount.com"
    )

    # Generate unique filename if not provided
    filename = req.filename or f"uploads/{uuid.uuid4().hex}.jpg"
    content_type = req.content_type or "application/octet-stream"

    try:
        result = generate_signed_url_iam(
            bucket_name=bucket_name,
            blob_name=filename,
            service_account_email=service_account_email,
            content_type=content_type,
            expiration_minutes=req.expires_minutes or 15,
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating signed URL: {str(e)}"
        )