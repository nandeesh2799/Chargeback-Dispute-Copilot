import csv
import io
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app.repositories.dispute_repo import DisputeRepository
from app.agents.investigation_agent import DisputeInvestigationAgent
from app.scoring.pipeline import ExplainableScoringPipeline
from app.exports.pdf_generator import generate_dispute_pdf_report
from app.integrations.mock_source import MockDisputeSource
from app.integrations.razorpay.client import RazorpayDisputeSource
from app.core.config import settings
from app.schemas.domain import (
    DisputeListSchema, DisputeDetailSchema, AIInvestigationSchema, ScoringResultSchema
)
from app.models import Dispute, Order, Payment, Customer, FulfilmentRecord, CustomerMessage, ResponseDraft, ScoringResult, DisputeStatus

router = APIRouter()


@router.get("/disputes", response_model=List[DisputeListSchema])
def list_disputes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    reason: Optional[str] = None,
    readiness: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    response: Response = None,
    db: Session = Depends(get_db_session)
):
    disputes, total = DisputeRepository.get_disputes(
        db, skip=skip, limit=limit, status=status, reason=reason,
        readiness=readiness, search=search, sort_by=sort_by, sort_dir=sort_dir
    )

    if response:
        response.headers["X-Total-Count"] = str(total)
        response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"

    results = []
    for d in disputes:
        results.append({
            "id": d.id,
            "order_id": d.order_id,
            "order_number": d.order.order_number if d.order else "N/A",
            "payment_id": d.payment_id,
            "customer_name": d.customer.name if d.customer else "N/A",
            "customer_email": d.customer.email if d.customer else "N/A",
            "amount": d.amount,
            "currency": d.currency,
            "reason_code": d.reason_code,
            "reason_description": d.reason_description,
            "status": d.status.value if hasattr(d.status, "value") else str(d.status),
            "phase": d.phase.value if hasattr(d.phase, "value") else str(d.phase),
            "evidence_readiness": d.evidence_readiness.value if hasattr(d.evidence_readiness, "value") else str(d.evidence_readiness),
            "evidence_completeness_pct": d.evidence_completeness_pct,
            "win_probability_score": d.win_probability_score,
            "win_score_tier": d.win_score_tier.value if d.win_score_tier else None,
            "response_deadline": d.response_deadline,
            "is_synthetic": d.is_synthetic,
            "created_at": d.created_at,
            "updated_at": d.updated_at
        })
    return results


