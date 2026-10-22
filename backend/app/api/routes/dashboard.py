from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app.repositories.dispute_repo import DisputeRepository
from app.schemas.domain import DashboardSummary

router = APIRouter()


@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db_session)):
    """
    Returns aggregated executive metrics, amounts at risk, win rate, and urgent dispute queue.
    """
    summary = DisputeRepository.get_dashboard_summary(db)
    return summary
