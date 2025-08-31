#!/usr/bin/env python3
"""Test script to verify the MCP entry point restructure is working."""

import subprocess
import sys
import os
import time


def test_mcp_server_entry():
    """Test that python -m discord_mcp starts the MCP server."""
    print("🧪 Testing MCP Server Entry Point...")
    try:
        # Start the server and kill it after 2 seconds
        proc = subprocess.Popen(
            [sys.executable, "-m", "discord_mcp"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait a bit for startup
        time.sleep(2)
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=5)

        if "Starting Discord MCP Server" in stderr:
            print("   ✅ MCP server entry point works")
            return True
        else:
            print(f"   ❌ MCP server failed: {stderr[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing MCP server: {e}")
        return False


def test_file_structure():
    """Test that files are in the right places."""
    print("🧪 Testing File Structure...")

    required_files = [
        "src/discord_mcp/__main__.py",
        "cli/main.py",
        "cli/claude.py",
        "cli/chat.py",
        "cli/cli_chat.py",
        "cli/cli.py",
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print(f"   ❌ Missing files: {missing_files}")
        return False
    else:
        print("   ✅ All required files exist")
        return True


def test_imports():
    """Test that imports work correctly."""
    print("🧪 Testing Import Structure...")

    try:
        # Test MCP server import
        import src.discord_mcp.server

        print("   ✅ MCP server imports work")

        # Test __main__ import
        import src.discord_mcp.__main__

        print("   ✅ __main__ module imports work")

        return True
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 MCP Entry Point Restructure Verification")
    print("=" * 50)

    tests = [
        test_file_structure,
        test_imports,
        test_mcp_server_entry,
    ]

    results = []
    for test in tests:
        results.append(test())
        print()

    print("📊 Test Summary:")
    print(f"   Passed: {sum(results)}/{len(results)}")

    if all(results):
        print("🎉 All tests passed! MCP entry point restructure is working.")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
