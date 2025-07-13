# Discord MCP Server: Complete Implementation Guide

## Architecture Overview

```
Discord User Message
    ↓
Discord Bot (MCP Client)
    ↓ (HTTP/WebSocket)
MCP Server (FastAPI)
    ↓
Tool Registry & Context Manager
    ↓
Claude API (with tools & context)
    ↓
Response Pipeline
    ↓
Discord Message Response
```

## Phase 1: MCP Server Foundation

### 1.1 Project Structure

```
discord-mcp-server/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py        # MCP server implementation
│   │   ├── protocol.py      # MCP protocol definitions
│   │   └── tools.py         # Tool registry
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py      # Database models
│   │   └── schemas.py       # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── claude.py        # Claude API integration
│   │   ├── memory.py        # Conversation memory
│   │   └── discord_tools.py # Discord-specific tools
│   └── utils/
│       ├── __init__.py
│       └── config.py        # Configuration
├── discord_bot/
│   ├── __init__.py
│   ├── bot.py              # Discord bot main
│   └── cogs/
│       ├── __init__.py
│       └── mcp_cog.py      # MCP integration cog
├── requirements.txt
├── docker-compose.yml
└── README.md
```

### 1.2 Core Dependencies

```
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
discord.py==2.3.2
anthropic==0.7.8
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.0
redis==5.0.1
pydantic==2.5.0
python-multipart==0.0.6
websockets==12.0
```

### 1.3 MCP Protocol Implementation

```python
# app/mcp/protocol.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from enum import Enum

class MCPMessageType(str, Enum):
    INITIALIZE = "initialize"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    CONTEXT_UPDATE = "context_update"

class MCPMessage(BaseModel):
    type: MCPMessageType
    id: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class MCPTool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: str  # Function name to call

class MCPContext(BaseModel):
    session_id: str
    user_id: str
    channel_id: str
    guild_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = []
    user_preferences: Dict[str, Any] = {}
    active_tools: List[str] = []
```

### 1.4 MCP Server Core

```python
# app/mcp/server.py
import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from fastapi import WebSocket, HTTPException
from .protocol import MCPMessage, MCPTool, MCPContext, MCPMessageType
from ..services.claude import ClaudeService
from ..services.memory import MemoryService
from ..services.discord_tools import DiscordToolsService

class MCPServer:
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        self.active_sessions: Dict[str, MCPContext] = {}
        self.claude_service = ClaudeService()
        self.memory_service = MemoryService()
        self.discord_tools = DiscordToolsService()

    async def initialize(self):
        """Initialize MCP server with Discord tools"""
        await self.discord_tools.register_tools(self)

    def register_tool(self, tool: MCPTool, handler: Callable):
        """Register a tool with its handler"""
        self.tools[tool.name] = tool
        self.tool_handlers[tool.name] = handler

    async def handle_message(self, message: MCPMessage, websocket: WebSocket = None) -> Dict[str, Any]:
        """Main message handler for MCP protocol"""
        try:
            if message.type == MCPMessageType.INITIALIZE:
                return await self._handle_initialize(message)
            elif message.type == MCPMessageType.TOOL_CALL:
                return await self._handle_tool_call(message)
            elif message.type == MCPMessageType.CONTEXT_UPDATE:
                return await self._handle_context_update(message)
            else:
                raise ValueError(f"Unknown message type: {message.type}")
        except Exception as e:
            return {"error": str(e), "message_id": message.id}

    async def _handle_initialize(self, message: MCPMessage) -> Dict[str, Any]:
        """Handle session initialization"""
        session_data = message.data
        context = MCPContext(
            session_id=session_data["session_id"],
            user_id=session_data["user_id"],
            channel_id=session_data["channel_id"],
            guild_id=session_data.get("guild_id")
        )

        # Load conversation history
        history = await self.memory_service.load_conversation_history(
            context.user_id, context.channel_id
        )
        context.conversation_history = history

        self.active_sessions[context.session_id] = context

        return {
            "session_id": context.session_id,
            "available_tools": [tool.name for tool in self.tools.values()],
            "context": context.dict()
        }

    async def _handle_tool_call(self, message: MCPMessage) -> Dict[str, Any]:
        """Handle tool execution"""
        tool_name = message.data["tool_name"]
        tool_args = message.data.get("arguments", {})
        session_id = message.data["session_id"]

        if tool_name not in self.tool_handlers:
            raise ValueError(f"Unknown tool: {tool_name}")

        context = self.active_sessions.get(session_id)
        if not context:
            raise ValueError(f"Session not found: {session_id}")

        # Execute tool
        handler = self.tool_handlers[tool_name]
        result = await handler(context, **tool_args)

        return {
            "tool_name": tool_name,
            "result": result,
            "session_id": session_id
        }

    async def process_discord_message(self, user_message: str, context: MCPContext) -> str:
        """Process a Discord message through Claude with MCP tools"""
        # Update conversation history
        context.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": asyncio.get_event_loop().time()
        })

        # Prepare tools for Claude
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters
            }
            for tool in self.tools.values()
        ]

        # Get Claude response
        response = await self.claude_service.get_response(
            messages=context.conversation_history,
            tools=available_tools,
            context=context
        )

        # Handle any tool calls in the response
        if response.get("tool_calls"):
            for tool_call in response["tool_calls"]:
                tool_result = await self._handle_tool_call(MCPMessage(
                    type=MCPMessageType.TOOL_CALL,
                    id=f"tool_{tool_call['id']}",
                    data={
                        "tool_name": tool_call["name"],
                        "arguments": tool_call["arguments"],
                        "session_id": context.session_id
                    }
                ))

                # Add tool result to context
                context.conversation_history.append({
                    "role": "tool",
                    "content": json.dumps(tool_result),
                    "tool_name": tool_call["name"]
                })

        # Get final response after tool calls
        final_response = response.get("content", "I encountered an error processing your request.")

        # Update conversation history
        context.conversation_history.append({
            "role": "assistant",
            "content": final_response,
            "timestamp": asyncio.get_event_loop().time()
        })

        # Save to persistent memory
        await self.memory_service.save_conversation_history(
            context.user_id, context.channel_id, context.conversation_history
        )

        return final_response
```

