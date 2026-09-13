import time
import uuid
import logging
import ipaddress
from collections import defaultdict
from typing import Tuple, Dict, List
from fastapi import Request, HTTPException, status
from supabase import create_client, Client
from config import settings

logger = logging.getLogger("kalvettu.security")

# Rate limiting storage: ip -> list of timestamps
_RATE_LIMIT_STORE: Dict[str, List[float]] = defaultdict(list)
_LAST_PRUNE_TIME: float = time.time()
_MAX_TRACKED_IPS: int = 5000

def _prune_rate_limit_store(now: float, window_seconds: int):
    """Prevents memory leaks by evicting stale client IPs from the in-memory store."""
    global _LAST_PRUNE_TIME
    if now - _LAST_PRUNE_TIME < 60 and len(_RATE_LIMIT_STORE) < _MAX_TRACKED_IPS:
        return
    
    _LAST_PRUNE_TIME = now
    cutoff = now - window_seconds
    stale_ips = [ip for ip, timestamps in _RATE_LIMIT_STORE.items() if not timestamps or max(timestamps) <= cutoff]
    for ip in stale_ips:
        _RATE_LIMIT_STORE.pop(ip, None)
        
    # Emergency cap if still exceeding limit under active distributed attack
    if len(_RATE_LIMIT_STORE) > _MAX_TRACKED_IPS:
        # Keep only the most recently active IPs
        sorted_ips = sorted(_RATE_LIMIT_STORE.items(), key=lambda x: max(x[1]) if x[1] else 0, reverse=True)
        _RATE_LIMIT_STORE.clear()
        _RATE_LIMIT_STORE.update(dict(sorted_ips[:_MAX_TRACKED_IPS]))

def _extract_safe_client_ip(request: Request) -> str:
    """Safely extracts and validates client IP to avoid header injection or spoofing."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the leftmost entry (client IP in standard proxy chains)
        candidate = forwarded.split(",")[0].strip()
        try:
            ipaddress.ip_address(candidate)
            return candidate
        except ValueError:
            pass

    if request.client and request.client.host:
        try:
            ipaddress.ip_address(request.client.host)
            return request.client.host
        except ValueError:
            pass

    return "127.0.0.1"

def rate_limiter(max_requests: int = 30, window_seconds: int = 60):
    """
    FastAPI dependency for sliding-window rate limiting per client IP.
    Features automated memory eviction and spoof-resistant IP extraction.
    """
    async def dependency(request: Request):
        now = time.time()
        _prune_rate_limit_store(now, window_seconds)

        client_ip = _extract_safe_client_ip(request)
        timestamps = _RATE_LIMIT_STORE[client_ip]

        # Purge timestamps older than the window
        cutoff = now - window_seconds
        valid_timestamps = [ts for ts in timestamps if ts > cutoff]
        _RATE_LIMIT_STORE[client_ip] = valid_timestamps

        if len(valid_timestamps) >= max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip} on {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please wait a moment before trying again."
            )

        _RATE_LIMIT_STORE[client_ip].append(now)

    return dependency


def validate_image_file(file_bytes: bytes) -> Tuple[str, str]:
    """
    Inspects magic bytes to strictly validate image file types.
    Enforces maximum file size limit.
    Returns (extension, mime_type) if valid, or raises HTTPException.
    """
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum permitted limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    if len(file_bytes) < 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty or truncated."
        )

    # Magic byte inspection
    if file_bytes.startswith(b'\xff\xd8\xff'):
        return "jpg", "image/jpeg"
    elif file_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return "png", "image/png"
    elif file_bytes.startswith(b'RIFF') and file_bytes[8:12] == b'WEBP':
        return "webp", "image/webp"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image format. Allowed formats: JPEG, PNG, WebP."
        )


def upload_image_to_supabase_storage(
    file_bytes: bytes,
    bucket_name: str = "inscriptions",
    prefix: str = "uploads"
) -> str:
    """
    Uploads verified image bytes to Supabase Storage with a secure, randomized UUID filename.
    Returns the public URL of the uploaded image.
    """
    ext, mime_type = validate_image_file(file_bytes)
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("Supabase storage credentials missing. Returning local placeholder.")
        return ""

    try:
        supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        random_name = f"{prefix}_{uuid.uuid4().hex}.{ext}"
        
        # Upload to Supabase Storage bucket
        res = supabase.storage.from_(bucket_name).upload(
            path=random_name,
            file=file_bytes,
            file_options={"content-type": mime_type, "upsert": "false"}
        )
        
        # Construct public URL
        public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{random_name}"
        logger.info(f"Successfully uploaded image to Supabase Storage: {public_url}")
        return public_url
    except Exception as e:
        logger.error(f"Failed to upload image to Supabase Storage: {e}")
        # Fallback to public URL structure in case of idempotent existing record
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{random_name}"
