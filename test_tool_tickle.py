#!/usr/bin/env python3
"""
Simple test for the tool tickle functionality.
This tests the core logic without requiring an actual MCP server.
"""

import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcpeek.discovery import DiscoveryEngine
from mcpeek.formatters.base import ToolInfo
import re


def test_safe_tool_pattern():
    """Test that the regex pattern correctly identifies safe tools."""
    pattern = DiscoveryEngine.SAFE_TOOL_PATTERN
    
    # Tools that should match (safe)
    safe_tools = [
        "list_files",
        "get_status", 
        "help_command",
        "list_users",
        "show_status",
        "help",
        "status",
        "list",
        "filesystem_list",
        "system_status_check",
        "get_help_info"
    ]
    
    # Tools that should NOT match (potentially unsafe)
    unsafe_tools = [
        "delete_file",
        "create_user", 
        "execute_command",
        "write_data",
        "update_config",
        "remove_entry",
        "modify_settings"
    ]
    
    print("Testing safe tool pattern matching...")
    
    # Test safe tools
    for tool in safe_tools:
        if pattern.match(tool):
            print(f"✓ '{tool}' correctly identified as safe")
        else:
            print(f"✗ '{tool}' incorrectly identified as unsafe")
            return False
    
    # Test unsafe tools  
    for tool in unsafe_tools:
        if not pattern.match(tool):
            print(f"✓ '{tool}' correctly identified as unsafe")
        else:
            print(f"✗ '{tool}' incorrectly identified as safe")
            return False
    
    return True


def test_filter_safe_tools():
    """Test the filter_safe_tools method."""
    # Create mock discovery engine
    class MockClient:
        pass
    
    discovery = DiscoveryEngine(MockClient(), verbosity=0, tool_tickle=True)
    
    # Create test tools
    test_tools = [
        ToolInfo(name="list_files", description="List files"),
        ToolInfo(name="delete_file", description="Delete a file"),
        ToolInfo(name="get_status", description="Get system status"),
        ToolInfo(name="create_user", description="Create new user"),
        ToolInfo(name="help_command", description="Show help"),
    ]
    
    # Filter safe tools
    safe_tools = discovery.filter_safe_tools(test_tools)
    safe_names = [tool.name for tool in safe_tools]
    
    expected_safe = ["list_files", "get_status", "help_command"]
    
    print("\nTesting tool filtering...")
    print(f"Input tools: {[tool.name for tool in test_tools]}")
    print(f"Filtered safe tools: {safe_names}")
    print(f"Expected safe tools: {expected_safe}")
    
    if set(safe_names) == set(expected_safe):
        print("✓ Tool filtering works correctly")
        return True
    else:
        print("✗ Tool filtering failed")
        return False


def test_cli_argument_validation():
    """Test CLI argument validation logic."""
    from mcpeek.cli import MCPeekCLI
    import argparse
    
    cli = MCPeekCLI()
    
    # Test that tool-tickle requires discover
    print("\nTesting CLI validation...")
    
    # Create a mock namespace
    args = argparse.Namespace()
    args.endpoint = "http://test"
    args.discover = False
    args.tool_tickle = True
    args.tool = None
    args.resource = None
    args.prompt = None
    args.stdin = False
    args.input = None
    args.verbosity = 1
    
    try:
        cli.validate_arguments(args)
        print("✗ CLI validation failed - should have raised ValidationError")
        return False
    except Exception as e:
        if "tool-tickle requires --discover mode" in str(e):
            print("✓ CLI validation correctly requires --discover for --tool-tickle")
            return True
        else:
            print(f"✗ CLI validation failed with unexpected error: {e}")
            return False


def main():
    """Run all tests."""
    print("Running Tool Tickle Feature Tests")
    print("=" * 50)
    
    tests = [
        test_safe_tool_pattern,
        test_filter_safe_tools,
        test_cli_argument_validation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✓ {test.__name__} PASSED\n")
            else:
                failed += 1
                print(f"✗ {test.__name__} FAILED\n")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} FAILED with exception: {e}\n")
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())