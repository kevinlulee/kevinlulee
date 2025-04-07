from datetime import datetime, timedelta
import os

def to_datetime(x=None):
    if x is None:
        return datetime.now()
    if isinstance(x, str):
        path = os.path.expanduser(x)
        assert os.path.isfile(path), f'Not a valid file: {path}'
        return datetime.fromtimestamp(os.path.getmtime(path))
    if isinstance(x, (int, float)):
        return datetime.fromtimestamp(x)
    return x


def get_season(d):
    if dt.month in range(3, 6):
        return "Spring"
    elif dt.month in range(6, 9):
        return "Summer"
    elif dt.month in range(9, 12):
        return "Autumn"
    else:
        return "Winter"


def strftime(source=None, mode="iso8601"):
    templates = {
        "iso8601": "%Y-%m-%d",
        "clock": "%-I:%M%p",
        "human": "%m/%d/%Y",
        "timestamp": "%s",
        "date": "%A %-I:%M%p %m/%d/%Y",
    }

    return to_datetime(source).strftime(templates[mode])


def resolve_timedelta(
    hours=0,
    seconds=0,
    minutes=0,
    days=0,
    weeks=0,
    months=0,
    years=0,
):
    now = datetime.now()
    cutoff = now - timedelta(
        hours=hours,
        seconds=seconds,
        minutes=minutes,
        days=days + weeks * 7 + months * 30 + years * 365,
    )
    return cutoff.timestamp()

def is_recentf(mode = "after", **opts):
    cutoff = resolve_timedelta(**opts)
    if mode == "after":
        return lambda x: x >= cutoff
    else:
        return lambda x: x < cutoff
