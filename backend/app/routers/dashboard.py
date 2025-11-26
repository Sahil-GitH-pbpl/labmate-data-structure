from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FeedbackResponse, FeedbackTicket
from app.routers.auth import get_current_user

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    total_feedback = db.query(func.count(FeedbackResponse.id)).scalar() or 0
    total_complaints = db.query(func.count(FeedbackResponse.id)).filter(FeedbackResponse.is_complaint.is_(True)).scalar() or 0
    avg_rating = db.query(func.avg(FeedbackResponse.overall_score)).scalar()
    avg_rating = round(avg_rating, 2) if avg_rating else None
    open_tickets = db.query(FeedbackTicket).filter(FeedbackTicket.status != "closed").count()
    monthly_trend = (
        db.query(func.date(FeedbackResponse.submission_time).label("date"), func.count(FeedbackResponse.id))
        .group_by(func.date(FeedbackResponse.submission_time))
        .order_by(func.date(FeedbackResponse.submission_time))
        .all()
    )
    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "user": user,
            "stats": {
                "total_feedback": total_feedback,
                "total_complaints": total_complaints,
                "avg_rating": avg_rating,
                "open_tickets": open_tickets,
                "monthly_trend": monthly_trend,
            },
        },
    )
