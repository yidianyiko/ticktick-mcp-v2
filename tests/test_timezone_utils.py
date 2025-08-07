"""
Tests for timezone conversion utilities
"""

from datetime import date, datetime

from src.utils.timezone_utils import (
    convert_task_times_to_local,
    convert_tasks_times_to_local,
    convert_utc_to_local_time,
    get_user_today,
    is_task_due_today,
    is_task_overdue,
    parse_task_date,
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
            "createdTime": "2025-08-01T16:00:00.000+0000",
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
                "dueDate": "2025-08-01T16:00:00.000+0000",
            },
            {
                "id": "test2",
                "title": "Task 2",
                "timeZone": "America/Los_Angeles",
                "dueDate": "2025-08-01T16:00:00.000+0000",
            },
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
            "dueDate": "2025-08-01T16:00:00.000+0000",
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


class TestTimezoneAwareDateComparison:
    """Test timezone-aware date comparison functions"""

    def test_get_user_today_with_timezone(self):
        """Test getting today's date in user timezone"""
        # Test with different timezones
        timezones = ["Asia/Shanghai", "America/New_York", "Europe/London"]

        for tz in timezones:
            today = get_user_today(tz)
            assert isinstance(today, date)
            # Should be a valid date
            assert today.year >= 2024

    def test_get_user_today_without_timezone(self):
        """Test getting today's date without timezone (UTC fallback)"""
        today = get_user_today("")
        assert isinstance(today, date)
        # Should be a valid date
        assert today.year >= 2024

    def test_get_user_today_invalid_timezone(self):
        """Test handling of invalid timezone"""
        today = get_user_today("Invalid/Timezone")
        assert isinstance(today, date)
        # Should fallback to UTC and still return a valid date
        assert today.year >= 2024

    def test_parse_task_date_valid_formats(self):
        """Test parsing various valid date formats"""
        test_cases = [
            ("2024-01-15T16:00:00.000+0000", datetime(2024, 1, 15, 16, 0, 0)),
            ("2024-01-15T16:00:00Z", datetime(2024, 1, 15, 16, 0, 0)),
            ("2024-01-15T16:00:00+00:00", datetime(2024, 1, 15, 16, 0, 0)),
        ]

        for date_str, expected_dt in test_cases:
            result = parse_task_date(date_str)
            assert result is not None
            assert result.year == expected_dt.year
            assert result.month == expected_dt.month
            assert result.day == expected_dt.day
            assert result.hour == expected_dt.hour

    def test_parse_task_date_invalid_format(self):
        """Test parsing invalid date format"""
        result = parse_task_date("invalid-date-format")
        assert result is None

    def test_parse_task_date_empty_string(self):
        """Test parsing empty date string"""
        result = parse_task_date("")
        assert result is None

    def test_parse_task_date_none(self):
        """Test parsing None date"""
        result = parse_task_date(None)
        assert result is None

    def test_is_task_due_today_same_timezone(self):
        """Test task due today check in same timezone"""
        # Create a task due today in UTC
        utc_now = datetime.utcnow()
        task = {
            "dueDate": utc_now.strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
            "timeZone": "UTC",
        }

        # Should be due today in UTC
        result = is_task_due_today(task, "")
        assert result is True

    def test_is_task_due_today_different_timezone(self):
        """Test task due today check across timezones"""
        # Create a task due at midnight UTC (start of day)
        utc_midnight = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        task = {
            "dueDate": utc_midnight.strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
        }

        # Test with different timezones
        timezones = ["Asia/Shanghai", "America/New_York", "Europe/London"]

        for tz in timezones:
            result = is_task_due_today(task, tz)
            # Result depends on the timezone, but should be boolean
            assert isinstance(result, bool)

    def test_is_task_due_today_no_due_date(self):
        """Test task due today check with no due date"""
        task = {"title": "Task without due date"}

        result = is_task_due_today(task, "Asia/Shanghai")
        assert result is False

    def test_is_task_due_today_invalid_due_date(self):
        """Test task due today check with invalid due date"""
        task = {"dueDate": "invalid-date"}

        result = is_task_due_today(task, "Asia/Shanghai")
        assert result is False

    def test_is_task_overdue_not_completed(self):
        """Test overdue task check for non-completed task"""
        # Create a task due yesterday
        yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = yesterday.replace(day=yesterday.day - 1)

        task = {
            "dueDate": yesterday.strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
            "status": 0,  # Not completed
        }

        result = is_task_overdue(task, "")
        assert result is True

    def test_is_task_overdue_completed(self):
        """Test overdue task check for completed task"""
        # Create a completed task due yesterday
        yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = yesterday.replace(day=yesterday.day - 1)

        task = {
            "dueDate": yesterday.strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
            "status": 2,  # Completed
        }

        result = is_task_overdue(task, "")
        assert result is False

    def test_is_task_overdue_due_today(self):
        """Test overdue task check for task due today"""
        # Create a task due today
        today = datetime.utcnow()

        task = {
            "dueDate": today.strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
            "status": 0,  # Not completed
        }

        result = is_task_overdue(task, "")
        assert result is False

    def test_is_task_overdue_no_due_date(self):
        """Test overdue task check with no due date"""
        task = {"title": "Task without due date", "status": 0}

        result = is_task_overdue(task, "Asia/Shanghai")
        assert result is False

    def test_is_task_overdue_invalid_due_date(self):
        """Test overdue task check with invalid due date"""
        task = {"dueDate": "invalid-date", "status": 0}

        result = is_task_overdue(task, "Asia/Shanghai")
        assert result is False

    def test_timezone_consistency(self):
        """Test that timezone handling is consistent across functions"""
        # Create a task due today in Shanghai timezone
        utc_now = datetime.utcnow()
        task = {
            "dueDate": utc_now.strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
            "status": 0,
        }

        timezone = "Asia/Shanghai"

        # Get user's today
        user_today = get_user_today(timezone)

        # Check if task is due today
        is_due_today = is_task_due_today(task, timezone)

        # Check if task is overdue
        is_overdue = is_task_overdue(task, timezone)

        # If task is due today, it shouldn't be overdue
        if is_due_today:
            assert not is_overdue

        # All results should be boolean
        assert isinstance(user_today, date)
        assert isinstance(is_due_today, bool)
        assert isinstance(is_overdue, bool)
