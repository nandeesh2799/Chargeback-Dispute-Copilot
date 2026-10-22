import pytest
from app.integrations.razorpay.client import RazorpayDisputeSource
from app.core.security import verify_razorpay_signature, sanitize_filename, safe_join_path


def test_synthetic_dispute_safety_guardrail():
    """
    Ensure RazorpayDisputeSource rejects any attempt to query or contest synthetic dispute IDs.
    """
    client = RazorpayDisputeSource(key_id="rzp_test_sample", key_secret="secret_sample")

    with pytest.raises(ValueError, match="Safety constraint"):
        client.get_dispute("disp_synth_1001")

    with pytest.raises(ValueError, match="Safety constraint"):
        client.submit_contest("disp_synth_1001", "Summary", ["doc_1"])


def test_character_limit_guardrail():
    client = RazorpayDisputeSource(key_id="rzp_test_sample", key_secret="secret_sample")

    with pytest.raises(ValueError, match="1000 characters"):
        client.submit_contest("disp_real_9999", "A" * 1005, ["doc_1"])


def test_webhook_signature_verification():
    secret = "test_webhook_secret_123"
    payload = b'{"event":"dispute.won"}'

    # Proper HMAC-SHA256 signature
    import hmac, hashlib
    valid_sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    assert verify_razorpay_signature(payload, valid_sig, secret) is True
    assert verify_razorpay_signature(payload, "invalid_sig", secret) is False
    assert verify_razorpay_signature(payload, "", secret) is False


def test_path_traversal_sanitization():
    unsafe = "../../../etc/passwd"
    clean = sanitize_filename(unsafe)
    assert clean == "passwd"

    base_dir = "/tmp/copilot_test_uploads"
    import os
    os.makedirs(base_dir, exist_ok=True)
    target = safe_join_path(base_dir, "document.pdf")
    assert str(target).startswith(base_dir)
