from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

from ..config import get_settings
from ..db import SessionLocal
from ..models import InfraTicket
from ..utils.time import now_ist
from .report_service import build_daily_summary, send_summary_email

settings = get_settings()
scheduler = BackgroundScheduler(timezone=settings.timezone)


def delayed_pick_job():
    db = SessionLocal()
    try:
        cutoff = now_ist() - timedelta(hours=3)
        stmt = select(InfraTicket).where(InfraTicket.status == "New", InfraTicket.created_at < cutoff)
        tickets = db.scalars(stmt).all()
        newly_flagged = 0
        for ticket in tickets:
            if not ticket.is_delayed_pick:
                ticket.is_delayed_pick = True
                newly_flagged += 1
                db.add(ticket)
        if newly_flagged:
            db.commit()
        print(f"Delayed pick job flagged {newly_flagged} tickets")
    finally:
        db.close()


def daily_summary_job():
    db = SessionLocal()
    try:
        summary = build_daily_summary(db)
        send_summary_email(summary, settings.admin_emails)
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(delayed_pick_job, "interval", minutes=15, id="delayed_pick")
    scheduler.add_job(daily_summary_job, "cron", hour=11, minute=0, id="daily_summary")
    scheduler.start()


def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
