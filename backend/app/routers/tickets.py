from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from ..auth.arpra_jwt import User
from ..schemas import InvalidRequest, PickTicketRequest, ResolveRequest, TicketCreate, TicketListResponse, TicketSummary
from ..services import ticket_service
from ..utils.deps import get_current_active_user, get_db_session, get_it_admin_user
from ..utils.time import now_ist

router = APIRouter(prefix="/infra", tags=["tickets"])


@router.post("/create", response_model=TicketSummary)
async def create_ticket(
    category: str = Form(...),
    subcategory: str = Form(...),
    department: str = Form(...),
    workstation: Optional[str] = Form(None),
    description: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_active_user),
):
    payload = TicketCreate(
        category=category,
        subcategory=subcategory,
        department=department,
        workstation=workstation,
        description=description,
    )
    ticket = ticket_service.create_ticket(db, payload, user, image)
    return ticket


@router.get("/all", response_model=TicketListResponse)
async def list_all(
    status_filter: Optional[str] = Query(None, alias="status"),
    category_filter: Optional[str] = Query(None, alias="category"),
    department_filter: Optional[str] = Query(None, alias="department"),
    q: Optional[str] = Query(None),
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_it_admin_user),
):
    total, tickets = ticket_service.list_all_tickets(db, status_filter, category_filter, department_filter, q, page, per_page)
    return TicketListResponse(total=total, page=page, per_page=per_page, items=tickets)


@router.get("/my", response_model=TicketListResponse)
async def list_my(
    scope: str = Query("me", regex="^(me|department)$"),
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_active_user),
):
    total, tickets = ticket_service.list_my_tickets(db, user, scope, page, per_page)
    return TicketListResponse(total=total, page=page, per_page=per_page, items=tickets)


@router.post("/pick/{ticket_id}", response_model=TicketSummary)
async def pick_ticket(
    ticket_id: int,
    request: PickTicketRequest,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_it_admin_user),
):
    ticket = ticket_service.pick_ticket(db, ticket_id, request.assigned_to, request.commitment_time, user)
    return ticket


@router.post("/resolve/{ticket_id}", response_model=TicketSummary)
async def resolve_ticket(
    ticket_id: int,
    request: ResolveRequest,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_it_admin_user),
):
    ticket = ticket_service.resolve_ticket(db, ticket_id, user, request.note)
    return ticket


@router.post("/invalid/{ticket_id}", response_model=TicketSummary)
async def invalid_ticket(
    ticket_id: int,
    request: InvalidRequest,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_it_admin_user),
):
    ticket = ticket_service.mark_invalid(db, ticket_id, user, request.invalid_reason)
    return ticket
