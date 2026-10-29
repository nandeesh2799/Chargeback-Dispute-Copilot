# Chargeback & Dispute Copilot

[![CI Pipeline](https://github.com/nandeesh2799/Chargeback-Dispute-Copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/nandeesh2799/Chargeback-Dispute-Copilot/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6?logo=typescript&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4+-F7931E?logo=scikit-learn&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen?logo=pytest)

> **An AI-Powered Payment Dispute Investigation, Evidence Intelligence & Resolution Platform**
> Built for online merchants, specialized for **RJ Kitchen** (cloud kitchen operations). Bridges payment gateways, courier telematics, explainable machine learning win-probability scoring, and an auditable 10-step AI investigation agent.

---

## 1. Product Overview

Online merchants face substantial operational friction and revenue leakage when contesting cardholder chargebacks and UPI payment disputes. **Chargeback & Dispute Copilot** transforms manual, reactive dispute firefighting into an automated, auditable, and intelligence-driven resolution workflow.

The platform provides:
- **Dispute Queue Operations**: Real-time filtering, urgency ranking, and countdown monitoring against issuer deadlines.
- **Evidence Vault**: Secure aggregation of courier telematics (Proof of Delivery, OTP, carrier tracking), itemized GST tax invoices, Kitchen Order Tickets (KOT), and customer communication transcripts.
- **10-Step Auditable AI Investigation Agent**: Deterministic record reconciliation, reason-specific evidence checklists, and contradiction detection. Claims are strictly grounded in database entity IDs.
- **Explainable ML Win-Score Model**: Scikit-learn Logistic Regression pipeline providing calibrated probabilities ($0–100\%$) and human-interpretable feature contribution breakdowns ($\pm \text{pts}$).
- **Response Studio**: Two-stage rebuttal generator producing both a **Razorpay contest summary** (strictly $\le 1,000$ characters) and a comprehensive formal **Dispute Representation Letter**.
- **Executive PDF Export**: ReportLab-powered publication-grade PDF evidence report complete with visual tables, timestamps, and provenance badges.
- **Payment Gateway Safety Guardrails**: Zero-configuration mock provider default with hard programmatic constraints that reject synthetic dispute IDs at the live API boundary.

---

## 2. Architecture & Data Flow

```
                           +--------------------------------+
                           |       Merchant Operator        |
                           +--------------------------------+
                                          |
                                          v
                      +------------------------------------------+
                      |         React 18 + Vite Frontend         |
                      |   (Tailwind CSS, TanStack Query, Radix)  |
                      +------------------------------------------+
                                          |
                                          | REST / JSON / HTTP
                                          v
+------------------------------------------------------------------------------------+
|                                FastAPI Backend                                     |
|                                                                                    |
|  [ API Layer: Routes & Routers ]                                                   |
|      /api/health       /api/dashboard    /api/disputes     /api/evidence           |
|      /api/scoring      /api/analytics    /api/integrations /api/webhooks           |
|                                                                                    |
|  [ Core Application & Domain Services ]                                            |
|      DisputeService    EvidenceService   AuditService      ExportService           |
|                                                                                    |
|  [ Intelligence Engines ]                                                          |
|      DisputeInvestigationAgent   ExplainableScoringPipeline (scikit-learn)         |
|      (10-Step Deterministic + LLM) (Feature engineering + Logistic Regression)      |
|                                                                                    |
|  [ Gateway & Integration Boundary ]                                                |
|      DisputeSource Interface ──► MockDisputeSource (Deterministic 50 fixtures)      |
|                              ──► RazorpayDisputeSource (Test-mode Gateway API)     |
|      LLMProvider Interface   ──► ClaudeProvider / Deterministic Fallback           |
|                                                                                    |
|  [ Persistence Layer: SQLAlchemy 2.0 ORM ]                                         |
+------------------------------------------------------------------------------------+
                                    |
                                    v
                     +------------------------------+
                     |  SQLite (Local/Demo)         |
                     |  PostgreSQL (Production)     |
                     +------------------------------+
```

---

## 3. The 10-Step Auditable AI Investigation Agent

Free-running LLMs that execute arbitrary tools or make irreversible payment decisions are prohibited. The agent follows a typed, auditable 10-step pipeline:

```
[Step 1: Load Context] ──► Dispute + Payment + Order + Fulfilment + Messages + Evidence
             │
[Step 2: Normalize] ──► Map gateway data into canonical internal entities
             │
[Step 3: Classify] ──► Map to: product_not_received, cancelled_charge, fraud_unauthorized,
             │         not_as_described, duplicate_charge
             │
[Step 4: Checklist] ──► Build reason-specific evidence criteria (e.g. OTP proof vs policy)
             │
[Step 5: Extract Signals] ──► Pydantic-validated factual claims tied to source IDs
             │
[Step 6: Reconcile] ──► Detect temporal conflicts (e.g. delivery earlier than order)
             │          or customer chat admissions
             │
[Step 7: Audit] ──► Calculate evidence completeness % and missing requirements
             │
[Step 8: Draft] ──► Generate 1,000-char contest summary & formal letter
             │
[Step 9: Validate] ──► Assert len(summary) <= 1000 and verify all cited exhibits exist
             │
[Step 10: Persist] ──► Save ai_investigations record, update dispute readiness
```

---

## 4. Explainable Win-Score Methodology

Win probability is never an invented LLM percentage. It is computed via a Scikit-learn **Logistic Regression** baseline model trained on 10 objective features:

| Feature Name | Type | Description |
|---|---|---|
| `f_evidence_completeness` | Float [0, 1] | Ratio of mandatory checklist criteria fulfilled |
| `f_delivery_otp_verified` | Binary {0, 1} | Delivery verified with OTP or biometric/physical signature |
| `f_customer_acknowledgement`| Binary {0, 1} | Customer explicitly acknowledged receipt in chat logs |
| `f_contradiction_count` | Integer | Penalty for temporal or factual record inconsistencies |
| `f_refund_completed` | Binary {0, 1} | Gateway refund was already completed before dispute |
| `f_cancellation_within_policy`| Binary {0, 1} | Cancellation occurred within merchant policy window |
| `f_hours_to_deadline` | Float [0, 1] | Buffer time remaining before response window closes |
| `f_amount_tier` | Float [0, 1] | Transaction exposure risk tier |
| `f_previous_orders_count` | Float [0, 1] | Customer relationship history |
| `f_reason_weight` | Float [0, 1] | Historical merchant defense baseline for dispute category |

The output provides:
- **Calibrated Win Probability** ($0.0\% - 100.0\%$) and Tier (`VERY_LOW`, `LOW`, `MEDIUM`, `HIGH`, `VERY_HIGH`).
- **Feature Contribution Weights** ($\beta_i \cdot x_i$): Explains exact score drivers (e.g., `+18.5 pts: Verified Delivery OTP matches courier drop-off timestamp`).
- **Negative Penalties** (e.g., `-22.0 pts: Detected customer chat receipt acknowledgement conflicting with non-delivery claim`).

---

## 5. Razorpay Gateway Integration & Safety Guardrails

The application communicates with official Razorpay endpoints (`/v1/disputes`, `/v1/payments`) while maintaining strict safety guardrails:
1. **Mock Dispute ID Interception**: Attempting to query or contest a synthetic dispute (`disp_synth_*`) via the Razorpay client raises an immediate `ValueError` before any HTTP request is dispatched.
2. **1,000-Character Limit Validation**: The backend validates that `len(contest_summary) <= 1000` at the integration boundary, matching official gateway constraints.
3. **Two-Stage Human Confirmation**: Contesting or accepting a dispute requires explicit operator confirmation via a modal dialog.
4. **HMAC-SHA256 Webhook Verification**: Inbound webhooks (`POST /api/webhooks/razorpay`) are cryptographically verified against raw request bytes using `RAZORPAY_WEBHOOK_SECRET` and deduplicated via `webhook_events.event_id`.

---

## 6. Synthetic Dataset: RJ Kitchen Cloud Kitchen

The platform includes **50 deterministic synthetic disputes** modeled around **RJ Kitchen**, a high-volume cloud kitchen in Cyber Hub, Gurugram.

Categories covered:
1. **Product Not Received (15 disputes)**: Courier telematics, OTP verification, carrier drop-off logs, customer delivery chat transcripts.
2. **Order Cancelled But Charged (10 disputes)**: Cancellation policies, kitchen prep timestamps, refund transaction statuses.
3. **Fraud / Unauthorized Transaction (10 disputes)**: 3D-Secure 2FA authentication logs, device IP and residential ISP geo-logs.
4. **Product Not As Described (10 disputes)**: Itemized Kitchen Order Tickets (KOT), packaging quality inspection records, customer complaints.
5. **Duplicate Charge (5 disputes)**: Settlement ledger reconciliation, card authorization logs.

Edge cases included:
- Customer confirmed delivery in chat ("Thanks, received Butter Chicken warm!") but later filed non-delivery chargeback.
- Delivery timestamp logging prior to order placement due to courier clock drift.
- Order cancelled before kitchen prep with gateway refund pending.

---

## 7. Installation & Quickstart

### Prerequisites
- Python 3.10+ (tested on Python 3.12.3)
- Node.js 18+ (tested on Node.js v22.23.3)
- npm 9+

### Step 1: Clone & Navigate
```bash
cd /home/nanu/chargeback-dispute-copilot
```

### Step 2: Set Up Python Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Step 3: Seed Database & Train Model
```bash
# Seed 50 realistic disputes and linked orders/payments/evidence
python scripts/seed_db.py

# Train baseline Logistic Regression win-score model
python scripts/train_scoring_model.py
```

### Step 4: Run Automated Tests
```bash
# Run backend pytest suite (11 test cases)
PYTHONPATH=backend:.:$PYTHONPATH pytest backend/tests/

# Run complete 12-step end-to-end workflow verification
python scripts/verify_e2e_workflow.py
```

### Step 5: Start Unified Application
```bash
# Option A: Single Unified Server (Serves React Frontend SPA + FastAPI on Port 8000)
.venv/bin/uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000

# Option B: Development Mode with Hot Reload
# Terminal 1: Backend
.venv/bin/uvicorn app.main:app --app-dir backend --reload --port 8000

# Terminal 2: Frontend (Vite)
cd frontend
npm run dev
```

Open your browser at **`http://localhost:8000`** (or **`http://localhost:5173`** for Vite dev server).

---

## 8. Environment Configuration (`.env`)

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `development` | Deployment environment (`development`, `production`) |
| `PORT` | `8000` | Server listen port |
| `DATABASE_URL` | `sqlite:///./copilot.db` | Database connection string (SQLite or PostgreSQL) |
| `DISPUTE_SOURCE` | `mock` | Active provider: `mock` (deterministic) or `razorpay` |
| `RAZORPAY_KEY_ID` | `rzp_test_...` | Razorpay test mode Key ID |
| `RAZORPAY_KEY_SECRET` | `...` | Razorpay test mode Key Secret |
| `RAZORPAY_WEBHOOK_SECRET` | `...` | Secret for HMAC-SHA256 webhook signature validation |
| `LLM_PROVIDER` | `fallback` | Reasoner: `fallback` (offline rule engine) or `claude` |
| `ANTHROPIC_API_KEY` | `""` | Optional Anthropic API key for Claude 3.7 Sonnet |
| `UPLOAD_DIR` | `./uploads` | Directory for evidence document storage |
| `MAX_UPLOAD_SIZE_MB` | `10` | Maximum upload file size in megabytes |

---

## 9. Portfolio Demonstration Scenario

### Case Study: Non-Delivery Dispute with Chat Admission
1. **Queue Inspection**: Navigate to **Dispute Queue** and filter by `Reason: Product Not Received`.
2. **Open Dispute `disp_synth_1004`**: Review the disputed amount (₹499.00) for Order #RJK-1004.
3. **Timeline Inspection**: Observe that carrier Dunzo Express confirmed delivery via `OTP_VERIFIED` at the registered delivery address.
4. **Trigger AI Investigation**: The agent audits required evidence, discovers customer chat acknowledgment, and flags an alert:
   > `[HIGH ALERT] Customer Explicitly Confirmed Receipt in Chat: Customer stated: 'Thanks, received Butter Chicken warm!'`
5. **Inspect Explainable Win-Score**: Model computes **`98.1% (VERY HIGH)`** with breakdown:
   - `+30.1 pts`: Delivery verified with OTP or signature
   - `+15.2 pts`: Evidence completeness (100%)
6. **Response Studio**: Review the automatically generated Razorpay contest summary ($449 / 1,000$ characters).
7. **Download PDF Report**: Click **PDF Report** to stream the formal representation package.

---

## 10. Known Limitations & Roadmap

- **Model Calibration on Synthetic Data**: The baseline Logistic Regression model is evaluated on 50 synthetic RJ Kitchen disputes. Calibration metrics are displayed with appropriate sample-size caveats and must be re-calibrated on real-world bank dispute outcomes before production underwriting.
- **Razorpay Test Mode Dispute Generation**: In Razorpay test mode, dispute creation is simulated because gateway test sandboxes do not support arbitrary chargeback generation on demand.
- **Future Enhancements**: Multi-merchant tenancy, automated delivery courier webhook listeners (Dunzo / Shadowfax / Delhivery), and WhatsApp notification dispatch for customer receipt acknowledgments.
