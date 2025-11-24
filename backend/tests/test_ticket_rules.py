from datetime import datetime, timedelta

import pytest

from app.services.job_scheduler import delayed_pick_job


def test_commitment_future_validation(client):
    # create ticket
    resp = client.post(
        "/infra/create",
        headers={"Authorization": "Bearer alice"},
        data={
            "category": "Hardware",
            "subcategory": "Desktop",
            "department": "Ops",
            "description": "Test",
        },
    )
    ticket_id = resp.json()["ticket_id"]
    past_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    resp = client.post(
        f"/infra/pick/{ticket_id}",
        headers={"Authorization": "Bearer bob"},
        json={"commitment_time": past_time},
    )
    assert resp.status_code == 400


def test_delayed_pick_flag(client):
    from app.db import SessionLocal
    from app.models import InfraTicket

    db = SessionLocal()
    ticket = InfraTicket(
        created_by="alice",
        department="Ops",
        category="Hardware",
        subcategory="Desktop",
        description="Stale ticket",
        status="New",
        created_at=datetime.utcnow() - timedelta(hours=4),
        updated_at=datetime.utcnow() - timedelta(hours=4),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    db.close()

    delayed_pick_job()

    db = SessionLocal()
    refreshed = db.get(InfraTicket, ticket.ticket_id)
    assert refreshed.is_delayed_pick is True
    db.close()
