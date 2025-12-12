from __future__ import annotations
import kevinlulee as kx


from datetime import datetime, timedelta, time
from dateutil import parser
from dateutil.relativedelta import relativedelta
import re
from typing import Tuple, Optional
import calendar

def parse_date_range(date_range: str, reference_date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """
    Parse natural language date ranges into a tuple of datetime objects.
    
    Args:
        date_range: Natural language date range string
        reference_date: Optional reference date for relative calculations (defaults to now)
    
    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    # Normalize the input
    date_range = date_range.lower().strip()
    
    # Helper function to get the most recent occurrence of a weekday
    def get_last_weekday(weekday_num, ref_date=reference_date):
        """Get the most recent occurrence of a weekday (0=Monday, 6=Sunday)"""
        days_back = (ref_date.weekday() - weekday_num) % 7
        if days_back == 0:
            days_back = 7  # If it's the same weekday, go back a full week
        return ref_date - timedelta(days=days_back)
    
    # Helper function to get the next occurrence of a weekday
    def get_next_weekday(weekday_num, ref_date=reference_date):
        """Get the next occurrence of a weekday (0=Monday, 6=Sunday)"""
        days_ahead = (weekday_num - ref_date.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7  # If it's the same weekday, go ahead a full week
        return ref_date + timedelta(days=days_ahead)
    
    # Helper function to interpret "last" or "next" weekday intelligently
    def get_smart_weekday(weekday_str, modifier, ref_date=reference_date):
        """Get a weekday based on 'last', 'next', or no modifier"""
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        weekday_num = weekdays.get(weekday_str.lower())
        if weekday_num is None:
            return None
        
        if modifier == 'last':
            return get_last_weekday(weekday_num, ref_date)
        elif modifier == 'next':
            return get_next_weekday(weekday_num, ref_date)
        else:
            # No modifier - use smart logic based on context
            # If today is Friday and we say "Thursday", we likely mean yesterday
            # If today is Wednesday and we say "Thursday", we likely mean tomorrow
            days_diff = weekday_num - ref_date.weekday()
            if days_diff == -1:  # Yesterday
                return ref_date - timedelta(days=1)
            elif days_diff == 1:  # Tomorrow
                return ref_date + timedelta(days=1)
            elif days_diff < -1:  # Earlier this week
                return ref_date + timedelta(days=days_diff)
            elif days_diff > 1:  # Later this week
                return ref_date + timedelta(days=days_diff)
            else:  # Same day or ambiguous - use nearest occurrence
                if days_diff == 0:
                    return ref_date
                # For larger gaps, choose based on which is closer
                last_occurrence = get_last_weekday(weekday_num, ref_date)
                next_occurrence = get_next_weekday(weekday_num, ref_date)
                if abs((last_occurrence - ref_date).days) <= abs((next_occurrence - ref_date).days):
                    return last_occurrence
                else:
                    return next_occurrence
    
    # Helper to parse time modifiers
    def apply_time_modifier(dt, modifier):
        """Apply time modifiers like 'morning', 'noon', '5PM' etc."""
        if 'morning' in modifier:
            return dt.replace(hour=9, minute=0, second=0, microsecond=0)
        elif 'noon' in modifier:
            return dt.replace(hour=12, minute=0, second=0, microsecond=0)
        elif 'afternoon' in modifier:
            return dt.replace(hour=14, minute=0, second=0, microsecond=0)
        elif 'evening' in modifier:
            return dt.replace(hour=18, minute=0, second=0, microsecond=0)
        elif 'night' in modifier:
            return dt.replace(hour=21, minute=0, second=0, microsecond=0)
        else:
            # Try to parse specific times like "5PM", "3:30PM"
            time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)?', modifier, re.IGNORECASE)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                ampm = time_match.group(3)
                if ampm and ampm.lower() == 'pm' and hour < 12:
                    hour += 12
                elif ampm and ampm.lower() == 'am' and hour == 12:
                    hour = 0
                return dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return dt
    
    # Pattern: "from X to Y"
    from_to_pattern = r'from\s+(.+?)\s+to\s+(.+)'
    from_to_match = re.match(from_to_pattern, date_range)
    
    if from_to_match:
        start_str = from_to_match.group(1)
        end_str = from_to_match.group(2)
        
        # Parse start date
        if 'yesterday' in start_str:
            start_date = reference_date - timedelta(days=1)
            if 'morning' in start_str:
                start_date = apply_time_modifier(start_date, 'morning')
            else:
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'today' in start_str:
            start_date = reference_date
            if 'morning' in start_str:
                start_date = apply_time_modifier(start_date, 'morning')
            else:
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'last month' in start_str:
            start_date = reference_date - relativedelta(months=1)
            start_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif 'last week' in start_str:
            start_date = reference_date - timedelta(weeks=1)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'days ago' in start_str:
            days_match = re.search(r'(\d+|a few)\s+days?\s+ago', start_str)
            if days_match:
                if days_match.group(1) == 'a few':
                    days = 3  # Interpret "a few" as 3
                else:
                    days = int(days_match.group(1))
                start_date = reference_date - timedelta(days=days)
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'last' in start_str:
            weekday_match = re.search(r'last\s+(\w+day)', start_str)
            if weekday_match:
                start_date = get_smart_weekday(weekday_match.group(1), 'last')
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'next' in start_str:
            weekday_match = re.search(r'next\s+(\w+day)', start_str)
            if weekday_match:
                start_date = get_smart_weekday(weekday_match.group(1), 'next')
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # Check for bare weekday names
            weekday_match = re.search(r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', start_str)
            if weekday_match:
                start_date = get_smart_weekday(weekday_match.group(1), None)
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                start_date = reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Parse end date
        if 'this morning' in end_str:
            end_date = reference_date
            end_date = apply_time_modifier(end_date, 'morning')
        elif 'this afternoon' in end_str:
            end_date = reference_date
            end_date = apply_time_modifier(end_date, 'afternoon')
        elif 'today' in end_str:
            end_date = reference_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif 'tomorrow' in end_str:
            end_date = reference_date + timedelta(days=1)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif 'last week' in end_str:
            end_date = reference_date - timedelta(weeks=1)
            # End of that week (Sunday)
            days_to_sunday = 6 - end_date.weekday()
            end_date = end_date + timedelta(days=days_to_sunday)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif 'next' in end_str:
            weekday_match = re.search(r'next\s+(\w+day)', end_str)
            if weekday_match:
                end_date = get_smart_weekday(weekday_match.group(1), 'next')
                # Check for time modifier
                end_date = apply_time_modifier(end_date, end_str)
                if 'noon' not in end_str and not re.search(r'\d{1,2}(:\d{2})?\s*(am|pm)', end_str):
                    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            # Check for bare weekday names with possible time modifiers
            weekday_match = re.search(r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', end_str)
            if weekday_match:
                end_date = get_smart_weekday(weekday_match.group(1), None)
                # Apply time modifier if present
                end_date = apply_time_modifier(end_date, end_str)
                # If no specific time was given, use end of day
                if 'noon' not in end_str and not re.search(r'\d{1,2}(:\d{2})?\s*(am|pm)', end_str):
                    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            else:
                end_date = reference_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Pattern: "from X" (implies "to now")
    elif date_range.startswith('from '):
        start_str = date_range[5:]  # Remove "from "
        
        if 'yesterday' in start_str:
            start_date = reference_date - timedelta(days=1)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'last month' in start_str:
            start_date = reference_date - relativedelta(months=1)
            start_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif 'days ago' in start_str:
            days_match = re.search(r'(\d+)\s+days?\s+ago', start_str)
            if days_match:
                days = int(days_match.group(1))
                start_date = reference_date - timedelta(days=days)
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'last' in start_str:
            weekday_match = re.search(r'last\s+(\w+day)', start_str)
            if weekday_match:
                start_date = get_smart_weekday(weekday_match.group(1), 'last')
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        end_date = reference_date  # Current time
    
    else:
        # Default: treat as single day or current day
        start_date = reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = reference_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return (start_date, end_date)


# Test function with examples
def test_date_parser():
    # Set a reference date for consistent testing
    ref_date = datetime(2025, 12, 13, 14, 30)  # Friday, Dec 13, 2024, 2:30 PM
    
    test_cases = [
        'from yesterday to this morning',
        'from yesterday morning to this afternoon',
        'from last month to last week',
        'from last month',
        'from 3 days ago',
        'from last thursday to next thursday',
        'from thursday to sunday noon',
        'from thursday to sunday 5PM',
        'from thursday morning to sunday',
        'from a few days ago to tomorrow',
    ]
    
    print(f"Reference date: {ref_date.strftime('%A, %B %d, %Y %I:%M %p')}\n")
    print("-" * 80)
    
    for test in test_cases:
        start, end = parse_date_range(test, ref_date)
        print(f"Input: '{test}'")
        print(f"Start: {start.strftime('%A, %B %d, %Y %I:%M %p')}")
        print(f"End:   {end.strftime('%A, %B %d, %Y %I:%M %p')}")
        print("-" * 80)


if __name__ == "__main__":
    # Run tests
    test_date_parser()


INSTRUCTIONS = """

        'from thursday morning to sunday' is not properly handling morning
        morning should be around 9AM

        'from thursday 8AM to sunday' is not properly handling 8AM

        when the pattern is from x to y, the 'from' can be omitted.
"""

