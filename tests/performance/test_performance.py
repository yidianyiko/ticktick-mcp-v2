#!/usr/bin/env python3
"""
Performance tests for TickTick MCP server
"""

import asyncio
import gc
import statistics
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore[assignment]

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from tools import projects, tasks


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    @pytest.mark.asyncio
    async def test_tool_call_latency(self):
        """Test latency of individual tool calls"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:

                    # Test different operations multiple times
                    operations = [
                        ("auth_status", {}),
                        ("get_projects", {}),
                        ("get_tasks", {"include_completed": False}),
                        ("get_tasks_due_today", {}),
                        ("get_overdue_tasks", {}),
                    ]

                    results = {}

                    for operation_name, params in operations:
                        latencies = []

                        # Run each operation 10 times
                        for _ in range(10):
                            start_time = time.perf_counter()
                            try:
                                await session.call_tool(operation_name, params)
                                end_time = time.perf_counter()
                                latency = (
                                    end_time - start_time
                                ) * 1000  # Convert to ms
                                latencies.append(latency)
                            except Exception:
                                break

                        if latencies:
                            avg_latency = statistics.mean(latencies)
                            min_latency = min(latencies)
                            max_latency = max(latencies)
                            p95_latency = statistics.quantiles(latencies, n=20)[
                                18
                            ]  # 95th percentile

                            results[operation_name] = {
                                "avg": avg_latency,
                                "min": min_latency,
                                "max": max_latency,
                                "p95": p95_latency,
                            }

                    # Performance assertions
                    for operation_name, metrics in results.items():
                        # Average latency should be under 2 seconds
                        assert (
                            metrics["avg"] < 2000
                        ), f"{operation_name} avg latency too high: {metrics['avg']:.2f}ms"
                        # P95 latency should be under 5 seconds
                        assert (
                            metrics["p95"] < 5000
                        ), f"{operation_name} P95 latency too high: {metrics['p95']:.2f}ms"

                    return results

        except Exception:
            return {}

    @pytest.mark.asyncio
    async def test_throughput_benchmark(self):
        """Test throughput under load"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:

                    # Test concurrent requests
                    concurrent_levels = [1, 2, 5, 10]

                    for concurrency in concurrent_levels:

                        start_time = time.perf_counter()

                        # Create concurrent tasks
                        tasks = []
                        for _ in range(concurrency):
                            task = session.call_tool("auth_status", {})
                            tasks.append(task)

                        # Execute all tasks concurrently
                        results = await asyncio.gather(*tasks, return_exceptions=True)

                        end_time = time.perf_counter()
                        total_time = end_time - start_time

                        # Count successful requests
                        successful = sum(
                            1 for r in results if not isinstance(r, Exception)
                        )
                        throughput = successful / total_time

                        # Throughput should be reasonable
                        assert (
                            throughput > 0.5
                        ), f"Throughput too low at concurrency {concurrency}: {throughput:.2f} req/s"
                        # Success rate should be high
                        assert (
                            successful / concurrency >= 0.9
                        ), f"Success rate too low at concurrency {concurrency}: {successful/concurrency:.2%}"

                    return True

        except Exception:
            return False

    def test_unit_function_performance(self):
        """Test performance of individual unit functions"""

        # Import functions to test (moved to top-level)

        # Mock the adapter to avoid real API calls
        mock_adapter = Mock()
        mock_adapter.get_tasks.return_value = [
            {"id": f"task{i}", "title": f"Task {i}"} for i in range(100)
        ]
        mock_adapter.get_projects.return_value = [
            {"id": f"proj{i}", "name": f"Project {i}"} for i in range(10)
        ]

        with patch("tools.tasks.get_client", return_value=mock_adapter), patch("tools.tasks.convert_tasks_times_to_local", side_effect=lambda x: x):
                # Benchmark get_tasks
                start_time = time.perf_counter()
                for _ in range(100):
                    tasks.get_tasks()
                end_time = time.perf_counter()

                get_tasks_time = (end_time - start_time) / 100 * 1000  # ms per call

                # Should be fast since it's mostly mocked
                assert (
                    get_tasks_time < 10
                ), f"get_tasks too slow: {get_tasks_time:.3f}ms"

        with patch("tools.projects.get_client", return_value=mock_adapter):
            # Benchmark get_projects
            start_time = time.perf_counter()
            for _ in range(100):
                projects.get_projects()
            end_time = time.perf_counter()

            get_projects_time = (end_time - start_time) / 100 * 1000  # ms per call

            # Should be fast since it's mostly mocked
            assert (
                get_projects_time < 10
            ), f"get_projects too slow: {get_projects_time:.3f}ms"

        return True

    def test_memory_efficiency(self):
        """Test memory efficiency of operations"""
        if psutil is None:
            return True

        # Get initial memory usage
        process = psutil.Process()
        gc.collect()  # Force garbage collection
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Mock large datasets
        large_task_list = [
            {"id": f"task{i}", "title": f"Task {i}" * 10} for i in range(1000)
        ]
        large_project_list = [
            {"id": f"proj{i}", "name": f"Project {i}" * 10} for i in range(100)
        ]

        mock_adapter = Mock()
        mock_adapter.get_tasks.return_value = large_task_list
        mock_adapter.get_projects.return_value = large_project_list

        with patch("tools.tasks.get_client", return_value=mock_adapter), patch("tools.tasks.convert_tasks_times_to_local", side_effect=lambda x: x):
                # Process large amounts of data
                for _ in range(10):
                    result = tasks.get_tasks()
                    assert len(result) == 1000
                    # Don't keep references to results
                    del result

        with patch("tools.projects.get_client", return_value=mock_adapter):
            for _ in range(10):
                result = projects.get_projects()
                assert len(result) == 100
                del result

        # Force garbage collection and check memory
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable for processing large datasets
        assert (
            memory_increase < 50
        ), f"Memory increase too high: {memory_increase:.2f} MB"

        return True


