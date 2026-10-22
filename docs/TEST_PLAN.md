# Chargeback & Dispute Copilot — Test Plan

## 1. Testing Strategy & Multi-Tier Matrix

The application must be rigorously tested across unit, integration, model evaluation, and end-to-end workflows:

```
+-----------------------------------------------------------+
|              End-to-End Playwright Tests                  |
|    Complete operator workflows, UI state machines, PDF    |
+-----------------------------------------------------------+
                            |
+-----------------------------------------------------------+
|            API & Integration Tests (HTTPX / Pytest)       |
|    Endpoint contracts, webhook signature, mock source     |
+-----------------------------------------------------------+
                            |
+-----------------------------------------------------------+
|           Unit Tests: Logic, Agent, Scoring, PDF          |
|    Feature extraction, 10-step agent, 1000-char limiter   |
+-----------------------------------------------------------+
```

---

## 2. Test Suites

### 2.1 Backend Unit & Logic Tests (`backend/tests/`)
- `test_models.py`: Verify model relationships, constraints, and integer minor units calculations.
- `test_seeding.py`: Verify deterministic generation of 50 disputes with realistic edge cases.
- `test_agent_workflow.py`: Test all 10 steps of the investigation agent with mocked and deterministic outputs.
- `test_contradiction_detector.py`: Ensure timestamp conflicts and false claims trigger alerts.
- `test_scoring_pipeline.py`: Verify feature vector generation, logistic regression predictions, and explainability factors.
- `test_razorpay_adapter.py`: Validate SDK adapter, safety guardrails preventing mock submissions to live gateways, and character limit checks.
- `test_webhooks.py`: Validate HMAC-SHA256 signature verification, idempotency duplicate rejection, and malformed payload handling.
- `test_pdf_export.py`: Ensure PDF generates cleanly without errors and includes correct dispute metadata and provenance tags.

### 2.2 Frontend Component & Integration Tests
- Verify dispute queue rendering, search, filtering, and pagination.
- Verify status badges, readiness pills, and countdown timers.
- Test 1,000-character contest summary input enforcement and real-time counter.
- Test tab navigation in the dispute workspace.

### 2.3 End-to-End Workflow Verification
1. Access `/` (Dashboard) — verify loaded synthetic KPIs (total disputes, amount at risk, win rate).
2. Navigate to Dispute Queue — filter by `Reason: Product Not Received` and `Status: Open`.
3. Open high-urgency dispute `disp_synth_1001`.
4. Inspect Overview & Timeline tab — confirm delivery timestamp vs order time.
5. Trigger AI Investigation — verify findings summary and contradiction detection badges.
6. Open Response Studio — verify auto-drafted 1,000-char contest summary and full letter.
7. Edit response draft and save — verify persistence.
8. View Explainable Score — verify factor weights and top positive/negative drivers.
9. Download PDF Report — verify response stream is valid PDF application/octet-stream.
10. Trigger Demo Reset — verify database state is restored cleanly.
