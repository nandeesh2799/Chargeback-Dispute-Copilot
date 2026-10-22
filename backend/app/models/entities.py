import enum
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, BigInteger, Integer, Float, Boolean, Text, JSON, DateTime, ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    RISK_ANALYST = "risk_analyst"
    FINANCE_LEAD = "finance_lead"
    VIEWER = "viewer"


class OrderStatus(str, enum.Enum):
    PLACED = "placed"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentStatus(str, enum.Enum):
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


class FulfilmentStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    DELIVERED = "delivered"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class DeliveryProofType(str, enum.Enum):
    OTP_VERIFIED = "otp_verified"
    SIGNATURE = "signature"
    GEO_FENCE_PING = "geo_fence_ping"
    PHOTO = "photo"
    NONE = "none"


class DisputeStatus(str, enum.Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    EVIDENCE_READY = "evidence_ready"
    CONTESTED = "contested"
    WON = "won"
    LOST = "lost"
    CLOSED = "closed"


class DisputePhase(str, enum.Enum):
    RETRIEVAL = "retrieval"
    CHARGEBACK = "chargeback"
    PRE_ARBITRATION = "pre_arbitration"
    ARBITRATION = "arbitration"


class EvidenceReadiness(str, enum.Enum):
    NOT_STARTED = "not_started"
    GATHERING = "gathering"
    CONTRADICTIONS_DETECTED = "contradictions_detected"
    READY_TO_DRAFT = "ready_to_draft"
    READY_TO_SUBMIT = "ready_to_submit"


class WinScoreTier(str, enum.Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class EvidenceType(str, enum.Enum):
    DELIVERY_PROOF = "delivery_proof"
    ORDER_INVOICE = "order_invoice"
    CANCELLATION_POLICY = "cancellation_policy"
    CUSTOMER_CHAT_LOG = "customer_chat_log"
    REFUND_RECEIPT = "refund_receipt"
    IP_GEO_LOG = "ip_geo_log"
    DUPLICATE_AUDIT_LOG = "duplicate_audit_log"
    OTHER = "other"


class EvidenceVerificationStatus(str, enum.Enum):
    VERIFIED = "verified"
    PENDING_REVIEW = "pending_review"
    CONTRADICTORY = "contradictory"
    REJECTED = "rejected"


class EvidenceSource(str, enum.Enum):
    POS_SYSTEM = "pos_system"
    LOGISTICS_API = "logistics_api"
    SUPPORT_DESK = "support_desk"
    MANUAL_UPLOAD = "manual_upload"
    PAYMENT_GATEWAY = "payment_gateway"


class InvestigationStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# 1. Merchant
class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_entity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_currency: Mapped[str] = mapped_column(String(3), default="INR")
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    users: Mapped[List["User"]] = relationship(back_populates="merchant", cascade="all, delete-orphan")
    orders: Mapped[List["Order"]] = relationship(back_populates="merchant", cascade="all, delete-orphan")
    disputes: Mapped[List["Dispute"]] = relationship(back_populates="merchant", cascade="all, delete-orphan")


# 2. User
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.RISK_ANALYST)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    merchant: Mapped["Merchant"] = relationship(back_populates="users")


# 3. Customer
class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    orders: Mapped[List["Order"]] = relationship(back_populates="customer")
    disputes: Mapped[List["Dispute"]] = relationship(back_populates="customer")


# 4. Order
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False)
    order_number: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)  # in paise
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.FULFILLED)
    item_summary: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    ordered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    merchant: Mapped["Merchant"] = relationship(back_populates="orders")
    customer: Mapped["Customer"] = relationship(back_populates="orders")
    payments: Mapped[List["Payment"]] = relationship(back_populates="order")
    fulfilment_records: Mapped[List["FulfilmentRecord"]] = relationship(back_populates="order")
    disputes: Mapped[List["Dispute"]] = relationship(back_populates="order")


# 5. Payment
class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False)
    order_id: Mapped[str] = mapped_column(String(64), ForeignKey("orders.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(32), default="mock")
    gateway_payment_id: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)  # in paise
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    method: Mapped[str] = mapped_column(String(32), default="upi")
    card_network: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    card_last4: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    upi_vpa: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus), default=PaymentStatus.CAPTURED)
    captured_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    refund_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    amount_refunded: Mapped[int] = mapped_column(BigInteger, default=0)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True)

    order: Mapped["Order"] = relationship(back_populates="payments")
    disputes: Mapped[List["Dispute"]] = relationship(back_populates="payment")