@router.get("/disputes/export/csv")
def export_disputes_csv(
    status: Optional[str] = None,
    reason: Optional[str] = None,
    db: Session = Depends(get_db_session)
):
    disputes, _ = DisputeRepository.get_disputes(db, skip=0, limit=500, status=status, reason=reason)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Dispute ID", "Order Ref", "Customer Name", "Amount (INR)", "Reason", "Status", "Deadline", "Win Score", "Completeness %"])

    for d in disputes:
        amt_fmt = f"{d.amount / 100:.2f}"
        writer.writerow([
            d.id,
            d.order.order_number if d.order else "N/A",
            d.customer.name if d.customer else "N/A",
            amt_fmt,
            d.reason_code,
            d.status.value if hasattr(d.status, "value") else str(d.status),
            d.response_deadline.strftime("%Y-%m-%d %H:%M"),
            f"{d.win_probability_score:.1f}%" if d.win_probability_score else "N/A",
            f"{d.evidence_completeness_pct:.0f}%"
        ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=disputes_export.csv"}
    )


@router.get("/disputes/{dispute_id}", response_model=DisputeDetailSchema)
def get_dispute_detail(dispute_id: str, db: Session = Depends(get_db_session)):
    d = DisputeRepository.get_dispute_by_id(db, dispute_id)
    if not d:
        raise HTTPException(status_code=404, detail="Dispute not found")

    fulfilment = d.order.fulfilment_records[0] if (d.order and d.order.fulfilment_records) else None
    latest_draft = d.drafts[-1] if d.drafts else None

    # Map evidence links
    evidence_links_data = []
    for el in d.evidence_links:
        ei = el.evidence_item
        evidence_links_data.append({
            "id": el.id,
            "dispute_id": el.dispute_id,
            "evidence_id": el.evidence_id,
            "relevance_note": el.relevance_note,
            "linked_at": el.linked_at,
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

    return {
        "id": d.id,
        "order_id": d.order_id,
        "order_number": d.order.order_number if d.order else "N/A",
        "payment_id": d.payment_id,
        "customer_name": d.customer.name if d.customer else "N/A",
        "customer_email": d.customer.email if d.customer else "N/A",
        "amount": d.amount,
        "currency": d.currency,
        "reason_code": d.reason_code,
        "reason_description": d.reason_description,
        "status": d.status.value if hasattr(d.status, "value") else str(d.status),
        "phase": d.phase.value if hasattr(d.phase, "value") else str(d.phase),
        "evidence_readiness": d.evidence_readiness.value if hasattr(d.evidence_readiness, "value") else str(d.evidence_readiness),
        "evidence_completeness_pct": d.evidence_completeness_pct,
        "win_probability_score": d.win_probability_score,
        "win_score_tier": d.win_score_tier.value if d.win_score_tier else None,
        "response_deadline": d.response_deadline,
        "is_synthetic": d.is_synthetic,
        "created_at": d.created_at,
        "updated_at": d.updated_at,
        "customer": {
            "id": d.customer.id,
            "name": d.customer.name,
            "email": d.customer.email,
            "phone": d.customer.phone,
            "is_synthetic": d.customer.is_synthetic
        },
        "order": {
            "id": d.order.id,
            "order_number": d.order.order_number,
            "amount": d.order.amount,
            "currency": d.order.currency,
            "status": d.order.status.value if hasattr(d.order.status, "value") else str(d.order.status),
            "item_summary": d.order.item_summary or {},
            "ordered_at": d.order.ordered_at,
            "cancelled_at": d.order.cancelled_at,
            "cancellation_reason": d.order.cancellation_reason
        },
        "payment": {
            "id": d.payment.id,
            "order_id": d.payment.order_id,
            "provider": d.payment.provider,
            "gateway_payment_id": d.payment.gateway_payment_id,
            "amount": d.payment.amount,
            "currency": d.payment.currency,
            "method": d.payment.method,
            "card_network": d.payment.card_network,
            "card_last4": d.payment.card_last4,
            "bank_name": d.payment.bank_name,
            "upi_vpa": d.payment.upi_vpa,
            "status": d.payment.status.value if hasattr(d.payment.status, "value") else str(d.payment.status),
            "captured_at": d.payment.captured_at,
            "refund_status": d.payment.refund_status,
            "amount_refunded": d.payment.amount_refunded,
            "is_synthetic": d.payment.is_synthetic
        },
        "fulfilment": {
            "id": fulfilment.id,
            "order_id": fulfilment.order_id,
            "carrier": fulfilment.carrier,
            "tracking_number": fulfilment.tracking_number,
            "status": fulfilment.status.value if hasattr(fulfilment.status, "value") else str(fulfilment.status),
            "dispatch_at": fulfilment.dispatch_at,
            "delivered_at": fulfilment.delivered_at,
            "delivery_proof_type": fulfilment.delivery_proof_type.value if hasattr(fulfilment.delivery_proof_type, "value") else str(fulfilment.delivery_proof_type),
            "delivery_otp_entered": fulfilment.delivery_otp_entered,
            "delivery_address": fulfilment.delivery_address,
            "recipient_name": fulfilment.recipient_name,
            "notes": fulfilment.notes
        } if fulfilment else None,
        "messages": [
            {
                "id": m.id,
                "order_id": m.order_id,
                "customer_id": m.customer_id,
                "direction": m.direction,
                "channel": m.channel,
                "sender_name": m.sender_name,
                "content": m.content,
                "sent_at": m.sent_at
            }
            for m in d.customer_messages
        ],
        "evidence_links": evidence_links_data,
        "investigation": {
            "id": d.investigation.id,
            "dispute_id": d.investigation.dispute_id,
            "investigation_status": d.investigation.investigation_status.value if hasattr(d.investigation.investigation_status, "value") else str(d.investigation.investigation_status),
            "normalized_reason": d.investigation.normalized_reason,
            "findings_summary": d.investigation.findings_summary,
            "checklist_audit": d.investigation.checklist_audit or {},
            "contradictions": d.investigation.contradictions or [],
            "facts_extracted": d.investigation.facts_extracted or [],
            "model_provider": d.investigation.model_provider,
            "model_version": d.investigation.model_version,
            "execution_duration_ms": d.investigation.execution_duration_ms,
            "created_at": d.investigation.created_at
        } if d.investigation else None,
        "latest_draft": {
            "id": latest_draft.id,
            "dispute_id": latest_draft.dispute_id,
            "contest_summary": latest_draft.contest_summary,
            "representation_letter": latest_draft.representation_letter,
            "cited_evidence_ids": latest_draft.cited_evidence_ids or [],
            "version": latest_draft.version,
            "is_approved": latest_draft.is_approved,
            "created_at": latest_draft.created_at,
            "updated_at": latest_draft.updated_at
        } if latest_draft else None,
        "scoring": {
            "id": d.scoring.id,
            "dispute_id": d.scoring.dispute_id,
            "score": d.scoring.score,
            "tier": d.scoring.tier.value if hasattr(d.scoring.tier, "value") else str(d.scoring.tier),
            "model_name": d.scoring.model_name,
            "model_version": d.scoring.model_version,
            "top_positive_factors": d.scoring.top_positive_factors or [],
            "top_negative_factors": d.scoring.top_negative_factors or [],
            "missing_information_penalties": d.scoring.missing_information_penalties or [],
            "feature_vector": d.scoring.feature_vector or {},
            "is_calibrated": d.scoring.is_calibrated,
            "calibration_note": d.scoring.calibration_note,
            "evaluated_at": d.scoring.evaluated_at
        } if d.scoring else None
    }


@router.post("/disputes/{dispute_id}/investigate", response_model=AIInvestigationSchema)
def trigger_investigation(dispute_id: str, db: Session = Depends(get_db_session)):
    agent = DisputeInvestigationAgent(db=db, model_provider=settings.LLM_PROVIDER)
    try:
        inv = agent.run_investigation(dispute_id)
        return {
            "id": inv.id,
            "dispute_id": inv.dispute_id,
            "investigation_status": inv.investigation_status.value if hasattr(inv.investigation_status, "value") else str(inv.investigation_status),
            "normalized_reason": inv.normalized_reason,
            "findings_summary": inv.findings_summary,
            "checklist_audit": inv.checklist_audit or {},
            "contradictions": inv.contradictions or [],
            "facts_extracted": inv.facts_extracted or [],
            "model_provider": inv.model_provider,
            "model_version": inv.model_version,
            "execution_duration_ms": inv.execution_duration_ms,
            "created_at": inv.created_at
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/disputes/{dispute_id}/score", response_model=ScoringResultSchema)
def calculate_score(dispute_id: str, db: Session = Depends(get_db_session)):
    d = DisputeRepository.get_dispute_by_id(db, dispute_id)
    if not d:
        raise HTTPException(status_code=404, detail="Dispute not found")

    fulfilment = d.order.fulfilment_records[0] if (d.order and d.order.fulfilment_records) else None
    pipeline = ExplainableScoringPipeline()
    features = pipeline.extract_features(d, d.order, d.payment, fulfilment, d.customer_messages, d.investigation)
    score_data = pipeline.predict_score(features)

    # Persist in DB
    existing_score = db.query(ScoringResult).filter(ScoringResult.dispute_id == dispute_id).first()
    if existing_score:
        existing_score.score = score_data["score"]
        existing_score.tier = score_data["tier"]
        existing_score.top_positive_factors = score_data["top_positive_factors"]
        existing_score.top_negative_factors = score_data["top_negative_factors"]
        existing_score.feature_vector = score_data["feature_vector"]
    else:
        existing_score = ScoringResult(
            id=f"score_{dispute_id.replace('disp_', '')}",
            dispute_id=dispute_id,
            score=score_data["score"],
            tier=score_data["tier"],
            model_name=score_data["model_name"],
            model_version=score_data["model_version"],
            top_positive_factors=score_data["top_positive_factors"],
            top_negative_factors=score_data["top_negative_factors"],
            missing_information_penalties=score_data["missing_information_penalties"],
            feature_vector=score_data["feature_vector"],
            is_calibrated=score_data["is_calibrated"],
            calibration_note=score_data["calibration_note"]
        )
        db.add(existing_score)

    d.win_probability_score = score_data["score"]
    d.win_score_tier = score_data["tier"]
    db.commit()

    return {
        "id": existing_score.id,
        "dispute_id": dispute_id,
        "score": score_data["score"],
        "tier": score_data["tier"],
        "model_name": score_data["model_name"],
        "model_version": score_data["model_version"],
        "top_positive_factors": score_data["top_positive_factors"],
        "top_negative_factors": score_data["top_negative_factors"],
        "missing_information_penalties": score_data["missing_information_penalties"],
        "feature_vector": score_data["feature_vector"],
        "is_calibrated": score_data["is_calibrated"],
        "calibration_note": score_data["calibration_note"],
        "evaluated_at": existing_score.evaluated_at
    }


@router.get("/disputes/{dispute_id}/report")
def download_pdf_report(dispute_id: str, db: Session = Depends(get_db_session)):
    d = DisputeRepository.get_dispute_by_id(db, dispute_id)
    if not d:
        raise HTTPException(status_code=404, detail="Dispute not found")

    fulfilment = d.order.fulfilment_records[0] if (d.order and d.order.fulfilment_records) else None
    latest_draft = d.drafts[-1] if d.drafts else None

    pdf_bytes = generate_dispute_pdf_report(
        dispute=d,
        order=d.order,
        payment=d.payment,
        customer=d.customer,
        fulfilment=fulfilment,
        investigation=d.investigation,
        draft=latest_draft,
        scoring=d.scoring
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=dispute_report_{dispute_id}.pdf"}
    )


@router.post("/disputes/{dispute_id}/contest")
def submit_contest(dispute_id: str, db: Session = Depends(get_db_session)):
    d = DisputeRepository.get_dispute_by_id(db, dispute_id)
    if not d:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # State-machine guard: only contestable statuses may proceed
    contestable_statuses = {
        DisputeStatus.OPEN,
        DisputeStatus.UNDER_REVIEW,
        DisputeStatus.EVIDENCE_READY,
        DisputeStatus.CONTESTED,
    }
    if d.status not in contestable_statuses:
        status_val = d.status.value if hasattr(d.status, "value") else str(d.status)
        raise HTTPException(
            status_code=409,
            detail=f"Dispute cannot be contested in status '{status_val}'. Must be open, under_review, evidence_ready, or contested."
        )

    latest_draft = d.drafts[-1] if d.drafts else None
    summary = latest_draft.contest_summary if latest_draft else "Merchant contests dispute with attached proof of delivery."
    doc_ids = latest_draft.cited_evidence_ids if latest_draft else []

    if settings.DISPUTE_SOURCE == "razorpay" and not d.is_synthetic:
        provider = RazorpayDisputeSource()
    else:
        provider = MockDisputeSource(db=db)

    try:
        result = provider.submit_contest(dispute_id, summary, doc_ids)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
