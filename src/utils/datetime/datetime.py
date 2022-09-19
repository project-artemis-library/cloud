from datetime import datetime, timedelta, timezone

JST = timezone(offset=timedelta(hours=+9), name="JST")


def now() -> datetime:
    return datetime.now(JST)
