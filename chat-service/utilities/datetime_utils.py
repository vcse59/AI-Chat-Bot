"""
Date and time utility functions
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import pytz

def get_utc_now() -> datetime:
    """
    Get current UTC datetime
    
    Returns:
        Current UTC datetime
    """
    return datetime.utcnow()

def get_utc_timestamp() -> float:
    """
    Get current UTC timestamp
    
    Returns:
        Current UTC timestamp as float
    """
    return datetime.utcnow().timestamp()

def format_timestamp(dt: Optional[datetime] = None, format_string: str = "%Y-%m-%dT%H:%M:%S.%fZ") -> str:
    """
    Format datetime to ISO timestamp string
    
    Args:
        dt: Datetime object to format (defaults to current UTC time)
        format_string: Format string (default ISO format with microseconds)
        
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = get_utc_now()
    return dt.strftime(format_string)

def format_datetime(
    dt: datetime, 
    format_string: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Format datetime to string
    
    Args:
        dt: Datetime object to format
        format_string: Format string (default ISO-like format)
        
    Returns:
        Formatted datetime string
    """
    if dt is None:
        return ""
    return dt.strftime(format_string)

def parse_datetime(
    date_string: str, 
    format_string: str = "%Y-%m-%d %H:%M:%S"
) -> Optional[datetime]:
    """
    Parse datetime string to datetime object
    
    Args:
        date_string: String representation of datetime
        format_string: Expected format of the string
        
    Returns:
        Datetime object or None if parsing fails
    """
    try:
        return datetime.strptime(date_string, format_string)
    except (ValueError, TypeError):
        return None

def get_iso_string(dt: Optional[datetime] = None) -> str:
    """
    Get ISO format string of datetime
    
    Args:
        dt: Datetime object (uses current UTC if None)
        
    Returns:
        ISO format datetime string
    """
    if dt is None:
        dt = get_utc_now()
    return dt.isoformat()

def add_timezone(dt: datetime, timezone_name: str = "UTC") -> datetime:
    """
    Add timezone info to naive datetime
    
    Args:
        dt: Naive datetime object
        timezone_name: Name of timezone (e.g., 'UTC', 'US/Eastern')
        
    Returns:
        Datetime with timezone info
    """
    try:
        tz = pytz.timezone(timezone_name)
        if dt.tzinfo is None:
            return tz.localize(dt)
        else:
            return dt.astimezone(tz)
    except:
        # Fallback to UTC
        return dt.replace(tzinfo=timezone.utc)

def convert_timezone(
    dt: datetime, 
    target_timezone: str = "UTC"
) -> datetime:
    """
    Convert datetime to different timezone
    
    Args:
        dt: Datetime object with timezone info
        target_timezone: Target timezone name
        
    Returns:
        Datetime converted to target timezone
    """
    try:
        target_tz = pytz.timezone(target_timezone)
        return dt.astimezone(target_tz)
    except:
        # Fallback to UTC
        return dt.astimezone(timezone.utc)

def time_ago_string(dt: datetime) -> str:
    """
    Convert datetime to human-readable "time ago" string
    
    Args:
        dt: Datetime object to convert
        
    Returns:
        Human-readable time ago string
    """
    if dt is None:
        return "unknown"
    
    now = get_utc_now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"

def is_within_timeframe(
    dt: datetime, 
    timeframe_minutes: int
) -> bool:
    """
    Check if datetime is within specified timeframe from now
    
    Args:
        dt: Datetime to check
        timeframe_minutes: Timeframe in minutes
        
    Returns:
        True if within timeframe, False otherwise
    """
    if dt is None:
        return False
    
    now = get_utc_now()
    threshold = now - timedelta(minutes=timeframe_minutes)
    return dt >= threshold

def get_start_of_day(dt: Optional[datetime] = None) -> datetime:
    """
    Get start of day (00:00:00) for given datetime
    
    Args:
        dt: Datetime object (uses current if None)
        
    Returns:
        Datetime at start of day
    """
    if dt is None:
        dt = get_utc_now()
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def get_end_of_day(dt: Optional[datetime] = None) -> datetime:
    """
    Get end of day (23:59:59.999999) for given datetime
    
    Args:
        dt: Datetime object (uses current if None)
        
    Returns:
        Datetime at end of day
    """
    if dt is None:
        dt = get_utc_now()
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)

def calculate_duration_string(
    start_time: datetime, 
    end_time: Optional[datetime] = None
) -> str:
    """
    Calculate duration between two datetimes as human-readable string
    
    Args:
        start_time: Start datetime
        end_time: End datetime (uses current if None)
        
    Returns:
        Duration string (e.g., "2 hours 15 minutes")
    """
    if end_time is None:
        end_time = get_utc_now()
    
    if start_time > end_time:
        return "0 seconds"
    
    duration = end_time - start_time
    
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if not parts and seconds > 0:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    if not parts:
        return "0 seconds"
    
    return " ".join(parts)

def get_date_range(
    start_date: datetime,
    days: int
) -> tuple[datetime, datetime]:
    """
    Get date range from start date for specified number of days
    
    Args:
        start_date: Starting date
        days: Number of days to include
        
    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    start_dt = get_start_of_day(start_date)
    end_dt = get_end_of_day(start_date + timedelta(days=days-1))
    return start_dt, end_dt

def validate_datetime_range(
    start_time: datetime,
    end_time: datetime,
    max_duration_hours: Optional[int] = None
) -> bool:
    """
    Validate that datetime range is logical and within limits
    
    Args:
        start_time: Start datetime
        end_time: End datetime
        max_duration_hours: Maximum allowed duration in hours
        
    Returns:
        True if valid range, False otherwise
    """
    # Check that end time is after start time
    if end_time <= start_time:
        return False
    
    # Check maximum duration if specified
    if max_duration_hours is not None:
        duration = end_time - start_time
        max_duration = timedelta(hours=max_duration_hours)
        if duration > max_duration:
            return False
    
    return True