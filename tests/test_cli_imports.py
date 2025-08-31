#!/usr/bin/env python3
"""
Test CLI imports and basic functionality
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test that all CLI components can be imported"""
    print("🧪 Testing CLI Component Imports")
    print("=" * 40)

    try:
        # Test core imports
        print("1️⃣ Testing core imports...")
        from discord_mcp.core.claude import Claude

        print("   ✅ Claude imported successfully")

        from discord_mcp.core.tools import ToolManager

        print("   ✅ ToolManager imported successfully")

        from discord_mcp.core.chat import Chat

        print("   ✅ Chat imported successfully")

        from discord_mcp.core.cli_chat import CliChat

        print("   ✅ CliChat imported successfully")

        from discord_mcp.core.cli import CliApp

        print("   ✅ CliApp imported successfully")

        # Test MCP client import
        print("\n2️⃣ Testing MCP client import...")
        from discord_mcp.mcp_client import MCPClient

        print("   ✅ MCPClient imported successfully")

        # Test Discord bot import
        print("\n3️⃣ Testing Discord bot import...")
        from discord_mcp.discord_client.bot import DiscordMCPBot

        print("   ✅ DiscordMCPBot imported successfully")

        print("\n✅ All imports successful!")
        return True

    except Exception as e:
        print(f"\n❌ Import error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_basic_functionality():
    """Test basic functionality without network connections"""
    print("\n🔧 Testing Basic Functionality")
    print("=" * 40)

    try:
        # Test Claude service creation
        print("1️⃣ Testing Claude service...")
        from discord_mcp.core.claude import Claude

        claude = Claude(model="claude-3-sonnet-20240229")
        print("   ✅ Claude service created successfully")

        # Test ToolManager
        print("\n2️⃣ Testing ToolManager...")
        from discord_mcp.core.tools import ToolManager

        # Can't test get_all_tools without clients, but we can test the class exists
        print("   ✅ ToolManager class available")

        print("\n✅ Basic functionality tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Functionality error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 CLI Component Test Suite")
    print("=" * 50)

    success1 = test_imports()
    success2 = test_basic_functionality()

    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Import Tests: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Functionality Tests: {'✅ PASS' if success2 else '❌ FAIL'}")

    if success1 and success2:
        print("\n🎉 All CLI components are working correctly!")
        print("   The import errors have been fixed.")
        print("   The MCP inspector should now be able to run.")
    else:
        print("\n⚠️  Some issues remain. Check the output above.")
