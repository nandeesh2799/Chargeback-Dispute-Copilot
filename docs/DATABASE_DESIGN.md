# Chargeback & Dispute Copilot — Database Schema Specification

## 1. Overview & Data Integrity Principles

The persistence layer uses **SQLAlchemy 2.0 ORM** with **Alembic** migrations.
- **Monetary values**: Always represented as **integer minor units** (e.g. INR paise or USD cents: `150000` = ₹1,500.00). Floating-point arithmetic is strictly prohibited for monetary values.
- **Timestamps**: All dates are stored as UTC (`DateTime(timezone=True)`). Presentation formatting applies the merchant's configured timezone (default: `Asia/Kolkata`).
- **Auditability**: Critical updates record who, when, and what changed in `audit_logs`.
- **Synthetic Flagging**: Synthetic records carry `is_synthetic = True` to guarantee complete separation from live gateway records.

---

## 2. Entity Relational Model

```
[merchants] 1 ────< N [users]
      │
      ├────< N [orders] 1 ────< N [fulfilment_records]
      │           │
      │           └────< 1 [payments]
      │                       │
      ├───────────────────────┴────< N [disputes]
      │                                   │
      │                                   ├────< N [customer_messages]
      │                                   ├────< N [evidence_links] >──── 1 [evidence_items]
      │                                   ├────< 1 [ai_investigations]
      │                                   ├────< N [response_drafts]
      │                                   ├────< 1 [scoring_results]
      │                                   └────< 0..1 [dispute_outcomes]
      │
      ├────< N [integration_configs]
      ├────< N [webhook_events]
      └────< N [audit_logs]
```

---

## 3. Entity Details

### 3.1 `merchants`
- `id`: String(36) PK (e.g. `mer_rjkitchen_01`)
- `name`: String(255) (e.g. "RJ Kitchen - Cyber Hub Cloud Kitchen")
- `legal_entity_name`: String(255)
- `default_currency`: String(3) (default `"INR"`)
- `timezone`: String(64) (default `"Asia/Kolkata"`)
- `created_at`: DateTime(timezone=True)
- `updated_at`: DateTime(timezone=True)

### 3.2 `users`
- `id`: String(36) PK
- `merchant_id`: String(36) FK -> `merchants.id`
- `email`: String(255) UNIQUE
- `name`: String(255)
- `role`: Enum (`admin`, `risk_analyst`, `finance_lead`, `viewer`)
- `is_active`: Boolean (default True)
- `created_at`: DateTime(timezone=True)

### 3.3 `customers`
- `id`: String(36) PK (e.g. `cust_synth_001`)
- `merchant_id`: String(36) FK -> `merchants.id`
- `name`: String(255)
- `email`: String(255)
- `phone`: String(32)
- `is_synthetic`: Boolean (default True)
- `created_at`: DateTime(timezone=True)

### 3.4 `orders`
- `id`: String(64) PK (e.g. `order_synth_1001`)
- `merchant_id`: String(36) FK -> `merchants.id`
- `customer_id`: String(36) FK -> `customers.id`
- `order_number`: String(64)
- `amount`: BigInteger (paise/cents)
- `currency`: String(3)
- `status`: Enum (`placed`, `fulfilled`, `cancelled`, `refunded`, `partially_refunded`)
- `item_summary`: JSON (list of line items, quantity, item amount)
- `ordered_at`: DateTime(timezone=True)
- `cancelled_at`: Optional DateTime(timezone=True)
- `cancellation_reason`: Optional String(255)

### 3.5 `payments`
- `id`: String(64) PK (e.g. `pay_synth_1001`)
- `merchant_id`: String(36) FK -> `merchants.id`
- `order_id`: String(64) FK -> `orders.id`
- `provider`: String(32) (e.g. `razorpay`, `mock`)
- `gateway_payment_id`: String(64)
- `amount`: BigInteger
- `currency`: String(3)
- `method`: String(32) (e.g. `upi`, `card`, `netbanking`)
- `card_network`: Optional String(32)
- `card_last4`: Optional String(4)
- `bank_name`: Optional String(64)
- `upi_vpa`: Optional String(64)
- `status`: Enum (`authorized`, `captured`, `failed`, `refunded`)
- `captured_at`: Optional DateTime(timezone=True)
- `refund_status`: Optional String(32)
- `amount_refunded`: BigInteger (default 0)
- `is_synthetic`: Boolean (default True)

