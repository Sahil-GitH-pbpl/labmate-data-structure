import logging
from datetime import datetime, timedelta

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services import report_service
from app.integrations.whatsapp import send_whatsapp_message
from app.services.hiccup_service import compute_flags
from app.db.models import Hiccup, HiccupStatus, FollowupStatus

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler: BackgroundScheduler | None = None


def with_session(fn):
    def wrapper():
        db: Session = SessionLocal()
        try:
            fn(db)
        except Exception as exc:  # pragma: no cover - scheduler safety
            logger.error("Scheduler job failed: %s", exc)
        finally:
            db.close()

    return wrapper


def run_daily_summary(db: Session):
    digest = report_service.daily_digest(db)
    message_lines = [
        f"📊 Daily Hiccup Summary – {digest.date.date()}",
        f"Raised: {digest.raised}",
        f"Responded: {digest.responded}",
        f"Closed: {digest.closed}",
        f"Escalated to NC: {digest.escalated}",
        "",
        "By Department:",
    ]
    for row in digest.by_department:
        message_lines.append(f"Dept {row['department_id']}: {row['count']}")
    message_lines.append("\nSample Hiccups:")
    for sample in digest.sample:
        message_lines.extend(
            [
                f"#{sample['hiccup_id']} – {sample['raised_by']} → {sample['raised_against']}",
                f"Desc: {sample['short_desc']}",
                f"Status: {sample['status']}",
                "",
            ]
        )
    send_whatsapp_message(settings.management_numbers, "\n".join(message_lines))


def check_overdues(db: Session):
    open_items = db.query(Hiccup).filter(Hiccup.status.in_([HiccupStatus.open, HiccupStatus.responded])).all()
    for item in open_items:
        flags = compute_flags(item)
        if flags["is_response_overdue"] or flags["is_closure_overdue"]:
            logger.info("Overdue hiccup %s", item.hiccup_id)


def schedule_followups(db: Session):
    due = db.query(Hiccup).filter(
        Hiccup.followup_due <= datetime.utcnow(), Hiccup.followup_status == FollowupStatus.pending
    ).all()
    for h in due:
        logger.info("Followup pending for hiccup %s", h.hiccup_id)


def start_scheduler():
    global scheduler
    if scheduler:
        return scheduler
    scheduler = BackgroundScheduler(timezone=pytz.timezone(settings.timezone))
    scheduler.add_job(with_session(run_daily_summary), CronTrigger(hour=11, minute=0))
    scheduler.add_job(with_session(check_overdues), IntervalTrigger(hours=1))
    scheduler.add_job(with_session(schedule_followups), IntervalTrigger(hours=6))
    scheduler.start()
    logger.info("Scheduler started")
    return scheduler


def shutdown_scheduler():
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
