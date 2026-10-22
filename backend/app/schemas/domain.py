from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class MerchantBase(BaseModel):
    id: str
    name: str
    legal_entity_name: str
    default_currency: str = "INR"
    timezone: str = "Asia/Kolkata"


class CustomerBase(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    is_synthetic: bool = True


class FulfilmentRecordBase(BaseModel):
    id: str
    order_id: str
    carrier: str
    tracking_number: Optional[str] = None
    status: str
    dispatch_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    delivery_proof_type: str
    delivery_otp_entered: Optional[str] = None
    delivery_address: str
    recipient_name: Optional[str] = None
    notes: Optional[str] = None


class CustomerMessageBase(BaseModel):
    id: str
    order_id: str
    customer_id: str
    direction: str
    channel: str
    sender_name: str
    content: str
    sent_at: datetime


class PaymentBase(BaseModel):
    id: str
    order_id: str
    provider: str
    gateway_payment_id: str
    amount: int  # in paise
    currency: str
    method: str
    card_network: Optional[str] = None
    card_last4: Optional[str] = None
    bank_name: Optional[str] = None
    upi_vpa: Optional[str] = None
    status: str
    captured_at: Optional[datetime] = None
    refund_status: Optional[str] = None
    amount_refunded: int = 0
    is_synthetic: bool = True


class OrderBase(BaseModel):
    id: str
    order_number: str
    amount: int
    currency: str
    status: str
    item_summary: Dict[str, Any]
    ordered_at: datetime
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None


class EvidenceItemSchema(BaseModel):
    id: str
    evidence_type: str
    title: str
    description: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    sha256_hash: Optional[str] = None
    verification_status: str
    source: str
    created_at: datetime


class EvidenceLinkSchema(BaseModel):
    id: str
    dispute_id: str
    evidence_id: str
    relevance_note: Optional[str] = None
    linked_at: datetime
    evidence_item: Optional[EvidenceItemSchema] = None


# Investigation & Signal schemas
class ContradictionItem(BaseModel):
    code: str
    severity: str  # high, medium, low
    title: str
    description: str
    conflicting_records: List[str]


class FactItem(BaseModel):
    claim: str
    source_type: str
    source_id: str
    verified: bool


class ChecklistItem(BaseModel):
    code: str
    label: str
    is_mandatory: bool
    status: str  # fulfilled, missing, contradictory
    matched_evidence_id: Optional[str] = None
    details: Optional[str] = None


class AIInvestigationSchema(BaseModel):
    id: str
    dispute_id: str
    investigation_status: str
    normalized_reason: str
    findings_summary: str
    checklist_audit: Dict[str, Any]
    contradictions: List[ContradictionItem]
    facts_extracted: List[FactItem]
    model_provider: str
    model_version: str
    execution_duration_ms: int
    created_at: datetime


# Draft schemas
class ResponseDraftSchema(BaseModel):
    id: str
    dispute_id: str
    contest_summary: str = Field(..., max_length=1000, description="Strict 1,000 char Razorpay contest summary")
    representation_letter: str
    cited_evidence_ids: List[str]
    version: int
    is_approved: bool
    created_at: datetime
    updated_at: datetime


class DraftUpdateRequest(BaseModel):
    contest_summary: str = Field(..., max_length=1000)
    representation_letter: str
    cited_evidence_ids: Optional[List[str]] = None


# Scoring schemas
class FactorContribution(BaseModel):
    feature_name: str
    description: str
    weight: float
    impact_points: float


class ScoringResultSchema(BaseModel):
    id: str
    dispute_id: str
    score: float
    tier: str
    model_name: str
    model_version: str
    top_positive_factors: List[FactorContribution]
    top_negative_factors: List[FactorContribution]
    missing_information_penalties: List[FactorContribution]
    feature_vector: Dict[str, Any]
    is_calibrated: bool
    calibration_note: str
    evaluated_at: datetime


# Dispute schemas
class DisputeListSchema(BaseModel):
    id: str
    order_id: str
    order_number: str
    payment_id: str
    customer_name: str
    customer_email: str
    amount: int
    currency: str
    reason_code: str
    reason_description: str
    status: str
    phase: str
    evidence_readiness: str
    evidence_completeness_pct: float
    win_probability_score: Optional[float] = None
    win_score_tier: Optional[str] = None
    response_deadline: datetime
    is_synthetic: bool
    created_at: datetime
    updated_at: datetime


class DisputeDetailSchema(DisputeListSchema):
    customer: CustomerBase
    order: OrderBase
    payment: PaymentBase
    fulfilment: Optional[FulfilmentRecordBase] = None
    messages: List[CustomerMessageBase] = []
    evidence_links: List[EvidenceLinkSchema] = []
    investigation: Optional[AIInvestigationSchema] = None
    latest_draft: Optional[ResponseDraftSchema] = None
    scoring: Optional[ScoringResultSchema] = None


# Dashboard & Analytics schemas
class UrgentDisputeItem(BaseModel):
    id: str
    order_number: str
    amount: int
    currency: str
    reason_code: str
    status: str
    response_deadline: datetime
    hours_remaining: float
    win_probability_score: Optional[float] = None


class DashboardSummary(BaseModel):
    total_disputes: int
    open_disputes: int
    evidence_ready_disputes: int
    urgent_disputes_count: int
    total_amount_at_risk: int  # in paise
    won_amount: int
    lost_amount: int
    win_rate_percentage: float
    average_evidence_completeness: float
    disputes_by_reason: Dict[str, int]
    disputes_by_status: Dict[str, int]
    win_score_distribution: Dict[str, int]
    recent_trend: List[Dict[str, Any]]
    urgent_queue: List[UrgentDisputeItem]


class ModelEvaluationMetrics(BaseModel):
    model_name: str
    version: str
    sample_size: int
    train_size: int
    test_size: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    brier_score: float
    confusion_matrix: Dict[str, int]
    calibration_curve: List[Dict[str, float]]
    feature_importances: List[Dict[str, Any]]
    sample_size_warning: Optional[str] = None


class IntegrationUpdateRequest(BaseModel):
    dispute_source: str = "mock"
    razorpay_key_id: Optional[str] = None
    razorpay_key_secret: Optional[str] = None
    razorpay_webhook_secret: Optional[str] = None
    llm_provider: Optional[str] = "fallback"
    anthropic_api_key: Optional[str] = None


class TestConnectionRequest(BaseModel):
    key_id: str
    key_secret: str