### 3.6 `fulfilment_records`
- `id`: String(36) PK
- `order_id`: String(64) FK -> `orders.id`
- `carrier`: String(64) (e.g. "Dunzo Express", "Shadowfax Fleet", "Direct In-House")
- `tracking_number`: Optional String(64)
- `status`: Enum (`assigned`, `picked_up`, `delivered`, `returned`, `cancelled`)
- `dispatch_at`: Optional DateTime(timezone=True)
- `delivered_at`: Optional DateTime(timezone=True)
- `delivery_proof_type`: Enum (`otp_verified`, `signature`, `geo_fence_ping`, `photo`, `none`)
- `delivery_otp_entered`: Optional String(16)
- `delivery_address`: String(512)
- `recipient_name`: Optional String(255)
- `notes`: Optional Text

### 3.7 `customer_messages`
- `id`: String(36) PK
- `dispute_id`: Optional String(64) FK -> `disputes.id`
- `order_id`: String(64) FK -> `orders.id`
- `customer_id`: String(36) FK -> `customers.id`
- `direction`: Enum (`inbound`, `outbound`)
- `channel`: Enum (`chat`, `email`, `sms`, `call_log`)
- `sender_name`: String(255)
- `content`: Text
- `sent_at`: DateTime(timezone=True)

### 3.8 `disputes`
- `id`: String(64) PK (e.g. `disp_synth_1001`)
- `merchant_id`: String(36) FK -> `merchants.id`
- `payment_id`: String(64) FK -> `payments.id`
- `order_id`: String(64) FK -> `orders.id`
- `customer_id`: String(36) FK -> `customers.id`
- `gateway_dispute_id`: Optional String(64)
- `provider`: String(32) (default `mock`)
- `amount`: BigInteger (in dispute)
- `currency`: String(3)
- `reason_code`: String(64) (e.g. `product_not_received`, `cancelled_charge`, `fraud_unauthorized`, `not_as_described`, `duplicate_charge`)
- `reason_description`: String(512)
- `status`: Enum (`open`, `under_review`, `evidence_ready`, `contested`, `won`, `lost`, `closed`)
- `phase`: Enum (`retrieval`, `chargeback`, `pre_arbitration`, `arbitration`)
- `evidence_readiness`: Enum (`not_started`, `gathering`, `contradictions_detected`, `ready_to_draft`, `ready_to_submit`)
- `evidence_completeness_pct`: Float (0.0 to 100.0)
- `win_probability_score`: Optional Float (0.0 to 100.0)
- `win_score_tier`: Optional Enum (`very_low`, `low`, `medium`, `high`, `very_high`)
- `response_deadline`: DateTime(timezone=True)
- `contested_at`: Optional DateTime(timezone=True)
- `closed_at`: Optional DateTime(timezone=True)
- `is_synthetic`: Boolean (default True)
- `created_at`: DateTime(timezone=True)
- `updated_at`: DateTime(timezone=True)

### 3.9 `evidence_items`
- `id`: String(64) PK (e.g. `evi_synth_1001`)
- `merchant_id`: String(36) FK -> `merchants.id`
- `evidence_type`: Enum (`delivery_proof`, `order_invoice`, `cancellation_policy`, `customer_chat_log`, `refund_receipt`, `ip_geo_log`, `duplicate_audit_log`, `other`)
- `title`: String(255)
- `description`: Text
- `file_path`: Optional String(512)
- `file_name`: Optional String(255)
- `file_size_bytes`: Optional Integer
- `mime_type`: Optional String(64)
- `sha256_hash`: Optional String(64)
- `verification_status`: Enum (`verified`, `pending_review`, `contradictory`, `rejected`)
- `source`: Enum (`pos_system`, `logistics_api`, `support_desk`, `manual_upload`, `payment_gateway`)
- `created_at`: DateTime(timezone=True)

### 3.10 `evidence_links`
- `id`: String(36) PK
- `dispute_id`: String(64) FK -> `disputes.id`
- `evidence_id`: String(64) FK -> `evidence_items.id`
- `linked_by`: String(36) FK -> `users.id`
- `relevance_note`: Optional Text
- `linked_at`: DateTime(timezone=True)

