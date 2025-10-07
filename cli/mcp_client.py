import sys
import os
import asyncio
import json
from pydantic import AnyUrl
from typing import Optional, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
    ):
        self._command = command
        self._args = args
        self._env = env or {}
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

        # Set default environment variables if not provided
        if (
            "MCP_DISCORD_DB_PATH" not in self._env
            and "MCP_DISCORD_DB_PATH" in os.environ
        ):
            self._env["MCP_DISCORD_DB_PATH"] = os.environ["MCP_DISCORD_DB_PATH"]

    async def connect(self):
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        _stdio, _write = stdio_transport
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(_stdio, _write)
        )
        await self._session.initialize()

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized or cache not populated. Call connect_to_server first."
            )
        return self._session

    async def list_tools(self) -> list[types.Tool]:
        result = await self.session().list_tools()
        if result is None:
            raise RuntimeError("Failed to retrieve tools from the MCP server.")
        return result.tools

    async def call_tool(
        self, tool_name: str, tool_input: dict
    ) -> types.CallToolResult | None:
        return await self.session().call_tool(
            tool_name,
            tool_input,
        )

    async def list_prompts(self) -> list[types.Prompt]:
        result = await self.session().list_prompts()
        if result is None:
            raise RuntimeError("Failed to retrieve prompts from the MCP server.")
        return result.prompts

    async def get_prompt(self, prompt_name, args: dict[str, str]):
        result = await self.session().get_prompt(prompt_name, args)
        if result is None:
            raise RuntimeError(
                f"Failed to retrieve prompt '{prompt_name}' from the MCP server."
            )
        return result.messages

    async def read_resource(self, uri: str) -> Any:
        result = await self.session().read_resource(AnyUrl(uri))
        resource = result.contents[0]

        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)

            return resource.text

    async def cleanup(self):
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()


# For testing
async def main():
    # Set up environment variables for testing
    env = {}

    # Use environment variable for database path if provided
    db_path = os.getenv("MCP_DISCORD_DB_PATH")
    if db_path:
        env["MCP_DISCORD_DB_PATH"] = db_path

    async with MCPClient(
        # If using Python without UV, update command to 'python' and remove "run" from args.
        command="uv",
        args=["run", "python", "-m", "discord_mcp"],
        env=env,
    ) as _client:
        # List available tools
        tools = await _client.list_tools()
        print("Available tools:", [tool.name for tool in tools])

        # Get bot status
        status = await _client.call_tool("discord_bot_status", {})
        print("Bot status:", status)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.get_event_loop().run_until_complete(main())
