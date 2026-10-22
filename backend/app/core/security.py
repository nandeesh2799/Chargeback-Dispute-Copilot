import hmac
import hashlib
import os
from pathlib import Path
from typing import Optional


def verify_razorpay_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    """
    Verify Razorpay webhook signature using HMAC-SHA256 over raw request body.
    """
    if not signature or not secret:
        return False
    generated_sig = hmac.new(
        key=secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(generated_sig, signature)


def sanitize_filename(filename: str) -> str:
    """
    Remove directory traversal sequences and unsafe characters from filenames.
    """
    clean_name = os.path.basename(filename).replace("..", "").replace("/", "").replace("\\", "")
    return clean_name or "file.bin"


def safe_join_path(base_dir: str, filename: str) -> Path:
    """
    Safely construct file path and ensure it doesn't escape base_dir.
    """
    base = Path(base_dir).resolve()
    target = (base / sanitize_filename(filename)).resolve()
    if not str(target).startswith(str(base)):
        raise ValueError("Path traversal attempt detected")
    return target