### 3.11 `ai_investigations`
- `id`: String(36) PK
- `dispute_id`: String(64) FK -> `disputes.id` UNIQUE
- `investigation_status`: Enum (`in_progress`, `completed`, `failed`)
- `normalized_reason`: String(64)
- `findings_summary`: Text
- `checklist_audit`: JSON (structured checks, present items, missing requirements)
- `contradictions`: JSON (list of detected inconsistencies with record IDs)
- `facts_extracted`: JSON (verified facts linked to provenance)
- `model_provider`: String(64) (e.g. `claude-3-7-sonnet`, `deterministic_fallback`)
- `model_version`: String(64)
- `execution_duration_ms`: Integer
- `created_at`: DateTime(timezone=True)
- `updated_at`: DateTime(timezone=True)

### 3.12 `response_drafts`
- `id`: String(36) PK
- `dispute_id`: String(64) FK -> `disputes.id`
- `contest_summary`: String(1000) (Strict <= 1,000 characters for Razorpay contest API)
- `representation_letter`: Text (Long-form supporting representation)
- `cited_evidence_ids`: JSON (list of evidence IDs cited in the response)
- `version`: Integer (default 1)
- `is_approved`: Boolean (default False)
- `approved_by`: Optional String(36) FK -> `users.id`
- `last_edited_by`: Optional String(36) FK -> `users.id`
- `created_at`: DateTime(timezone=True)
- `updated_at`: DateTime(timezone=True)

### 3.13 `scoring_results`
- `id`: String(36) PK
- `dispute_id`: String(64) FK -> `disputes.id` UNIQUE
- `score`: Float (0.0 to 100.0)
- `tier`: Enum (`very_low`, `low`, `medium`, `high`, `very_high`)
- `model_name`: String(64) (e.g. `LogisticRegression_Baseline_v1`)
- `model_version`: String(32)
- `top_positive_factors`: JSON (list of factors with positive weights)
- `top_negative_factors`: JSON (list of factors with negative weights)
- `missing_information_penalties`: JSON
- `feature_vector`: JSON (raw inputs fed into model)
- `is_calibrated`: Boolean (default True)
- `calibration_note`: Text
- `evaluated_at`: DateTime(timezone=True)

### 3.14 `dispute_outcomes`
- `id`: String(36) PK
- `dispute_id`: String(64) FK -> `disputes.id` UNIQUE
- `outcome`: Enum (`won`, `lost`, `accepted_by_merchant`, `closed_by_gateway`)
- `amount_deducted`: BigInteger
- `fee_deducted`: BigInteger
- `decided_at`: DateTime(timezone=True)
- `resolution_remarks`: Optional Text

### 3.15 `integration_configs`
- `id`: String(36) PK
- `merchant_id`: String(36) FK -> `merchants.id`
- `provider`: Enum (`razorpay`, `mock`, `claude`, `openai_compatible`)
- `is_enabled`: Boolean (default True)
- `key_id_masked`: String(32)
- `encrypted_secret`: Optional Text
- `webhook_secret_masked`: Optional String(32)
- `environment`: Enum (`test`, `live`, `mock`)
- `last_synced_at`: Optional DateTime(timezone=True)
- `sync_status`: Enum (`healthy`, `degraded`, `disconnected`)

### 3.16 `webhook_events`
- `id`: String(36) PK
- `provider`: String(32)
- `event_id`: String(64) UNIQUE
- `event_type`: String(64)
- `raw_payload`: JSON
- `signature_verified`: Boolean
- `processing_status`: Enum (`pending`, `processed`, `failed`, `ignored`)
- `error_message`: Optional Text
- `received_at`: DateTime(timezone=True)
- `processed_at`: Optional DateTime(timezone=True)

### 3.17 `audit_logs`
- `id`: String(36) PK
- `merchant_id`: String(36) FK -> `merchants.id`
- `user_id`: Optional String(36) FK -> `users.id`
- `action`: String(64) (e.g. `INVESTIGATION_TRIGGERED`, `DRAFT_UPDATED`, `CONTEST_SUBMITTED`, `DEMO_RESET`)
- `resource_type`: String(64)
- `resource_id`: String(64)
- `details`: JSON
- `ip_address`: Optional String(64)
- `created_at`: DateTime(timezone=True)
