#!/usr/bin/env python3
"""
Test runner for TickTick MCP v2
"""

import argparse
import subprocess
import sys


def run_unit_tests():
    """Run unit tests"""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/", "-v"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def run_integration_tests():
    """Run integration tests"""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/integration/", "-v"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def run_e2e_tests():
    """Run end-to-end tests"""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/e2e/", "-v"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def run_all_tests():
    """Run all tests"""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def run_quick_tests():
    """Run quick tests (unit tests only)"""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def run_auth_tests():
    """Run authentication tests"""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/test_auth.py", "-v"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def run_mcp_tests():
    """Run MCP tests"""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/integration/test_mcp_server_modern.py", "-v"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run TickTick MCP v2 tests")
    parser.add_argument(
        "type",
        choices=["unit", "integration", "e2e", "all", "quick", "auth", "mcp"],
        help="Type of tests to run",
    )

    args = parser.parse_args()

    test_functions = {
        "unit": run_unit_tests,
        "integration": run_integration_tests,
        "e2e": run_e2e_tests,
        "all": run_all_tests,
        "quick": run_quick_tests,
        "auth": run_auth_tests,
        "mcp": run_mcp_tests,
    }

    if args.type not in test_functions:
        sys.exit(1)

    success = test_functions[args.type]()

    if success:
        pass
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
