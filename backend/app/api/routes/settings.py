from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app.models import Merchant, AuditLog
from app.services.seeder import seed_database

router = APIRouter()


@router.get("/settings/merchant")
def get_merchant_profile(db: Session = Depends(get_db_session)):
    merchant = db.query(Merchant).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant profile not found")

    return {
        "id": merchant.id,
        "name": merchant.name,
        "legal_entity_name": merchant.legal_entity_name,
        "default_currency": merchant.default_currency,
        "timezone": merchant.timezone,
        "created_at": merchant.created_at,
        "updated_at": merchant.updated_at
    }


@router.post("/settings/demo-reset")
def reset_demo_database(db: Session = Depends(get_db_session)):
    """
    Safely resets the local database and re-seeds 50 synthetic RJ Kitchen disputes.
    """
    count = seed_database(db, force_reset=True)
    return {
        "success": True,
        "message": f"Demo database cleanly reset and seeded with {count} RJ Kitchen dispute fixtures.",
        "disputes_seeded": count
    }


@router.get("/settings/audit-logs")
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db_session)) -> List[Dict[str, Any]]:
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": log.id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details or {},
            "created_at": log.created_at
        }
        for log in logs
    ]
