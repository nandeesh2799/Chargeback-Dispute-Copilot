from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app.models import ResponseDraft, Dispute, EvidenceReadiness
from app.schemas.domain import ResponseDraftSchema, DraftUpdateRequest

router = APIRouter()


@router.get("/disputes/{dispute_id}/draft", response_model=ResponseDraftSchema)
def get_draft(dispute_id: str, db: Session = Depends(get_db_session)):
    draft = db.query(ResponseDraft).filter(ResponseDraft.dispute_id == dispute_id).order_by(ResponseDraft.version.desc()).first()
    if not draft:
        raise HTTPException(status_code=404, detail="No response draft found for this dispute")

    return {
        "id": draft.id,
        "dispute_id": draft.dispute_id,
        "contest_summary": draft.contest_summary,
        "representation_letter": draft.representation_letter,
        "cited_evidence_ids": draft.cited_evidence_ids or [],
        "version": draft.version,
        "is_approved": draft.is_approved,
        "created_at": draft.created_at,
        "updated_at": draft.updated_at
    }


@router.patch("/disputes/{dispute_id}/draft", response_model=ResponseDraftSchema)
def update_draft(dispute_id: str, payload: DraftUpdateRequest, db: Session = Depends(get_db_session)):
    # Validate Razorpay contest summary character length
    if len(payload.contest_summary) > 1000:
        raise HTTPException(status_code=400, detail=f"Contest summary exceeds strict Razorpay 1,000-character limit ({len(payload.contest_summary)} chars)")

    draft = db.query(ResponseDraft).filter(ResponseDraft.dispute_id == dispute_id).order_by(ResponseDraft.version.desc()).first()
    if not draft:
        # Create draft if missing
        draft = ResponseDraft(
            id=f"draft_{dispute_id.replace('disp_', '')}",
            dispute_id=dispute_id,
            contest_summary=payload.contest_summary,
            representation_letter=payload.representation_letter,
            cited_evidence_ids=payload.cited_evidence_ids or [],
            version=1,
            is_approved=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(draft)
    else:
        draft.contest_summary = payload.contest_summary
        draft.representation_letter = payload.representation_letter
        if payload.cited_evidence_ids is not None:
            draft.cited_evidence_ids = payload.cited_evidence_ids
        draft.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(draft)

    return {
        "id": draft.id,
        "dispute_id": draft.dispute_id,
        "contest_summary": draft.contest_summary,
        "representation_letter": draft.representation_letter,
        "cited_evidence_ids": draft.cited_evidence_ids or [],
        "version": draft.version,
        "is_approved": draft.is_approved,
        "created_at": draft.created_at,
        "updated_at": draft.updated_at
    }


@router.post("/disputes/{dispute_id}/draft/approve", response_model=ResponseDraftSchema)
def approve_draft(dispute_id: str, db: Session = Depends(get_db_session)):
    draft = db.query(ResponseDraft).filter(ResponseDraft.dispute_id == dispute_id).order_by(ResponseDraft.version.desc()).first()
    if not draft:
        raise HTTPException(status_code=404, detail="No response draft found to approve")

    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    draft.is_approved = True
    draft.updated_at = datetime.now(timezone.utc)

    if dispute:
        dispute.evidence_readiness = EvidenceReadiness.READY_TO_SUBMIT

    db.commit()
    db.refresh(draft)

    return {
        "id": draft.id,
        "dispute_id": draft.dispute_id,
        "contest_summary": draft.contest_summary,
        "representation_letter": draft.representation_letter,
        "cited_evidence_ids": draft.cited_evidence_ids or [],
        "version": draft.version,
        "is_approved": draft.is_approved,
        "created_at": draft.created_at,
        "updated_at": draft.updated_at
    }
