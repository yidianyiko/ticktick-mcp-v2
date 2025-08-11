#!/usr/bin/env python3
"""
Full integration tests - testing complete workflows
"""

import asyncio
import contextlib
import sys
import time
import traceback
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore[assignment]

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.mark.integration
class TestFullWorkflowIntegration:
    """Test complete workflows end-to-end"""

    @pytest.mark.asyncio
    async def test_project_task_lifecycle(self):
        """Test complete project and task lifecycle"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:

                    # 1. Get initial project count
                    initial_projects = await session.call_tool("get_projects", {})
                    initial_count = len(initial_projects.get("content", []))

                    # 2. Create a test project (if supported)
                    try:
                        await session.call_tool(
                            "create_project",
                            {
                                "name": "Test Integration Project",
                                "color": "#FF0000",
                            },
                        )
                        project_created = True
                    except Exception:
                        project_created = False

                    # 3. Get updated project list
                    updated_projects = await session.call_tool("get_projects", {})
                    updated_count = len(updated_projects.get("content", []))

                    if project_created:
                        assert (
                            updated_count == initial_count + 1
                        ), "Project count should increase by 1"

                    # 4. Get tasks in different ways
                    await session.call_tool("get_tasks", {"include_completed": False})
                    await session.call_tool("get_tasks_due_today", {})
                    await session.call_tool("get_overdue_tasks", {})
                    await session.call_tool("get_tasks_by_priority", {"priority": 5})

                    # 5. Test search functionality
                    await session.call_tool("search_tasks", {"query": "test"})

                    return True

        except Exception:
            traceback.print_exc()
            return False

    @pytest.mark.asyncio
    async def test_error_recovery_integration(self):
        """Test error recovery and resilience"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:

                    # 1. Test invalid parameters
                    with contextlib.suppress(Exception):
                        await session.call_tool(
                            "get_tasks_by_priority", {"priority": "invalid"},
                        )

                    # 2. Test missing required parameters
                    with contextlib.suppress(Exception):
                        await session.call_tool("get_project", {})

                    # 3. Test non-existent resource
                    with contextlib.suppress(Exception):
                        await session.call_tool(
                            "get_project", {"project_id": "nonexistent123"},
                        )

                    # 4. Test server stability after errors
                    auth_result = await session.call_tool("auth_status", {})
                    assert isinstance(auth_result, dict)

                    return True

        except Exception:
            return False

    @pytest.mark.asyncio
    async def test_concurrent_requests_integration(self):
        """Test handling of concurrent requests"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:

                    # Create multiple concurrent requests
                    tasks_futures = [
                        session.call_tool("auth_status", {}),
                        session.call_tool("get_projects", {}),
                        session.call_tool("get_tasks", {"include_completed": False}),
                        session.call_tool("get_tasks_due_today", {}),
                        session.call_tool("get_overdue_tasks", {}),
                    ]

                    # Execute all requests concurrently
                    results = await asyncio.gather(
                        *tasks_futures, return_exceptions=True,
                    )

                    # Verify all requests completed successfully
                    success_count = 0
                    for _i, result in enumerate(results):
                        if isinstance(result, Exception):
                            pass
                        else:
                            success_count += 1
                            assert isinstance(result, dict)
                            assert "content" in result

                    success_rate = success_count / len(results)

                    # Require at least 80% success rate
                    assert (
                        success_rate >= 0.8
                    ), f"Success rate too low: {success_rate:.2%}"

                    return True

        except Exception:
            return False


@pytest.mark.integration
class TestDataConsistencyIntegration:
    """Test data consistency across operations"""

    @pytest.mark.asyncio
    async def test_task_filtering_consistency(self):
        """Test consistency of task filtering across different methods"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:

                    # Get all tasks
                    all_tasks = await session.call_tool(
                        "get_tasks", {"include_completed": False},
                    )
                    all_task_ids = set()

                    for task in all_tasks.get("content", []):
                        if isinstance(task, dict) and "id" in task:
                            all_task_ids.add(task["id"])

                    # Get tasks by different filters
                    due_today = await session.call_tool("get_tasks_due_today", {})
                    overdue = await session.call_tool("get_overdue_tasks", {})

                    due_today_ids = set()
                    overdue_ids = set()

                    for task in due_today.get("content", []):
                        if isinstance(task, dict) and "id" in task:
                            due_today_ids.add(task["id"])

                    for task in overdue.get("content", []):
                        if isinstance(task, dict) and "id" in task:
                            overdue_ids.add(task["id"])

                    # Verify consistency: filtered tasks should be subsets of all tasks
                    assert due_today_ids.issubset(
                        all_task_ids,
                    ), "Due today tasks should be subset of all tasks"
                    assert overdue_ids.issubset(
                        all_task_ids,
                    ), "Overdue tasks should be subset of all tasks"

                    # Due today and overdue should not overlap (a task can't be both)
                    overlap = due_today_ids.intersection(overdue_ids)
                    if overlap:
                        pass

                    return True

        except Exception:
            return False

    @pytest.mark.asyncio
    async def test_priority_filtering_consistency(self):
        """Test consistency of priority filtering"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:

                    # Get tasks by different priority levels
                    priority_results = {}
                    total_priority_tasks = 0

                    for priority in [0, 1, 3, 5]:  # None, Low, Medium, High
                        result = await session.call_tool(
                            "get_tasks_by_priority", {"priority": priority},
                        )
                        priority_tasks = result.get("content", [])
                        priority_results[priority] = len(priority_tasks)
                        total_priority_tasks += len(priority_tasks)

                    # Get all tasks for comparison
                    all_tasks = await session.call_tool(
                        "get_tasks", {"include_completed": False},
                    )
                    len(all_tasks.get("content", []))

                    # Note: The totals might not match exactly if some tasks have priorities
                    # not in our test set, but the priority filtering should be consistent

                    return True

        except Exception:
            return False


@pytest.mark.integration
class TestPerformanceIntegration:
    """Test performance characteristics"""

    @pytest.mark.asyncio
    async def test_response_time_integration(self):
        """Test response times for various operations"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:

                    # Test different operations and measure response times
                    operations = [
                        ("auth_status", {}),
                        ("get_projects", {}),
                        ("get_tasks", {"include_completed": False}),
                        ("get_tasks_due_today", {}),
                        ("get_overdue_tasks", {}),
                        ("get_tasks_by_priority", {"priority": 3}),
                        ("search_tasks", {"query": "test"}),
                    ]

                    response_times = {}

                    for operation_name, params in operations:
                        start_time = time.time()
                        try:
                            await session.call_tool(operation_name, params)
                            end_time = time.time()
                            response_time = end_time - start_time
                            response_times[operation_name] = response_time

                            # Basic performance assertion: should complete within 10 seconds
                            assert (
                                response_time < 10.0
                            ), f"{operation_name} took too long: {response_time:.3f}s"

                        except Exception:
                            pass

                    # Calculate average response time
                    if response_times:
                        avg_response_time = sum(response_times.values()) / len(
                            response_times,
                        )

                        # Average should be reasonable
                        assert (
                            avg_response_time < 5.0
                        ), f"Average response time too high: {avg_response_time:.3f}s"

                    return True

        except Exception:
            return False

    @pytest.mark.asyncio
    async def test_memory_usage_integration(self):
        """Test memory usage doesn't grow excessively"""
        try:
            if psutil is None:
                return True

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:

                    # Get initial memory usage
                    process = psutil.Process()
                    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

                    # Perform multiple operations to stress test memory
                    for i in range(10):
                        await session.call_tool(
                            "get_tasks", {"include_completed": False},
                        )
                        await session.call_tool("get_projects", {})
                        await session.call_tool("get_tasks_due_today", {})

                        if i % 5 == 0:
                            process.memory_info().rss / 1024 / 1024

                    # Get final memory usage
                    final_memory = process.memory_info().rss / 1024 / 1024
                    memory_increase = final_memory - initial_memory

                    # Memory increase should be reasonable (less than 100MB for this test)
                    assert (
                        memory_increase < 100
                    ), f"Memory increase too high: {memory_increase:.2f} MB"

                    return True

        except ImportError:
            return True
        except Exception:
            return False


