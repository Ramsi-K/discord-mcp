#!/usr/bin/env python3
"""Discord MCP Server - Legacy Entry Point

This file is kept for backward compatibility.
The main server implementation has moved to src/discord_mcp/server.py

For CLI functionality, use cli/main.py instead.
"""

import warnings
from src.discord_mcp.server import main

if __name__ == "__main__":
    warnings.warn(
        "Using main.py is deprecated. Use 'python -m discord_mcp' for MCP server or 'python cli/main.py' for CLI functionality.",
        DeprecationWarning,
        stacklevel=2,
    )
    main()
