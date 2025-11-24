from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.schemas import TicketCreate
from app.services import ticket_service
from app.services.job_scheduler import delayed_pick_job
from app.utils.time import now_ist


def test_commitment_future_validation(db_session, users):
    payload = TicketCreate(
        category="Hardware",
        subcategory="Desktop",
        department="Ops",
        description="Test",
        workstation=None,
    )
    ticket = ticket_service.create_ticket(db_session, payload, users["alice"], image=None)
    past_time = now_ist() - timedelta(hours=1)
    with pytest.raises(HTTPException) as exc:
        ticket_service.pick_ticket(db_session, ticket.ticket_id, None, past_time, users["bob"])
    assert exc.value.status_code == 400


def test_delayed_pick_flag(db_session, users):
    from app.models import InfraTicket

    ticket = InfraTicket(
        created_by=users["alice"].username,
        department="Ops",
        category="Hardware",
        subcategory="Desktop",
        description="Stale ticket",
        status="New",
        created_at=now_ist() - timedelta(hours=4),
        updated_at=now_ist() - timedelta(hours=4),
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)

    delayed_pick_job()

    db_session.expire_all()
    refreshed = db_session.get(InfraTicket, ticket.ticket_id)
    assert refreshed.is_delayed_pick is True
