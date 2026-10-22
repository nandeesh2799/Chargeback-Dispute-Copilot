import os
import uuid
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app.models import EvidenceItem, EvidenceLink, Dispute, EvidenceType, EvidenceVerificationStatus, EvidenceSource
from app.schemas.domain import EvidenceItemSchema, EvidenceLinkSchema
from app.core.config import settings
from app.core.security import sanitize_filename, safe_join_path

router = APIRouter()


@router.get("/disputes/{dispute_id}/evidence", response_model=List[EvidenceLinkSchema])
def get_dispute_evidence(dispute_id: str, db: Session = Depends(get_db_session)):
    links = db.query(EvidenceLink).filter(EvidenceLink.dispute_id == dispute_id).all()
    results = []
    for link in links:
        ei = link.evidence_item
        results.append({
            "id": link.id,
            "dispute_id": link.dispute_id,
            "evidence_id": link.evidence_id,
            "relevance_note": link.relevance_note,
            "linked_at": link.linked_at,
            "evidence_item": {
                "id": ei.id,
                "evidence_type": ei.evidence_type.value if hasattr(ei.evidence_type, "value") else str(ei.evidence_type),
                "title": ei.title,
                "description": ei.description,
                "file_path": ei.file_path,
                "file_name": ei.file_name,
                "file_size_bytes": ei.file_size_bytes,
                "mime_type": ei.mime_type,
                "sha256_hash": ei.sha256_hash,
                "verification_status": ei.verification_status.value if hasattr(ei.verification_status, "value") else str(ei.verification_status),
                "source": ei.source.value if hasattr(ei.source, "value") else str(ei.source),
                "created_at": ei.created_at
            } if ei else None
        })
    return results


@router.post("/disputes/{dispute_id}/evidence", response_model=EvidenceLinkSchema)
async def upload_evidence(
    dispute_id: str,
    title: str = Form(...),
    description: str = Form(""),
    evidence_type: str = Form("other"),
    file: UploadFile = File(None),
    db: Session = Depends(get_db_session)
):
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    file_name = None
    file_path = None
    file_size = 0
    mime_type = "application/octet-stream"

    if file:
        clean_name = sanitize_filename(file.filename)
        ext = os.path.splitext(clean_name)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        target_path = safe_join_path(settings.UPLOAD_DIR, unique_name)

        content = await file.read()
        file_size = len(content)

        # Enforce file size limit
        if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB")

        with open(target_path, "wb") as f:
            f.write(content)

        file_name = clean_name
        file_path = f"/uploads/{unique_name}"
        mime_type = file.content_type or mime_type

    evi_id = f"evi_{uuid.uuid4().hex[:12]}"
    evi_item = EvidenceItem(
        id=evi_id,
        merchant_id=dispute.merchant_id,
        evidence_type=EvidenceType(evidence_type) if evidence_type in EvidenceType.__members__.values() else EvidenceType.OTHER,
        title=title,
        description=description,
        file_path=file_path,
        file_name=file_name,
        file_size_bytes=file_size,
        mime_type=mime_type,
        verification_status=EvidenceVerificationStatus.VERIFIED,
        source=EvidenceSource.MANUAL_UPLOAD,
        created_at=datetime.now(timezone.utc)
    )
    db.add(evi_item)

    link = EvidenceLink(
        id=f"link_{uuid.uuid4().hex[:12]}",
        dispute_id=dispute_id,
        evidence_id=evi_id,
        relevance_note="Uploaded via Evidence Management Studio",
        linked_at=datetime.now(timezone.utc)
    )
    db.add(link)

    # Re-evaluate completeness
    dispute.evidence_completeness_pct = min(100.0, dispute.evidence_completeness_pct + 15.0)
    db.commit()
    db.refresh(link)

    return {
        "id": link.id,
        "dispute_id": link.dispute_id,
        "evidence_id": link.evidence_id,
        "relevance_note": link.relevance_note,
        "linked_at": link.linked_at,
        "evidence_item": {
            "id": evi_item.id,
            "evidence_type": evi_item.evidence_type.value,
            "title": evi_item.title,
            "description": evi_item.description,
            "file_path": evi_item.file_path,
            "file_name": evi_item.file_name,
            "file_size_bytes": evi_item.file_size_bytes,
            "mime_type": evi_item.mime_type,
            "sha256_hash": evi_item.sha256_hash,
            "verification_status": evi_item.verification_status.value,
            "source": evi_item.source.value,
            "created_at": evi_item.created_at
        }
    }


@router.delete("/disputes/{dispute_id}/evidence/{evidence_id}")
def delete_evidence_link(dispute_id: str, evidence_id: str, db: Session = Depends(get_db_session)):
    link = db.query(EvidenceLink).filter(
        EvidenceLink.dispute_id == dispute_id,
        EvidenceLink.evidence_id == evidence_id
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Evidence link not found")

    db.delete(link)
    db.commit()
    return {"success": True, "message": "Evidence unlinked successfully"}
