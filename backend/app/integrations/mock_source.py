from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.integrations.dispute_source import DisputeSource
from app.models import Dispute, DisputeStatus
from app.core.logging import logger


class MockDisputeSource(DisputeSource):
    """
    Deterministic local dispute source backed by SQLite seeded records.
    """

    def __init__(self, db: Session):
        self.db = db

    def list_disputes(self, limit: int = 50, skip: int = 0, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = self.db.query(Dispute)
        if status:
            query = query.filter(Dispute.status == status)
        records = query.offset(skip).limit(limit).all()
        return [
            {
                "id": d.id,
                "amount": d.amount,
                "currency": d.currency,
                "reason_code": d.reason_code,
                "status": d.status.value if hasattr(d.status, "value") else str(d.status),
                "response_deadline": d.response_deadline.isoformat(),
                "is_synthetic": True
            }
            for d in records
        ]

    def get_dispute(self, dispute_id: str) -> Optional[Dict[str, Any]]:
        d = self.db.query(Dispute).filter(Dispute.id == dispute_id).first()
        if not d:
            return None
        return {
            "id": d.id,
            "amount": d.amount,
            "currency": d.currency,
            "reason_code": d.reason_code,
            "status": d.status.value if hasattr(d.status, "value") else str(d.status),
            "response_deadline": d.response_deadline.isoformat(),
            "is_synthetic": True
        }

    def submit_contest(self, dispute_id: str, summary: str, document_ids: List[str]) -> Dict[str, Any]:
        logger.info(f"Mock contest submitted for {dispute_id} with {len(document_ids)} documents")
        d = self.db.query(Dispute).filter(Dispute.id == dispute_id).first()
        if d:
            d.status = DisputeStatus.CONTESTED
            d.contested_at = datetime.now(timezone.utc)
            self.db.commit()

        return {
            "success": True,
            "provider": "mock",
            "dispute_id": dispute_id,
            "status": "contested",
            "message": "Contest recorded in mock database. Synthetic dispute state updated to CONTESTED.",
            "submitted_at": datetime.now(timezone.utc).isoformat()
        }