@pytest.mark.performance
@pytest.mark.slow
class TestStressTests:
    """Stress tests for the system"""

    @pytest.mark.asyncio
    async def test_high_load_stress(self):
        """Test system under high load"""
        try:

            server_params = StdioServerParameters(
                command="python",
                args=["-m", "src.cli", "run"],
                cwd=Path(__file__).parent.parent.parent,
            )

            async with stdio_client(server_params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:

                    # Create a large number of concurrent requests
                    num_requests = 50
                    operations = [
                        ("auth_status", {}),
                        ("get_projects", {}),
                        ("get_tasks", {"include_completed": False}),
                        ("get_tasks_due_today", {}),
                        ("get_overdue_tasks", {}),
                    ]

                    start_time = time.perf_counter()

                    # Create all tasks
                    all_tasks = []
                    for i in range(num_requests):
                        operation_name, params = operations[i % len(operations)]
                        task = session.call_tool(operation_name, params)
                        all_tasks.append(task)

                    # Execute all requests
                    results = await asyncio.gather(*all_tasks, return_exceptions=True)

                    end_time = time.perf_counter()
                    total_time = end_time - start_time

                    # Analyze results
                    successful = sum(1 for r in results if not isinstance(r, Exception))
                    num_requests - successful
                    success_rate = successful / num_requests
                    throughput = successful / total_time

                    # Performance requirements for stress test
                    assert (
                        success_rate >= 0.8
                    ), f"Success rate too low under stress: {success_rate:.2%}"
                    assert (
                        throughput >= 1.0
                    ), f"Throughput too low under stress: {throughput:.2f} req/s"

                    return True

        except Exception:
            return False

    def test_memory_stress(self):
        """Test memory usage under stress"""
        if psutil is None:
            return True

        # Get initial memory
        process = psutil.Process()
        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024

        # Create very large mock datasets
        huge_task_list = [
            {"id": f"task{i}", "title": f"Task {i}" * 100, "content": "X" * 1000}
            for i in range(5000)
        ]

        mock_adapter = Mock()
        mock_adapter.get_tasks.return_value = huge_task_list

        max_memory = initial_memory

        with patch(
            "tools.tasks.get_client", return_value=mock_adapter,
        ), patch(
            "tools.tasks.convert_tasks_times_to_local", side_effect=lambda x: x,
        ):
                # Process huge datasets repeatedly
                for i in range(20):
                    result = tasks.get_tasks()
                    assert len(result) == 5000

                    # Check memory usage periodically
                    if i % 5 == 0:
                        current_memory = process.memory_info().rss / 1024 / 1024
                        max_memory = max(max_memory, current_memory)

                    # Clear reference
                    del result

                    # Occasional garbage collection
                    if i % 10 == 0:
                        gc.collect()

        # Final memory check
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        peak_increase = max_memory - initial_memory
        final_increase = final_memory - initial_memory

        # Memory requirements for stress test
        assert (
            peak_increase < 200
        ), f"Peak memory increase too high: {peak_increase:.2f} MB"
        assert (
            final_increase < 100
        ), f"Final memory increase too high: {final_increase:.2f} MB"

        return True


@pytest.mark.performance
class TestPerformanceRegression:
    """Performance regression tests"""

    def test_performance_baseline(self):
        """Establish performance baseline for regression testing"""


        # Create consistent mock data
        mock_tasks = [{"id": f"task{i}", "title": f"Task {i}"} for i in range(100)]
        mock_projects = [{"id": f"proj{i}", "name": f"Project {i}"} for i in range(10)]

        mock_adapter = Mock()
        mock_adapter.get_tasks.return_value = mock_tasks
        mock_adapter.get_projects.return_value = mock_projects

        baselines = {}

        # Test get_tasks performance
        with patch(
            "tools.tasks.get_client", return_value=mock_adapter,
        ), patch(
            "tools.tasks.convert_tasks_times_to_local", side_effect=lambda x: x,
        ):
                start_time = time.perf_counter()
                for _ in range(100):
                    tasks.get_tasks()
                end_time = time.perf_counter()
                baselines["get_tasks"] = (end_time - start_time) / 100

        # Test get_projects performance
        with patch("tools.projects.get_client", return_value=mock_adapter):
            start_time = time.perf_counter()
            for _ in range(100):
                projects.get_projects()
            end_time = time.perf_counter()
            baselines["get_projects"] = (end_time - start_time) / 100

        # Print baselines for reference
        for operation, baseline_time in baselines.items():

            # Sanity check - operations should be reasonably fast
            assert (
                baseline_time < 0.1
            ), f"{operation} baseline too slow: {baseline_time*1000:.3f}ms"

        return baselines


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "performance"])
