"""Tests for time utility functions."""
import pytest
from datetime import datetime, time

from bot.utils.time_utils import parse_time_string, is_time_to_send, time_to_string

class TestParseTimeString:
    """Test time string parsing functionality."""

    def test_valid_time_formats(self):
        """Test parsing of valid time formats."""
        valid_times = [
            ("07:00", time(7, 0)),
            ("23:59", time(23, 59)),
            ("00:00", time(0, 0)),
            ("12:30", time(12, 30)),
        ]
        
        for time_str, expected in valid_times:
            result = parse_time_string(time_str)
            assert result == expected

    def test_invalid_time_formats(self):
        """Test that invalid time formats return None."""
        invalid_times = ["25:00", "12:60", "7:00", "12:3", "invalid", "", "24:00"]
        
        for time_str in invalid_times:
            result = parse_time_string(time_str)
            assert result is None

class TestIsTimeToSend:
    """Test time comparison functionality."""

    def test_exact_time_match(self):
        """Test exact time matching."""
        scheduled_time = time(7, 30)
        current_time = datetime(2023, 1, 1, 7, 30, 0)
        
        assert is_time_to_send(scheduled_time, current_time) is True

    def test_time_mismatch(self):
        """Test time mismatch scenarios."""
        scheduled_time = time(7, 30)
        
        # Different hour
        current_time = datetime(2023, 1, 1, 8, 30, 0)
        assert is_time_to_send(scheduled_time, current_time) is False
        
        # Different minute
        current_time = datetime(2023, 1, 1, 7, 31, 0)
        assert is_time_to_send(scheduled_time, current_time) is False

    def test_default_current_time(self):
        """Test using default current time (utcnow)."""
        scheduled_time = time(7, 30)
        # This test mainly ensures the function doesn't crash when current_time is None
        result = is_time_to_send(scheduled_time)
        assert isinstance(result, bool)

class TestTimeToString:
    """Test time to string conversion."""

    def test_time_to_string_conversion(self):
        """Test converting time objects to strings."""
        test_cases = [
            (time(0, 0), "00:00"),
            (time(7, 30), "07:30"),
            (time(23, 59), "23:59"),
            (time(12, 0), "12:00"),
        ]
        
        for time_obj, expected in test_cases:
            result = time_to_string(time_obj)
            assert result == expected
