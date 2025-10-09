#!/usr/bin/env python3
"""
Development script for Discord MCP server
Use this for development, testing, and running MCP inspector
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))


def run_mcp_inspector():
    """Run MCP inspector for development"""
    print("🔍 Starting MCP Inspector for Discord MCP")
    print("This will start the MCP server and inspector for development")

    # Run the MCP server with inspector
    os.system("python -m src.discord_mcp.server")


def run_server_directly():
    """Run the server directly for testing"""
    print("🚀 Starting Discord MCP Server directly")
    from src.discord_mcp.server import main

    asyncio.run(main())


def run_tests():
    """Run all tests"""
    print("🧪 Running Discord MCP tests")
    test_files = [
        "test_simple_real.py",
        "test_timing_issue.py",
        "debug_guilds.py",
    ]

    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n▶️ Running {test_file}...")
            os.system(f"python {test_file}")


def show_help():
    """Show available commands"""
    print("🛠️  Discord MCP Development Script")
    print("=" * 50)
    print("Available commands:")
    print("  python dev.py inspector  - Run MCP inspector")
    print("  python dev.py server     - Run server directly")
    print("  python dev.py test       - Run tests")
    print("  python dev.py help       - Show this help")
    print("\nFor production use:")
    print("  uvx discord-mcp@latest   - Run via uvx")
    print("  discord-mcp              - Run installed package")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "inspector":
        run_mcp_inspector()
    elif command == "server":
        run_server_directly()
    elif command == "test":
        run_tests()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)
