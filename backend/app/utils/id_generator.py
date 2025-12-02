from datetime import datetime
from sqlalchemy.orm import Session

from app.db.models import Hiccup


def generate_hiccup_id(db: Session) -> str:
    year_suffix = datetime.utcnow().strftime("%y")
    prefix = f"HCP-{year_suffix}-"
    latest = (
        db.query(Hiccup)
        .filter(Hiccup.hiccup_id.like(f"{prefix}%"))
        .order_by(Hiccup.hiccup_id.desc())
        .first()
    )
    if latest:
        try:
            seq = int(latest.hiccup_id.split("-")[-1]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f"{prefix}{seq:03d}"
