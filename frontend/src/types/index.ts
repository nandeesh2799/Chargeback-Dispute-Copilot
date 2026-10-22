export interface Customer {
  id: string;
  name: string;
  email: string;
  phone: string;
  is_synthetic: boolean;
}

export interface Order {
  id: string;
  order_number: string;
  amount: number; // in paise
  currency: string;
  status: string;
  item_summary: {
    items?: Array<{ name: string; price: number }>;
    subtotal?: number;
    tax?: number;
  };
  ordered_at: string;
  cancelled_at?: string | null;
  cancellation_reason?: string | null;
}

export interface Payment {
  id: string;
  order_id: string;
  provider: string;
  gateway_payment_id: string;
  amount: number;
  currency: string;
  method: string;
  card_network?: string | null;
  card_last4?: string | null;
  bank_name?: string | null;
  upi_vpa?: string | null;
  status: string;
  captured_at?: string | null;
  refund_status?: string | null;
  amount_refunded: number;
  is_synthetic: boolean;
}

export interface FulfilmentRecord {
  id: string;
  order_id: string;
  carrier: string;
  tracking_number?: string | null;
  status: string;
  dispatch_at?: string | null;
  delivered_at?: string | null;
  delivery_proof_type: string;
  delivery_otp_entered?: string | null;
  delivery_address: string;
  recipient_name?: string | null;
  notes?: string | null;
}

export interface CustomerMessage {
  id: string;
  order_id: string;
  customer_id: string;
  direction: string;
  channel: string;
  sender_name: string;
  content: string;
  sent_at: string;
}

export interface EvidenceItem {
  id: string;
  evidence_type: string;
  title: string;
  description: string;
  file_path?: string | null;
  file_name?: string | null;
  file_size_bytes?: number | null;
  mime_type?: string | null;
  sha256_hash?: string | null;
  verification_status: string;
  source: string;
  created_at: string;
}

export interface EvidenceLink {
  id: string;
  dispute_id: string;
  evidence_id: string;
  relevance_note?: string | null;
  linked_at: string;
  evidence_item?: EvidenceItem | null;
}

export interface ContradictionItem {
  code: string;
  severity: string;
  title: string;
  description: string;
  conflicting_records: string[];
}

export interface FactItem {
  claim: string;
  source_type: string;
  source_id: string;
  verified: boolean;
}

export interface ChecklistItem {
  code: string;
  label: string;
  is_mandatory: boolean;
  status: string; // fulfilled, missing, contradictory
  matched_evidence_id?: string | null;
  details?: string | null;
}

export interface AIInvestigation {
  id: string;
  dispute_id: string;
  investigation_status: string;
  normalized_reason: string;
  findings_summary: string;
  checklist_audit: {
    items?: ChecklistItem[];
    completeness_pct?: number;
    summary?: string;
  };
  contradictions: ContradictionItem[];
  facts_extracted: FactItem[];
  model_provider: string;
  model_version: string;
  execution_duration_ms: number;
  created_at: string;
}

export interface ResponseDraft {
  id: string;
  dispute_id: string;
  contest_summary: string; // max 1000 chars
  representation_letter: string;
  cited_evidence_ids: string[];
  version: number;
  is_approved: boolean;
  created_at: string;
  updated_at: string;
}

export interface FactorContribution {
  feature_name: string;
  description: string;
  weight: number;
  impact_points: number;
}

export interface ScoringResult {
  id: string;
  dispute_id: string;
  score: number;
  tier: string;
  model_name: string;
  model_version: string;
  top_positive_factors: FactorContribution[];
  top_negative_factors: FactorContribution[];
  missing_information_penalties: FactorContribution[];
  feature_vector: Record<string, any>;
  is_calibrated: boolean;
  calibration_note: string;
  evaluated_at: string;
}

export interface DisputeSummaryItem {
  id: string;
  order_id: string;
  order_number: string;
  payment_id: string;
  customer_name: string;
  customer_email: string;
  amount: number;
  currency: string;
  reason_code: string;
  reason_description: string;
  status: string;
  phase: string;
  evidence_readiness: string;
  evidence_completeness_pct: number;
  win_probability_score?: number | null;
  win_score_tier?: string | null;
  response_deadline: string;
  is_synthetic: boolean;
  created_at: string;
  updated_at: string;
}

export interface DisputeDetail extends DisputeSummaryItem {
  customer: Customer;
  order: Order;
  payment: Payment;
  fulfilment?: FulfilmentRecord | null;
  messages: CustomerMessage[];
  evidence_links: EvidenceLink[];
  investigation?: AIInvestigation | null;
  latest_draft?: ResponseDraft | null;
  scoring?: ScoringResult | null;
}

export interface DashboardSummary {
  total_disputes: number;
  open_disputes: number;
  evidence_ready_disputes: number;
  urgent_disputes_count: number;
  total_amount_at_risk: number;
  won_amount: number;
  lost_amount: number;
  win_rate_percentage: number;
  average_evidence_completeness: number;
  disputes_by_reason: Record<string, number>;
  disputes_by_status: Record<string, number>;
  win_score_distribution: Record<string, number>;
  recent_trend: Array<{ date: string; opened: number; won: number; lost: number }>;
  urgent_queue: Array<{
    id: string;
    order_number: string;
    amount: number;
    currency: string;
    reason_code: string;
    status: string;
    response_deadline: string;
    hours_remaining: number;
    win_probability_score?: number | null;
  }>;
}

export interface ModelEvaluationMetrics {
  model_name: string;
  version: string;
  sample_size: number;
  train_size: number;
  test_size: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  brier_score: number;
  confusion_matrix: {
    true_negatives: number;
    false_positives: number;
    false_negatives: number;
    true_positives: number;
  };
  calibration_curve: Array<{ predicted: number; actual: number }>;
  feature_importances: Array<{ feature: string; weight: number; description: string }>;
  sample_size_warning?: string | null;
}
