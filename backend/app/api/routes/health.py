from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.deps import get_db_session
from app.core.config import settings

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db_session)):
    # Check database connectivity
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "service": "Chargeback & Dispute Copilot API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "dispute_source": settings.DISPUTE_SOURCE,
        "llm_provider": settings.LLM_PROVIDER,
        "database": db_status
    }
