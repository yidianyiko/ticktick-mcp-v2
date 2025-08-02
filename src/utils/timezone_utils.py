"""
Timezone conversion utilities for TickTick MCP tools
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional
import pytz

logger = logging.getLogger(__name__)

def convert_utc_to_local_time(utc_time_str: str, timezone_str: str) -> str:
    """
    Convert UTC time string to local time string based on timezone
    
    Args:
        utc_time_str: UTC time string in format like "2025-08-01T16:00:00.000+0000"
        timezone_str: Timezone string like "Asia/Shanghai"
    
    Returns:
        Local time string in format like "2025-08-02T00:00:00"
    """
    try:
        # Parse UTC time string
        if utc_time_str.endswith('Z'):
            utc_time_str = utc_time_str.replace('Z', '+00:00')
        elif utc_time_str.endswith('+0000'):
            utc_time_str = utc_time_str.replace('+0000', '+00:00')
        
        # Parse the datetime
        utc_dt = datetime.fromisoformat(utc_time_str)
        
        # Get timezone
        if timezone_str and timezone_str.strip():
            tz = pytz.timezone(timezone_str)
            # Convert to local time
            local_dt = utc_dt.astimezone(tz)
            # Format as local time string (without timezone info for user-friendly display)
            return local_dt.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            # If no timezone info, return UTC time as is
            return utc_dt.strftime('%Y-%m-%dT%H:%M:%S')
            
    except Exception as e:
        logger.error(f"Failed to convert time {utc_time_str} with timezone {timezone_str}: {e}")
        return utc_time_str

def convert_task_times_to_local(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert all time fields in a task from UTC to local time
    
    Args:
        task: Task dictionary containing time fields and timezone info
    
    Returns:
        Task dictionary with converted local times
    """
    try:
        # Get timezone from task
        timezone_str = task.get('timeZone', '')
        
        # Convert startDate if present
        if 'startDate' in task and task['startDate']:
            task['startDate'] = convert_utc_to_local_time(task['startDate'], timezone_str)
        
        # Convert dueDate if present
        if 'dueDate' in task and task['dueDate']:
            task['dueDate'] = convert_utc_to_local_time(task['dueDate'], timezone_str)
        
        # Convert modifiedTime if present
        if 'modifiedTime' in task and task['modifiedTime']:
            task['modifiedTime'] = convert_utc_to_local_time(task['modifiedTime'], timezone_str)
        
        # Convert createdTime if present
        if 'createdTime' in task and task['createdTime']:
            task['createdTime'] = convert_utc_to_local_time(task['createdTime'], timezone_str)
        
        return task
        
    except Exception as e:
        logger.error(f"Failed to convert task times: {e}")
        return task

def convert_tasks_times_to_local(tasks: list) -> list:
    """
    Convert all time fields in a list of tasks from UTC to local time
    
    Args:
        tasks: List of task dictionaries
    
    Returns:
        List of task dictionaries with converted local times
    """
    try:
        converted_tasks = []
        for task in tasks:
            converted_task = convert_task_times_to_local(task)
            converted_tasks.append(converted_task)
        return converted_tasks
    except Exception as e:
        logger.error(f"Failed to convert tasks times: {e}")
        return tasks 