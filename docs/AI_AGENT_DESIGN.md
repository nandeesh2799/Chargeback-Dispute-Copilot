# Chargeback & Dispute Copilot — AI Agent & Scoring Design

## 1. Core Principles

1. **Deterministic Guardrails**: The agent is not a free-running loop with unbounded tool execution. It executes an auditable 10-step pipeline with strictly typed Pydantic inputs and outputs.
2. **Grounding & Provenance**: The agent cannot invent facts, timestamps, OTPs, or evidence IDs. Every claim in the draft links to a verified database entity ID.
3. **Graceful Fallback**: If LLM API credentials (Claude/OpenAI) are unavailable, a deterministic rule-based engine generates grounded signal extraction, checklist audit, and dispute drafts.
4. **Decoupled Scoring**: Win likelihood is never an LLM hallucination. It is calculated by a Scikit-learn Logistic Regression model trained on objective feature vectors.

---

## 2. 10-Step Investigation Agent Workflow

```
[Step 1: Load Context]
  Fetch Dispute + Payment + Order + Fulfilment + Messages + Evidence
             │
[Step 2: Normalize Records]
  Convert Gateway representation to canonical internal entities
             │
[Step 3: Classify Reason]
  Deterministic mapping to:
  - product_not_received
  - cancelled_charge
  - fraud_unauthorized
  - not_as_described
  - duplicate_charge
             │
[Step 4: Build Reason-Specific Checklist]
  Query requirement criteria based on classified reason
             │
[Step 5: Extract Structured Signals]
  LLM / Deterministic Parser yields Pydantic ExtractedSignals
             │
[Step 6: Reconcile Evidence & Detect Contradictions]
  Check timestamp order, delivery vs claim, refund status vs order
             │
[Step 7: Produce Evidence Audit]
  Completeness %, missing mandatory docs, quality rating
             │
[Step 8: Generate Response Draft]
  1,000-char Razorpay contest summary + comprehensive representation letter
             │
[Step 9: Validate Output]
  Enforce length limits, verify cited evidence exists, reject unsupported claims
             │
[Step 10: Persist Audit Record]
  Write ai_investigations record, audit_logs entry, update dispute readiness
```

---

## 3. Reason-Specific Evidence Checklists

| Dispute Reason | Mandatory Evidence Items | Supporting Evidence Items |
|---|---|---|
| `product_not_received` | Delivery Proof (OTP/Signature), Carrier Tracking | Customer Chat Acknowledgement, Geofence Ping |
| `cancelled_charge` | Cancellation Policy, Timestamp Audit Log | Refund Transaction Reference, Support Ticket |
| `fraud_unauthorized` | 3D-Secure / 2FA Auth Log, Device IP/Geo Log | Delivery Address Consistency, Previous Order History |
| `not_as_described` | Detailed Item Description & Menu Specs, Packaging Photo | Customer Resolution Offer Log, Return Shipping Label |
| `duplicate_charge` | Independent Order Invoices, Gateway Auth IDs | Fulfilment Logs for Each Order, Cardholder Receipts |

---

## 4. Explainable Scoring Pipeline (Logistic Regression)

### 4.1 Feature Vector Formulation
The model computes an interpretable log-odds score using 10 engineered features:
1. `f_evidence_completeness` (float 0.0 - 1.0): Ratio of fulfilled checklist criteria.
2. `f_delivery_otp_verified` (binary 0/1): Delivery verified with one-time password or physical signature.
3. `f_customer_acknowledgement` (binary 0/1): Customer explicitly acknowledged receipt or terms in communication.
4. `f_contradiction_count` (int): Number of detected temporal or factual inconsistencies.
5. `f_refund_completed` (binary 0/1): Whether a refund was already processed before dispute.
6. `f_cancellation_within_policy` (binary 0/1): Order cancellation respected merchant policy window.
7. `f_hours_to_deadline` (float): Time remaining before response window closes.
8. `f_amount_tier` (int 1-4): Risk tier based on dispute value.
9. `f_previous_orders_count` (int): Customer relationship history.
10. `f_reason_baseline_weight` (float): Historical merchant win baseline for dispute category.

### 4.2 Score Calculation & Calibration
- The model outputs a probability $P(\text{Win}) \in [0, 1]$, mapped to integer score $0 - 100$.
- Feature weights ($\beta_i \cdot x_i$) are extracted to surface:
  - Top 3 Positive Factors (e.g., `+28 pts: Verified Delivery OTP matches courier drop-off timestamp`)
  - Top Negative Factors (e.g., `-18 pts: Missing cancellation policy acknowledgment at checkout`)
  - Missing Information Impact (e.g., `Potential +15 pts if carrier GPS log is attached`)
