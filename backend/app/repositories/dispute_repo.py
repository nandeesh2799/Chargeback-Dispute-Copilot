from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, asc, or_
from app.models import (
    Dispute, Order, Payment, Customer, FulfilmentRecord,
    CustomerMessage, EvidenceItem, EvidenceLink, AIInvestigation,
    ResponseDraft, ScoringResult, DisputeOutcome,
    DisputeStatus, EvidenceReadiness
)


class DisputeRepository:
    @staticmethod
    def get_disputes(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        reason: Optional[str] = None,
        readiness: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc"
    ) -> Tuple[List[Dispute], int]:
        query = db.query(Dispute).join(Dispute.order).join(Dispute.payment).join(Dispute.customer)

        if status:
            query = query.filter(Dispute.status == status)
        if reason:
            query = query.filter(Dispute.reason_code == reason)
        if readiness:
            query = query.filter(Dispute.evidence_readiness == readiness)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Dispute.id.ilike(search_term),
                    Order.order_number.ilike(search_term),
                    Payment.gateway_payment_id.ilike(search_term),
                    Customer.name.ilike(search_term),
                    Customer.email.ilike(search_term),
                    Dispute.reason_description.ilike(search_term)
                )
            )

        total = query.count()

        # Sorting
        sort_col = getattr(Dispute, sort_by, Dispute.created_at)
        if sort_dir.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        disputes = query.offset(skip).limit(limit).all()
        return disputes, total

    @staticmethod
    def get_dispute_by_id(db: Session, dispute_id: str) -> Optional[Dispute]:
        return db.query(Dispute).filter(Dispute.id == dispute_id).options(
            joinedload(Dispute.customer),
            joinedload(Dispute.order).joinedload(Order.fulfilment_records),
            joinedload(Dispute.payment),
            joinedload(Dispute.customer_messages),
            joinedload(Dispute.evidence_links).joinedload(EvidenceLink.evidence_item),
            joinedload(Dispute.investigation),
            joinedload(Dispute.drafts),
            joinedload(Dispute.scoring),
            joinedload(Dispute.outcome)
        ).first()

    @staticmethod
    def get_dashboard_summary(db: Session) -> Dict[str, Any]:
        all_disputes = db.query(Dispute).all()
        now = datetime.now(timezone.utc)

        total_disputes = len(all_disputes)
        open_disputes = sum(1 for d in all_disputes if d.status in [DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW])
        evidence_ready = sum(1 for d in all_disputes if d.evidence_readiness == EvidenceReadiness.READY_TO_SUBMIT)

        # Amount metrics
        amount_at_risk = sum(d.amount for d in all_disputes if d.status in [DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW, DisputeStatus.EVIDENCE_READY])
        won_amount = sum(d.amount for d in all_disputes if d.status == DisputeStatus.WON)
        lost_amount = sum(d.amount for d in all_disputes if d.status == DisputeStatus.LOST)

        won_count = sum(1 for d in all_disputes if d.status == DisputeStatus.WON)
        decided_count = sum(1 for d in all_disputes if d.status in [DisputeStatus.WON, DisputeStatus.LOST])
        win_rate = (won_count / decided_count * 100.0) if decided_count > 0 else 0.0

        avg_completeness = (
            sum(d.evidence_completeness_pct for d in all_disputes) / total_disputes
        ) if total_disputes > 0 else 0.0

        # Group by reason
        disputes_by_reason: Dict[str, int] = {}
        for d in all_disputes:
            disputes_by_reason[d.reason_code] = disputes_by_reason.get(d.reason_code, 0) + 1

        # Group by status
        disputes_by_status: Dict[str, int] = {}
        for d in all_disputes:
            status_val = d.status.value if hasattr(d.status, "value") else str(d.status)
            disputes_by_status[status_val] = disputes_by_status.get(status_val, 0) + 1

        # Score distribution
        win_score_dist: Dict[str, int] = {"very_low": 0, "low": 0, "medium": 0, "high": 0, "very_high": 0}
        for d in all_disputes:
            tier_val = d.win_score_tier.value if hasattr(d.win_score_tier, "value") else str(d.win_score_tier)
            if tier_val in win_score_dist:
                win_score_dist[tier_val] += 1

        # Urgent queue (open disputes sorted by response_deadline ascending)
        open_list = [d for d in all_disputes if d.status in [DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW]]
        open_list.sort(key=lambda x: x.response_deadline)

        urgent_queue = []
        for d in open_list[:8]:
            deadline_utc = d.response_deadline if d.response_deadline.tzinfo else d.response_deadline.replace(tzinfo=timezone.utc)
            hours_rem = max(0.0, (deadline_utc - now).total_seconds() / 3600.0)
            urgent_queue.append({
                "id": d.id,
                "order_number": d.order.order_number if d.order else "N/A",
                "amount": d.amount,
                "currency": d.currency,
                "reason_code": d.reason_code,
                "status": d.status.value if hasattr(d.status, "value") else str(d.status),
                "response_deadline": d.response_deadline,
                "hours_remaining": round(hours_rem, 1),
                "win_probability_score": d.win_probability_score
            })

        # Recent 7-day trend (chronologically sorted by date key)
        trend_buckets: Dict[str, Dict[str, Any]] = {}
        for d in all_disputes:
            date_key = d.created_at.strftime("%Y-%m-%d")
            if date_key not in trend_buckets:
                trend_buckets[date_key] = {"date": d.created_at.strftime("%b %d"), "opened": 0, "won": 0, "lost": 0}
            trend_buckets[date_key]["opened"] += 1
            if d.status == DisputeStatus.WON:
                trend_buckets[date_key]["won"] += 1
            elif d.status == DisputeStatus.LOST:
                trend_buckets[date_key]["lost"] += 1

        sorted_keys = sorted(trend_buckets.keys())[-7:]
        trend_list = [trend_buckets[k] for k in sorted_keys]

        return {
            "total_disputes": total_disputes,
            "open_disputes": open_disputes,
            "evidence_ready_disputes": evidence_ready,
            "urgent_disputes_count": len([
                d for d in open_list 
                if ((d.response_deadline if d.response_deadline.tzinfo else d.response_deadline.replace(tzinfo=timezone.utc)) - now).total_seconds() < 86400 * 3
            ]),
            "total_amount_at_risk": amount_at_risk,
            "won_amount": won_amount,
            "lost_amount": lost_amount,
            "win_rate_percentage": round(win_rate, 1),
            "average_evidence_completeness": round(avg_completeness, 1),
            "disputes_by_reason": disputes_by_reason,
            "disputes_by_status": disputes_by_status,
            "win_score_distribution": win_score_dist,
            "recent_trend": trend_list,
            "urgent_queue": urgent_queue
        }
