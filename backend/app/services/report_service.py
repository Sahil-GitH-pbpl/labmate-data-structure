from datetime import date
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import InfraTicket

settings = get_settings()


def build_daily_summary(db: Session) -> str:
    today = date.today()
    tickets_today = db.scalar(
        select(func.count()).select_from(InfraTicket).where(func.date(InfraTicket.created_at) == today)
    )
    resolved_today = db.scalar(
        select(func.count())
        .select_from(InfraTicket)
        .where(func.date(InfraTicket.updated_at) == today, InfraTicket.status == "Resolved")
    )
    delayed = db.scalars(select(InfraTicket).where(InfraTicket.is_delayed_pick.is_(True))).all()

    lines = [
        f"Infra HelpDesk Daily Summary - {today.isoformat()}",
        f"Tickets raised today: {tickets_today or 0}",
        f"Tickets resolved today: {resolved_today or 0}",
        "Delayed picks:",
    ]
    if delayed:
        for ticket in delayed:
            lines.append(
                f"- #{ticket.ticket_id} {ticket.department}/{ticket.category} - created {ticket.created_at.strftime('%H:%M')}"
            )
    else:
        lines.append("- None")
    return "\n".join(lines)


def send_summary_email(body: str, recipients: List[str]) -> None:
    # Placeholder for email/WhatsApp integration
    print("Sending summary email to", ",".join(recipients))
    print(body)