## Phase 2: Discord Bot Integration

### 2.1 Discord Bot Main

```python
# discord_bot/bot.py
import discord
from discord.ext import commands
import aiohttp
import asyncio
from typing import Dict, Any

class DiscordMCPBot(commands.Bot):
    def __init__(self, mcp_server_url: str):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(command_prefix='!', intents=intents)
        self.mcp_server_url = mcp_server_url
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id

    async def setup_hook(self):
        """Initialize bot and load cogs"""
        await self.load_extension('discord_bot.cogs.mcp_cog')

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def create_mcp_session(self, user_id: str, channel_id: str, guild_id: str = None) -> str:
        """Create new MCP session"""
        session_data = {
            "session_id": f"{user_id}_{channel_id}_{asyncio.get_event_loop().time()}",
            "user_id": user_id,
            "channel_id": channel_id,
            "guild_id": guild_id
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.mcp_server_url}/mcp/initialize",
                json=session_data
            ) as response:
                result = await response.json()
                return result["session_id"]

    async def send_to_mcp(self, session_id: str, message: str) -> str:
        """Send message to MCP server"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.mcp_server_url}/mcp/process",
                json={
                    "session_id": session_id,
                    "message": message
                }
            ) as response:
                result = await response.json()
                return result.get("response", "Error processing message")
```

### 2.2 MCP Integration Cog

