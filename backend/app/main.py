import os
import sys

# Ensure project root is in sys.path so root packages like 'data' are always importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import (
    health,
    dashboard,
    disputes,
    evidence,
    drafts,
    analytics,
    integrations,
    webhooks,
    settings as settings_router
)

setup_logging()

app = FastAPI(
    title="Chargeback & Dispute Copilot API",
    description="AI-Powered Payment Dispute Investigation, Evidence Intelligence & Resolution Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(disputes.router, prefix="/api", tags=["Disputes"])
app.include_router(evidence.router, prefix="/api", tags=["Evidence"])
app.include_router(drafts.router, prefix="/api", tags=["Response Studio"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics & Scoring"])
app.include_router(integrations.router, prefix="/api", tags=["Integrations"])
app.include_router(webhooks.router, prefix="/api", tags=["Webhooks"])
app.include_router(settings_router.router, prefix="/api", tags=["Settings & Audit"])


# Mount frontend production build if available
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "service": "Chargeback & Dispute Copilot API",
            "status": "operational",
            "docs": "/api/docs",
            "health": "/api/health"
        }
