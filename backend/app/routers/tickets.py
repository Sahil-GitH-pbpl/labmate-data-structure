from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FeedbackTicket, TicketUpdate
from app.routers.auth import get_current_user, require_role

router = APIRouter(tags=["tickets"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def list_tickets(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    tickets = db.query(FeedbackTicket).order_by(FeedbackTicket.created_at.desc()).all()
    return templates.TemplateResponse(
        "tickets/list.html", {"request": request, "tickets": tickets, "user": user}
    )


@router.get("/{ticket_id}")
async def view_ticket(ticket_id: int, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ticket = db.query(FeedbackTicket).get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return templates.TemplateResponse(
        "tickets/detail.html", {"request": request, "ticket": ticket, "user": user}
    )


@router.post("/{ticket_id}/update")
async def add_update(
    ticket_id: int,
    request: Request,
    update_text: str = Form(...),
    status: str = Form("open"),
    closure_mood: str | None = Form(None),
    db: Session = Depends(get_db),
    user=Depends(require_role("l2")),
):
    ticket = db.query(FeedbackTicket).get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.status = status
    if closure_mood:
        ticket.closure_mood = closure_mood
    update = TicketUpdate(ticket_id=ticket_id, update_text=update_text, updated_by_user_id=user.id)
    db.add(update)
    db.commit()
    return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=302)