```python
# discord_bot/cogs/mcp_cog.py
import discord
from discord.ext import commands
import asyncio

class MCPCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle incoming messages"""
        if message.author.bot:
            return

        # Check if message mentions the bot or is a DM
        if not (self.bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel)):
            return

        # Get or create session
        user_id = str(message.author.id)
        channel_id = str(message.channel.id)
        guild_id = str(message.guild.id) if message.guild else None

        session_key = f"{user_id}_{channel_id}"

        if session_key not in self.bot.user_sessions:
            session_id = await self.bot.create_mcp_session(user_id, channel_id, guild_id)
            self.bot.user_sessions[session_key] = session_id

        # Send typing indicator
        async with message.channel.typing():
            # Process message through MCP
            response = await self.bot.send_to_mcp(
                self.bot.user_sessions[session_key],
                message.content
            )

            # Send response (split if too long)
            if len(response) > 2000:
                # Split into chunks
                chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(response)

    @commands.command(name="reset")
    async def reset_session(self, ctx):
        """Reset MCP session for user"""
        user_id = str(ctx.author.id)
        channel_id = str(ctx.channel.id)
        session_key = f"{user_id}_{channel_id}"

        if session_key in self.bot.user_sessions:
            del self.bot.user_sessions[session_key]

        await ctx.send("Session reset! Starting fresh conversation.")

    @commands.command(name="tools")
    async def list_tools(self, ctx):
        """List available MCP tools"""
        # This would query the MCP server for available tools
        embed = discord.Embed(
            title="Available Tools",
            description="Tools available through MCP server",
            color=discord.Color.blue()
        )

        # Add fields for each tool
        tools = [
            ("Discord User Lookup", "Get information about Discord users"),
            ("Channel Management", "Manage channel settings and permissions"),
            ("Message History", "Search and analyze message history"),
            ("Server Stats", "Get server statistics and insights")
        ]

        for name, description in tools:
            embed.add_field(name=name, value=description, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MCPCog(bot))
```

## Phase 3: Tool System Implementation

### 3.1 Discord-Specific Tools

```python
# app/services/discord_tools.py
from typing import Dict, Any, List
import discord
from ..mcp.protocol import MCPTool, MCPContext
from ..mcp.server import MCPServer

class DiscordToolsService:
    def __init__(self):
        self.discord_client = None  # Will be set by bot

    async def register_tools(self, mcp_server: MCPServer):
        """Register all Discord tools with MCP server"""

        # User lookup tool
        user_lookup_tool = MCPTool(
            name="discord_user_lookup",
            description="Get information about a Discord user",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Discord user ID"
                    }
                },
                "required": ["user_id"]
            },
            handler="handle_user_lookup"
        )
        mcp_server.register_tool(user_lookup_tool, self.handle_user_lookup)

        # Channel info tool
        channel_info_tool = MCPTool(
            name="discord_channel_info",
            description="Get information about a Discord channel",
            parameters={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Discord channel ID"
                    }
                },
                "required": ["channel_id"]
            },
            handler="handle_channel_info"
        )
        mcp_server.register_tool(channel_info_tool, self.handle_channel_info)

        # Message history tool
        message_history_tool = MCPTool(
            name="discord_message_history",
            description="Get recent message history from a channel",
            parameters={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Discord channel ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of messages to retrieve",
                        "default": 10
                    }
                },
                "required": ["channel_id"]
            },
            handler="handle_message_history"
        )
        mcp_server.register_tool(message_history_tool, self.handle_message_history)

        # Server stats tool
        server_stats_tool = MCPTool(
            name="discord_server_stats",
            description="Get statistics about a Discord server",
            parameters={
                "type": "object",
                "properties": {
                    "guild_id": {
                        "type": "string",
                        "description": "Discord guild ID"
                    }
                },
                "required": ["guild_id"]
            },
            handler="handle_server_stats"
        )
        mcp_server.register_tool(server_stats_tool, self.handle_server_stats)

    async def handle_user_lookup(self, context: MCPContext, user_id: str) -> Dict[str, Any]:
        """Handle user lookup tool call"""
        try:
            # This would use the Discord client to fetch user info
            # For now, return mock data
            return {
                "user_id": user_id,
                "username": f"User_{user_id}",
                "discriminator": "0001",
                "avatar": None,
                "bot": False,
                "created_at": "2023-01-01T00:00:00Z"
            }
        except Exception as e:
            return {"error": f"Failed to lookup user: {str(e)}"}

    async def handle_channel_info(self, context: MCPContext, channel_id: str) -> Dict[str, Any]:
        """Handle channel info tool call"""
        try:
            return {
                "channel_id": channel_id,
                "name": f"channel_{channel_id}",
                "type": "text",
                "guild_id": context.guild_id,
                "created_at": "2023-01-01T00:00:00Z"
            }
        except Exception as e:
            return {"error": f"Failed to get channel info: {str(e)}"}

    async def handle_message_history(self, context: MCPContext, channel_id: str, limit: int = 10) -> Dict[str, Any]:
        """Handle message history tool call"""
        try:
            # This would fetch actual message history
            return {
                "channel_id": channel_id,
                "messages": [
                    {
                        "id": f"msg_{i}",
                        "content": f"Message {i}",
                        "author": {"id": "123", "username": "TestUser"},
                        "timestamp": "2023-01-01T00:00:00Z"
                    }
                    for i in range(limit)
                ]
            }
        except Exception as e:
            return {"error": f"Failed to get message history: {str(e)}"}

    async def handle_server_stats(self, context: MCPContext, guild_id: str) -> Dict[str, Any]:
        """Handle server stats tool call"""
        try:
            return {
                "guild_id": guild_id,
                "name": f"Server_{guild_id}",
                "member_count": 1000,
                "channel_count": 50,
                "role_count": 10,
                "created_at": "2023-01-01T00:00:00Z"
            }
        except Exception as e:
            return {"error": f"Failed to get server stats: {str(e)}"}
```

