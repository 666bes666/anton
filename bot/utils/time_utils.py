"""Time-related utilities for the Discord bot."""
from datetime import datetime, time
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def parse_time_string(time_str: str) -> Optional[time]:
    """
    Parse a time string in HH:MM format.
    
    Args:
        time_str: Time string in HH:MM format (e.g., "07:00")
        
    Returns:
        time object if parsing is successful, None otherwise
    """
    try:
        return datetime.strptime(time_str, '%H:%M').time()
    except ValueError as e:
        logger.error(f"Failed to parse time string '{time_str}': {e}")
        return None

def is_time_to_send(scheduled_time: time, current_time: Optional[datetime] = None) -> bool:
    """
    Check if it's time to send a message based on the scheduled time.
    
    Args:
        scheduled_time: The scheduled time to send the message
        current_time: Current time (defaults to utcnow())
        
    Returns:
        True if it's time to send the message, False otherwise
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    return (scheduled_time.hour == current_time.hour and 
            scheduled_time.minute == current_time.minute)

def time_to_string(time_obj: time) -> str:
    """
    Convert a time object to a string in HH:MM format.
    
    Args:
        time_obj: time object to convert
        
    Returns:
        Time string in HH:MM format
    """
    return time_obj.strftime('%H:%M')
