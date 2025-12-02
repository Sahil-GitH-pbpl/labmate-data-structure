from datetime import datetime
import pytz

from app.core.config import get_settings

settings = get_settings()

def now_utc() -> datetime:
    return datetime.utcnow()


def now_local() -> datetime:
    tz = pytz.timezone(settings.timezone)
    return datetime.now(tz)
