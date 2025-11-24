import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

os.environ.setdefault("DATABASE_URL", "sqlite:///./seed.db")

from app.models import Base, InfraTicket, InfraUpdate  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.utils.time import now_ist  # noqa: E402

settings = get_settings()
engine = create_engine(settings.sqlalchemy_database_uri)
Base.metadata.create_all(engine)

sample_tickets = [
    InfraTicket(created_by="alice", department="Operations", category="Hardware", subcategory="Desktop", description="Monitor not working", status="New", created_at=now_ist(), updated_at=now_ist()),
    InfraTicket(created_by="alice", department="Operations", category="Software", subcategory="OS", description="OS update", status="Assigned", assigned_to="bob", commitment_time=now_ist(), created_at=now_ist(), updated_at=now_ist()),
]

with Session(engine) as session:
    for ticket in sample_tickets:
        session.add(ticket)
    session.commit()
    session.refresh(sample_tickets[0])
    session.add(InfraUpdate(ticket_id=sample_tickets[0].ticket_id, note="Initial check", created_by="bob"))
    session.commit()

print("Seed data inserted")
