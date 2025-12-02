from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_management
from app.db.session import get_db
from app.schemas import DigestResponse, TrendSummary
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/daily", response_model=DigestResponse)
def get_daily_digest(db: Session = Depends(get_db), _: object = Depends(require_management)):
    return report_service.daily_digest(db)


@router.get("/trends", response_model=list[TrendSummary])
def get_trends(db: Session = Depends(get_db), _: object = Depends(require_management)):
    return report_service.trend_alerts(db)


@router.get("/monthly")
def get_monthly(db: Session = Depends(get_db), _: object = Depends(require_management)):
    return report_service.monthly_digest(db)
