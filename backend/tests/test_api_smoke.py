from datetime import timedelta

from app.schemas import TicketCreate
from app.services import ticket_service
from app.utils.time import now_ist


def test_smoke_flow(db_session, users):
    # create ticket
    payload = TicketCreate(
        category="Hardware",
        subcategory="Desktop",
        department="Ops",
        description="PC not working",
        workstation=None,
    )
    ticket = ticket_service.create_ticket(db_session, payload, users["alice"], image=None)

    # list my tickets
    _, tickets = ticket_service.list_my_tickets(db_session, users["alice"], scope="me", page=1, per_page=20)
    assert any(t.ticket_id == ticket.ticket_id for t in tickets)

    # pick ticket
    commitment = now_ist() + timedelta(hours=4)
    picked = ticket_service.pick_ticket(db_session, ticket.ticket_id, None, commitment, users["bob"])
    assert picked.status == "Assigned"

    # add update
    update = ticket_service.add_update(db_session, ticket.ticket_id, note="Investigating", user=users["bob"], status_change="In Progress")
    assert update.note == "Investigating"

    # resolve
    resolved = ticket_service.resolve_ticket(db_session, ticket.ticket_id, users["bob"], note="Fixed")
    assert resolved.status == "Resolved"
