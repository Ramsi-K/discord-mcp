# MCP Discord

A Discord MCP (Model Context Protocol) server for AI-assisted Discord server management.

## Overview

This project implements a Discord MCP server that provides tools for AI assistants like Claude to interact with Discord servers. It includes:

- MCP server with Discord-specific tools
- Simple Discord bot for testing
- SQLite database for local storage

## Getting Started

### Prerequisites

- Python 3.10 or higher
- UV package manager (`pip install uv`)
- Discord bot token (create one at [Discord Developer Portal](https://discord.com/developers/applications))

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/mcp-discord.git
   cd mcp-discord
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   uv venv
   uv pip install -e .
   ```

3. Set up your Discord bot token:

   ```bash
   # On Windows
   set DISCORD_TOKEN=your_token_here

   # On Linux/macOS
   export DISCORD_TOKEN=your_token_here
   ```

### Running the MCP Server

Run the MCP server:

```bash
uv run mcp_server/server.py
```

### Running the Discord Bot

Run the Discord bot in a separate terminal:

```bash
uv run bot/bot.py
```

### Testing with the Client

Test the MCP server with the test client:

```bash
uv run client.py
```

## Project Structure

```
mcp-discord/
├── mcp_server/         # MCP server implementation
│   ├── __init__.py
│   ├── server.py       # Main FastMCP server
│   └── tools/          # Tool implementations
│       ├── __init__.py
│       └── message_tools.py  # Simple message tools
├── bot/                # Discord bot implementation
│   ├── __init__.py
│   └── bot.py          # Simple Discord bot
├── client.py           # Test client
├── pyproject.toml      # Project configuration
└── README.md           # Project documentation
```

## Available Tools

Currently implemented tools:

- `discord_send_message`: Send a message to a Discord channel
- `discord_get_channel_info`: Get information about a Discord channel

## Connecting to Kiro IDE

To use this MCP server with Kiro IDE, add the following to your `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "discord-tools": {
      "command": "uv",
      "args": ["run", "path/to/mcp-discord/mcp_server/server.py"],
      "disabled": false
    }
  }
}
```

## Development

### Adding New Tools

To add new tools, create a new file in the `mcp_server/tools/` directory and register your tools with the MCP server.

Example:

```python
async def register_my_tools(mcp: FastMCP):
    @mcp.tool(name="my_tool")
    async def my_tool(param: str, *, ctx: Context):
        return {"result": f"Processed {param}"}
```

Then import and register your tools in `mcp_server/server.py`.

### Running Tests

```bash
uv pip install -e ".[dev]"
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# MCP Chat

MCP Chat is a command-line interface application that enables interactive chat capabilities with AI models through the Anthropic API. The application supports document retrieval, command-based prompts, and extensible tool integrations via the MCP (Model Control Protocol) architecture.

## Prerequisites

- Python 3.9+
- Anthropic API Key

## Setup

### Step 1: Configure the environment variables

1. Create or edit the `.env` file in the project root and verify that the following variables are set correctly:

```
ANTHROPIC_API_KEY=""  # Enter your Anthropic API secret key
```

### Step 2: Install dependencies

#### Option 1: Setup with uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

1. Install uv, if not already installed:

```bash
pip install uv
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/Scripts/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
uv pip install -e .
```

4. Run the project

```bash
uv run main.py
```

#### Option 2: Setup without uv

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install anthropic python-dotenv prompt-toolkit "mcp[cli]==1.8.0"
```

3. Run the project

```bash
python main.py
```

## Usage

### Basic Interaction

Simply type your message and press Enter to chat with the model.

### Document Retrieval

Use the @ symbol followed by a document ID to include document content in your query:

```
> Tell me about @deposition.md
```

### Commands

Use the / prefix to execute commands defined in the MCP server:

```
> /summarize deposition.md
```

Commands will auto-complete when you press Tab.

## Development

### Adding New Documents

Edit the `mcp_server.py` file to add new documents to the `docs` dictionary.

### Implementing MCP Features

To fully implement the MCP features:

1. Complete the TODOs in `mcp_server.py`
2. Implement the missing functionality in `mcp_client.py`

### Linting and Typing Check

There are no lint or type checks implemented.
