from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign, FeedbackResponse
from app.routers.auth import get_current_user

router = APIRouter(tags=["responses"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def list_responses(
    request: Request,
    campaign_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = db.query(FeedbackResponse)
    if campaign_id:
        query = query.filter(FeedbackResponse.campaign_id == campaign_id)
    responses = query.order_by(FeedbackResponse.submission_time.desc()).all()
    campaigns = db.query(Campaign).all()
    return templates.TemplateResponse(
        "responses/list.html",
        {
            "request": request,
            "responses": responses,
            "campaigns": campaigns,
            "selected_campaign": campaign_id,
            "user": user,
        },
    )


@router.get("/{response_id}")
async def response_detail(
    response_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    response = db.query(FeedbackResponse).get(response_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    return templates.TemplateResponse(
        "responses/detail.html",
        {"request": request, "response": response, "user": user},
    )
