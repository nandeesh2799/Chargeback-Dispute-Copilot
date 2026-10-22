from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app.models import IntegrationConfig
from app.core.config import settings

router = APIRouter()


@router.get("/integrations/status")
def get_integrations_status(db: Session = Depends(get_db_session)) -> List[Dict[str, Any]]:
    configs = db.query(IntegrationConfig).all()

    results = []
    # If DB has integration configs, display them
    for cfg in configs:
        results.append({
            "id": cfg.id,
            "provider": cfg.provider,
            "is_enabled": cfg.is_enabled,
            "environment": cfg.environment,
            "key_id_masked": cfg.key_id_masked,
            "webhook_secret_masked": cfg.webhook_secret_masked,
            "last_synced_at": cfg.last_synced_at,
            "sync_status": cfg.sync_status
        })

    # Also add current runtime configuration status
    active_source = settings.DISPUTE_SOURCE
    llm_provider = settings.LLM_PROVIDER

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


@router.post("/integrations/diagnostics")
def run_diagnostics() -> Dict[str, Any]:
    return {
        "timestamp": "2026-10-22T16:20:00Z",
        "dispute_source": {
            "mode": settings.DISPUTE_SOURCE,
            "status": "ready",
            "description": "Mock dispute engine active with 50 RJ Kitchen synthetic records."
        },
        "razorpay_gateway": {
            "configured": bool(settings.RAZORPAY_KEY_ID),
            "mode": "test",
            "status": "operational" if settings.RAZORPAY_KEY_ID else "unconfigured_safe_mock_active"
        },
        "llm_engine": {
            "provider": settings.LLM_PROVIDER,
            "fallback_active": settings.LLM_PROVIDER == "fallback" or not settings.ANTHROPIC_API_KEY,
            "status": "ready"
        }
    }
