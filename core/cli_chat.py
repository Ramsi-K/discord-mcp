from typing import List, Tuple
from mcp.types import Prompt, PromptMessage
from anthropic.types import MessageParam

from core.chat import Chat
from core.claude import Claude
from mcp_client import MCPClient


class CliChat(Chat):
    def __init__(
        self,
        discord_client: MCPClient,
        clients: dict[str, MCPClient],
        claude_service: Claude,
    ):
        super().__init__(clients=clients, claude_service=claude_service)

        self.discord_client: MCPClient = discord_client

    async def list_prompts(self) -> list[Prompt]:
        # Try to get prompts from the discord_client, but handle if there are none
        try:
            return await self.discord_client.list_prompts()
        except Exception as e:
            print(f"Warning: Could not list prompts: {e}")
            return []

    async def list_docs_ids(self) -> list[str]:
        # This method is from the old project and may not be applicable
        # Try to get documents, but return empty list if not available
        # try:
        #     return await self.discord_client.read_resource("docs://documents")
        # except Exception as e:
        #     print(f"Warning: Could not list documents: {e}")
        return []

    async def get_doc_content(self, doc_id: str) -> str:
        # This method is from the old project and may not be applicable
        # Try to get document content, but return empty string if not available
        # try:
        #     return await self.discord_client.read_resource(
        #         f"docs://documents/{doc_id}"
        #     )
        # except Exception as e:
        #     print(f"Warning: Could not get document content: {e}")
        return ""

    async def get_prompt(
        self, command: str, doc_id: str
    ) -> list[PromptMessage]:
        # This method is from the old project and may not be applicable
        # Try to get prompt, but handle if not available
        try:
            return await self.discord_client.get_prompt(
                command, {"doc_id": doc_id}
            )
        except Exception as e:
            print(f"Warning: Could not get prompt: {e}")
            return []

    async def _extract_resources(self, query: str) -> str:
        # mentions = [word[1:] for word in query.split() if word.startswith("@")]

        # doc_ids = await self.list_docs_ids()
        # mentioned_docs: list[Tuple[str, str]] = []

        # for doc_id in doc_ids:
        #     if doc_id in mentions:
        #         content = await self.get_doc_content(doc_id)
        #         mentioned_docs.append((doc_id, content))

        # return "".join(
        #     f'\n<document id="{doc_id}">\n{content}\n</document>\n'
        #     for doc_id, content in mentioned_docs
        # )
        return ""

    async def _process_command(self, query: str) -> bool:
        if not query.startswith("/"):
            return False

        words = query.split()
        command = words[0].replace("/", "")

        try:

            messages = await self.discord_client.get_prompt(
                command, {"doc_id": words[1]}
            )

            self.messages += convert_prompt_messages_to_message_params(
                messages
            )
            return True
        except Exception as e:
            print(f"Warning: Could not process command: {e}")
            return False

    async def _process_query(self, query: str):
        # Check if this is a command first
        if await self._process_command(query):
            return

        # # Try to extract resources (keeping for compatibility)
        added_resources = await self._extract_resources(query)

        # Check if this is a Discord-specific command
        discord_commands = {
            "send": "discord_send_message",
            "channel": "discord_get_channel_info",
        }

        words = query.split()
        if len(words) >= 2 and words[0].lower() in discord_commands:
            command = discord_commands[words[0].lower()]

            # Handle discord_send_message
            if command == "discord_send_message" and len(words) >= 3:
                channel_id = words[1]
                message = " ".join(words[2:])

                print(
                    f"Processing send command: channel_id={channel_id}, message={message}"
                )

                # First try to use the direct method on the Discord bot
                discord_bot = self.clients.get("discord_bot")
                if discord_bot and hasattr(discord_bot, "send_direct_message"):
                    print(f"Using direct method on Discord bot")
                    try:
                        result = await discord_bot.send_direct_message(
                            channel_id, message, mention_everyone=False
                        )
                        print(f"Direct message result: {result}")

                        if result.get("success", False):
                            # Add the result to the conversation
                            self.messages.append(
                                {
                                    "role": "user",
                                    "content": f"Send message '{message}' to channel {channel_id}",
                                }
                            )
                            self.messages.append(
                                {
                                    "role": "assistant",
                                    "content": f"Message sent successfully to channel {channel_id}.",
                                }
                            )
                            return
                        else:
                            print(
                                f"Direct message failed: {result.get('error', 'Unknown error')}"
                            )
                    except Exception as e:
                        print(f"Error sending direct message: {e}")
                        import traceback

                        print(f"Traceback: {traceback.format_exc()}")

                # If direct method failed or not available, try using the MCP tools
                print(f"Available clients: {list(self.clients.keys())}")
                for client_name, client in self.clients.items():
                    print(
                        f"Trying client: {client_name}, type: {type(client)}"
                    )
                    try:
                        if not hasattr(client, "list_tools"):
                            print(
                                f"Client {client_name} doesn't have list_tools method, skipping"
                            )
                            continue

                        print(f"Getting tools for client {client_name}")
                        tools = await client.list_tools()
                        tool_names = [tool.name for tool in tools]
                        print(
                            f"Available tools for client {client_name}: {tool_names}"
                        )

                        if command in tool_names:
                            print(
                                f"Found tool {command} in client {client_name}, calling it"
                            )
                            result = await client.call_tool(
                                command,
                                {
                                    "channel_id": channel_id,
                                    "message": message,
                                    "mention_everyone": False,
                                },
                            )
                            print(f"Tool call result: {result}")

                            # Add the result to the conversation
                            self.messages.append(
                                {
                                    "role": "user",
                                    "content": f"Send message '{message}' to channel {channel_id}",
                                }
                            )
                            self.messages.append(
                                {
                                    "role": "assistant",
                                    "content": f"Message sent successfully to channel {channel_id}.",
                                }
                            )
                            return
                    except Exception as e:
                        print(
                            f"Error calling Discord tool with client {client_name}: {e}"
                        )
                        import traceback

                        print(f"Traceback: {traceback.format_exc()}")

            # Handle discord_get_channel_info
            elif command == "discord_get_channel_info" and len(words) >= 2:
                channel_id = words[1]

                print(
                    f"Processing channel info command: channel_id={channel_id}"
                )

                # First try to use the direct method on the Discord bot
                discord_bot = self.clients.get("discord_bot")
                if discord_bot and hasattr(discord_bot, "get_channel_info"):
                    print(
                        f"Using direct method on Discord bot for channel info"
                    )
                    try:
                        result = await discord_bot.get_channel_info(channel_id)
                        print(f"Direct channel info result: {result}")

                        if result.get("success", False):
                            # Format the channel info nicely
                            channel_info = (
                                f"Channel ID: {result['id']}\n"
                                f"Name: {result['name']}\n"
                                f"Type: {result['type']}\n"
                                f"Topic: {result['topic'] or 'No topic'}\n"
                                f"NSFW: {result['nsfw']}\n"
                                f"Position: {result['position']}\n"
                                f"Created at: {result['created_at']}"
                            )

                            # Add the result to the conversation
                            self.messages.append(
                                {
                                    "role": "user",
                                    "content": f"Get information about channel {channel_id}",
                                }
                            )
                            self.messages.append(
                                {
                                    "role": "assistant",
                                    "content": f"Channel information:\n{channel_info}",
                                }
                            )
                            return
                        else:
                            print(
                                f"Direct channel info failed: {result.get('error', 'Unknown error')}"
                            )
                    except Exception as e:
                        print(f"Error getting channel info: {e}")
                        import traceback

                        print(f"Traceback: {traceback.format_exc()}")

                # If direct method failed or not available, try using the MCP tools
                print(f"Available clients: {list(self.clients.keys())}")
                for client_name, client in self.clients.items():
                    try:
                        if not hasattr(client, "list_tools"):
                            print(
                                f"Client {client_name} doesn't have list_tools method, skipping"
                            )
                            continue

                        print(f"Getting tools for client {client_name}")
                        tools = await client.list_tools()
                        tool_names = [tool.name for tool in tools]
                        print(
                            f"Available tools for client {client_name}: {tool_names}"
                        )

                        if command in tool_names:
                            print(
                                f"Found tool {command} in client {client_name}, calling it"
                            )
                            result = await client.call_tool(
                                command, {"channel_id": channel_id}
                            )
                            print(f"Tool call result: {result}")

                            # Extract the content from the result
                            content = "Channel information not available"
                            if hasattr(result, "content") and result.content:
                                content_items = [
                                    item.text
                                    for item in result.content
                                    if hasattr(item, "text")
                                ]
                                if content_items:
                                    content = "\n".join(content_items)

                            # Add the result to the conversation
                            self.messages.append(
                                {
                                    "role": "user",
                                    "content": f"Get information about channel {channel_id}",
                                }
                            )
                            self.messages.append(
                                {
                                    "role": "assistant",
                                    "content": f"Channel information:\n{content}",
                                }
                            )
                            return
                    except Exception as e:
                        print(f"Error calling Discord tool: {e}")
                        import traceback

                        print(f"Traceback: {traceback.format_exc()}")

        # If not a Discord command, process as a regular query
        prompt = f"""
        The user has a question:
        <query>
        {query}
        </query>

        The following context may be useful in answering their question:
        <context>
        {added_resources}
        </context>

        Note: You have access to Discord tools that can be used to interact with Discord:
        - discord_send_message: Send a message to a Discord channel
        - discord_get_channel_info: Get information about a Discord channel

        If the user is asking to send a message or get channel information, suggest using
        the appropriate command format:
        - "send [channel_id] [message]" to send a message
        - "channel [channel_id]" to get channel information

        Answer the user's question directly and concisely. Start with the exact information they need.
        """

        self.messages.append({"role": "user", "content": prompt})


