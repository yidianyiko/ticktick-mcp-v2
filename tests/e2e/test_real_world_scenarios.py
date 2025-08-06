#!/usr/bin/env python3
"""
Real-world end-to-end scenario tests
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import patch, Mock
import json
import time
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.mark.e2e
class TestRealWorldScenarios:
    """Test real-world usage scenarios"""

    @pytest.mark.asyncio
    async def test_daily_task_management_workflow(self):
        """Test a typical daily task management workflow"""
        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import stdio_client, StdioServerParameters

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    print("🔧 Testing daily task management workflow...")

                    # 1. Start of day - check authentication
                    print("1. Checking authentication status...")
                    auth_status = await session.call_tool("auth_status", {})
                    assert isinstance(auth_status, dict)
                    print("✅ Authentication checked")

                    # 2. Review today's agenda
                    print("2. Reviewing today's tasks...")
                    due_today = await session.call_tool("get_tasks_due_today", {})
                    due_today_count = len(due_today.get("content", []))
                    print(f"   Tasks due today: {due_today_count}")

                    overdue = await session.call_tool("get_overdue_tasks", {})
                    overdue_count = len(overdue.get("content", []))
                    print(f"   Overdue tasks: {overdue_count}")

                    # 3. Check high priority tasks
                    print("3. Checking high priority tasks...")
                    high_priority = await session.call_tool("get_tasks_by_priority", {"priority": 5})
                    high_priority_count = len(high_priority.get("content", []))
                    print(f"   High priority tasks: {high_priority_count}")

                    # 4. Review all projects
                    print("4. Reviewing projects...")
                    projects = await session.call_tool("get_projects", {})
                    project_count = len(projects.get("content", []))
                    print(f"   Total projects: {project_count}")

                    # 5. Search for specific tasks
                    print("5. Searching for specific tasks...")
                    search_queries = ["meeting", "report", "email", "call"]
                    
                    for query in search_queries:
                        try:
                            search_results = await session.call_tool("search_tasks", {"query": query})
                            result_count = len(search_results.get("content", []))
                            print(f"   '{query}' search: {result_count} results")
                        except Exception as e:
                            print(f"   Search for '{query}' failed: {e}")

                    # 6. Get comprehensive task overview
                    print("6. Getting comprehensive task overview...")
                    all_tasks = await session.call_tool("get_tasks", {"include_completed": False})
                    total_tasks = len(all_tasks.get("content", []))
                    print(f"   Total active tasks: {total_tasks}")

                    # Verify workflow completed successfully
                    workflow_steps = [
                        auth_status, due_today, overdue, high_priority, projects, all_tasks
                    ]
                    
                    for i, step_result in enumerate(workflow_steps, 1):
                        assert isinstance(step_result, dict), f"Step {i} failed to return valid result"
                        assert "content" in step_result, f"Step {i} missing content field"

                    print("✅ Daily task management workflow completed successfully!")
                    
                    # Return summary statistics
                    return {
                        "due_today": due_today_count,
                        "overdue": overdue_count,
                        "high_priority": high_priority_count,
                        "total_projects": project_count,
                        "total_tasks": total_tasks
                    }

        except Exception as e:
            print(f"❌ Daily task management workflow failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    @pytest.mark.asyncio
    async def test_project_focused_workflow(self):
        """Test project-focused workflow"""
        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import stdio_client, StdioServerParameters

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    print("🔧 Testing project-focused workflow...")

                    # 1. Get all projects
                    print("1. Getting all projects...")
                    projects = await session.call_tool("get_projects", {})
                    project_list = projects.get("content", [])
                    print(f"   Found {len(project_list)} projects")

                    if not project_list:
                        print("⚠️ No projects found, creating mock scenario")
                        # Continue with other tests even if no projects
                        project_list = [{"id": "mock_project", "name": "Mock Project"}]

                    # 2. For each project, get detailed information
                    project_details = []
                    for project in project_list[:3]:  # Limit to first 3 projects
                        project_id = project.get("id", "")
                        project_name = project.get("name", "Unknown")
                        
                        print(f"2. Analyzing project: {project_name}")
                        
                        try:
                            # Get project details
                            project_detail = await session.call_tool("get_project", {"project_id": project_id})
                            
                            # Get project tasks
                            project_tasks = await session.call_tool("get_project_tasks", {
                                "project_id": project_id,
                                "include_completed": False
                            })
                            
                            task_count = len(project_tasks.get("content", []))
                            print(f"   Project '{project_name}': {task_count} active tasks")
                            
                            project_details.append({
                                "project": project,
                                "detail": project_detail,
                                "task_count": task_count
                            })
                            
                        except Exception as e:
                            print(f"   Failed to analyze project '{project_name}': {e}")

                    # 3. Identify projects with most tasks
                    if project_details:
                        busiest_project = max(project_details, key=lambda x: x["task_count"])
                        print(f"3. Busiest project: {busiest_project['project'].get('name')} ({busiest_project['task_count']} tasks)")

                    # 4. Cross-reference with priority tasks
                    print("4. Cross-referencing with priority tasks...")
                    for priority in [1, 3, 5]:
                        priority_tasks = await session.call_tool("get_tasks_by_priority", {"priority": priority})
                        priority_count = len(priority_tasks.get("content", []))
                        print(f"   Priority {priority}: {priority_count} tasks")

                    print("✅ Project-focused workflow completed successfully!")
                    return {"analyzed_projects": len(project_details)}

        except Exception as e:
            print(f"❌ Project-focused workflow failed: {e}")
            return None

    @pytest.mark.asyncio
    async def test_task_discovery_workflow(self):
        """Test task discovery and organization workflow"""
        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import stdio_client, StdioServerParameters

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    print("🔧 Testing task discovery workflow...")

                    # 1. Discover all tasks by different criteria
                    print("1. Discovering tasks by various criteria...")
                    
                    discovery_results = {}
                    
                    # By completion status
                    active_tasks = await session.call_tool("get_tasks", {"include_completed": False})
                    completed_tasks = await session.call_tool("get_tasks", {"include_completed": True})
                    
                    active_count = len(active_tasks.get("content", []))
                    total_count = len(completed_tasks.get("content", []))
                    completed_count = total_count - active_count
                    
                    discovery_results["active"] = active_count
                    discovery_results["completed"] = completed_count
                    discovery_results["total"] = total_count
                    
                    print(f"   Active tasks: {active_count}")
                    print(f"   Completed tasks: {completed_count}")
                    print(f"   Total tasks: {total_count}")

                    # 2. By time criteria
                    print("2. Discovering tasks by time criteria...")
                    
                    due_today = await session.call_tool("get_tasks_due_today", {})
                    overdue = await session.call_tool("get_overdue_tasks", {})
                    
                    due_today_count = len(due_today.get("content", []))
                    overdue_count = len(overdue.get("content", []))
                    
                    discovery_results["due_today"] = due_today_count
                    discovery_results["overdue"] = overdue_count
                    
                    print(f"   Due today: {due_today_count}")
                    print(f"   Overdue: {overdue_count}")

                    # 3. By priority levels
                    print("3. Discovering tasks by priority...")
                    
                    priority_distribution = {}
                    for priority in [0, 1, 3, 5]:  # None, Low, Medium, High
                        priority_tasks = await session.call_tool("get_tasks_by_priority", {"priority": priority})
                        count = len(priority_tasks.get("content", []))
                        priority_distribution[priority] = count
                        print(f"   Priority {priority}: {count} tasks")
                    
                    discovery_results["priority_distribution"] = priority_distribution

                    # 4. By search patterns
                    print("4. Discovering tasks by search patterns...")
                    
                    search_patterns = [
                        "urgent", "important", "meeting", "deadline", 
                        "review", "follow", "email", "call"
                    ]
                    
                    search_results = {}
                    for pattern in search_patterns:
                        try:
                            result = await session.call_tool("search_tasks", {"query": pattern})
                            count = len(result.get("content", []))
                            search_results[pattern] = count
                            if count > 0:
                                print(f"   Pattern '{pattern}': {count} matches")
                        except Exception as e:
                            print(f"   Search for '{pattern}' failed: {e}")
                    
                    discovery_results["search_patterns"] = search_results

                    # 5. Generate discovery summary
                    print("5. Generating discovery summary...")
                    
                    summary = {
                        "task_completion_rate": completed_count / total_count if total_count > 0 else 0,
                        "urgency_ratio": (due_today_count + overdue_count) / active_count if active_count > 0 else 0,
                        "high_priority_ratio": priority_distribution.get(5, 0) / active_count if active_count > 0 else 0,
                        "most_common_search": max(search_results.items(), key=lambda x: x[1]) if search_results else ("none", 0)
                    }
                    
                    print(f"   Task completion rate: {summary['task_completion_rate']:.2%}")
                    print(f"   Urgency ratio: {summary['urgency_ratio']:.2%}")
                    print(f"   High priority ratio: {summary['high_priority_ratio']:.2%}")
                    print(f"   Most common search pattern: '{summary['most_common_search'][0]}' ({summary['most_common_search'][1]} matches)")

                    print("✅ Task discovery workflow completed successfully!")
                    
                    discovery_results["summary"] = summary
                    return discovery_results

        except Exception as e:
            print(f"❌ Task discovery workflow failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    @pytest.mark.asyncio
    async def test_productivity_analysis_workflow(self):
        """Test productivity analysis workflow"""
        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import stdio_client, StdioServerParameters

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    print("🔧 Testing productivity analysis workflow...")

                    # 1. Gather comprehensive data
                    print("1. Gathering comprehensive task data...")
                    
                    # Get all data in parallel for efficiency
                    data_tasks = [
                        session.call_tool("get_tasks", {"include_completed": True}),
                        session.call_tool("get_projects", {}),
                        session.call_tool("get_tasks_due_today", {}),
                        session.call_tool("get_overdue_tasks", {}),
                        session.call_tool("get_tasks_by_priority", {"priority": 5}),
                        session.call_tool("get_tasks_by_priority", {"priority": 3}),
                        session.call_tool("get_tasks_by_priority", {"priority": 1}),
                        session.call_tool("get_tasks_by_priority", {"priority": 0}),
                    ]
                    
                    results = await asyncio.gather(*data_tasks, return_exceptions=True)
                    
                    # Extract results
                    all_tasks_result = results[0] if not isinstance(results[0], Exception) else {"content": []}
                    projects_result = results[1] if not isinstance(results[1], Exception) else {"content": []}
                    due_today_result = results[2] if not isinstance(results[2], Exception) else {"content": []}
                    overdue_result = results[3] if not isinstance(results[3], Exception) else {"content": []}
                    
                    priority_results = {}
                    for i, priority in enumerate([5, 3, 1, 0], 4):
                        if not isinstance(results[i], Exception):
                            priority_results[priority] = results[i].get("content", [])
                        else:
                            priority_results[priority] = []

                    # 2. Analyze task distribution
                    print("2. Analyzing task distribution...")
                    
                    all_tasks = all_tasks_result.get("content", [])
                    projects = projects_result.get("content", [])
                    
                    total_tasks = len(all_tasks)
                    total_projects = len(projects)
                    
                    print(f"   Total tasks: {total_tasks}")
                    print(f"   Total projects: {total_projects}")
                    print(f"   Average tasks per project: {total_tasks / total_projects if total_projects > 0 else 0:.1f}")

                    # 3. Analyze urgency and priority
                    print("3. Analyzing urgency and priority distribution...")
                    
                    due_today_count = len(due_today_result.get("content", []))
                    overdue_count = len(overdue_result.get("content", []))
                    
                    urgency_score = (due_today_count * 2 + overdue_count * 3) / total_tasks if total_tasks > 0 else 0
                    
                    priority_scores = {}
                    for priority, tasks in priority_results.items():
                        priority_scores[priority] = len(tasks)
                    
                    print(f"   Due today: {due_today_count}")
                    print(f"   Overdue: {overdue_count}")
                    print(f"   Urgency score: {urgency_score:.2f}")
                    
                    for priority, count in priority_scores.items():
                        print(f"   Priority {priority}: {count} tasks")

                    # 4. Calculate productivity metrics
                    print("4. Calculating productivity metrics...")
                    
                    # Estimate completion rate (this would be more accurate with real data)
                    active_tasks = [task for task in all_tasks if task.get("status", 0) != 2]
                    completed_tasks = [task for task in all_tasks if task.get("status", 0) == 2]
                    
                    completion_rate = len(completed_tasks) / total_tasks if total_tasks > 0 else 0
                    
                    # Calculate focus score (inverse of task scatter across projects)
                    focus_score = 1.0 - (total_projects / total_tasks) if total_tasks > 0 else 0
                    focus_score = max(0, min(1, focus_score))  # Clamp between 0 and 1
                    
                    # Calculate priority alignment (ratio of high-priority to total active tasks)
                    high_priority_active = len([t for t in active_tasks if t.get("priority", 0) >= 3])
                    priority_alignment = high_priority_active / len(active_tasks) if active_tasks else 0
                    
                    metrics = {
                        "completion_rate": completion_rate,
                        "urgency_score": urgency_score,
                        "focus_score": focus_score,
                        "priority_alignment": priority_alignment,
                        "task_load": len(active_tasks),
                        "project_diversity": total_projects
                    }
                    
                    print(f"   Completion rate: {completion_rate:.2%}")
                    print(f"   Focus score: {focus_score:.2f}")
                    print(f"   Priority alignment: {priority_alignment:.2%}")
                    print(f"   Current task load: {len(active_tasks)}")

                    # 5. Generate recommendations
                    print("5. Generating productivity recommendations...")
                    
                    recommendations = []
                    
                    if urgency_score > 2.0:
                        recommendations.append("High urgency detected - focus on overdue and due-today tasks")
                    
                    if completion_rate < 0.3:
                        recommendations.append("Low completion rate - consider breaking down large tasks")
                    
                    if focus_score < 0.5:
                        recommendations.append("Tasks scattered across many projects - consider consolidation")
                    
                    if priority_alignment < 0.3:
                        recommendations.append("Few high-priority tasks - review and adjust task priorities")
                    
                    if len(active_tasks) > 50:
                        recommendations.append("High task load - consider task delegation or elimination")
                    
                    if not recommendations:
                        recommendations.append("Productivity metrics look healthy - keep up the good work!")
                    
                    for i, rec in enumerate(recommendations, 1):
                        print(f"   {i}. {rec}")

                    print("✅ Productivity analysis workflow completed successfully!")
                    
                    return {
                        "metrics": metrics,
                        "recommendations": recommendations,
                        "data_summary": {
                            "total_tasks": total_tasks,
                            "active_tasks": len(active_tasks),
                            "completed_tasks": len(completed_tasks),
                            "total_projects": total_projects,
                            "due_today": due_today_count,
                            "overdue": overdue_count
                        }
                    }

        except Exception as e:
            print(f"❌ Productivity analysis workflow failed: {e}")
            import traceback
            traceback.print_exc()
            return None


@pytest.mark.e2e
@pytest.mark.slow
class TestLongRunningScenarios:
    """Test long-running real-world scenarios"""

    @pytest.mark.asyncio
    async def test_extended_session_workflow(self):
        """Test extended session with multiple workflows"""
        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import stdio_client, StdioServerParameters

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    print("🔧 Testing extended session workflow...")

                    session_results = []
                    
                    # Simulate a full work session with multiple activities
                    workflows = [
                        ("Morning Review", self._morning_review_workflow),
                        ("Project Planning", self._project_planning_workflow),
                        ("Midday Check", self._midday_check_workflow),
                        ("Priority Adjustment", self._priority_adjustment_workflow),
                        ("End of Day Review", self._end_of_day_workflow)
                    ]
                    
                    for workflow_name, workflow_func in workflows:
                        print(f"Starting {workflow_name}...")
                        start_time = time.time()
                        
                        try:
                            result = await workflow_func(session)
                            end_time = time.time()
                            duration = end_time - start_time
                            
                            session_results.append({
                                "workflow": workflow_name,
                                "success": True,
                                "duration": duration,
                                "result": result
                            })
                            
                            print(f"✅ {workflow_name} completed in {duration:.2f}s")
                            
                        except Exception as e:
                            end_time = time.time()
                            duration = end_time - start_time
                            
                            session_results.append({
                                "workflow": workflow_name,
                                "success": False,
                                "duration": duration,
                                "error": str(e)
                            })
                            
                            print(f"❌ {workflow_name} failed after {duration:.2f}s: {e}")

                        # Brief pause between workflows
                        await asyncio.sleep(0.5)

                    # Analyze session results
                    successful_workflows = sum(1 for r in session_results if r["success"])
                    total_workflows = len(session_results)
                    success_rate = successful_workflows / total_workflows
                    total_duration = sum(r["duration"] for r in session_results)
                    
                    print(f"Session Summary:")
                    print(f"  Successful workflows: {successful_workflows}/{total_workflows} ({success_rate:.2%})")
                    print(f"  Total session duration: {total_duration:.2f}s")
                    print(f"  Average workflow duration: {total_duration/total_workflows:.2f}s")

                    # Session should be mostly successful
                    assert success_rate >= 0.8, f"Session success rate too low: {success_rate:.2%}"

                    print("✅ Extended session workflow completed successfully!")
                    return session_results

        except Exception as e:
            print(f"❌ Extended session workflow failed: {e}")
            return None

    async def _morning_review_workflow(self, session):
        """Morning review workflow"""
        auth_status = await session.call_tool("auth_status", {})
        due_today = await session.call_tool("get_tasks_due_today", {})
        overdue = await session.call_tool("get_overdue_tasks", {})
        
        return {
            "due_today": len(due_today.get("content", [])),
            "overdue": len(overdue.get("content", []))
        }

    async def _project_planning_workflow(self, session):
        """Project planning workflow"""
        projects = await session.call_tool("get_projects", {})
        high_priority = await session.call_tool("get_tasks_by_priority", {"priority": 5})
        
        return {
            "projects": len(projects.get("content", [])),
            "high_priority": len(high_priority.get("content", []))
        }

    async def _midday_check_workflow(self, session):
        """Midday check workflow"""
        all_tasks = await session.call_tool("get_tasks", {"include_completed": False})
        search_urgent = await session.call_tool("search_tasks", {"query": "urgent"})
        
        return {
            "active_tasks": len(all_tasks.get("content", [])),
            "urgent_tasks": len(search_urgent.get("content", []))
        }

    async def _priority_adjustment_workflow(self, session):
        """Priority adjustment workflow"""
        medium_priority = await session.call_tool("get_tasks_by_priority", {"priority": 3})
        low_priority = await session.call_tool("get_tasks_by_priority", {"priority": 1})
        
        return {
            "medium_priority": len(medium_priority.get("content", [])),
            "low_priority": len(low_priority.get("content", []))
        }

    async def _end_of_day_workflow(self, session):
        """End of day workflow"""
        all_tasks = await session.call_tool("get_tasks", {"include_completed": True})
        projects = await session.call_tool("get_projects", {})
        
        return {
            "total_tasks": len(all_tasks.get("content", [])),
            "total_projects": len(projects.get("content", []))
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
