import json
import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from datetime import datetime
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import (
    Merchant, User, Customer, Order, Payment, FulfilmentRecord,
    CustomerMessage, Dispute, EvidenceItem, EvidenceLink,
    AIInvestigation, ResponseDraft, ScoringResult, DisputeOutcome,
    IntegrationConfig, AuditLog,
    OrderStatus, PaymentStatus, FulfilmentStatus, DeliveryProofType,
    DisputeStatus, DisputePhase, EvidenceReadiness, WinScoreTier,
    EvidenceType, EvidenceVerificationStatus, EvidenceSource, InvestigationStatus
)
from data.synthetic.generator import generate_rj_kitchen_fixtures


def seed_database(db: Session, force_reset: bool = True) -> int:
    """
    Populate database with 50 deterministic synthetic disputes and linked entities for RJ Kitchen.
    """
    if force_reset:
        # Recreate tables cleanly
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    fixtures = generate_rj_kitchen_fixtures(seed=42)

    # 1. Merchant
    m_data = fixtures["merchant"]
    merchant = Merchant(
        id=m_data["id"],
        name=m_data["name"],
        legal_entity_name=m_data["legal_entity_name"],
        default_currency=m_data["default_currency"],
        timezone=m_data["timezone"],
        created_at=datetime.fromisoformat(m_data["created_at"]),
        updated_at=datetime.fromisoformat(m_data["updated_at"])
    )
    db.add(merchant)
    db.flush()

    # 2. Users
    for u in fixtures["users"]:
        user = User(
            id=u["id"],
            merchant_id=u["merchant_id"],
            email=u["email"],
            name=u["name"],
            role=u["role"],
            is_active=u["is_active"],
            created_at=datetime.fromisoformat(u["created_at"])
        )
        db.add(user)

    # 3. Customers
    for c in fixtures["customers"]:
        cust = Customer(
            id=c["id"],
            merchant_id=c["merchant_id"],
            name=c["name"],
            email=c["email"],
            phone=c["phone"],
            is_synthetic=c["is_synthetic"],
            created_at=datetime.fromisoformat(c["created_at"])
        )
        db.add(cust)

    # 4. Orders
    for o in fixtures["orders"]:
        order = Order(
            id=o["id"],
            merchant_id=o["merchant_id"],
            customer_id=o["customer_id"],
            order_number=o["order_number"],
            amount=o["amount"],
            currency=o["currency"],
            status=OrderStatus(o["status"]),
            item_summary=o["item_summary"],
            ordered_at=datetime.fromisoformat(o["ordered_at"]),
            cancelled_at=datetime.fromisoformat(o["cancelled_at"]) if o["cancelled_at"] else None,
            cancellation_reason=o["cancellation_reason"]
        )
        db.add(order)

    # 5. Payments
    for p in fixtures["payments"]:
        payment = Payment(
            id=p["id"],
            merchant_id=p["merchant_id"],
            order_id=p["order_id"],
            provider=p["provider"],
            gateway_payment_id=p["gateway_payment_id"],
            amount=p["amount"],
            currency=p["currency"],
            method=p["method"],
            card_network=p["card_network"],
            card_last4=p["card_last4"],
            bank_name=p["bank_name"],
            upi_vpa=p["upi_vpa"],
            status=PaymentStatus(p["status"]),
            captured_at=datetime.fromisoformat(p["captured_at"]) if p["captured_at"] else None,
            refund_status=p["refund_status"],
            amount_refunded=p["amount_refunded"],
            is_synthetic=p["is_synthetic"]
        )
        db.add(payment)

    # 6. Fulfilment
    for f in fixtures["fulfilments"]:
        ful = FulfilmentRecord(
            id=f["id"],
            order_id=f["order_id"],
            carrier=f["carrier"],
            tracking_number=f["tracking_number"],
            status=FulfilmentStatus(f["status"]),
            dispatch_at=datetime.fromisoformat(f["dispatch_at"]) if f["dispatch_at"] else None,
            delivered_at=datetime.fromisoformat(f["delivered_at"]) if f["delivered_at"] else None,
            delivery_proof_type=DeliveryProofType(f["delivery_proof_type"]),
            delivery_otp_entered=f["delivery_otp_entered"],
            delivery_address=f["delivery_address"],
            recipient_name=f["recipient_name"],
            notes=f["notes"]
        )
        db.add(ful)

    # 7. Customer Messages
    for m in fixtures["customer_messages"]:
        msg = CustomerMessage(
            id=m["id"],
            dispute_id=m["dispute_id"],
            order_id=m["order_id"],
            customer_id=m["customer_id"],
            direction=m["direction"],
            channel=m["channel"],
            sender_name=m["sender_name"],
            content=m["content"],
            sent_at=datetime.fromisoformat(m["sent_at"])
        )
        db.add(msg)

    # 8. Disputes
    for d in fixtures["disputes"]:
        disp = Dispute(
            id=d["id"],
            merchant_id=d["merchant_id"],
            payment_id=d["payment_id"],
            order_id=d["order_id"],
            customer_id=d["customer_id"],
            gateway_dispute_id=d["gateway_dispute_id"],
            provider=d["provider"],
            amount=d["amount"],
            currency=d["currency"],
            reason_code=d["reason_code"],
            reason_description=d["reason_description"],
            status=DisputeStatus(d["status"]),
            phase=DisputePhase(d["phase"]),
            evidence_readiness=EvidenceReadiness(d["evidence_readiness"]),
            evidence_completeness_pct=d["evidence_completeness_pct"],
            win_probability_score=d["win_probability_score"],
            win_score_tier=WinScoreTier(d["win_score_tier"]) if d["win_score_tier"] else None,
            response_deadline=datetime.fromisoformat(d["response_deadline"]),
            contested_at=datetime.fromisoformat(d["contested_at"]) if d["contested_at"] else None,
            closed_at=datetime.fromisoformat(d["closed_at"]) if d["closed_at"] else None,
            is_synthetic=d["is_synthetic"],
            created_at=datetime.fromisoformat(d["created_at"]),
            updated_at=datetime.fromisoformat(d["updated_at"])
        )
        db.add(disp)

    # 9. Evidence Items
    for e in fixtures["evidence_items"]:
        evi = EvidenceItem(
            id=e["id"],
            merchant_id=e["merchant_id"],
            evidence_type=EvidenceType(e["evidence_type"]),
            title=e["title"],
            description=e["description"],
            file_path=e["file_path"],
            file_name=e["file_name"],
            file_size_bytes=e["file_size_bytes"],
            mime_type=e["mime_type"],
            sha256_hash=e["sha256_hash"],
            verification_status=EvidenceVerificationStatus(e["verification_status"]),
            source=EvidenceSource(e["source"]),
            created_at=datetime.fromisoformat(e["created_at"])
        )
        db.add(evi)

    # 10. Evidence Links
    for el in fixtures["evidence_links"]:
        link = EvidenceLink(
            id=el["id"],
            dispute_id=el["dispute_id"],
            evidence_id=el["evidence_id"],
            linked_by=el["linked_by"],
            relevance_note=el["relevance_note"],
            linked_at=datetime.fromisoformat(el["linked_at"])
        )
        db.add(link)

    # 11. AI Investigations
    for inv in fixtures["ai_investigations"]:
        ai_inv = AIInvestigation(
            id=inv["id"],
            dispute_id=inv["dispute_id"],
            investigation_status=InvestigationStatus(inv["investigation_status"]),
            normalized_reason=inv["normalized_reason"],
            findings_summary=inv["findings_summary"],
            checklist_audit=inv["checklist_audit"],
            contradictions=inv["contradictions"],
            facts_extracted=inv["facts_extracted"],
            model_provider=inv["model_provider"],
            model_version=inv["model_version"],
            execution_duration_ms=inv["execution_duration_ms"],
            created_at=datetime.fromisoformat(inv["created_at"]),
            updated_at=datetime.fromisoformat(inv["updated_at"])
        )
        db.add(ai_inv)

    # 12. Response Drafts
    for dr in fixtures["response_drafts"]:
        draft = ResponseDraft(
            id=dr["id"],
            dispute_id=dr["dispute_id"],
            contest_summary=dr["contest_summary"][:1000],
            representation_letter=dr["representation_letter"],
            cited_evidence_ids=dr["cited_evidence_ids"],
            version=dr["version"],
            is_approved=dr["is_approved"],
            approved_by=dr["approved_by"],
            last_edited_by=dr["last_edited_by"],
            created_at=datetime.fromisoformat(dr["created_at"]),
            updated_at=datetime.fromisoformat(dr["updated_at"])
        )
        db.add(draft)

    # 13. Scoring Results
    for sc in fixtures["scoring_results"]:
        score = ScoringResult(
            id=sc["id"],
            dispute_id=sc["dispute_id"],
            score=sc["score"],
            tier=WinScoreTier(sc["tier"]),
            model_name=sc["model_name"],
            model_version=sc["model_version"],
            top_positive_factors=sc["top_positive_factors"],
            top_negative_factors=sc["top_negative_factors"],
            missing_information_penalties=sc["missing_information_penalties"],
            feature_vector=sc["feature_vector"],
            is_calibrated=sc["is_calibrated"],
            calibration_note=sc["calibration_note"],
            evaluated_at=datetime.fromisoformat(sc["evaluated_at"])
        )
        db.add(score)

    # 14. Dispute Outcomes
    for out in fixtures["dispute_outcomes"]:
        outcome = DisputeOutcome(
            id=out["id"],
            dispute_id=out["dispute_id"],
            outcome=out["outcome"],
            amount_deducted=out["amount_deducted"],
            fee_deducted=out["fee_deducted"],
            decided_at=datetime.fromisoformat(out["decided_at"]),
            resolution_remarks=out["resolution_remarks"]
        )
        db.add(outcome)

    # 15. Integration Configs
    for ic in fixtures["integrations"]:
        cfg = IntegrationConfig(
            id=ic["id"],
            merchant_id=ic["merchant_id"],
            provider=ic["provider"],
            is_enabled=ic["is_enabled"],
            key_id_masked=ic["key_id_masked"],
            encrypted_secret=ic["encrypted_secret"],
            webhook_secret_masked=ic["webhook_secret_masked"],
            environment=ic["environment"],
            last_synced_at=datetime.fromisoformat(ic["last_synced_at"]) if ic["last_synced_at"] else None,
            sync_status=ic["sync_status"]
        )
        db.add(cfg)

    # 16. Audit Log
    audit = AuditLog(
        id="aud_seed_init",
        merchant_id=merchant.id,
        user_id="usr_rohit_01",
        action="DATABASE_SEEDED",
        resource_type="system",
        resource_id=merchant.id,
        details={"disputes_seeded": len(fixtures["disputes"]), "merchant": merchant.name},
        ip_address="127.0.0.1",
        created_at=datetime.utcnow()
    )
    db.add(audit)

    db.commit()
    return len(fixtures["disputes"])


if __name__ == "__main__":
    db = SessionLocal()
    try:
        count = seed_database(db, force_reset=True)
        print(f"Successfully seeded database with {count} disputes and all related entities.")
    finally:
        db.close()
