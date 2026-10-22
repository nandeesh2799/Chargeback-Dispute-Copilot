# Chargeback & Dispute Copilot — Architecture Specification

## 1. System Context & Overview

Chargeback & Dispute Copilot is architected as a modular, decoupled web application that enables merchants to ingest, audit, score, and respond to payment disputes.

```
                           +--------------------------------+
                           |       Merchant Operator        |
                           +--------------------------------+
                                          |
                                          v
                      +------------------------------------------+
                      |         React + Vite Frontend            |
                      |   (Tailwind CSS, TanStack Query, Radix)  |
                      +------------------------------------------+
                                          |
                                          | HTTPS / REST / JSON
                                          v
+------------------------------------------------------------------------------------+
|                                FastAPI Backend                                     |
|                                                                                    |
|  [ API Layer: Routes & Routers ]                                                   |
|      /api/health       /api/dashboard    /api/disputes     /api/evidence           |
|      /api/scoring      /api/analytics    /api/integrations /api/webhooks           |
|                                                                                    |
|  [ Application & Business Services ]                                               |
|      DisputeService    EvidenceService   AuditService      ExportService           |
|                                                                                    |
|  [ Intelligence Engines ]                                                          |
|      DisputeInvestigationAgent   ExplainableScoringPipeline (scikit-learn)         |
|      (10-Step Deterministic + LLM) (Feature engineering + Logistic Regression)      |
|                                                                                    |
|  [ Integration Boundary ]                                                          |
|      DisputeSource Interface ──► MockDisputeSource (Deterministic 50 fixtures)      |
|                              ──► RazorpayDisputeSource (Test-mode Gateway API)     |
|      LLMProvider Interface   ──► ClaudeProvider / OpenAIProvider / Fallback        |
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

## 2. Monorepo Structural Blueprint

```
chargeback-dispute-copilot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py               # Dependency injection (db session, auth, sources)
│   │   │   └── routes/
│   │   │       ├── health.py         # System health & readiness
│   │   │       ├── dashboard.py      # Aggregated metrics & queue previews
│   │   │       ├── disputes.py       # CRUD & state-machine operations
│   │   │       ├── evidence.py       # Vault, uploads, links, integrity checks
│   │   │       ├── drafts.py         # AI generation, human edit, 1,000-char limits
│   │   │       ├── scoring.py        # Explainable model inference & weights
│   │   │       ├── analytics.py      # Win-rates, reason breakdown, calibration
│   │   │       ├── integrations.py   # Gateway & LLM credentials & diagnostics
│   │   │       ├── webhooks.py       # Razorpay HMAC verification & event ingestion
│   │   │       └── settings.py       # Merchant profile, demo data reset
│   │   ├── core/
│   │   │   ├── config.py             # Pydantic BaseSettings (.env loading)
│   │   │   ├── logging.py            # Structured contextual logging
│   │   │   ├── security.py           # HMAC verification, token utilities, path sanitization
│   │   │   └── exceptions.py         # Custom application domain exceptions
│   │   ├── db/
│   │   │   ├── base.py               # SQLAlchemy DeclarativeBase
│   │   │   └── session.py            # Engine and sessionmaker factories
│   │   ├── models/                   # 17 normalized SQLAlchemy entity models
│   │   ├── schemas/                  # Pydantic v2 schemas for request/response contracts
│   │   ├── repositories/             # Clean repository pattern isolating DB queries
│   │   ├── services/                 # Core domain business logic
│   │   ├── agents/                   # 10-step auditable dispute investigation agent
│   │   ├── scoring/                  # Logistic regression, feature extraction, evaluation
│   │   ├── evidence/                 # Checklist auditor, contradiction detector
│   │   ├── exports/                  # ReportLab PDF generator, CSV/JSON exporters
│   │   ├── integrations/             # Source adapters (Mock, Razorpay, LLM providers)
│   │   └── main.py                   # FastAPI application factory & CORS configuration
│   ├── tests/                        # Comprehensive pytest suite
│   ├── requirements.txt              # Pinned backend dependencies
│   └── alembic.ini                   # Migration configuration
├── frontend/
│   ├── src/
│   │   ├── app/                      # App router, theme provider, query client
│   │   ├── components/               # Accessible UI components (buttons, badges, modals, cards)
│   │   ├── features/
│   │   │   ├── dashboard/            # Executive summary widgets, KPIs, charts
│   │   │   ├── disputes/             # Searchable queue table, filter panel, pagination
│   │   │   │   └── workspace/        # Split-pane investigation workspace
│   │   │   ├── evidence/             # Evidence vault, attachment previews, integrity badges
│   │   │   ├── analytics/            # Model performance, ROC/AUC, calibration curve
│   │   │   ├── integrations/         # Gateway connection cards, webhook diagnostic logs
│   │   │   └── settings/             # Demo reset controls, merchant profile
│   │   ├── hooks/                    # Reusable React hooks
│   │   ├── lib/                      # Axios/fetch API client, formatting utilities
│   │   ├── types/                    # TypeScript interfaces matching backend schemas
│   │   └── styles/                   # Tailwind CSS root styles
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── data/
│   └── synthetic/                    # 50 deterministic RJ Kitchen dispute fixtures
├── docs/                             # Architecture & developer specifications
├── scripts/                          # Seeding, training, and verification scripts
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 3. Core Interface Contracts

### 3.1 Dispute Source (`backend/app/integrations/dispute_source.py`)
```python
class DisputeSource(ABC):
    @abstractmethod
    async def list_disputes(self, limit: int = 50, offset: int = 0, status: Optional[str] = None) -> List[DisputeEntity]:
        pass

    @abstractmethod
    async def get_dispute(self, dispute_id: str) -> Optional[DisputeEntity]:
        pass

    @abstractmethod
    async def fetch_payment(self, payment_id: str) -> Optional[PaymentEntity]:
        pass

    @abstractmethod
    async def submit_contest(self, dispute_id: str, summary: str, document_ids: List[str]) -> ContestSubmissionResult:
        pass
```

### 3.2 LLM Provider (`backend/app/integrations/llm/base.py`)
```python
class LLMProvider(ABC):
    @abstractmethod
    async def extract_signals(self, dispute_context: DisputeInvestigationContext) -> ExtractedSignals:
        pass

    @abstractmethod
    async def generate_contest_draft(self, dispute_context: DisputeInvestigationContext, evidence_inventory: EvidenceInventory) -> GeneratedDraft:
        pass
```

---

## 4. Security & Safety Boundaries

1. **Gateways are Read-First**: By default, `DISPUTE_SOURCE=mock`. When switching to `razorpay`, all contest submissions require manual two-stage human review and explicit frontend confirmation.
2. **Character Constraint Enforcement**: Razorpay limits contest summaries to 1,000 characters. The backend enforces this validation before any payload leaves the integration boundary.
3. **No Mock Submissions**: Any attempt to submit a synthetic dispute (`disp_synth_...`) to Razorpay is intercepted and rejected with an explicit safety exception.
4. **Data Isolation**: Synthetic records are marked with `is_synthetic=True` in the database, and clearly badged in the UI to prevent merchant confusion.