## Phase 4: Memory & Context Management

### 4.1 Memory Service

```python
# app/services/memory.py
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..models.database import ConversationHistory, UserPreferences
from ..utils.database import get_db

class MemoryService:
    def __init__(self):
        self.memory_cache: Dict[str, List[Dict[str, Any]]] = {}

    async def load_conversation_history(self, user_id: str, channel_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Load conversation history from database"""
        cache_key = f"{user_id}_{channel_id}"

        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key][-limit:]

        # Load from database
        db = next(get_db())
        try:
            history_records = (
                db.query(ConversationHistory)
                .filter(
                    ConversationHistory.user_id == user_id,
                    ConversationHistory.channel_id == channel_id
                )
                .order_by(ConversationHistory.timestamp.desc())
                .limit(limit)
                .all()
            )

            history = []
            for record in reversed(history_records):
                history.append({
                    "role": record.role,
                    "content": record.content,
                    "timestamp": record.timestamp.timestamp(),
                    "metadata": json.loads(record.metadata) if record.metadata else {}
                })

            self.memory_cache[cache_key] = history
            return history

        finally:
            db.close()

    async def save_conversation_history(self, user_id: str, channel_id: str, history: List[Dict[str, Any]]):
        """Save conversation history to database"""
        cache_key = f"{user_id}_{channel_id}"
        self.memory_cache[cache_key] = history

        # Save recent messages to database
        db = next(get_db())
        try:
            # Only save new messages (last few in the history)
            for message in history[-5:]:  # Save last 5 messages
                existing = (
                    db.query(ConversationHistory)
                    .filter(
                        ConversationHistory.user_id == user_id,
                        ConversationHistory.channel_id == channel_id,
                        ConversationHistory.timestamp == message["timestamp"]
                    )
                    .first()
                )

                if not existing:
                    db.add(ConversationHistory(
                        user_id=user_id,
                        channel_id=channel_id,
                        role=message["role"],
                        content=message["content"],
                        timestamp=message["timestamp"],
                        metadata=json.dumps(message.get("metadata", {}))
                    ))

            db.commit()

        finally:
            db.close()

    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        db = next(get_db())
        try:
            prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
            if prefs:
                return json.loads(prefs.preferences)
            return {}
        finally:
            db.close()

    async def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Save user preferences"""
        db = next(get_db())
        try:
            prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
            if prefs:
                prefs.preferences = json.dumps(preferences)
            else:
                db.add(UserPreferences(
                    user_id=user_id,
                    preferences=json.dumps(preferences)
                ))
            db.commit()
        finally:
            db.close()
```

### 4.2 Database Models

```python
# app/models/database.py
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    channel_id = Column(String, index=True)
    role = Column(String)  # user, assistant, tool
    content = Column(Text)
    timestamp = Column(DateTime, default=func.now())
    metadata = Column(JSON)

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    preferences = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class MCPSessions(Base):
    __tablename__ = "mcp_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    channel_id = Column(String, index=True)
    guild_id = Column(String, index=True)
    created_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    session_data = Column(JSON)
```

## Phase 5: Production Deployment

### 5.1 FastAPI Main Application