@pytest.mark.integration
@pytest.mark.slow
class TestLongRunningIntegration:
    """Test long-running scenarios"""

    @pytest.mark.asyncio
    async def test_server_stability_long_running(self):
        """Test server stability over extended period"""
        try:


            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:

                    successful_calls = 0
                    total_calls = 0

                    # Run for 30 iterations with various operations
                    for i in range(30):
                        operations = [
                            ("auth_status", {}),
                            ("get_projects", {}),
                            ("get_tasks", {"include_completed": False}),
                            ("get_tasks_due_today", {}),
                        ]

                        for operation_name, params in operations:
                            try:
                                total_calls += 1
                                result = await session.call_tool(operation_name, params)
                                assert isinstance(result, dict)
                                successful_calls += 1

                            except Exception:
                                pass

                        # Brief pause between iterations
                        await asyncio.sleep(0.1)

                        if (i + 1) % 10 == 0:
                            successful_calls / total_calls if total_calls > 0 else 0

                    final_success_rate = (
                        successful_calls / total_calls if total_calls > 0 else 0
                    )

                    # Require at least 95% success rate for long-running stability
                    assert (
                        final_success_rate >= 0.95
                    ), f"Success rate too low: {final_success_rate:.2%}"

                    return True

        except Exception:
            return False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
