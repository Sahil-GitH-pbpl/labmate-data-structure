from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign, CampaignQuestion, CampaignQuestionOption
from app.routers.auth import get_current_user, require_role

router = APIRouter(tags=["questionnaire"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/{campaign_id}")
async def view_questionnaire(
    campaign_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    campaign = db.query(Campaign).get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    questions = (
        db.query(CampaignQuestion)
        .filter(CampaignQuestion.campaign_id == campaign_id)
        .order_by(CampaignQuestion.order_index)
        .all()
    )
    return templates.TemplateResponse(
        "campaigns/edit.html",
        {
            "request": request,
            "campaign": campaign,
            "questions": questions,
            "action": f"/campaigns/{campaign_id}/edit",
            "user": user,
            "channels": [],
        },
    )


@router.post("/{campaign_id}/add_question")
async def add_question(
    campaign_id: int,
    request: Request,
    question_text_en: str = Form(...),
    question_type: str = Form(...),
    is_required: bool = Form(False),
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    campaign = db.query(Campaign).get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    order_index = (
        db.query(CampaignQuestion)
        .filter(CampaignQuestion.campaign_id == campaign_id)
        .count()
    )
    question = CampaignQuestion(
        campaign_id=campaign_id,
        question_text_en=question_text_en,
        question_type=question_type,
        is_required=is_required,
        order_index=order_index + 1,
    )
    db.add(question)
    db.commit()
    return RedirectResponse(url=f"/questionnaire/{campaign_id}", status_code=302)


@router.post("/{campaign_id}/questions/{question_id}/add_option")
async def add_option(
    campaign_id: int,
    question_id: int,
    option_text_en: str = Form(...),
    option_value: str = Form(...),
    sentiment: str = Form("neutral"),
    score_value: int = Form(0),
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    question = db.query(CampaignQuestion).get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    option = CampaignQuestionOption(
        campaign_question_id=question_id,
        option_text_en=option_text_en,
        option_value=option_value,
        sentiment=sentiment,
        score_value=score_value,
    )
    db.add(option)
    db.commit()
    return RedirectResponse(url=f"/questionnaire/{campaign_id}", status_code=302)
