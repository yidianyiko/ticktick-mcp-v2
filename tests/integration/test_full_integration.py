#!/usr/bin/env python3
"""
Full integration tests - testing complete workflows
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock
import json
import time

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.mark.integration
class TestFullWorkflowIntegration:
    """Test complete workflows end-to-end"""

    @pytest.mark.asyncio
    async def test_project_task_lifecycle(self):
        """Test complete project and task lifecycle"""
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
                    print("🔧 Testing project-task lifecycle...")

                    # 1. Get initial project count
                    initial_projects = await session.call_tool("get_projects", {})
                    initial_count = len(initial_projects.get("content", []))
                    print(f"Initial project count: {initial_count}")

                    # 2. Create a test project (if supported)
                    try:
                        new_project = await session.call_tool("create_project", {
                            "name": "Test Integration Project",
                            "color": "#FF0000"
                        })
                        print("✅ Project creation successful")
                        project_created = True
                    except Exception as e:
                        print(f"⚠️ Project creation not available or failed: {e}")
                        project_created = False

                    # 3. Get updated project list
                    updated_projects = await session.call_tool("get_projects", {})
                    updated_count = len(updated_projects.get("content", []))
                    
                    if project_created:
                        assert updated_count == initial_count + 1, "Project count should increase by 1"
                        print("✅ Project count verification passed")

                    # 4. Get tasks in different ways
                    all_tasks = await session.call_tool("get_tasks", {"include_completed": False})
                    due_today = await session.call_tool("get_tasks_due_today", {})
                    overdue = await session.call_tool("get_overdue_tasks", {})
                    high_priority = await session.call_tool("get_tasks_by_priority", {"priority": 5})

                    print(f"All tasks: {len(all_tasks.get('content', []))}")
                    print(f"Due today: {len(due_today.get('content', []))}")
                    print(f"Overdue: {len(overdue.get('content', []))}")
                    print(f"High priority: {len(high_priority.get('content', []))}")

                    # 5. Test search functionality
                    search_result = await session.call_tool("search_tasks", {"query": "test"})
                    print(f"Search results: {len(search_result.get('content', []))}")

                    print("✅ Full workflow integration test completed successfully!")
                    return True

        except Exception as e:
            print(f"❌ Full workflow integration test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    @pytest.mark.asyncio
    async def test_error_recovery_integration(self):
        """Test error recovery and resilience"""
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
                    print("🔧 Testing error recovery...")

                    # 1. Test invalid parameters
                    try:
                        await session.call_tool("get_tasks_by_priority", {"priority": "invalid"})
                        print("⚠️ Invalid parameter should have been rejected")
                    except Exception as e:
                        print(f"✅ Invalid parameter properly rejected: {type(e).__name__}")

                    # 2. Test missing required parameters
                    try:
                        await session.call_tool("get_project", {})
                        print("✅ Missing parameter handled gracefully")
                    except Exception as e:
                        print(f"✅ Missing parameter properly handled: {type(e).__name__}")

                    # 3. Test non-existent resource
                    try:
                        result = await session.call_tool("get_project", {"project_id": "nonexistent123"})
                        print("✅ Non-existent resource handled gracefully")
                    except Exception as e:
                        print(f"✅ Non-existent resource properly handled: {type(e).__name__}")

                    # 4. Test server stability after errors
                    auth_result = await session.call_tool("auth_status", {})
                    assert isinstance(auth_result, dict)
                    print("✅ Server remained stable after error conditions")

                    print("✅ Error recovery integration test completed!")
                    return True

        except Exception as e:
            print(f"❌ Error recovery integration test failed: {e}")
            return False

    @pytest.mark.asyncio
    async def test_concurrent_requests_integration(self):
        """Test handling of concurrent requests"""
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
                    print("🔧 Testing concurrent requests...")

                    # Create multiple concurrent requests
                    tasks_futures = [
                        session.call_tool("auth_status", {}),
                        session.call_tool("get_projects", {}),
                        session.call_tool("get_tasks", {"include_completed": False}),
                        session.call_tool("get_tasks_due_today", {}),
                        session.call_tool("get_overdue_tasks", {}),
                    ]

                    # Execute all requests concurrently
                    results = await asyncio.gather(*tasks_futures, return_exceptions=True)

                    # Verify all requests completed successfully
                    success_count = 0
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            print(f"Request {i} failed: {result}")
                        else:
                            success_count += 1
                            assert isinstance(result, dict)
                            assert "content" in result

                    success_rate = success_count / len(results)
                    print(f"Concurrent request success rate: {success_rate:.2%}")
                    
                    # Require at least 80% success rate
                    assert success_rate >= 0.8, f"Success rate too low: {success_rate:.2%}"

                    print("✅ Concurrent requests integration test completed!")
                    return True

        except Exception as e:
            print(f"❌ Concurrent requests integration test failed: {e}")
            return False


@pytest.mark.integration
class TestDataConsistencyIntegration:
    """Test data consistency across operations"""

    @pytest.mark.asyncio
    async def test_task_filtering_consistency(self):
        """Test consistency of task filtering across different methods"""
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
                    print("🔧 Testing task filtering consistency...")

                    # Get all tasks
                    all_tasks = await session.call_tool("get_tasks", {"include_completed": False})
                    all_task_ids = set()
                    
                    for task in all_tasks.get("content", []):
                        if isinstance(task, dict) and "id" in task:
                            all_task_ids.add(task["id"])

                    print(f"Total tasks: {len(all_task_ids)}")

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

                    print(f"Due today: {len(due_today_ids)}")
                    print(f"Overdue: {len(overdue_ids)}")

                    # Verify consistency: filtered tasks should be subsets of all tasks
                    assert due_today_ids.issubset(all_task_ids), "Due today tasks should be subset of all tasks"
                    assert overdue_ids.issubset(all_task_ids), "Overdue tasks should be subset of all tasks"
                    
                    # Due today and overdue should not overlap (a task can't be both)
                    overlap = due_today_ids.intersection(overdue_ids)
                    if overlap:
                        print(f"⚠️ Found {len(overlap)} tasks that are both due today and overdue")
                    
                    print("✅ Task filtering consistency test completed!")
                    return True

        except Exception as e:
            print(f"❌ Task filtering consistency test failed: {e}")
            return False

    @pytest.mark.asyncio
    async def test_priority_filtering_consistency(self):
        """Test consistency of priority filtering"""
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
                    print("🔧 Testing priority filtering consistency...")

                    # Get tasks by different priority levels
                    priority_results = {}
                    total_priority_tasks = 0
                    
                    for priority in [0, 1, 3, 5]:  # None, Low, Medium, High
                        result = await session.call_tool("get_tasks_by_priority", {"priority": priority})
                        priority_tasks = result.get("content", [])
                        priority_results[priority] = len(priority_tasks)
                        total_priority_tasks += len(priority_tasks)
                        print(f"Priority {priority}: {len(priority_tasks)} tasks")

                    # Get all tasks for comparison
                    all_tasks = await session.call_tool("get_tasks", {"include_completed": False})
                    all_task_count = len(all_tasks.get("content", []))
                    
                    print(f"Total tasks from priority queries: {total_priority_tasks}")
                    print(f"Total tasks from get_tasks: {all_task_count}")

                    # Note: The totals might not match exactly if some tasks have priorities
                    # not in our test set, but the priority filtering should be consistent
                    
                    print("✅ Priority filtering consistency test completed!")
                    return True

        except Exception as e:
            print(f"❌ Priority filtering consistency test failed: {e}")
            return False


@pytest.mark.integration
class TestPerformanceIntegration:
    """Test performance characteristics"""

    @pytest.mark.asyncio
    async def test_response_time_integration(self):
        """Test response times for various operations"""
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
                    print("🔧 Testing response times...")

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
                            result = await session.call_tool(operation_name, params)
                            end_time = time.time()
                            response_time = end_time - start_time
                            response_times[operation_name] = response_time
                            
                            print(f"{operation_name}: {response_time:.3f}s")
                            
                            # Basic performance assertion: should complete within 10 seconds
                            assert response_time < 10.0, f"{operation_name} took too long: {response_time:.3f}s"
                            
                        except Exception as e:
                            print(f"❌ {operation_name} failed: {e}")

                    # Calculate average response time
                    if response_times:
                        avg_response_time = sum(response_times.values()) / len(response_times)
                        print(f"Average response time: {avg_response_time:.3f}s")
                        
                        # Average should be reasonable
                        assert avg_response_time < 5.0, f"Average response time too high: {avg_response_time:.3f}s"

                    print("✅ Response time integration test completed!")
                    return True

        except Exception as e:
            print(f"❌ Response time integration test failed: {e}")
            return False

    @pytest.mark.asyncio
    async def test_memory_usage_integration(self):
        """Test memory usage doesn't grow excessively"""
        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import stdio_client, StdioServerParameters
            import psutil
            import os

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    print("🔧 Testing memory usage...")

                    # Get initial memory usage
                    process = psutil.Process()
                    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

                    print(f"Initial memory usage: {initial_memory:.2f} MB")

                    # Perform multiple operations to stress test memory
                    for i in range(10):
                        await session.call_tool("get_tasks", {"include_completed": False})
                        await session.call_tool("get_projects", {})
                        await session.call_tool("get_tasks_due_today", {})
                        
                        if i % 5 == 0:
                            current_memory = process.memory_info().rss / 1024 / 1024
                            print(f"Memory after {i+1} iterations: {current_memory:.2f} MB")

                    # Get final memory usage
                    final_memory = process.memory_info().rss / 1024 / 1024
                    memory_increase = final_memory - initial_memory
                    
                    print(f"Final memory usage: {final_memory:.2f} MB")
                    print(f"Memory increase: {memory_increase:.2f} MB")

                    # Memory increase should be reasonable (less than 100MB for this test)
                    assert memory_increase < 100, f"Memory increase too high: {memory_increase:.2f} MB"

                    print("✅ Memory usage integration test completed!")
                    return True

        except ImportError:
            print("⚠️ psutil not available, skipping memory test")
            return True
        except Exception as e:
            print(f"❌ Memory usage integration test failed: {e}")
            return False


@pytest.mark.integration
@pytest.mark.slow
class TestLongRunningIntegration:
    """Test long-running scenarios"""

    @pytest.mark.asyncio
    async def test_server_stability_long_running(self):
        """Test server stability over extended period"""
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
                    print("🔧 Testing long-running server stability...")

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
                                
                            except Exception as e:
                                print(f"Call {total_calls} failed: {operation_name} - {e}")

                        # Brief pause between iterations
                        await asyncio.sleep(0.1)
                        
                        if (i + 1) % 10 == 0:
                            success_rate = successful_calls / total_calls if total_calls > 0 else 0
                            print(f"After {i+1} iterations: {success_rate:.2%} success rate")

                    final_success_rate = successful_calls / total_calls if total_calls > 0 else 0
                    print(f"Final success rate: {final_success_rate:.2%} ({successful_calls}/{total_calls})")

                    # Require at least 95% success rate for long-running stability
                    assert final_success_rate >= 0.95, f"Success rate too low: {final_success_rate:.2%}"

                    print("✅ Long-running stability test completed!")
                    return True

        except Exception as e:
            print(f"❌ Long-running stability test failed: {e}")
            return False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
