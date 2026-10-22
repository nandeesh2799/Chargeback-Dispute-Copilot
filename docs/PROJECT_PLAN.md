# Chargeback & Dispute Copilot — Project Plan

## Executive Overview
**Chargeback & Dispute Copilot** is an enterprise-grade financial operations platform designed for online merchants to investigate, manage, and resolve payment disputes and chargebacks. Focussing on **RJ Kitchen** (a high-volume cloud kitchen), the application bridges payment gateways (Razorpay test mode and deterministic mock sources) with an evidence intelligence engine, an explainable machine learning win-probability scoring pipeline, and an auditable AI investigation agent.

---

## Phased Implementation Plan

### Phase 0: Environment Inspection & Planning
- [x] Inspect tools, runtime versions (Node v22.23.3, Python 3.12.3, npm 10.9.9).
- [x] Inspect existing skills and design system guidelines.
- [x] Establish monorepo structure: `backend/`, `frontend/`, `data/`, `docs/`, `scripts/`.
- [x] Author comprehensive project architecture, database, API, AI agent, test, and security specifications.
- [x] Create `.env.example` and `.gitignore`.

### Phase 1: Foundation Architecture
- [ ] Initialize Python backend with FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2.
- [ ] Initialize Vite + React 18/TypeScript frontend with Tailwind CSS, Lucide icons, Recharts, TanStack Query, Radix UI primitives.
- [ ] Configure unified design tokens: Slate/Navy backgrounds, Indigo accent `#4F46E5`, Emerald positive `#10B981`, Amber review `#F59E0B`, Crimson alert `#EF4444`.
- [ ] Implement backend health endpoint `GET /api/health` and verify cross-origin communication.

### Phase 2: Database Models & Synthetic Data Generation
- [ ] Implement normalized SQLAlchemy models:
  - `merchants`, `users`, `disputes`, `payments`, `orders`, `customers`
  - `fulfilment_records`, `customer_messages`, `evidence_items`, `evidence_links`
  - `ai_investigations`, `response_drafts`, `scoring_results`, `dispute_outcomes`
  - `integration_configs`, `webhook_events`, `audit_logs`
- [ ] Author deterministic synthetic generator producing **50 realistic disputes** for RJ Kitchen.
- [ ] Cover all 5 core chargeback categories:
  1. Product or service not received (15 cases)
  2. Order cancelled but charged (10 cases)
  3. Fraud / unauthorized transaction (10 cases)
  4. Product or service not as described (10 cases)
  5. Duplicate charge (5 cases)
- [ ] Embed realistic edge cases: conflicting timestamps, delivery without OTP, signed OTP delivery, partial refunds, duplicate charges across multiple orders.
- [ ] Implement database seeding and reset scripts (`scripts/seed_db.py`, `POST /api/settings/demo-reset`).

### Phase 3: Dispute Queue & Executive Dashboard UI
- [ ] Implement Executive Dashboard:
  - Live metric aggregations (Total disputes, Win rate, Amount at risk, Evidence completeness, Urgent deadlines).
  - Trend charts, dispute reason distribution, outcome breakdown.
  - Urgent dispute alert banner and queue preview.
- [ ] Implement Dispute Queue Table:
  - Real-time search by dispute ID, order ID, payment ID, customer name.
  - Multi-attribute filtering (Status, Reason, Readiness, Risk tier).
  - Column sorting and responsive pagination.
  - Visual status badges and urgency indicators.

### Phase 4: Dispute Investigation Workspace & Evidence Intelligence
- [ ] Build split-pane Investigation Workspace:
  - Summary header with countdown to response deadline and status indicators.
  - Multi-tab navigation: Overview & Timeline, Evidence Vault, AI Investigation, Response Studio, Scoring & Audit.
  - Visual payment & fulfilment timeline.
  - Customer communication thread inspector.
- [ ] Implement `DisputeInvestigationAgent`:
  - 10-step auditable pipeline.
  - Reason-specific evidence checklist evaluation.
  - Contradiction and gap detection.
  - Fact extraction and provenance attribution (linking claims to underlying IDs).
  - Deterministic fallback provider for offline/credential-less environments.

### Phase 5: Response Studio & PDF/Data Exports
- [ ] Build AI Response Studio:
  - Razorpay contest summary editor (strict 1,000-character limit enforcement with visual counter).
  - Comprehensive formal Dispute Representation Letter generator.
  - Cited evidence attachment mapper.
  - One-click copy, draft auto-save, and manual edits.
- [ ] Implement high-fidelity PDF report generation (ReportLab) with executive typography, visual charts/tables, and provenance labels.
- [ ] Implement CSV and JSON dispute queue exports.

### Phase 6: Explainable Scoring Pipeline & Model Evaluation
- [ ] Implement Scikit-learn Logistic Regression scoring pipeline:
  - Feature engineering (evidence completeness, delivery verification strength, contradiction penalties, time buffer, refund status).
  - Group-stratified train/test evaluation (80/20 split).
  - Transparent feature contribution breakdown (top positive and negative factors).
  - Model metrics calculation (Precision, Recall, F1, ROC-AUC, Brier score, Confusion Matrix).
- [ ] Implement Analytics & Model Evaluation UI:
  - Model diagnostic dashboard with calibration status and sample-size warnings.

### Phase 7: Gateway & Provider Integrations (Razorpay & LLM)
- [ ] Implement abstract `DisputeSource` interface with `MockDisputeSource` and `RazorpayDisputeSource`.
- [ ] Implement Razorpay test-mode API adapter (`/v1/disputes`, `/v1/payments`).
- [ ] Implement secure Webhook endpoint (`POST /api/webhooks/razorpay`) with HMAC-SHA256 signature verification and idempotency protection.
- [ ] Implement multi-provider LLM adapter (`ClaudeProvider`, `OpenAICompatibleProvider`, `DeterministicFallbackProvider`).
- [ ] Implement guardrails preventing mock IDs from reaching live gateway endpoints and requiring explicit two-step human confirmation for contest submission.

### Phase 8: Hardening, Automated Testing & Verification
- [ ] Author comprehensive backend tests (pytest): models, seeding, agent workflow, scoring, webhooks, PDF generation, security.
- [ ] Author frontend component and integration tests.
- [ ] Run full test suites, type checking, and linters.
- [ ] Execute automated browser tests with Playwright.

### Phase 9: Documentation & Portfolio Presentation
- [ ] Author comprehensive `README.md` with architecture diagrams, setup guides, API reference, demo walkthrough, and limitations.
- [ ] Verify clean startup from scratch.