```python
# app/main.py
from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .mcp.server import MCPServer
from .mcp.protocol import MCPMessage
from .utils.database import engine, Base
import asyncio

# Global MCP server instance
mcp_server = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global mcp_server
    Base.metadata.create_all(bind=engine)
    mcp_server = MCPServer()
    await mcp_server.initialize()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Discord MCP Server",
    description="Model-Context Protocol server for Discord integration",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/mcp/initialize")
async def initialize_session(session_data: dict):
    """Initialize MCP session"""
    message = MCPMessage(
        type="initialize",
        id=f"init_{session_data['session_id']}",
        data=session_data
    )
    result = await mcp_server.handle_message(message)
    return result

@app.post("/mcp/process")
async def process_message(request: dict):
    """Process message through MCP"""
    session_id = request["session_id"]
    message_content = request["message"]

    context = mcp_server.active_sessions.get(session_id)
    if not context:
        raise HTTPException(status_code=404, detail="Session not found")

    response = await mcp_server.process_discord_message(message_content, context)
    return {"response": response}

@app.websocket("/mcp/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time MCP communication"""
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            message = MCPMessage(**data)
            result = await mcp_server.handle_message(message, websocket)
            await websocket.send_json(result)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "active_sessions": len(mcp_server.active_sessions)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 5.2 Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# docker-compose.yml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/discord_mcp
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./app:/app/app
      - ./discord_bot:/app/discord_bot
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  discord-bot:
    build: .
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
      - MCP_SERVER_URL=http://mcp-server:8000
    depends_on:
      - mcp-server
    command: python -m discord_bot.bot

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=discord_mcp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 5.3 Claude API Integration

```python
# app/services/claude.py
import asyncio
from typing import Dict, Any, List, Optional
from anthropic import AsyncAnthropic
from ..mcp.protocol import MCPContext
from ..utils.config import get_settings

class ClaudeService:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=get_settings().anthropic_api_key)
        self.model = "claude-3-sonnet-20240229"

    async def get_response(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        context: MCPContext
    ) -> Dict[str, Any]:
        """Get response from Claude with tools and context"""

        # Prepare system message with Discord context
        system_message = self._build_system_message(context)

        # Format messages for Claude
        formatted_messages = self._format_messages(messages)

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                system=system_message,
                messages=formatted_messages,
                tools=tools if tools else None
            )

            # Process response
            if response.content:
                if hasattr(response.content[0], 'text'):
                    return {
                        "content": response.content[0].text,
                        "tool_calls": self._extract_tool_calls(response)
                    }
                else:
                    # Handle tool use
                    return {
                        "content": None,
                        "tool_calls": self._extract_tool_calls(response)
                    }

            return {"content": "I apologize, but I couldn't generate a response.", "tool_calls": []}

        except Exception as e:
            return {"content": f"Error: {str(e)}", "tool_calls": []}

    def _build_system_message(self, context: MCPContext) -> str:
        """Build system message with Discord context"""
        return f"""You are a helpful AI assistant integrated with Discord through MCP (Model-Context Protocol).

Context Information:
- User ID: {context.user_id}
- Channel ID: {context.channel_id}
- Guild ID: {context.guild_id or 'Direct Message'}
- Available Tools: {', '.join(context.active_tools)}

You have access to Discord-specific tools that can help you:
- Look up user information
- Get channel details
- Access message history
- Retrieve server statistics

Always be helpful, engaging, and Discord-appropriate. Use tools when they would be helpful to answer user questions or provide better context. Format your responses clearly for Discord's text interface.

If you need to use tools, use them proactively to provide better assistance."""

    def _format_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format messages for Claude API"""
        formatted = []

        for msg in messages:
            if msg["role"] in ["user", "assistant"]:
                formatted.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            elif msg["role"] == "tool":
                # Add tool results to the conversation
                formatted.append({
                    "role": "user",
                    "content": f"Tool Result ({msg.get('tool_name', 'unknown')}): {msg['content']}"
                })

        return formatted

    def _extract_tool_calls(self, response) -> List[Dict[str, Any]]:
        """Extract tool calls from Claude response"""
        tool_calls = []

        if hasattr(response, 'content'):
            for content_block in response.content:
                if hasattr(content_block, 'type') and content_block.type == 'tool_use':
                    tool_calls.append({
                        "id": content_block.id,
                        "name": content_block.name,
                        "arguments": content_block.input
                    })

        return tool_calls
```

### 5.4 Configuration Management

```python
# app/utils/config.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/discord_mcp"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # API Keys
    anthropic_api_key: str
    discord_token: str

    # MCP Server
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8000

    # Security
    secret_key: str = "your-secret-key-change-this"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

### 5.5 Database Configuration

```python
# app/utils/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Phase 6: Advanced Features & Best Practices

### 6.1 Real-time Features with WebSockets

```python
# app/services/websocket_manager.py
import json
from typing import Dict, List
from fastapi import WebSocket
from ..mcp.protocol import MCPContext

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a WebSocket to a session"""
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, session_id: str):
        """Disconnect a WebSocket from a session"""
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)

            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def send_personal_message(self, message: str, session_id: str):
        """Send message to specific session"""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove dead connections
                    self.active_connections[session_id].remove(connection)

    async def broadcast_to_session(self, message: dict, session_id: str):
        """Broadcast message to all connections in a session"""
        if session_id in self.active_connections:
            message_str = json.dumps(message)
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(message_str)
                except:
                    self.active_connections[session_id].remove(connection)
