#!/usr/bin/env python3
"""
Test timing issues with guild loading
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from discord_mcp.server import discord_bot_status, registry_update


async def test_guild_timing():
    """Test when guilds become available"""
    print("⏰ Testing Guild Loading Timing")
    print("=" * 50)

    # Test 1: Initial status
    print("\n1️⃣ Initial bot status...")
    status = await discord_bot_status()
    print(f"   {status}")

    # Test 2: Start bot
    print("\n2️⃣ Starting bot and updating registry...")
    update_result = await registry_update()
    print(f"   {update_result}")

    # Test 3: Check status immediately after startup
    print("\n3️⃣ Status immediately after startup...")
    status = await discord_bot_status()
    print(f"   {status}")

    # Test 4: Wait and check multiple times
    for i in range(5):
        await asyncio.sleep(2)
        print(f"\n4️⃣.{i+1} Status after {(i+1)*2} seconds...")
        status = await discord_bot_status()
        print(f"   Guild count: {status.get('guild_count', 'N/A')}")
        if status.get("guilds"):
            print(f"   Guilds: {[g['name'] for g in status['guilds']]}")
        else:
            print(f"   Guilds: None/Empty")

        # If we found guilds, we can stop
        if status.get("guild_count", 0) > 0:
            print(f"   ✅ Found {status['guild_count']} guilds!")
            break
    else:
        print(f"   ❌ Still no guilds after 10 seconds")

    # Test 5: Final comprehensive status
    print(f"\n5️⃣ Final comprehensive status...")
    final_status = await discord_bot_status()
    print(f"   {final_status}")


if __name__ == "__main__":
    asyncio.run(test_guild_timing())