# 6. FulfilmentRecord
class FulfilmentRecord(Base):
    __tablename__ = "fulfilment_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(64), ForeignKey("orders.id"), nullable=False)
    carrier: Mapped[str] = mapped_column(String(64), default="Dunzo Express")
    tracking_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[FulfilmentStatus] = mapped_column(SQLEnum(FulfilmentStatus), default=FulfilmentStatus.DELIVERED)
    dispatch_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_proof_type: Mapped[DeliveryProofType] = mapped_column(SQLEnum(DeliveryProofType), default=DeliveryProofType.OTP_VERIFIED)
    delivery_otp_entered: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    delivery_address: Mapped[str] = mapped_column(String(512), nullable=False)
    recipient_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    order: Mapped["Order"] = relationship(back_populates="fulfilment_records")


# 7. CustomerMessage
class CustomerMessage(Base):
    __tablename__ = "customer_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dispute_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("disputes.id"), nullable=True)
    order_id: Mapped[str] = mapped_column(String(64), ForeignKey("orders.id"), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False)
    direction: Mapped[str] = mapped_column(String(16), default="inbound")  # inbound / outbound
    channel: Mapped[str] = mapped_column(String(16), default="chat")        # chat, email, sms
    sender_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    dispute: Mapped[Optional["Dispute"]] = relationship(back_populates="customer_messages")


# 8. Dispute
class Dispute(Base):
    __tablename__ = "disputes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False)
    payment_id: Mapped[str] = mapped_column(String(64), ForeignKey("payments.id"), nullable=False)
    order_id: Mapped[str] = mapped_column(String(64), ForeignKey("orders.id"), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False)
    gateway_dispute_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    provider: Mapped[str] = mapped_column(String(32), default="mock")
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)  # in paise
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    reason_description: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[DisputeStatus] = mapped_column(SQLEnum(DisputeStatus), default=DisputeStatus.OPEN)
    phase: Mapped[DisputePhase] = mapped_column(SQLEnum(DisputePhase), default=DisputePhase.CHARGEBACK)
    evidence_readiness: Mapped[EvidenceReadiness] = mapped_column(SQLEnum(EvidenceReadiness), default=EvidenceReadiness.NOT_STARTED)
    evidence_completeness_pct: Mapped[float] = mapped_column(Float, default=0.0)
    win_probability_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    win_score_tier: Mapped[Optional[WinScoreTier]] = mapped_column(SQLEnum(WinScoreTier), nullable=True)
    response_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    contested_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    merchant: Mapped["Merchant"] = relationship(back_populates="disputes")
    payment: Mapped["Payment"] = relationship(back_populates="disputes")
    order: Mapped["Order"] = relationship(back_populates="disputes")
    customer: Mapped["Customer"] = relationship(back_populates="disputes")
    customer_messages: Mapped[List["CustomerMessage"]] = relationship(back_populates="dispute")
    evidence_links: Mapped[List["EvidenceLink"]] = relationship(back_populates="dispute", cascade="all, delete-orphan")
    investigation: Mapped[Optional["AIInvestigation"]] = relationship(back_populates="dispute", uselist=False, cascade="all, delete-orphan")
    drafts: Mapped[List["ResponseDraft"]] = relationship(back_populates="dispute", cascade="all, delete-orphan")
    scoring: Mapped[Optional["ScoringResult"]] = relationship(back_populates="dispute", uselist=False, cascade="all, delete-orphan")
    outcome: Mapped[Optional["DisputeOutcome"]] = relationship(back_populates="dispute", uselist=False, cascade="all, delete-orphan")


# 9. EvidenceItem
class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False)
    evidence_type: Mapped[EvidenceType] = mapped_column(SQLEnum(EvidenceType), default=EvidenceType.OTHER)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    sha256_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    verification_status: Mapped[EvidenceVerificationStatus] = mapped_column(SQLEnum(EvidenceVerificationStatus), default=EvidenceVerificationStatus.VERIFIED)
    source: Mapped[EvidenceSource] = mapped_column(SQLEnum(EvidenceSource), default=EvidenceSource.POS_SYSTEM)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    links: Mapped[List["EvidenceLink"]] = relationship(back_populates="evidence_item", cascade="all, delete-orphan")