```

### 6.2 Monitoring and Logging

```python
# app/utils/monitoring.py
import logging
import time
from typing import Dict, Any
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge
import asyncio

# Metrics
REQUEST_COUNT = Counter('mcp_requests_total', 'Total MCP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('mcp_request_duration_seconds', 'MCP request duration')
ACTIVE_SESSIONS = Gauge('mcp_active_sessions', 'Number of active MCP sessions')
TOOL_USAGE = Counter('mcp_tool_usage_total', 'Tool usage count', ['tool_name'])

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            REQUEST_COUNT.labels(method=func.__name__, endpoint='success').inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(method=func.__name__, endpoint='error').inc()
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_DURATION.observe(duration)
    return wrapper

class MCPMonitor:
    def __init__(self):
        self.session_metrics: Dict[str, Dict[str, Any]] = {}

    def track_session_start(self, session_id: str, context: Dict[str, Any]):
        """Track when a session starts"""
        self.session_metrics[session_id] = {
            'start_time': time.time(),
            'message_count': 0,
            'tool_calls': 0,
            'context': context
        }
        ACTIVE_SESSIONS.set(len(self.session_metrics))

    def track_message(self, session_id: str, message_type: str):
        """Track message processing"""
        if session_id in self.session_metrics:
            self.session_metrics[session_id]['message_count'] += 1

    def track_tool_use(self, session_id: str, tool_name: str):
        """Track tool usage"""
        if session_id in self.session_metrics:
            self.session_metrics[session_id]['tool_calls'] += 1

        TOOL_USAGE.labels(tool_name=tool_name).inc()

    def track_session_end(self, session_id: str):
        """Track when a session ends"""
        if session_id in self.session_metrics:
            session_data = self.session_metrics[session_id]
            duration = time.time() - session_data['start_time']

            logger.info(f"Session {session_id} ended. Duration: {duration:.2f}s, "
                       f"Messages: {session_data['message_count']}, "
                       f"Tool calls: {session_data['tool_calls']}")

            del self.session_metrics[session_id]
            ACTIVE_SESSIONS.set(len(self.session_metrics))
```

### 6.3 Security & Rate Limiting

```python
# app/utils/security.py
import time
from typing import Dict, Optional
from fastapi import HTTPException, Request
from functools import wraps
import hashlib
import hmac

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for identifier"""
        now = time.time()

        if identifier not in self.requests:
            self.requests[identifier] = []

        # Remove old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window_seconds
        ]

        # Check if under limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False

        # Add current request
        self.requests[identifier].append(now)
        return True

def rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    """Rate limiting decorator"""
    limiter = RateLimiter(max_requests, window_seconds)

    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host

            if not limiter.is_allowed(client_ip):
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded"
                )

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

def validate_discord_signature(request: Request, signature: str, timestamp: str, body: bytes) -> bool:
    """Validate Discord webhook signature"""
    # This would validate Discord's signature for webhook security
    # Implementation depends on Discord's webhook signature format
    return True  # Placeholder

class SecurityManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def generate_session_token(self, user_id: str, channel_id: str) -> str:
        """Generate secure session token"""
        data = f"{user_id}:{channel_id}:{time.time()}"
        return hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

    def validate_session_token(self, token: str, user_id: str, channel_id: str) -> bool:
        """Validate session token"""
        # Implementation would verify token authenticity and expiration
        return True  # Placeholder
```

### 6.4 Deployment Scripts

```bash
# scripts/deploy.sh
#!/bin/bash

set -e

echo "Starting Discord MCP Server deployment..."

# Check if required environment variables are set
if [ -z "$ANTHROPIC_API_KEY" ] || [ -z "$DISCORD_TOKEN" ]; then
    echo "Error: Required environment variables not set"
    echo "Please set ANTHROPIC_API_KEY and DISCORD_TOKEN"
    exit 1
fi

# Build and start services
echo "Building Docker images..."
docker-compose build

echo "Starting database..."
docker-compose up -d db redis

echo "Waiting for database to be ready..."
sleep 10

echo "Running database migrations..."
docker-compose run --rm mcp-server alembic upgrade head

echo "Starting MCP server..."
docker-compose up -d mcp-server

echo "Waiting for MCP server to be ready..."
sleep 5

echo "Starting Discord bot..."
docker-compose up -d discord-bot

echo "Deployment complete!"
echo "Health check: http://localhost:8000/health"
```

```bash
# scripts/setup.sh
#!/bin/bash

set -e

echo "Setting up Discord MCP Server development environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file template
cat > .env << EOL
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/discord_mcp

# Redis
REDIS_URL=redis://localhost:6379

# API Keys (Fill these in)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DISCORD_TOKEN=your_discord_token_here

# MCP Server
MCP_HOST=0.0.0.0
MCP_PORT=8000

# Security
SECRET_KEY=your-secret-key-change-this-in-production

# Logging
LOG_LEVEL=INFO
EOL

echo "Environment setup complete!"
echo "1. Fill in your API keys in .env file"
echo "2. Run: docker-compose up -d db redis"
echo "3. Run: alembic upgrade head"
echo "4. Run: python -m app.main"
```

## Production Considerations

### 6.5 Scaling Strategies

1. **Horizontal Scaling**: Use load balancers with Redis for session sharing
2. **Database Optimization**: Implement connection pooling and read replicas
3. **Caching**: Redis for conversation history and user preferences
4. **Message Queues**: Use Celery for background tasks

### 6.6 Monitoring & Observability

1. **Metrics**: Prometheus + Grafana for monitoring
2. **Logging**: Structured logging with ELK stack
3. **Alerting**: Set up alerts for high error rates, slow responses
4. **Health Checks**: Implement comprehensive health endpoints

### 6.7 Security Best Practices

1. **Input Validation**: Strict validation of all Discord inputs
2. **Rate Limiting**: Per-user and per-guild rate limits
3. **Authentication**: Secure session management
4. **Data Privacy**: Encrypt sensitive data at rest

### 6.8 Testing Strategy

```python
# tests/test_mcp_server.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.mcp.protocol import MCPMessage, MCPMessageType

client = TestClient(app)

class TestMCPServer:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_session_initialization(self):
        session_data = {
            "session_id": "test_session",
            "user_id": "123456789",
            "channel_id": "987654321",
            "guild_id": "111222333"
        }

        response = client.post("/mcp/initialize", json=session_data)
        assert response.status_code == 200
        assert response.json()["session_id"] == "test_session"

    def test_message_processing(self):
        # First initialize session
        session_data = {
            "session_id": "test_session_2",
            "user_id": "123456789",
            "channel_id": "987654321"
        }

        init_response = client.post("/mcp/initialize", json=session_data)
        assert init_response.status_code == 200

        # Then process message
        message_data = {
            "session_id": "test_session_2",
            "message": "Hello, how are you?"
        }

        response = client.post("/mcp/process", json=message_data)
        assert response.status_code == 200
        assert "response" in response.json()
```

This comprehensive guide provides you with:

1. **Complete MCP Architecture** - Understanding how MCP works with Discord
2. **Step-by-step Implementation** - From basic server to production deployment
3. **Production-ready Features** - Monitoring, security, scaling considerations
4. **Best Practices** - Code organization, error handling, testing

The architecture is designed to be:

- **Modular**: Easy to extend with new tools and features
- **Scalable**: Can handle multiple Discord servers simultaneously
- **Maintainable**: Clean separation of concerns
- **Production-ready**: Includes monitoring, security, and deployment

Start with Phase 1 to get the basic MCP server running, then progressively add features through each phase. The modular design allows you to customize and extend functionality as needed for your specific use case.
