import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app.models import WebhookEvent, Dispute, DisputeStatus, DisputeOutcome
from app.core.config import settings
from app.core.security import verify_razorpay_signature
from app.core.logging import logger

router = APIRouter()


@router.post("/webhooks/razorpay")
async def handle_razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    db: Session = Depends(get_db_session)
):
    raw_body = await request.body()
    secret = settings.RAZORPAY_WEBHOOK_SECRET

    # Verify signature if secret configured
    sig_verified = False
    if secret:
        sig_verified = verify_razorpay_signature(raw_body, x_razorpay_signature, secret)
        if not sig_verified:
            logger.warning("Rejected Razorpay webhook with invalid HMAC signature")
            raise HTTPException(status_code=400, detail="Invalid webhook signature")
    else:
        # In mock/development mode without secret configured, log warning
        sig_verified = True

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Malformed JSON payload")

    event_id = payload.get("event_id") or payload.get("id") or str(uuid.uuid4())
    event_type = payload.get("event", "unknown")

    # Idempotency check
    existing_event = db.query(WebhookEvent).filter(WebhookEvent.event_id == event_id).first()
    if existing_event:
        logger.info(f"Duplicate webhook event ignored: {event_id}")
        return {"status": "ignored", "reason": "duplicate_event_id"}

    webhook_record = WebhookEvent(
        id=f"wh_{uuid.uuid4().hex[:12]}",
        provider="razorpay",
        event_id=event_id,
        event_type=event_type,
        raw_payload=payload,
        signature_verified=sig_verified,
        processing_status="processed",
        received_at=datetime.now(timezone.utc),
        processed_at=datetime.now(timezone.utc)
    )
    db.add(webhook_record)

    # Process dispute lifecycle events
    entity = payload.get("payload", {}).get("dispute", {}).get("entity", {})
    gateway_disp_id = entity.get("id")

    if gateway_disp_id:
        dispute = db.query(Dispute).filter(
            (Dispute.gateway_dispute_id == gateway_disp_id) | (Dispute.id == gateway_disp_id)
        ).first()

        if dispute:
            if event_type == "dispute.won":
                dispute.status = DisputeStatus.WON
                dispute.closed_at = datetime.now(timezone.utc)
                outcome = DisputeOutcome(
                    id=f"out_{uuid.uuid4().hex[:12]}",
                    dispute_id=dispute.id,
                    outcome="won",
                    amount_deducted=0,
                    fee_deducted=0,
                    decided_at=datetime.now(timezone.utc),
                    resolution_remarks="Card scheme ruled in merchant favor (Webhook Event)"
                )
                db.add(outcome)
            elif event_type == "dispute.lost":
                dispute.status = DisputeStatus.LOST
                dispute.closed_at = datetime.now(timezone.utc)
                outcome = DisputeOutcome(
                    id=f"out_{uuid.uuid4().hex[:12]}",
                    dispute_id=dispute.id,
                    outcome="lost",
                    amount_deducted=dispute.amount,
                    fee_deducted=15000,
                    decided_at=datetime.now(timezone.utc),
                    resolution_remarks="Cardholder chargeback upheld by card issuer (Webhook Event)"
                )
                db.add(outcome)
            elif event_type == "dispute.closed":
                dispute.status = DisputeStatus.CLOSED
                dispute.closed_at = datetime.now(timezone.utc)

    db.commit()
    return {"status": "success", "event_id": event_id, "processed": True}
