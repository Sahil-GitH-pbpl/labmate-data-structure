from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth.arpra_jwt import User
from ..schemas import UpdateRequest, UpdateResponse, UpdatesList
from ..services import ticket_service
from ..utils.deps import get_current_active_user, get_db_session, get_it_admin_user

router = APIRouter(prefix="/infra", tags=["updates"])


@router.post("/update/{ticket_id}", response_model=UpdateResponse)
async def add_update(
    ticket_id: int,
    request: UpdateRequest,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_active_user),
):
    update = ticket_service.add_update(db, ticket_id, request.note, user, request.status)
    return update


@router.get("/updates/{ticket_id}", response_model=UpdatesList)
async def list_updates(ticket_id: int, db: Session = Depends(get_db_session), user: User = Depends(get_current_active_user)):
    updates = ticket_service.list_updates(db, ticket_id)
    return UpdatesList(ticket_id=ticket_id, updates=updates)
