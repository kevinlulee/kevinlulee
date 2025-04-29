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
        "usa": "%m/%d/%Y %I:%M:%S %p",
    }

    return to_datetime(source).strftime(templates.get(mode, mode))


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

def is_recentf(mode = "after", key = None, **opts):
    cutoff = resolve_timedelta(**opts)
    if mode == "after" or mode == "recent":
        fn = lambda x: x >= cutoff
    else:
        fn = lambda x: x < cutoff

    if key:
        return lambda x: fn(x[key])
    else:
        return fn
def timeago(time, now=None):
    def seconds_to_ago_string(seconds):
        # Define time units in seconds
        minute = 60
        hour = 60 * minute
        day = 24 * hour
        week = 7 * day
        month = 30.44 * day  # Average month length
    
        # Calculate the time units
        months, remainder = divmod(seconds, month)
        weeks, remainder = divmod(remainder, week)
        days, remainder = divmod(remainder, day)
        hours, remainder = divmod(remainder, hour)
        minutes, seconds = divmod(remainder, minute)
    
        # Convert to integers
        units = [
            ("month", int(months)),
            ("week", int(weeks)),
            ("day", int(days)),
            ("hour", int(hours)),
            ("minute", int(minutes)),
            ("second", int(seconds)),
        ]
    
        # Filter out zero values and create the string
        parts = []
        for unit, value in units:
            if value > 0:
                parts.append(f"{value} {unit}{'s' if value > 1 else ''}")
    
        if len(parts) == 0:
            return "just now"
        elif len(parts) == 1:
            return f"{parts[0]} ago"
        else:
            return f"{', '.join(parts[:-1])} and {parts[-1]} ago"

    past = to_datetime(time)
    now = to_datetime(now) if now else datetime.now()
    td = now - past
    s = seconds_to_ago_string(td.seconds)

    if td.days:
        return f"{td.days} days, {s}"
    else:
        return s
