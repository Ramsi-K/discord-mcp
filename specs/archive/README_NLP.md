# Natural Language Command Processor

The Natural Language Command Processor (NLP) allows users to interact with Discord servers using natural language rather than rigid command formats.

## Features

- Intent detection for common Discord operations
- Entity extraction for servers, channels, roles, and messages
- Context-aware entity resolution
- Ambiguity detection and handling
- Integration with the Server Registry

## Usage

### Processing Commands

```python
from mcp_server.nlp_processor import NLPProcessor

# Create processor with registry
processor = NLPProcessor(registry)

# Process a command
result = await processor.process_command("user_id", "Send a message in general saying Hello!")

# Check the result
print(f"Intent: {result['intent']}")
print(f"Entities: {result['entities']}")
print(f"Resolved: {result['resolved']}")
print(f"Ambiguous: {result['ambiguous']}")
```

### Executing Commands

The `nlp_execute_command` tool in the MCP server can be used to execute natural language commands:

```json
{
  "name": "nlp_execute_command",
  "arguments": {
    "command": "Send a message in general saying Hello from NLP!",
    "user_id": "user123"
  }
}
```

## Supported Intents

- `send_message`: Send a message to a channel
- `get_info`: Get information about a server, channel, or role
- `list_channels`: List channels in a server
- `list_roles`: List roles in a server

## Example Commands

- "Send a message in the general channel saying Hello world!"
- "List all channels in the coding server"
- "Show me the roles in the gaming server"
- "What channels are available in the book club server?"

## Ambiguity Resolution

When a command contains ambiguous references (e.g., multiple channels with similar names), the processor will return the ambiguous entities in the `ambiguous` field of the result. The caller can then prompt the user to clarify which entity they meant.

## Context Tracking

The processor uses the Server Registry's context tracking to maintain conversation context. This allows users to refer to entities mentioned in previous commands without specifying them again.

## Extending the Processor

To add support for new intents:

1. Add patterns to the `intents` dictionary in the `__init__` method
2. Update the `_extract_entities` method to handle entity extraction for the new intent
3. Add execution logic to the `nlp_execute_command` tool in server.py
