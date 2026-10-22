import os
import shutil
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app.models import IntegrationConfig, AuditLog, Merchant
from app.core.config import settings
from app.schemas.domain import IntegrationUpdateRequest, TestConnectionRequest
from app.core.logging import logger

router = APIRouter()


@router.get("/integrations/status")
def get_integrations_status(db: Session = Depends(get_db_session)) -> List[Dict[str, Any]]:
    active_source = settings.DISPUTE_SOURCE
    llm_provider = settings.LLM_PROVIDER

    configs = db.query(IntegrationConfig).all()
    results = []
    for cfg in configs:
        is_active = (cfg.provider == active_source) or (cfg.provider == llm_provider)
        results.append({
            "id": cfg.id,
            "provider": cfg.provider,
            "is_enabled": is_active,
            "environment": cfg.environment,
            "key_id_masked": cfg.key_id_masked,
            "webhook_secret_masked": cfg.webhook_secret_masked,
            "last_synced_at": cfg.last_synced_at,
            "sync_status": cfg.sync_status
        })

    return results or [
        {
            "id": "cfg_mock_01",
            "provider": "mock",
            "is_enabled": active_source == "mock",
            "environment": "mock",
            "key_id_masked": "internal_mock_engine",
            "webhook_secret_masked": None,
            "last_synced_at": None,
            "sync_status": "healthy"
        },
        {
            "id": "cfg_razorpay_01",
            "provider": "razorpay",
            "is_enabled": active_source == "razorpay",
            "environment": "test",
            "key_id_masked": settings.RAZORPAY_KEY_ID[:8] + "****" if settings.RAZORPAY_KEY_ID else "not_configured",
            "webhook_secret_masked": "whsec_****" if settings.RAZORPAY_WEBHOOK_SECRET else "not_configured",
            "last_synced_at": None,
            "sync_status": "healthy" if settings.RAZORPAY_KEY_ID else "disconnected"
        },
        {
            "id": "cfg_llm_01",
            "provider": llm_provider,
            "is_enabled": True,
            "environment": "cloud" if llm_provider != "fallback" else "offline",
            "key_id_masked": "anthropic_****" if settings.ANTHROPIC_API_KEY else "deterministic_offline",
            "webhook_secret_masked": None,
            "last_synced_at": None,
            "sync_status": "healthy"
        }
    ]


@router.get("/integrations/config")
def get_current_integration_config():
    """
    Returns current configuration values with secrets masked for display in Settings.
    """
    return {
        "dispute_source": settings.DISPUTE_SOURCE,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_key_secret_masked": "****" + settings.RAZORPAY_KEY_SECRET[-4:] if len(settings.RAZORPAY_KEY_SECRET) >= 4 else ("configured" if settings.RAZORPAY_KEY_SECRET else ""),
        "razorpay_webhook_secret_masked": "****" + settings.RAZORPAY_WEBHOOK_SECRET[-4:] if len(settings.RAZORPAY_WEBHOOK_SECRET) >= 4 else ("configured" if settings.RAZORPAY_WEBHOOK_SECRET else ""),
        "llm_provider": settings.LLM_PROVIDER,
        "anthropic_api_key_masked": "****" + settings.ANTHROPIC_API_KEY[-4:] if len(settings.ANTHROPIC_API_KEY) >= 4 else ("configured" if settings.ANTHROPIC_API_KEY else "")
    }


