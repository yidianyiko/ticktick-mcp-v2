"""
TickTick Client Adapter
Client adapter based on ticktick.py library
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from auth import TickTickAuth
from utils.helpers import search_tasks as search_tasks_helper

logger = logging.getLogger(__name__)

class TickTickAdapter:
    """TickTick client adapter based on ticktick.py library"""
    
    def __init__(self):
        """Initialize TickTick adapter"""
        self.auth = TickTickAuth()
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize client"""
        try:
            if self.auth.is_authenticated():
                self.client = self.auth.get_client()
                logger.info("TickTick client initialized successfully")
            else:
                logger.warning("Not authenticated. Please login first.")
        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")
            raise
    
    def _ensure_client(self):
        """Ensure client is initialized"""
        if not self.client:
            self._initialize_client()
        return self.client
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        try:
            client = self._ensure_client()
            
            # Use ticktick.py library's project manager
            projects = client.state.get('projects', [])
            
            logger.info(f"Retrieved {len(projects)} projects")
            return projects
            
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            return []
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get specific project details"""
        try:
            client = self._ensure_client()
            
            # Use ticktick.py library to find project
            projects = client.state.get('projects', [])
            for project in projects:
                if project.get('id') == project_id:
                    return project
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
            return None
    
    def get_tasks(self, include_completed: bool = False) -> List[Dict[str, Any]]:
        """Get all tasks"""
        try:
            client = self._ensure_client()
            
            # Use ticktick.py library's task manager
            tasks = client.state.get('tasks', [])
            
            # Filter based on completion status
            if not include_completed:
                tasks = [task for task in tasks if task.get('status') != 2]  # 2 means completed
            
            logger.info(f"Retrieved {len(tasks)} tasks")
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return []
    
    def create_task(self, title: str, project_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Create new task"""
        try:
            client = self._ensure_client()
            
            # Use ticktick.py library's task manager to create task
            task_data = {
                "title": title,
                **kwargs
            }
            
            # Only add projectId if provided
            if project_id:
                task_data["projectId"] = project_id
            
            # Use ticktick.py library's task.builder and task.create
            local_task = client.task.builder(title)
            local_task.update(task_data)
            
            created_task = client.task.create(local_task)
            
            logger.info(f"Created task: {title}")
            return created_task
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise
    
    def update_task(self, task_id: str, project_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Update existing task"""
        try:
            client = self._ensure_client()
            
            # Use ticktick.py library to update task
            # First get task details
            task = client.get_by_id(task_id)
            if not task:
                raise Exception(f"Task {task_id} not found")
            
            # Update task data
            task.update(kwargs)
            
            # Use ticktick.py library to update task
            updated_task = client.task.update(task)
            
            logger.info(f"Updated task: {task_id}")
            return updated_task
            
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            raise
    
    def delete_task(self, project_id: str, task_id: str) -> bool:
        """Delete task"""
        try:
            client = self._ensure_client()
            
            # Use ticktick.py library to delete task
            result = client.task.delete(task_id)
            
            logger.info(f"Deleted task: {task_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            raise
    
    def complete_task(self, task_id: str) -> bool:
        """Mark task as completed"""
        try:
            client = self._ensure_client()
            
            # Use ticktick.py library to complete task
            result = client.task.complete(task_id)
            
            logger.info(f"Completed task: {task_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to complete task {task_id}: {e}")
            raise
    
    def search_tasks(self, query: str) -> List[Dict[str, Any]]:
        """Search tasks by query"""
        try:
            client = self._ensure_client()
            
            # Get all tasks first
            all_tasks = self.get_tasks(include_completed=True)
            
            # Use helper function to search tasks
            tasks = search_tasks_helper(all_tasks, query)
            
            logger.info(f"Found {len(tasks)} tasks matching query: {query}")
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to search tasks: {e}")
            return []
    
    def get_tasks_by_priority(self, priority: int) -> List[Dict[str, Any]]:
        """Get tasks by priority level"""
        try:
            client = self._ensure_client()
            
            # Get all tasks and filter by priority
            tasks = client.state.get('tasks', [])
            filtered_tasks = [task for task in tasks if task.get('priority') == priority]
            
            logger.info(f"Found {len(filtered_tasks)} tasks with priority {priority}")
            return filtered_tasks
            
        except Exception as e:
            logger.error(f"Failed to get tasks by priority: {e}")
            return []
    
    def get_tasks_due_today(self) -> List[Dict[str, Any]]:
        """Get tasks due today"""
        try:
            client = self._ensure_client()
            
            # Get all tasks and filter by due date
            tasks = client.state.get('tasks', [])
            today = datetime.now().date()
            
            due_today = []
            for task in tasks:
                # Only check 'dueDate' field (correct field name)
                due_date = task.get('dueDate')
                if due_date:
                    try:
                        # Handle different date formats
                        if due_date.endswith('Z'):
                            due_date = due_date.replace('Z', '+00:00')
                        task_date = datetime.fromisoformat(due_date).date()
                        if task_date == today:
                            due_today.append(task)
                    except Exception as parse_error:
                        logger.debug(f"Failed to parse date {due_date}: {parse_error}")
                        continue
            
            logger.info(f"Found {len(due_today)} tasks due today")
            return due_today
            
        except Exception as e:
            logger.error(f"Failed to get tasks due today: {e}")
            return []
    
    def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """Get overdue tasks"""
        try:
            client = self._ensure_client()
            
            # Get all tasks and filter by overdue status
            tasks = client.state.get('tasks', [])
            today = datetime.now().date()
            
            overdue = []
            for task in tasks:
                # Only check 'dueDate' field (correct field name)
                due_date = task.get('dueDate')
                if due_date:
                    try:
                        # Handle different date formats
                        if due_date.endswith('Z'):
                            due_date = due_date.replace('Z', '+00:00')
                        task_date = datetime.fromisoformat(due_date).date()
                        if task_date < today and task.get('status') != 2:  # Not completed
                            overdue.append(task)
                    except Exception as parse_error:
                        logger.debug(f"Failed to parse date {due_date}: {parse_error}")
                        continue
            
            logger.info(f"Found {len(overdue)} overdue tasks")
            return overdue
            
        except Exception as e:
            logger.error(f"Failed to get overdue tasks: {e}")
            return []

# Global client instance
_global_client = None

def get_client() -> TickTickAdapter:
    """Get TickTick client instance (singleton pattern)"""
    global _global_client
    if _global_client is None:
        _global_client = TickTickAdapter()
    return _global_client 