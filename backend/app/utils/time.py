from datetime import datetime

import pytz

from ..config import get_settings

settings = get_settings()


def now_ist() -> datetime:
    tz = pytz.timezone(settings.timezone)
    return datetime.now(tz)
