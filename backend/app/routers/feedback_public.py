from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign, CampaignQuestion, CampaignRecipient, FeedbackAnswer, FeedbackResponse
from app.services.feedback import compute_scores, create_ticket_if_needed

router = APIRouter(tags=["feedback_public"], include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")


def load_campaign_by_token(db: Session, token: str) -> tuple[Campaign, Optional[CampaignRecipient]]:
    recipient = db.query(CampaignRecipient).filter(CampaignRecipient.personalized_link_token == token).first()
    if recipient:
        campaign = recipient.campaign
        return campaign, recipient
    campaign_query = db.query(Campaign).filter(Campaign.code == token)
    if token.isdigit():
        campaign_query = campaign_query.union(db.query(Campaign).filter(Campaign.id == int(token)))
    campaign = campaign_query.first()
    return campaign, None


@router.get("/{token}")
async def view_form(token: str, request: Request, db: Session = Depends(get_db)):
    campaign, recipient = load_campaign_by_token(db, token)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    questions = (
        db.query(CampaignQuestion)
        .filter(CampaignQuestion.campaign_id == campaign.id)
        .order_by(CampaignQuestion.order_index)
        .all()
    )
    total_questions = len(questions)
    return templates.TemplateResponse(
        "feedback/form.html",
        {
            "request": request,
            "campaign": campaign,
            "recipient": recipient,
            "questions": questions,
            "total_questions": total_questions,
            "token": token,
        },
    )


@router.post("/{token}")
async def submit_form(token: str, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    campaign, recipient = load_campaign_by_token(db, token)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    response = FeedbackResponse(campaign_id=campaign.id, recipient_id=recipient.id if recipient else None)
    db.add(response)
    db.commit()
    db.refresh(response)

    answers = []
    questions = db.query(CampaignQuestion).filter(CampaignQuestion.campaign_id == campaign.id).all()
    for question in questions:
        key = f"q_{question.id}"
        if question.question_type == "mcq_multi":
            value = form.getlist(key)
        else:
            value = form.get(key)
        selected_values = value if isinstance(value, list) else [value] if value else []
        answer_text = value if question.question_type in ["text"] else None
        selected_option_values = selected_values if question.question_type.startswith("mcq") or question.question_type.startswith("rating") else []
        sentiment = None
        score = None
        if selected_option_values:
            option = (
                db.query(CampaignQuestionOption)
                .filter(
                    CampaignQuestionOption.campaign_question_id == question.id,
                    CampaignQuestionOption.option_value == selected_option_values[0],
                )
                .first()
            )
            if option:
                sentiment = option.sentiment
                score = option.score_value
        ans = FeedbackAnswer(
            response_id=response.id,
            campaign_question_id=question.id,
            question=question,
            answer_text=answer_text,
            selected_option_values=selected_option_values,
            sentiment=sentiment,
            score_value=score,
            department=None,
            area=None,
        )
        db.add(ans)
        answers.append(ans)
    db.commit()

    compute_scores(response, answers)
    db.commit()
    create_ticket_if_needed(db, response)

    return templates.TemplateResponse(
        "feedback/thank_you.html",
        {"request": request, "campaign": campaign, "response": response},
    )


from app.models import CampaignQuestionOption  # noqa: E402  keep import local to avoid circular
