from datetime import datetime, timedelta
import calendar
from typing import Optional, TypedDict, Union, Literal
import os


class TimeOpts(TypedDict):
    hours: int = 0
    seconds: int = 0
    minutes: int = 0
    days: int = 0
    years: int = 0
    months: int = 0

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


# 2025-05-01 aicmp: literal type for mode based on the templates
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
    **kwargs
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

def is_recentf(mode = "after", key = None, **opts):
    cutoff = resolve_timedelta(**opts)
    if mode == "after" or mode == "recent" or mode == 'near':
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

class DateAccess:
    """A class that provides access to various date and time properties."""
    
    def __init__(self, date = None):
        """
        Initialize with either a specific date or the current date.
        
        Args:
            date: Optional datetime or date object. Defaults to current date/time.
        """
        if date is None:
            self._date = datetime.datetime.now()
        elif isinstance(date, datetime.date) and not isinstance(date, datetime.datetime):
            # Convert date to datetime at midnight
            self._date = datetime.datetime.combine(date, datetime.time())
        else:
            self._date = date
    
    @property
    def year(self) -> int:
        """Get the year as an integer."""
        return self._date.year
    
    @property
    def month(self) -> int:
        """Get the month as an integer (1-12)."""
        return self._date.month
    
    @property
    def day(self) -> int:
        """Get the day of month as an integer."""
        return self._date.day
    
    @property
    def hour(self) -> int:
        """Get the hour as an integer (0-23)."""
        return self._date.hour
    
    @property
    def minute(self) -> int:
        """Get the minute as an integer (0-59)."""
        return self._date.minute
    
    @property
    def second(self) -> int:
        """Get the second as an integer (0-59)."""
        return self._date.second
    
    @property
    def month(self) -> str:
        """Get the full month name (e.g., 'January')."""
        return calendar.month_name[self._date.month]
    
    @property
    def month_name_short(self) -> str:
        """Get the abbreviated month name (e.g., 'Jan')."""
        return calendar.month_abbr[self._date.month]
    
    @property
    def weekday(self) -> int:
        """Get the weekday as an integer (0=Monday, 6=Sunday)."""
        return self._date.weekday()
    
    @property
    def weekday_name(self) -> str:
        """Get the full weekday name (e.g., 'Monday')."""
        return calendar.day_name[self._date.weekday()]
    
    @property
    def weekday_name_short(self) -> str:
        """Get the abbreviated weekday name (e.g., 'Mon')."""
        return calendar.day_abbr[self._date.weekday()]
    
    @property
    def day_of_year(self) -> int:
        """Get the day of the year (1-366)."""
        return self._date.timetuple().tm_yday
    
    @property
    def week_of_year(self) -> int:
        """Get the ISO week number of the year (1-53)."""
        return self._date.isocalendar()[1]
    
    @property
    def quarter(self) -> int:
        """Get the quarter of the year (1-4)."""
        return (self._date.month - 1) // 3 + 1
    
    @property
    def is_leap_year(self) -> bool:
        """Check if the current year is a leap year."""
        return calendar.isleap(self._date.year)
    
    @property
    def days_in_month(self) -> int:
        """Get the number of days in the current month."""
        return calendar.monthrange(self._date.year, self._date.month)[1]
    
    @property
    def timestamp(self) -> float:
        """Get the UNIX timestamp."""
        return self._date.timestamp()
    
    @property
    def iso_format(self) -> str:
        """Get the date in ISO format (YYYY-MM-DD)."""
        return self._date.date().isoformat()
    
    @property
    def iso_datetime(self) -> str:
        """Get the date and time in ISO format."""
        return self._date.isoformat()
    
    @property
    def american_date(self) -> str:
        """Get the date in American format (MM/DD/YYYY)."""
        return f"{self._date.month:02d}/{self._date.day:02d}/{self._date.year}"
    
    @property
    def european_date(self) -> str:
        """Get the date in European format (DD/MM/YYYY)."""
        return f"{self._date.day:02d}/{self._date.month:02d}/{self._date.year}"
    
    @property
    def ordinal_day(self) -> str:
        """Get the day with ordinal suffix (1st, 2nd, 3rd, etc.)."""
        day = self._date.day
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return f"{day}{suffix}"



def get_recency_validator(mode: Literal['recent', 'distant'], **opts):
    cutoff = resolve_timedelta(**opts)
    if mode == 'recent':
        return lambda x: x >= cutoff
    else:
        return lambda x: x < cutoff


if __name__ == '__main__':
    # import vim
    # a = vim.funcs.getbufinfo(54)
    # print(a[0]['lastused'], 'X')
    print(get_recency_validator('recent',minutes = 1)( a[0]['lastused'] ))



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


def is_time_between(start: str | dict, end: str | dict):
    start_day, start_time = parse_day_and_time(start)
    end_day, end_time = parse_day_and_time(end)

    now = datetime.now()
    current_day = now.weekday()  # Monday = 0, Sunday = 6
    current_time = now.time()
    if start_day == None: start_day = current_day
    if end_day == None: end_day = current_day

    return (
        current_day >= start_day
        and current_day <= end_day
        and current_time > start_time.time()
        and current_time < end_time.time()
    )


if __name__ == "__main__":
    start = {"day": "friday", "time": "1pm"}
    end = {"day": "sunday", "time": "11pm"}
    start = "1:40pm"
    end = "11pm"

    # print(is_time_between(start, end))  # True
