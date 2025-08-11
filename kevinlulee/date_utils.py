from datetime import datetime, timedelta
import re
import calendar
from typing import Optional, TypedDict, Union, Literal
import os

from kevinlulee.string_utils import camel_case


class TimeOpts(TypedDict):
    hours: int = 0
    seconds: int = 0
    minutes: int = 0
    days: int = 0
    years: int = 0
    months: int = 0


from datetime import datetime, timezone
from typing import Optional, Iterable


def datetime_from_str(s: str) -> datetime:
    dt = None
    if dt is None:
        from dateutil import parser as _du

        dt = _du.parse(s)

    if dt is None:
        fmts = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%m/%d/%Y",
            "%m/%d/%Y %H:%M",
            "%m/%d/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%d/%m/%Y %H:%M",
            "%Y%m%dT%H%M%SZ",  # Zulu w/out offset
        ]

        for fmt in fmts:
            try:
                dt = datetime.strptime(s, fmt)
                break
            except Exception:
                pass

    if dt is None:
        raise ValueError(f"Could not parse datetime string: {s!r}")

    return dt



def rough_unit_from_digits(ts: int | str) -> Literal["s","ms","us","ns"]:
    """Quick heuristic by digit length: 10≈s, 13≈ms, 16≈µs, 19≈ns."""
    n = len(str(abs(int(ts))))
    if n >= 19: return "ns"
    if n >= 16: return "us"
    if n >= 13: return "ms"
    return "s"

def to_datetime(x=None):
    if x is None:
        return datetime.now()
    if isinstance(x, dict):
        return datetime_from_str(extract_datetime_str_from_dictionary(x))
    if isinstance(x, str):
        path = os.path.expanduser(x)
        if os.path.isfile(path):
            return datetime.fromtimestamp(os.path.getmtime(path))
        else:
            return datetime_from_str(x)
    if isinstance(x, (int, float)):
        if rough_unit_from_digits(x) == 'ms':
            x /= 1000
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


# 2025-05-01 aicmp: literal type for mode based on the templates
def strftime(source=None, mode="iso8601"):
    templates = {
        "iso8601": "%Y-%m-%d",
        "clock": "%-I:%M%p",
        "human": "%m/%d/%Y",
        "timestamp": "%s",
        "wordy": "%A %B %d, %Y",
        "date": "%A %-I:%M%p %m/%d/%Y",
        "usa": "%m/%d/%Y %I:%M:%S %p",
        "detailed": "%m/%d/%Y %I:%M:%S %p",
    }

    return to_datetime(source).strftime(templates.get(mode, mode))


def timestamp():
    return datetime.now().timestamp()


def resolve_timedelta(
    hours=0, seconds=0, minutes=0, days=0, weeks=0, months=0, years=0, **kwargs
):
    now = datetime.now()
    cutoff = now - timedelta(
        hours=hours,
        seconds=seconds,
        minutes=minutes,
        days=days + weeks * 7 + months * 30 + years * 365,
    )
    # print(now)
    # print(cutoff)
    return cutoff.timestamp()




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