@router.put("/integrations/config")
def update_integration_config(payload: IntegrationUpdateRequest, db: Session = Depends(get_db_session)):
    """
    Updates the active gateway and LLM configuration dynamically and logs to audit trail.
    """
    settings.DISPUTE_SOURCE = payload.dispute_source

    if payload.razorpay_key_id is not None:
        settings.RAZORPAY_KEY_ID = payload.razorpay_key_id.strip()

    if payload.razorpay_key_secret:
        settings.RAZORPAY_KEY_SECRET = payload.razorpay_key_secret.strip()

    if payload.razorpay_webhook_secret:
        settings.RAZORPAY_WEBHOOK_SECRET = payload.razorpay_webhook_secret.strip()

    if payload.llm_provider:
        settings.LLM_PROVIDER = payload.llm_provider

    if payload.anthropic_api_key:
        settings.ANTHROPIC_API_KEY = payload.anthropic_api_key.strip()

    # Update database records
    merchant = db.query(Merchant).first()
    merchant_id = merchant.id if merchant else "mer_rjkitchen_01"

    rzp_cfg = db.query(IntegrationConfig).filter(IntegrationConfig.provider == "razorpay").first()
    if rzp_cfg:
        rzp_cfg.is_enabled = (settings.DISPUTE_SOURCE == "razorpay")
        if settings.RAZORPAY_KEY_ID:
            rzp_cfg.key_id_masked = settings.RAZORPAY_KEY_ID[:8] + "****"
            rzp_cfg.sync_status = "healthy"
        else:
            rzp_cfg.sync_status = "disconnected"
        rzp_cfg.last_synced_at = datetime.now(timezone.utc)

    mock_cfg = db.query(IntegrationConfig).filter(IntegrationConfig.provider == "mock").first()
    if mock_cfg:
        mock_cfg.is_enabled = (settings.DISPUTE_SOURCE == "mock")
        mock_cfg.last_synced_at = datetime.now(timezone.utc)

    # Log to audit log
    audit = AuditLog(
        id=f"aud_cfg_{int(datetime.now(timezone.utc).timestamp())}",
        merchant_id=merchant_id,
        user_id="usr_rohit_01",
        action="INTEGRATION_SETTINGS_UPDATED",
        resource_type="integrations",
        resource_id=settings.DISPUTE_SOURCE,
        details={
            "dispute_source": settings.DISPUTE_SOURCE,
            "razorpay_configured": bool(settings.RAZORPAY_KEY_ID),
            "llm_provider": settings.LLM_PROVIDER
        },
        ip_address="127.0.0.1",
        created_at=datetime.now(timezone.utc)
    )
    db.add(audit)
    db.commit()

    # Persist updated values to .env so changes survive restarts
    try:
        from dotenv import set_key
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        env_file_path = os.path.join(project_root, ".env")
        if not os.path.exists(env_file_path):
            example_path = os.path.join(project_root, ".env.example")
            if os.path.exists(example_path):
                shutil.copyfile(example_path, env_file_path)
            else:
                with open(env_file_path, "w") as f:
                    pass

        set_key(env_file_path, "DISPUTE_SOURCE", settings.DISPUTE_SOURCE)
        if payload.razorpay_key_id is not None:
            set_key(env_file_path, "RAZORPAY_KEY_ID", settings.RAZORPAY_KEY_ID)
        if payload.razorpay_key_secret:
            set_key(env_file_path, "RAZORPAY_KEY_SECRET", settings.RAZORPAY_KEY_SECRET)
        if payload.razorpay_webhook_secret:
            set_key(env_file_path, "RAZORPAY_WEBHOOK_SECRET", settings.RAZORPAY_WEBHOOK_SECRET)
        if payload.llm_provider:
            set_key(env_file_path, "LLM_PROVIDER", settings.LLM_PROVIDER)
        if payload.anthropic_api_key:
            set_key(env_file_path, "ANTHROPIC_API_KEY", settings.ANTHROPIC_API_KEY)
    except Exception as e:
        logger.warning(f"Could not write settings to .env file: {e}")

    return {
        "success": True,
        "message": f"Integration settings saved! Active dispute source is now '{settings.DISPUTE_SOURCE.upper()}'.",
        "config": {
            "dispute_source": settings.DISPUTE_SOURCE,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "llm_provider": settings.LLM_PROVIDER
        }
    }


@router.post("/integrations/test-credentials")
def test_gateway_credentials(payload: TestConnectionRequest):
    """
    Tests live credentials against Razorpay /v1/payments endpoint.
    """
    key_id = payload.key_id.strip()
    key_secret = payload.key_secret.strip()

    if not key_id or not key_secret:
        raise HTTPException(status_code=400, detail="Key ID and Key Secret must both be provided.")

    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get("https://api.razorpay.com/v1/payments", auth=(key_id, key_secret), params={"count": 1})
            if resp.status_code == 200:
                return {
                    "success": True,
                    "status_code": 200,
                    "message": "Successfully authenticated with Razorpay Test Gateway!"
                }
            elif resp.status_code == 401:
                return {
                    "success": False,
                    "status_code": 401,
                    "message": "Authentication failed (HTTP 401). Please verify your Razorpay Key ID and Secret."
                }
            else:
                return {
                    "success": False,
                    "status_code": resp.status_code,
                    "message": f"Gateway responded with status {resp.status_code}: {resp.text}"
                }
    except Exception as e:
        return {
            "success": False,
            "status_code": 500,
            "message": f"Connection error: {str(e)}"
        }


@router.post("/integrations/diagnostics")
def run_diagnostics() -> Dict[str, Any]:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dispute_source": {
            "mode": settings.DISPUTE_SOURCE,
            "status": "ready",
            "description": f"Engine active in {settings.DISPUTE_SOURCE.upper()} mode."
        },
        "razorpay_gateway": {
            "configured": bool(settings.RAZORPAY_KEY_ID),
            "key_id": settings.RAZORPAY_KEY_ID[:8] + "****" if settings.RAZORPAY_KEY_ID else "not_configured",
            "status": "operational" if settings.RAZORPAY_KEY_ID else "unconfigured_safe_mock_active"
        },
        "llm_engine": {
            "provider": settings.LLM_PROVIDER,
            "fallback_active": settings.LLM_PROVIDER == "fallback" or not settings.ANTHROPIC_API_KEY,
            "status": "ready"
        }
    }
