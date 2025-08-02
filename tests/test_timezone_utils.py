"""
Tests for timezone conversion utilities
"""

import pytest
from datetime import datetime
from src.utils.timezone_utils import (
    convert_utc_to_local_time,
    convert_task_times_to_local,
    convert_tasks_times_to_local
)


class TestTimezoneUtils:
    """Test timezone conversion utilities"""
    
    def test_convert_utc_to_local_time_shanghai(self):
        """Test UTC to Shanghai time conversion"""
        utc_time = "2025-08-01T16:00:00.000+0000"
        timezone = "Asia/Shanghai"
        
        result = convert_utc_to_local_time(utc_time, timezone)
        
        # Shanghai is UTC+8, so 16:00 UTC = 00:00 next day Shanghai
        expected = "2025-08-02T00:00:00"
        assert result == expected
    
    def test_convert_utc_to_local_time_los_angeles(self):
        """Test UTC to Los Angeles time conversion"""
        utc_time = "2025-08-01T16:00:00.000+0000"
        timezone = "America/Los_Angeles"
        
        result = convert_utc_to_local_time(utc_time, timezone)
        
        # Los Angeles is UTC-7 in summer (PDT), so 16:00 UTC = 09:00 same day LA
        expected = "2025-08-01T09:00:00"
        assert result == expected
    
    def test_convert_utc_to_local_time_no_timezone(self):
        """Test UTC conversion when no timezone provided"""
        utc_time = "2025-08-01T16:00:00.000+0000"
        timezone = ""
        
        result = convert_utc_to_local_time(utc_time, timezone)
        
        # Should return UTC time as is
        expected = "2025-08-01T16:00:00"
        assert result == expected
    
    def test_convert_utc_to_local_time_z_format(self):
        """Test UTC conversion with Z format"""
        utc_time = "2025-08-01T16:00:00.000Z"
        timezone = "Asia/Shanghai"
        
        result = convert_utc_to_local_time(utc_time, timezone)
        
        expected = "2025-08-02T00:00:00"
        assert result == expected
    
    def test_convert_task_times_to_local(self):
        """Test converting task times to local time"""
        task = {
            "id": "test123",
            "title": "Test Task",
            "timeZone": "Asia/Shanghai",
            "startDate": "2025-08-01T16:00:00.000+0000",
            "dueDate": "2025-08-01T16:00:00.000+0000",
            "modifiedTime": "2025-08-01T16:00:00.000+0000",
            "createdTime": "2025-08-01T16:00:00.000+0000"
        }
        
        result = convert_task_times_to_local(task)
        
        # All times should be converted to Shanghai time (UTC+8)
        assert result["startDate"] == "2025-08-02T00:00:00"
        assert result["dueDate"] == "2025-08-02T00:00:00"
        assert result["modifiedTime"] == "2025-08-02T00:00:00"
        assert result["createdTime"] == "2025-08-02T00:00:00"
        assert result["timeZone"] == "Asia/Shanghai"
    
    def test_convert_tasks_times_to_local(self):
        """Test converting multiple tasks times to local time"""
        tasks = [
            {
                "id": "test1",
                "title": "Task 1",
                "timeZone": "Asia/Shanghai",
                "dueDate": "2025-08-01T16:00:00.000+0000"
            },
            {
                "id": "test2",
                "title": "Task 2",
                "timeZone": "America/Los_Angeles",
                "dueDate": "2025-08-01T16:00:00.000+0000"
            }
        ]
        
        result = convert_tasks_times_to_local(tasks)
        
        # First task should be Shanghai time (UTC+8)
        assert result[0]["dueDate"] == "2025-08-02T00:00:00"
        # Second task should be Los Angeles time (UTC-7 in summer)
        assert result[1]["dueDate"] == "2025-08-01T09:00:00"
    
    def test_convert_task_times_to_local_no_timezone(self):
        """Test converting task times when no timezone info"""
        task = {
            "id": "test123",
            "title": "Test Task",
            "timeZone": "",
            "dueDate": "2025-08-01T16:00:00.000+0000"
        }
        
        result = convert_task_times_to_local(task)
        
        # Should return UTC time as is when no timezone
        assert result["dueDate"] == "2025-08-01T16:00:00"
    
    def test_convert_utc_to_local_time_invalid_timezone(self):
        """Test handling of invalid timezone"""
        utc_time = "2025-08-01T16:00:00.000+0000"
        timezone = "Invalid/Timezone"
        
        # Should return original time string on error (with normalized format)
        result = convert_utc_to_local_time(utc_time, timezone)
        expected = "2025-08-01T16:00:00.000+00:00"  # Normalized format
        assert result == expected
    
    def test_convert_utc_to_local_time_invalid_time_format(self):
        """Test handling of invalid time format"""
        utc_time = "invalid-time-format"
        timezone = "Asia/Shanghai"
        
        # Should return original time string on error
        result = convert_utc_to_local_time(utc_time, timezone)
        assert result == utc_time 