class DateAccess:
    """A class that provides access to various date and time properties."""

    def __init__(self, date = None):
        self.init_date(date)

    def init_date(self, date):
        try:
            self._date = to_datetime(date)
        except Exception as e:
            self._date = None

    @property
    def date(self) -> datetime:
        return getattr(self, '_date', None) or datetime.datetime.now()

    @property
    def year(self) -> int:
        return self.date.year

    @property
    def month(self) -> int:
        """month as an integer (1-12)."""
        return self.date.month

    @property
    def day(self) -> int:
        """day of month as an integer."""
        return self.date.day

    @property
    def hour(self) -> int:
        """Get the hour as an integer (0-23)."""
        return self.date.hour

    @property
    def minute(self) -> int:
        return self.date.minute

    @property
    def second(self) -> int:
        return self.date.second

    @property
    def month_name(self) -> str:
        """Get the full month name (e.g., 'January')."""
        return calendar.month_name[self.date.month]

    @property
    def short_month_name(self) -> str:
        """Get the abbreviated month name (e.g., 'Jan')."""
        return calendar.month_abbr[self.date.month]

    @property
    def weekday(self) -> int:
        """Get the weekday as an integer (0=Monday, 6=Sunday)."""
        return self.date.weekday()

    @property
    def weekday_name(self) -> str:
        """Get the full weekday name (e.g., 'Monday')."""
        return calendar.day_name[self.date.weekday()]

    @property
    def short_weekday_name(self) -> str:
        """Get the abbreviated weekday name (e.g., 'Mon')."""
        return calendar.day_abbr[self.date.weekday()]

    @property
    def day_of_year(self) -> int:
        """Get the day of the year (1-366)."""
        return self.date.timetuple().tm_yday

    @property
    def week_of_year(self) -> int:
        """Get the ISO week number of the year (1-53)."""
        return self.date.isocalendar()[1]

    @property
    def quarter(self) -> int:
        """Get the quarter of the year (1-4)."""
        return (self.date.month - 1) // 3 + 1

    def is_leap_year(self) -> bool:
        """Check if the current year is a leap year."""
        return calendar.isleap(self.date.year)

    @property
    def get_days_in_month(self) -> int:
        """Get the number of days in the current month."""
        return calendar.monthrange(self.date.year, self.date.month)[1]

    @property
    def timestamp(self) -> float:
        """Get the UNIX timestamp."""
        return self.date.timestamp()

    @property
    def american_date(self) -> str:
        """Get the date in American format (MM/DD/YYYY)."""
        return f"{self.date.month:02d}/{self.date.day:02d}/{self.date.year}"


def get_recency_validator(mode: Literal["recent", "distant"], **opts):
    cutoff = resolve_timedelta(**opts)
    if mode == "recent":
        return lambda x: x >= cutoff
    else:
        return lambda x: x < cutoff


from datetime import datetime

# Mapping full day names and abbreviations to integers (Mon=0, ..., Sun=6)
DAY_MAPPING = {
    "Mon": 0,
    "Monday": 0,
    "Tue": 1,
    "Tuesday": 1,
    "Wed": 2,
    "Wednesday": 2,
    "Thu": 3,
    "Thursday": 3,
    "Fri": 4,
    "Friday": 4,
    "Sat": 5,
    "Saturday": 5,
    "Sun": 6,
    "Sunday": 6,
}


def parse_time(x):
    """Parse time string, inferring 'PM' if not provided."""
    # Check if "AM" or "PM" is explicitly mentioned
    if "AM" in x.upper() or "PM" in x.upper():
        try:
            return datetime.strptime(x, "%I:%M%p")
        except Exception as e:
            return datetime.strptime(x, "%I%p")

    # No "AM" or "PM" provided, assume PM
    try:
        # Try parsing full "HH:MM" format first
        return datetime.strptime(x, "%I:%M")
    except ValueError:
        # If only "HH" is given (e.g., '5' meaning '5PM')
        return datetime.strptime(x, "%I")


def parse_day_and_time(day_time_obj):
    if isinstance(day_time_obj, str):
        return None, parse_time(day_time_obj)
    """Parse day and time from the given object, handle flexible time formats."""
    # Handle both full and abbreviated day names
    day = DAY_MAPPING[day_time_obj["day"].capitalize()]
    time_str = day_time_obj["time"]
    time_obj = parse_time(time_str)  # Parse the flexible time string
    return day, time_obj


def to_timestamp(x):
    if isinstance(x, (int, float)):
        return x
    return to_datetime(x).timestamp()


def is_recent(x, **opts):
    cutoff = resolve_timedelta(**opts)
    return to_timestamp(x) >= cutoff

