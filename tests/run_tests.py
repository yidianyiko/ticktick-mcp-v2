#!/usr/bin/env python3
"""
Test runner for TickTick MCP v2
"""

import subprocess
import sys
import argparse


def run_unit_tests():
    """Run unit tests"""
    print("🧪 Running unit tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/", "-v"], capture_output=True, text=True
    )
    return result.returncode == 0


def run_integration_tests():
    """Run integration tests"""
    print("🔗 Running integration tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/integration/", "-v"], capture_output=True, text=True
    )
    return result.returncode == 0


def run_e2e_tests():
    """Run end-to-end tests"""
    print("🌐 Running end-to-end tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/e2e/", "-v"], capture_output=True, text=True
    )
    return result.returncode == 0


def run_all_tests():
    """Run all tests"""
    print("🚀 Running all tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-v"], capture_output=True, text=True
    )
    return result.returncode == 0


def run_quick_tests():
    """Run quick tests (unit tests only)"""
    print("⚡ Running quick tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def run_auth_tests():
    """Run authentication tests"""
    print("🔐 Running authentication tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/test_auth.py", "-v"], capture_output=True, text=True
    )
    return result.returncode == 0


def run_mcp_tests():
    """Run MCP tests"""
    print("🔧 Running MCP tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/integration/test_mcp_server_modern.py", "-v"],
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
        print(f"❌ Unknown test type: {args.type}")
        sys.exit(1)

    success = test_functions[args.type]()

    if success:
        print("✅ Tests passed!")
    else:
        print("❌ Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
