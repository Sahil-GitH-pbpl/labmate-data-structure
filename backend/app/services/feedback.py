from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import FeedbackAnswer, FeedbackResponse, FeedbackTicket


def compute_scores(response: FeedbackResponse, answers: List[FeedbackAnswer]):
    scored_values = [a.score_value for a in answers if a.score_value is not None]
    if scored_values:
        response.overall_score = int(sum(scored_values) / len(scored_values))
    negative = any(a.sentiment == "negative" or (a.score_value is not None and a.score_value <= 2) for a in answers)
    response.overall_sentiment = "negative" if negative else "positive"
    rating_answers = [a for a in answers if a.question.is_overall_rating]
    if rating_answers:
        response.overall_rating_value = rating_answers[0].score_value

    text_present = any(a.answer_text for a in answers)
    if negative or (response.overall_rating_value and response.overall_rating_value <= 2):
        response.is_complaint = True
        response.status = "under_review"
    elif text_present:
        response.needs_manual_review = True
        response.status = "under_review"
    else:
        response.status = "auto_processed"


def create_ticket_if_needed(db: Session, response: FeedbackResponse) -> Optional[FeedbackTicket]:
    if not response.is_complaint:
        return None
    ticket = FeedbackTicket(
        ticket_number=f"TKT-{response.id}",
        response_id=response.id,
        campaign_id=response.campaign_id,
        severity="high" if response.overall_sentiment == "negative" else "medium",
        summary="Complaint triggered by low rating",
        details="System generated ticket for complaint",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    response.ticket_id = ticket.id
    db.commit()
    return ticket