def is_recentf(mode="after", key=None, **opts):
    cutoff = resolve_timedelta(**opts)
    recency_modes = ['after', 'recent', 'near']
    fn = lambda x: to_timestamp(x) >= cutoff if mode in recency_modes else lambda x: to_timestamp(x) < cutoff

    return lambda x: fn(x[key]) if key else fn

def is_time_between(start: str | dict, end: str | dict):
    start_day, start_time = parse_day_and_time(start)
    end_day, end_time = parse_day_and_time(end)

    now = datetime.now()
    current_day = now.weekday()  # Monday = 0, Sunday = 6
    current_time = now.time()
    if start_day == None:
        start_day = current_day
    if end_day == None:
        end_day = current_day

    return (
        current_day >= start_day
        and current_day <= end_day
        and current_time > start_time.time()
        and current_time < end_time.time()
    )


from datetime import datetime, timedelta


def get_upcoming_day(target_day):
    """
    Get the date of the upcoming occurrence of a specific day of the week.

    Args:
        target_day (str): Day of the week ('Monday', 'Tuesday', etc.)
                         Case insensitive, can be full name or 3-letter abbreviation

    Returns:
        datetime: Date object for the upcoming occurrence of the target day
    """
    # Day name mappings
    days_full = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    days_abbr = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    target_day = target_day.lower().strip()

    # Find the target day index
    if target_day in days_full:
        target_index = days_full.index(target_day)
    elif target_day in days_abbr:
        target_index = days_abbr.index(target_day)
    else:
        raise ValueError(
            f"Invalid day: {target_day}. Use full name or 3-letter abbreviation."
        )

    # Get current date and day of week (0=Monday, 6=Sunday)
    today = datetime.now()
    current_day_index = today.weekday()

    # Calculate days until target day
    days_ahead = (target_index - current_day_index) % 7

    # If it's the same day, get next week's occurrence
    if days_ahead == 0:
        days_ahead = 7

    # Return the upcoming date
    upcoming_date = today + timedelta(days=days_ahead)
    return upcoming_date.replace(hour=0, minute=0, second=0, microsecond=0)


# Example usage and testing

if __name__ == "__main__":
    start = {"day": "friday", "time": "1pm"}
    end = {"day": "sunday", "time": "11pm"}
    start = "1:40pm"
    end = "11pm"
    # print(get_upcoming_day('sun'))

    # print(is_time_between(start, end))  # True


def asdf(x, **opts):
    cutoff = resolve_timedelta(**opts)
    a = to_datetime(x)
    print("datetime", a)
    print("datetime.timestamp", a.timestamp())  # the time the file was modified
    print("the file", strftime(a, mode="detailed"))
    print("the cutoff", strftime(cutoff, mode="detailed"))
    print("cutoff > file", cutoff > a.timestamp())
    # the file's touch time surpasses the cutoff date. that means it is a recent file.
    # when the cutoff is greater than the file, it means it is no longer recent.
    # the cutoff creates a buffer between the time it is right now and 50 minutes ago. so its value will be something like 566 seconds ago.


# asdf('~/scratch/hanzi.json', minutes = 30)
# print(to_datetime('5/6/2000 5:00am asdf asdf'))


# 2025-08-11 Whereami


def extract_datetime_str_from_dictionary(x: dict) -> Optional[str]:
    date_field_names = [
        "date",
        "datetime",
        "timestamp",
        "created_at",
        "updated_at",
        "creation_date",
        "modification_date",
        "time",
        "time_usec",
        "time_ms",
        "start_date",
        "end_date",
        "published_at",
        "created_on",
        "modified_on",
        "date_created",
        "date_modified",
        "birth_date",
        "expiry_date",
    ]

    # Check for exact matches
    for field in date_field_names:
        if field in x:
            return x[field]

    camels = [camel_case(field) for field in date_field_names]
    for field in camels:
        if field in x:
            return x[field]

    # Look for any key that contains 'date' or 'time'
    for key in x:
        m = re.search("date|time", key, flags=re.I)
        if m:
            return x[m]


def now():
    return datetime.now()