# 10. EvidenceLink
class EvidenceLink(Base):
    __tablename__ = "evidence_links"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dispute_id: Mapped[str] = mapped_column(String(64), ForeignKey("disputes.id"), nullable=False)
    evidence_id: Mapped[str] = mapped_column(String(64), ForeignKey("evidence_items.id"), nullable=False)
    linked_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    relevance_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    dispute: Mapped["Dispute"] = relationship(back_populates="evidence_links")
    evidence_item: Mapped["EvidenceItem"] = relationship(back_populates="links")


# 11. AIInvestigation
class AIInvestigation(Base):
    __tablename__ = "ai_investigations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dispute_id: Mapped[str] = mapped_column(String(64), ForeignKey("disputes.id"), unique=True, nullable=False)
    investigation_status: Mapped[InvestigationStatus] = mapped_column(SQLEnum(InvestigationStatus), default=InvestigationStatus.COMPLETED)
    normalized_reason: Mapped[str] = mapped_column(String(64), nullable=False)
    findings_summary: Mapped[str] = mapped_column(Text, nullable=False)
    checklist_audit: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    contradictions: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    facts_extracted: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    model_provider: Mapped[str] = mapped_column(String(64), default="deterministic_fallback")
    model_version: Mapped[str] = mapped_column(String(64), default="v1.0")
    execution_duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    dispute: Mapped["Dispute"] = relationship(back_populates="investigation")


# 12. ResponseDraft
class ResponseDraft(Base):
    __tablename__ = "response_drafts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dispute_id: Mapped[str] = mapped_column(String(64), ForeignKey("disputes.id"), nullable=False)
    contest_summary: Mapped[str] = mapped_column(String(1000), nullable=False)  # Strict <= 1000 chars
    representation_letter: Mapped[str] = mapped_column(Text, nullable=False)
    cited_evidence_ids: Mapped[List[str]] = mapped_column(JSON, default=list)
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    last_edited_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    dispute: Mapped["Dispute"] = relationship(back_populates="drafts")


# 13. ScoringResult
class ScoringResult(Base):
    __tablename__ = "scoring_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dispute_id: Mapped[str] = mapped_column(String(64), ForeignKey("disputes.id"), unique=True, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    tier: Mapped[WinScoreTier] = mapped_column(SQLEnum(WinScoreTier), default=WinScoreTier.MEDIUM)
    model_name: Mapped[str] = mapped_column(String(64), default="LogisticRegression_Baseline_v1")
    model_version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    top_positive_factors: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    top_negative_factors: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    missing_information_penalties: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    feature_vector: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    is_calibrated: Mapped[bool] = mapped_column(Boolean, default=True)
    calibration_note: Mapped[str] = mapped_column(Text, default="Trained on deterministic merchant feature baseline.")
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    dispute: Mapped["Dispute"] = relationship(back_populates="scoring")


# 14. DisputeOutcome
class DisputeOutcome(Base):
    __tablename__ = "dispute_outcomes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dispute_id: Mapped[str] = mapped_column(String(64), ForeignKey("disputes.id"), unique=True, nullable=False)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)  # won, lost, accepted_by_merchant
    amount_deducted: Mapped[int] = mapped_column(BigInteger, default=0)
    fee_deducted: Mapped[int] = mapped_column(BigInteger, default=0)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    resolution_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    dispute: Mapped["Dispute"] = relationship(back_populates="outcome")


# 15. IntegrationConfig
class IntegrationConfig(Base):
    __tablename__ = "integration_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)  # razorpay, mock, claude
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    key_id_masked: Mapped[str] = mapped_column(String(32), default="")
    encrypted_secret: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    webhook_secret_masked: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    environment: Mapped[str] = mapped_column(String(16), default="test")
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_status: Mapped[str] = mapped_column(String(32), default="healthy")


# 16. WebhookEvent
class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    provider: Mapped[str] = mapped_column(String(32), default="razorpay")
    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    signature_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_status: Mapped[str] = mapped_column(String(32), default="pending")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


# 17. AuditLog
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(64), nullable=False)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


# Performance indexes for common query patterns
Index("ix_disputes_status", Dispute.status)
Index("ix_disputes_reason_code", Dispute.reason_code)
Index("ix_disputes_response_deadline", Dispute.response_deadline)
Index("ix_disputes_merchant_id", Dispute.merchant_id)
Index("ix_disputes_created_at", Dispute.created_at)
Index("ix_disputes_evidence_readiness", Dispute.evidence_readiness)
