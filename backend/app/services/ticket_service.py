from datetime import datetime
from typing import Optional, Tuple

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..auth.arpra_jwt import User, is_it_or_admin
from ..models import InfraTicket, InfraUpdate
from ..schemas import TicketCreate
from ..storage import save_image
from ..utils.time import now_ist

V2_SELF_HELP_ENABLED = False


def create_ticket(db: Session, payload: TicketCreate, creator: User, image: Optional[UploadFile]) -> InfraTicket:
    image_path = save_image(image)
    ticket = InfraTicket(
        created_by=creator.username,
        department=payload.department,
        category=payload.category,
        subcategory=payload.subcategory,
        description=payload.description,
        workstation=payload.workstation,
        image_path=image_path,
        created_at=now_ist(),
        updated_at=now_ist(),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def list_all_tickets(
    db: Session,
    status_filter: Optional[str],
    category_filter: Optional[str],
    department_filter: Optional[str],
    query: Optional[str],
    page: int,
    per_page: int,
) -> Tuple[int, list[InfraTicket]]:
    stmt = select(InfraTicket)
    if status_filter:
        stmt = stmt.where(InfraTicket.status == status_filter)
    if category_filter:
        stmt = stmt.where(InfraTicket.category == category_filter)
    if department_filter:
        stmt = stmt.where(InfraTicket.department == department_filter)
    if query:
        stmt = stmt.where(or_(InfraTicket.description.ilike(f"%{query}%"), InfraTicket.subcategory.ilike(f"%{query}%")))

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    stmt = stmt.order_by(InfraTicket.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    tickets = db.scalars(stmt).all()
    return total or 0, tickets


def list_my_tickets(db: Session, user: User, scope: str, page: int, per_page: int) -> Tuple[int, list[InfraTicket]]:
    stmt = select(InfraTicket)
    if scope == "department":
        stmt = stmt.where(InfraTicket.department == user.department)
    else:
        stmt = stmt.where(InfraTicket.created_by == user.username)
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    stmt = stmt.order_by(InfraTicket.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    tickets = db.scalars(stmt).all()
    return total or 0, tickets


def _get_ticket(db: Session, ticket_id: int) -> InfraTicket:
    ticket = db.get(InfraTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


def pick_ticket(db: Session, ticket_id: int, assigned_to: Optional[str], commitment_time: datetime, user: User) -> InfraTicket:
    ticket = _get_ticket(db, ticket_id)
    if not is_it_or_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if commitment_time <= now_ist():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Commitment time must be future")
    ticket.assigned_to = assigned_to or user.username
    ticket.commitment_time = commitment_time
    ticket.status = "Assigned"
    ticket.is_delayed_pick = False
    ticket.updated_at = now_ist()
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def add_update(db: Session, ticket_id: int, note: str, user: User, status_change: Optional[str] = None) -> InfraUpdate:
    ticket = _get_ticket(db, ticket_id)
    if not is_it_or_admin(user) and ticket.assigned_to != user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if status_change:
        ticket.status = status_change
    ticket.updated_at = now_ist()
    update = InfraUpdate(ticket_id=ticket_id, note=note, created_by=user.username, created_at=now_ist())
    db.add(update)
    db.add(ticket)
    db.commit()
    db.refresh(update)
    return update


def resolve_ticket(db: Session, ticket_id: int, user: User, note: Optional[str]) -> InfraTicket:
    ticket = _get_ticket(db, ticket_id)
    if not is_it_or_admin(user) and ticket.assigned_to != user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    ticket.status = "Resolved"
    ticket.updated_at = now_ist()
    if note:
        db.add(InfraUpdate(ticket_id=ticket_id, note=note, created_by=user.username, created_at=now_ist()))
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def mark_invalid(db: Session, ticket_id: int, user: User, reason: str) -> InfraTicket:
    ticket = _get_ticket(db, ticket_id)
    if not is_it_or_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    ticket.is_invalid = True
    ticket.invalid_reason = reason
    ticket.updated_at = now_ist()
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def list_updates(db: Session, ticket_id: int) -> list[InfraUpdate]:
    _get_ticket(db, ticket_id)
    stmt = select(InfraUpdate).where(InfraUpdate.ticket_id == ticket_id).order_by(InfraUpdate.created_at.asc())
    return db.scalars(stmt).all()