def convert_prompt_message_to_message_param(
    prompt_message: "PromptMessage",
) -> MessageParam:
    role = "user" if prompt_message.role == "user" else "assistant"

    content = prompt_message.content

    # Check if content is a dict-like object with a "type" field
    if isinstance(content, dict) or hasattr(content, "__dict__"):
        content_type = (
            content.get("type", None)
            if isinstance(content, dict)
            else getattr(content, "type", None)
        )
        if content_type == "text":
            content_text = (
                content.get("text", "")
                if isinstance(content, dict)
                else getattr(content, "text", "")
            )
            return {"role": role, "content": content_text}

    if isinstance(content, list):
        text_blocks = []
        for item in content:
            # Check if item is a dict-like object with a "type" field
            if isinstance(item, dict) or hasattr(item, "__dict__"):
                item_type = (
                    item.get("type", None)
                    if isinstance(item, dict)
                    else getattr(item, "type", None)
                )
                if item_type == "text":
                    item_text = (
                        item.get("text", "")
                        if isinstance(item, dict)
                        else getattr(item, "text", "")
                    )
                    text_blocks.append({"type": "text", "text": item_text})

        if text_blocks:
            return {"role": role, "content": text_blocks}

    return {"role": role, "content": ""}


def convert_prompt_messages_to_message_params(
    prompt_messages: List[PromptMessage],
) -> List[MessageParam]:
    return [
        convert_prompt_message_to_message_param(msg) for msg in prompt_messages
    ]
