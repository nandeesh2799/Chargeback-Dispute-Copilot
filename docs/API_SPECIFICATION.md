# Chargeback & Dispute Copilot — REST API Specification

## 1. Conventions & Standards

- **Base URL**: `/api`
- **Format**: JSON (`Content-Type: application/json; charset=utf-8`)
- **Error Standard**: RFC 7807 compliant structured JSON error format:
  ```json
  {
    "detail": {
      "code": "DISPUTE_NOT_FOUND",
      "message": "Dispute with ID disp_synth_9999 was not found",
      "timestamp": "2026-10-22T16:00:00Z"
    }
  }
  ```
- **Monetary Representation**: Integer minor units (e.g., INR paise, `249900` = ₹2,499.00).

---

## 2. Endpoints Matrix

### System & Health
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & component connectivity status |

### Dashboard & Analytics
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/summary` | Executive metrics, KPIs, risk amounts, urgency queues |
| `GET` | `/api/analytics/overview` | Reason breakdowns, win-rate trends, completeness correlations |
| `GET` | `/api/analytics/model-evaluation` | Confusion matrix, ROC-AUC, Brier score, calibration curve |

### Disputes
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/disputes` | Paginated, filterable, searchable dispute queue |
| `GET` | `/api/disputes/{dispute_id}` | Deep dispute detail including payments, orders, fulfilment, timeline |
| `POST` | `/api/disputes/{dispute_id}/investigate` | Triggers 10-step AI investigation & signal extraction |
| `POST` | `/api/disputes/{dispute_id}/score` | Calculates explainable win score with factor breakdown |
| `GET` | `/api/disputes/{dispute_id}/report` | Streams PDF Representation Report |
| `GET` | `/api/disputes/export/csv` | Streams CSV export of filtered disputes |
| `POST` | `/api/disputes/{dispute_id}/contest` | Safe contest submission (mock or Razorpay with guardrails) |

### Evidence Management
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/disputes/{dispute_id}/evidence` | List linked and candidate evidence for a dispute |
| `POST` | `/api/disputes/{dispute_id}/evidence` | Upload & link new evidence item |
| `DELETE` | `/api/disputes/{dispute_id}/evidence/{evidence_id}` | Unlink evidence item |

### Response Studio (Drafts)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/disputes/{dispute_id}/draft` | Get latest response draft & revision history |
| `POST` | `/api/disputes/{dispute_id}/draft/generate` | Generate fresh draft via AI or deterministic template |
| `PATCH` | `/api/disputes/{dispute_id}/draft` | Save edits, update citations, validate 1,000-char limit |
| `POST` | `/api/disputes/{dispute_id}/draft/approve` | Mark draft approved by reviewer |

### Integrations & Webhooks
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/integrations/status` | Active gateway & LLM status, credential masking |
| `POST` | `/api/integrations/diagnostics` | Test gateway & LLM connectivity |
| `POST` | `/api/webhooks/razorpay` | Razorpay webhook receiver with HMAC signature verification |

### Settings & Audit
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/settings/merchant` | Merchant profile & configuration |
| `POST` | `/api/settings/demo-reset` | Re-seeds 50 synthetic RJ Kitchen disputes cleanly |
| `GET` | `/api/settings/audit-logs` | Recent audit trail entries |
