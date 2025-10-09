# Discord MCP Server Architecture

**Version**: 0.1.0
**Status**: Design Document (Implementation Pending)
**Date**: 2025-01-09

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [System Layers](#system-layers)
4. [Project Structure](#project-structure)
5. [Workflow System](#workflow-system)
6. [Resource & Template System](#resource--template-system)
7. [Internal Helpers](#internal-helpers)
8. [Context Object](#context-object)
9. [Testing Strategy](#testing-strategy)
10. [Migration Path](#migration-path)

---

## Overview

The Discord MCP Server provides AI assistants with Discord integration through a workflow-based architecture. The system consolidates 26+ atomic tools into **7-10 workflow orchestrators** backed by a rich internal helper library.

### Key Goals

- **Reduce tool count**: 26 → 7-10 workflows
- **DRY principle**: Shared helpers for common operations
- **Autonomous workflows**: Client triggers, server executes multi-step processes
- **Testability**: Unit → Integration → System test layers
- **Scalability**: Resource system for templates, prompts, and configs

---

## Architecture Principles

### 1. **Thin Tool Layer, Rich Internal Library**

```
┌─────────────────────────────────────┐
│  MCP Tools (Client-Facing)          │  ← 7-10 workflow tools
│  - discord_discovery                 │
│  - discord_campaign                  │
│  - discord_diagnostics               │
└──────────────┬──────────────────────┘
               │ delegates to
┌──────────────▼──────────────────────┐
│  Workflow Orchestrators              │  ← Multi-step logic
│  - Parse intent                      │
│  - Execute steps                     │
│  - Track execution                   │
└──────────────┬──────────────────────┘
               │ uses
┌──────────────▼──────────────────────┐
│  Internal Helpers                    │  ← Reusable building blocks
│  - _find_entity()                    │
│  - _validate_access()                │
│  - _parse_intent()                   │
└──────────────┬──────────────────────┘
               │ calls
┌──────────────▼──────────────────────┐
│  Discord.py Client                   │  ← Discord API
└─────────────────────────────────────┘
```

### 2. **Workflows as Orchestrators**

Workflows **chain** internal helpers, they don't **reimplement** them.

**Bad (monolithic):**

```python
async def discord_discovery_workflow(...):
    # 200 lines of entity finding logic
    pass
```

**Good (orchestration):**

```python
async def discord_discovery_workflow(...):
    guild = await _find_entity("server", name, ctx)  # ← reusable
    channel = await _find_entity("channel", name, ctx, guild_id=guild.id)
    details = await _get_entity_details("channel", channel.id, ctx)
    return WorkflowResult(...)
```

### 3. **Intent-Based API**

Tools accept natural language intents, not rigid parameters.

```python
# Instead of:
discord_find_server(name="Test")
discord_find_channel(server_id="123", name="general")
discord_send_message(channel_id="456", content="Hello")

# Single workflow:
discord_discovery("find channel general in Test server")
discord_message("send 'Hello' to general in Test")
```

---

## System Layers

### Layer 1: MCP Tools (Client-Facing)

**Workflow Tools** (Primary Interface):

- `discord_discovery` - Find entities (servers, channels, roles)
- `discord_campaign` - Campaign lifecycle management
- `discord_diagnostics` - Health checks and status
- `discord_message` - Message operations
- `discord_thread` _(v0.2)_ - Thread management
- `discord_member` _(v0.3)_ - Member operations
- `discord_context` _(v0.4)_ - Context/memory management

**Atomic Tools** (Power Users):

- `discord_send` - Send message by exact ID
- `discord_get` - Get entity by exact ID
- `discord_list` - List entities with filters

**Automation Tools** (Background Processes):

- `discord_run_due_reminders` - Process scheduled campaigns (cron/scheduler)

### Layer 2: Workflows

Located: `src/discord_mcp/workflows/`

**Responsibilities:**

- Parse user intent
- Orchestrate multi-step operations
- Track execution steps
- Handle errors and rollback
- Return structured results

**Pattern:**

```python
async def workflow_name(
    intent_or_action: str,
    *,
    ctx: Context,
    **kwargs
) -> WorkflowResult:
    steps = []

    # Step 1: Parse intent
    parsed = await _parse_intent(intent_or_action)
    steps.append({"action": "parse", "result": parsed})

    # Step 2: Execute operation
    result = await _internal_operation(parsed, ctx)
    steps.append({"action": "execute", "result": result})

    # Step 3: Post-process
    final = await _post_process(result, ctx)
    steps.append({"action": "post_process", "result": final})

    return WorkflowResult(
        success=True,
        action=workflow_name,
        data=final,
        steps=steps,
        errors=[]
    )
```

### Layer 3: Internal Helpers

Located: `src/discord_mcp/internal/`

**Modules:**

- `entity_operations.py` - Entity CRUD operations
- `access_control.py` - Permission validation
- `intent_parser.py` - Natural language parsing
- `discord_helpers.py` - Discord API wrappers
- `validation.py` - Input validation

**Example:**

```python
# internal/entity_operations.py

async def _find_entity(
    entity_type: Literal["server", "channel", "role", "member"],
    query: str,
    ctx: Context,
    *,
    guild_id: Optional[str] = None,
    exact_match: bool = False,
    limit: int = 5
) -> Dict[str, Any]:
    """Shared entity discovery logic."""

    # 1. DRY_RUN handling
    if ctx.config.dry_run:
        return _mock_entity_result(entity_type, query)

    # 2. Allowlist check
    await _validate_guild_access(guild_id, ctx)

    # 3. Dispatch to entity-specific retrieval
    fetcher = _get_entity_fetcher(entity_type)
    candidates = await fetcher(ctx.bot, guild_id)

    # 4. Fuzzy matching
    matches = _fuzzy_match(candidates, query, exact_match)

    # 5. Sort by relevance (exact > startswith > contains)
    sorted_matches = _sort_by_relevance(matches, query)

    return {
        "entity_type": entity_type,
        "query": query,
        "matches": sorted_matches[:limit],
        "total_candidates": len(candidates),
        "match_count": len(matches)
    }
```

### Layer 4: Resources & Templates

Located: `src/discord_mcp/resources/`

**Purpose:**

- Reusable message templates
- LLM prompts for intent parsing
- Workflow configurations
- Localization support

**Structure:**

```yaml
resources/
├── campaign/
│   ├── templates/
│   │   ├── reminder_message.txt.j2
│   │   └── campaign_summary.txt.j2
│   └── prompts/
│       ├── campaign_followup.yaml
│       └── opt_in_analysis.yaml
├── discovery/
│   └── prompts/
│       └── discovery_intent.yaml
└── loader.py # ResourceManager
```

---

## Project Structure

```
discord-mcp/
├── src/discord_mcp/
│   ├── server.py                  # MCP server entry point
│   ├── config.py                  # Configuration
│   │
│   ├── discord_client/            # Discord.py bot
│   │   ├── bot.py                 # DiscordMCPBot
│   │   └── events.py              # Event handlers
│   │
│   ├── database/                  # SQLite persistence
│   │   ├── models.py              # Data models
│   │   ├── repositories.py        # CRUD operations
│   │   └── migrations.py          # Schema migrations
│   │
│   ├── workflows/                 # 🆕 Workflow orchestrators
│   │   ├── __init__.py
│   │   ├── base.py                # WorkflowResult, BaseWorkflow
│   │   ├── discovery.py           # Discovery workflow
│   │   ├── campaign.py            # Campaign workflow
│   │   ├── diagnostics.py         # Diagnostics workflow
│   │   ├── message.py             # Message workflow
│   │   └── (future: thread.py, member.py, context.py)
│   │
│   ├── internal/                  # 🆕 Internal helper library
│   │   ├── __init__.py
│   │   ├── entity_operations.py  # _find_entity, _get_entity_details
│   │   ├── access_control.py     # _validate_access, _check_permissions
│   │   ├── intent_parser.py      # _parse_discovery_intent, etc.
│   │   ├── discord_helpers.py    # Discord API wrappers
│   │   ├── validation.py         # Input validation
│   │   └── formatters.py         # Output formatting
│   │
│   ├── resources/                 # 🆕 Templates & prompts
│   │   ├── __init__.py
│   │   ├── loader.py              # ResourceManager
│   │   ├── campaign/              # Campaign resources
│   │   │   ├── templates/
│   │   │   └── prompts/
│   │   ├── discovery/             # Discovery resources
│   │   │   └── prompts/
│   │   └── registry.py            # WORKFLOW_RESOURCES
│   │
│   ├── tools/                     # Tool registration (thin layer)
│   │   ├── __init__.py
│   │   ├── register_tools.py      # Register workflows + atomic tools
│   │   ├── atomic.py              # 🆕 discord_send, discord_get, discord_list
│   │   └── (legacy: core.py, campaigns.py, search_tools.py)
│   │
│   └── server_registry/           # Legacy entity registry (may deprecate)
│
├── tests/
│   ├── unit/                      # 🆕 Test internal helpers
│   │   ├── test_entity_operations.py
│   │   ├── test_access_control.py
│   │   └── test_intent_parser.py
│   ├── integration/               # 🆕 Test workflows
│   │   ├── test_discovery_workflow.py
│   │   ├── test_campaign_workflow.py
│   │   └── test_message_workflow.py
│   ├── system/                    # 🆕 Test MCP tools end-to-end
│   │   └── test_registered_tools.py
│   └── (existing test files)
│
├── docs/
│   ├── ARCHITECTURE.md            # This file
│   ├── WORKFLOWS.md               # 🆕 Workflow usage guide
│   ├── RESOURCES.md               # 🆕 Resource system guide
│   └── MIGRATION.md               # 🆕 v0.0.x → v0.1.0 migration
│
└── specs/                         # Feature specifications
```

---

## Workflow System

### Workflow Base Classes

```python
# src/discord_mcp/workflows/base.py

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    success: bool
    action: str
    data: Dict[str, Any]
    steps: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "data": self.data,
            "steps": self.steps,
            "errors": self.errors
        }


class BaseWorkflow:
    """Base class for all workflows."""

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.steps = []

    def add_step(self, action: str, **kwargs):
        """Add execution step for tracing."""
        self.steps.append({"action": action, **kwargs})

    async def validate_preconditions(self) -> bool:
        """Validate workflow can execute."""
        raise NotImplementedError

    async def execute(self, **kwargs) -> WorkflowResult:
        """Execute workflow logic."""
        raise NotImplementedError

    async def rollback(self):
        """Rollback changes on error."""
        pass
```

### Discovery Workflow

```python
# src/discord_mcp/workflows/discovery.py

async def discord_discovery_workflow(
    intent: str,
    *,
    ctx: Context
) -> WorkflowResult:
    """
    Discovery workflow - find entities and provide context.

    Examples:
        - "find channel named general in MyServer"
        - "get all channels in server 123456"
        - "find role moderator"

    Args:
        intent: Natural language discovery intent
        ctx: Execution context

    Returns:
        WorkflowResult with matched entities and details
    """
    from ..internal.intent_parser import parse_discovery_intent
    from ..internal.entity_operations import _find_entity, _get_entity_details

    steps = []

    try:
        # Step 1: Parse intent
        parsed = await parse_discovery_intent(intent, ctx)
        steps.append({"action": "parse_intent", "parsed": parsed})

        # Step 2: Resolve guild if needed
        guild_id = await _resolve_guild_context(parsed, ctx, steps)

        # Step 3: Find target entity
        result = await _find_entity(
            parsed["entity_type"],
            parsed["query"],
            ctx,
            guild_id=guild_id,
            limit=parsed.get("limit", 5)
        )
        steps.append({
            "action": "find_entity",
            "entity_type": parsed["entity_type"],
            "matches": len(result["matches"])
        })

        # Step 4: Get details for top match (if requested)
        if result["matches"] and parsed.get("detailed", True):
            top_match = result["matches"][0]
            details = await _get_entity_details(
                parsed["entity_type"],
                top_match["id"],
                ctx
            )
            top_match["details"] = details
            steps.append({"action": "fetch_details", "entity_id": top_match["id"]})

        return WorkflowResult(
            success=True,
            action="discovery",
            data=result,
            steps=steps,
            errors=[]
        )

    except Exception as e:
        return WorkflowResult(
            success=False,
            action="discovery",
            data={},
            steps=steps,
            errors=[str(e)]
        )


async def _resolve_guild_context(
    parsed: Dict[str, Any],
    ctx: Context,
    steps: List[Dict[str, Any]]
) -> Optional[str]:
    """Resolve guild ID from parsed intent."""
    if parsed.get("guild_id"):
        return parsed["guild_id"]

    if parsed.get("guild_name"):
        from ..internal.entity_operations import _find_entity

        guild_result = await _find_entity("server", parsed["guild_name"], ctx)
        if not guild_result["matches"]:
            raise ValueError(f"Server '{parsed['guild_name']}' not found")

        guild_id = guild_result["matches"][0]["id"]
        steps.append({"action": "resolve_guild", "guild_id": guild_id})
        return guild_id

    return None
```

### Campaign Workflow

**Note**: See [CAMPAIGN_FLOW.md](./CAMPAIGN_FLOW.md) for detailed campaign documentation.

**Key Design**: The `create` action schedules autonomous reminders. External automation (`discord_run_due_reminders`) handles scheduled sends, keeping the MCP server stateless.

```python
# src/discord_mcp/workflows/campaign.py

async def discord_campaign_workflow(
    action: Literal[
        "create",           # Create campaign (autonomous via discord_run_due_reminders)
        "execute_now",      # Tally + build + send immediately
        "preview",          # Tally + build (no send, for review)
        "send",             # Send previewed reminder
        "list",             # List campaigns with optional status filter
        "get",              # Get campaign details
        "list_optins",      # List who opted in
        "update_status",    # Change status (active/completed/cancelled)
        "delete"            # Delete campaign and opt-ins
    ],
    *,
    # For create
    channel_id: Optional[str] = None,
    message_id: Optional[str] = None,
    emoji: str = "👍",
    remind_at: Optional[str] = None,
    title: Optional[str] = None,

    # For execute_now / preview / send / list_optins / update_status / delete
    campaign_id: Optional[int] = None,

    # For list
    status_filter: Optional[str] = None,

    # For send
    dry_run: bool = True,

    ctx: Context
) -> WorkflowResult:
    """
    Campaign workflow - autonomous campaign management.

    Actions:
        - create_and_run: Create + monitor + send reminders (fully autonomous)
        - execute: Run existing campaign (tally + build + send + close)
        - create: Just create campaign and return
        - monitor: Watch for reactions and tally periodically
        - list: List campaigns with optional status filter
        - delete: Delete campaign and all opt-ins
    """

    if action == "create_and_run":
        return await _campaign_create_and_run(
            channel_id, message_content, emoji, remind_at, ctx
        )
    elif action == "execute":
        return await _campaign_execute(campaign_id, ctx)
    elif action == "create":
        return await _campaign_create(channel_id, message_content, emoji, remind_at, ctx)
    elif action == "monitor":
        return await _campaign_monitor(campaign_id, ctx)
    elif action == "list":
        return await _campaign_list(status_filter, ctx)
    elif action == "delete":
        return await _campaign_delete(campaign_id, ctx)
    else:
        return WorkflowResult(
            success=False,
            action="campaign",
            data={},
            steps=[],
            errors=[f"Unknown action: {action}"]
        )


async def _campaign_create_and_run(
    channel_id: str,
    message_content: str,
    emoji: str,
    remind_at: str,
    ctx: Context
) -> WorkflowResult:
    """Fully autonomous campaign workflow."""
    steps = []

    try:
        # Step 1: Create campaign
        from ..tools.campaigns import discord_create_campaign
        campaign_result = await discord_create_campaign(
            channel_id, message_content, emoji, remind_at
        )
        campaign_id = campaign_result["campaign"]["id"]
        steps.append({"action": "create_campaign", "campaign_id": campaign_id})

        # Step 2: Monitor reactions until due
        monitor_result = await _campaign_monitor_until_due(campaign_id, ctx)
        steps.extend(monitor_result.steps)

        # Step 3: Execute reminders
        execute_result = await _campaign_execute(campaign_id, ctx)
        steps.extend(execute_result.steps)

        # Step 4: Close campaign
        from ..tools.campaigns import discord_update_campaign_status
        await discord_update_campaign_status(campaign_id, "completed")
        steps.append({"action": "close_campaign", "campaign_id": campaign_id})

        return WorkflowResult(
            success=True,
            action="create_and_run",
            data={
                "campaign_id": campaign_id,
                "opt_in_count": execute_result.data["total_optins"],
                "reminders_sent": execute_result.data["chunks_sent"]
            },
            steps=steps,
            errors=[]
        )

    except Exception as e:
        return WorkflowResult(
            success=False,
            action="create_and_run",
            data={},
            steps=steps,
            errors=[str(e)]
        )


async def _campaign_execute(
    campaign_id: int,
    ctx: Context
) -> WorkflowResult:
    """Execute campaign: tally → build → send → close."""
    from ..tools.campaigns import (
        discord_tally_optins,
        discord_build_reminder,
        discord_send_reminder
    )

    steps = []

    try:
        # Tally opt-ins
        tally_result = await discord_tally_optins(campaign_id)
        steps.append({
            "action": "tally",
            "campaign_id": campaign_id,
            "opt_ins": tally_result["total"]
        })

        # Build reminder messages
        build_result = await discord_build_reminder(campaign_id)
        steps.append({
            "action": "build_reminder",
            "chunks": len(build_result["chunks"])
        })

        # Send reminders
        send_result = await discord_send_reminder(campaign_id)
        steps.append({
            "action": "send_reminder",
            "chunks_sent": send_result["chunks_sent"]
        })

        return WorkflowResult(
            success=True,
            action="execute_campaign",
            data={
                "campaign_id": campaign_id,
                "total_optins": tally_result["total"],
                "chunks_sent": send_result["chunks_sent"]
            },
            steps=steps,
            errors=[]
        )

    except Exception as e:
        return WorkflowResult(
            success=False,
            action="execute_campaign",
            data={},
            steps=steps,
            errors=[str(e)]
        )
```

---

## Resource & Template System

### Resource Structure

```
resources/
├── campaign/
│   ├── templates/
│   │   ├── reminder_message.txt.j2       # Jinja2 template
│   │   └── campaign_summary.txt.j2
│   └── prompts/
│       ├── campaign_followup.yaml        # LLM prompt
│       └── opt_in_analysis.yaml
├── discovery/
│   └── prompts/
│       └── discovery_intent.yaml
├── diagnostics/
│   └── templates/
│       └── health_report.txt.j2
└── loader.py  # ResourceManager
```

### Template Example

```jinja2
{# resources/campaign/templates/reminder_message.txt.j2 #}
📢 **Reminder: {{ campaign.message }}**

The following members have opted in by reacting with {{ campaign.emoji }}:

{% for user in users %}
- {{ user.mention }}
{% endfor %}

Total opt-ins: {{ total_optins }}
Campaign created: {{ campaign.created_at | datetime }}
```

### Prompt Example

```yaml
# resources/discovery/prompts/discovery_intent.yaml
intent: 'Discovery'
description: 'Parse natural language discovery intents into structured entity operations'
version: '1.0'
model: 'claude-3-5-sonnet-20250129'
input_vars:
  - intent # User's natural language input
output_format: |
  {
    "entity_type": "server" | "channel" | "role" | "member",
    "query": "search string",
    "guild_name": "optional server name",
    "guild_id": "optional server ID",
    "detailed": true | false,
    "limit": number
  }
template: |
  Parse the following user intent into a structured discovery query.

  Intent: "{{ intent }}"

  Extract:
  - entity_type: What type of entity (server, channel, role, member)?
  - query: The search term (name or ID)
  - guild_name: If mentioned, the server name
  - guild_id: If provided, the server ID
  - detailed: Whether to fetch full details (default: true)
  - limit: Max results (default: 5)

  Return ONLY valid JSON matching the output format.
```

### Resource Manager

```python
# src/discord_mcp/resources/loader.py

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from jinja2 import Environment, FileSystemLoader

class ResourceManager:
    """Manage workflow resources (templates, prompts, configs)."""

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.resources_dir = Path(__file__).parent
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.resources_dir),
            autoescape=True
        )

    def get_template(self, path: str) -> Any:
        """
        Load Jinja2 template.

        Args:
            path: Template path relative to resources/ (e.g., "campaign/templates/reminder_message.txt.j2")

        Returns:
            Jinja2 Template object
        """
        return self.jinja_env.get_template(path)

    def get_prompt(self, path: str) -> Dict[str, Any]:
        """
        Load LLM prompt configuration.

        Args:
            path: Prompt path relative to resources/ (e.g., "discovery/prompts/discovery_intent.yaml")

        Returns:
            Prompt configuration dict
        """
        prompt_path = self.resources_dir / path
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def render_template(self, path: str, **kwargs) -> str:
        """Render template with variables."""
        template = self.get_template(path)
        return template.render(**kwargs)


# Registry of workflow resources
WORKFLOW_RESOURCES = {
    "campaign": {
        "templates": [
            "campaign/templates/reminder_message.txt.j2",
            "campaign/templates/campaign_summary.txt.j2"
        ],
        "prompts": [
            "campaign/prompts/campaign_followup.yaml",
            "campaign/prompts/opt_in_analysis.yaml"
        ]
    },
    "discovery": {
        "prompts": [
            "discovery/prompts/discovery_intent.yaml"
        ]
    },
    "diagnostics": {
        "templates": [
            "diagnostics/templates/health_report.txt.j2"
        ]
    }
}
```

### Usage in Workflows

```python
# In a workflow
async def discord_campaign_workflow(..., ctx: Context):
    # Load template
    template = ctx.resources.get_template("campaign/templates/reminder_message.txt.j2")

    # Render with data
    message = template.render(
        campaign=campaign_data,
        users=opted_in_users,
        total_optins=len(opted_in_users)
    )

    # Send message
    await discord_send_message(channel_id, message)
```

---

## Internal Helpers

### Entity Operations

```python
# src/discord_mcp/internal/entity_operations.py

async def _find_entity(
    entity_type: Literal["server", "channel", "role", "member"],
    query: str,
    ctx: Context,
    *,
    guild_id: Optional[str] = None,
    exact_match: bool = False,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Shared entity discovery logic.

    Used by:
        - find_server_by_name()
        - find_channel_by_name()
        - find_role_by_name()
        - discord_discovery_workflow()
    """
    # 1. DRY_RUN handling
    if ctx.config.dry_run:
        return _mock_entity_result(entity_type, query)

    # 2. Allowlist check
    await _validate_guild_access(guild_id, ctx)

    # 3. Dispatch to entity-specific retrieval
    fetcher = _get_entity_fetcher(entity_type)
    candidates = await fetcher(ctx.bot, guild_id)

    # 4. Fuzzy matching
    matches = _fuzzy_match(candidates, query, exact_match)

    # 5. Sort by relevance (exact > startswith > contains)
    sorted_matches = _sort_by_relevance(matches, query)

    return {
        "entity_type": entity_type,
        "query": query,
        "matches": sorted_matches[:limit],
        "total_candidates": len(candidates),
        "match_count": len(matches)
    }


async def _get_entity_details(
    entity_type: str,
    entity_id: str,
    ctx: Context
) -> Dict[str, Any]:
    """Get detailed information about an entity."""
    if ctx.config.dry_run:
        return _mock_entity_details(entity_type, entity_id)

    fetcher = _get_detail_fetcher(entity_type)
    return await fetcher(ctx.bot, entity_id)


def _fuzzy_match(
    candidates: List[Any],
    query: str,
    exact_match: bool
) -> List[Dict[str, Any]]:
    """Perform fuzzy matching on candidates."""
    query_lower = query.lower()
    matches = []

    for candidate in candidates:
        name = candidate.name.lower()

        if exact_match:
            if name == query_lower:
                matches.append({
                    "id": str(candidate.id),
                    "name": candidate.name,
                    "match_type": "exact"
                })
        else:
            if name == query_lower:
                match_type = "exact"
            elif name.startswith(query_lower):
                match_type = "prefix"
            elif query_lower in name:
                match_type = "contains"
            else:
                continue

            matches.append({
                "id": str(candidate.id),
                "name": candidate.name,
                "match_type": match_type
            })

    return matches


def _sort_by_relevance(
    matches: List[Dict[str, Any]],
    query: str
) -> List[Dict[str, Any]]:
    """Sort matches by relevance."""
    relevance_order = {"exact": 0, "prefix": 1, "contains": 2}
    return sorted(matches, key=lambda m: relevance_order.get(m["match_type"], 3))
```

### Access Control

```python
# src/discord_mcp/internal/access_control.py

async def _validate_guild_access(
    guild_id: Optional[str],
    ctx: Context
) -> None:
    """
    Validate bot has access to guild.

    Raises:
        PermissionError: If guild not in allowlist
    """
    if not guild_id:
        return

    if ctx.config.guild_allowlist:
        if guild_id not in ctx.config.guild_allowlist:
            raise PermissionError(
                f"Access denied: Guild {guild_id} not in allowlist"
            )


async def _validate_entity_access(
    entity_type: str,
    entity_id: str,
    ctx: Context,
    *,
    required_permissions: List[str] = None
) -> bool:
    """
    Validate user has access to entity.

    Args:
        entity_type: Type of entity (server, channel, role, member)
        entity_id: Entity ID
        ctx: Context
        required_permissions: List of required Discord permissions

    Returns:
        True if access granted

    Raises:
        PermissionError: If access denied
    """
    # Check guild allowlist
    if entity_type in ["channel", "role", "member"]:
        entity = await _get_entity_by_id(entity_type, entity_id, ctx)
        await _validate_guild_access(str(entity.guild.id), ctx)

    # Check Discord permissions
    if required_permissions:
        has_perms = await _check_discord_permissions(
            entity_type, entity_id, required_permissions, ctx
        )
        if not has_perms:
            raise PermissionError(
                f"Missing required permissions: {', '.join(required_permissions)}"
            )

    return True
```

### Intent Parser

```python
# src/discord_mcp/internal/intent_parser.py

async def parse_discovery_intent(
    intent: str,
    ctx: Context
) -> Dict[str, Any]:
    """
    Parse natural language discovery intent.

    Examples:
        - "find channel general in MyServer"
        - "get all channels in server 123456"
        - "find role moderator"

    Returns:
        {
            "entity_type": "channel",
            "query": "general",
            "guild_name": "MyServer",
            "detailed": True,
            "limit": 5
        }
    """
    # Load prompt template
    prompt_config = ctx.resources.get_prompt("discovery/prompts/discovery_intent.yaml")

    # Build prompt with intent
    from jinja2 import Template
    prompt_template = Template(prompt_config["template"])
    prompt = prompt_template.render(intent=intent)

    # Call LLM to parse (using Anthropic SDK)
    from anthropic import Anthropic
    client = Anthropic()

    response = client.messages.create(
        model=prompt_config["model"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    # Parse JSON response
    import json
    parsed = json.loads(response.content[0].text)

    return parsed
```

---

## Context Object

### Extended Context

```python
# src/discord_mcp/context.py

from dataclasses import dataclass
from typing import Optional, Any
from .config import Config
from .discord_client.bot import DiscordMCPBot

@dataclass
class Context:
    """Execution context for workflows and tools."""

    config: Config
    bot: DiscordMCPBot
    user_id: Optional[str] = None  # MCP client user ID

    # Lazy-loaded properties
    _resources: Optional[Any] = None

    @property
    def resources(self):
        """Lazy-load resource manager."""
        if self._resources is None:
            from .resources.loader import ResourceManager
            self._resources = ResourceManager(self)
        return self._resources

    @property
    def dry_run(self) -> bool:
        """Shortcut for config.dry_run."""
        return self.config.dry_run

    def with_user(self, user_id: str) -> "Context":
        """Create new context with user ID."""
        return Context(
            config=self.config,
            bot=self.bot,
            user_id=user_id,
            _resources=self._resources
        )
```

---

## Testing Strategy

### Three-Layer Testing

```
┌─────────────────────────────────────┐
│  System Tests (End-to-End)          │  ← Test MCP tool registration
│  - Full FastMCP integration         │
│  - Test tool discovery               │
│  - Test stdio transport              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Integration Tests (Workflows)       │  ← Test workflow orchestration
│  - Mock Context                      │
│  - DRY_RUN mode                      │
│  - Test multi-step execution         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Unit Tests (Internal Helpers)       │  ← Test pure logic
│  - _find_entity()                    │
│  - _validate_access()                │
│  - _fuzzy_match()                    │
└─────────────────────────────────────┘
```

### Unit Tests

```python
# tests/unit/test_entity_operations.py

import pytest
from discord_mcp.internal.entity_operations import _fuzzy_match, _sort_by_relevance

def test_fuzzy_match_exact():
    """Test exact matching."""
    candidates = [
        MockEntity(id=1, name="General"),
        MockEntity(id=2, name="general-chat"),
        MockEntity(id=3, name="off-topic")
    ]

    matches = _fuzzy_match(candidates, "General", exact_match=True)

    assert len(matches) == 1
    assert matches[0]["id"] == "1"
    assert matches[0]["match_type"] == "exact"


def test_fuzzy_match_prefix():
    """Test prefix matching."""
    candidates = [
        MockEntity(id=1, name="general"),
        MockEntity(id=2, name="general-chat"),
        MockEntity(id=3, name="off-topic")
    ]

    matches = _fuzzy_match(candidates, "gen", exact_match=False)

    assert len(matches) == 2
    assert all(m["match_type"] in ["exact", "prefix"] for m in matches)


def test_sort_by_relevance():
    """Test relevance sorting."""
    matches = [
        {"id": "1", "name": "general-chat", "match_type": "contains"},
        {"id": "2", "name": "general", "match_type": "exact"},
        {"id": "3", "name": "gen-talk", "match_type": "prefix"}
    ]

    sorted_matches = _sort_by_relevance(matches, "general")

    assert sorted_matches[0]["match_type"] == "exact"
    assert sorted_matches[1]["match_type"] == "prefix"
    assert sorted_matches[2]["match_type"] == "contains"
```

### Integration Tests

```python
# tests/integration/test_discovery_workflow.py

import pytest
from discord_mcp.workflows.discovery import discord_discovery_workflow
from discord_mcp.context import Context

@pytest.mark.asyncio
async def test_discovery_workflow_find_channel(mock_ctx):
    """Test discovery workflow finds channel."""
    result = await discord_discovery_workflow(
        "find channel general in TestServer",
        ctx=mock_ctx
    )

    assert result.success
    assert result.action == "discovery"
    assert len(result.data["matches"]) > 0
    assert result.data["matches"][0]["name"] == "general"

    # Verify execution steps
    step_actions = [s["action"] for s in result.steps]
    assert "parse_intent" in step_actions
    assert "resolve_guild" in step_actions
    assert "find_entity" in step_actions
    assert "fetch_details" in step_actions
```

### System Tests

```python
# tests/system/test_registered_tools.py

import pytest
from mcp.server.fastmcp import FastMCP

@pytest.mark.asyncio
async def test_tools_registered():
    """Test all workflow tools are registered."""
    mcp = FastMCP("test-server")

    from discord_mcp.tools.register_tools import register_tools
    await register_tools(mcp)

    # Check workflow tools exist
    assert "discord_discovery" in mcp.list_tools()
    assert "discord_campaign" in mcp.list_tools()
    assert "discord_diagnostics" in mcp.list_tools()
    assert "discord_message" in mcp.list_tools()

    # Check atomic tools exist
    assert "discord_send" in mcp.list_tools()
    assert "discord_get" in mcp.list_tools()
    assert "discord_list" in mcp.list_tools()


@pytest.mark.asyncio
async def test_discovery_tool_execution(mcp_server, mock_discord_bot):
    """Test discovery tool executes end-to-end."""
    result = await mcp_server.call_tool(
        "discord_discovery",
        {"intent": "find server TestServer"}
    )

    assert result["success"]
    assert "matches" in result["data"]
```

---

## Migration Path

### Phase 1: Build Workflow Layer (Non-Breaking)

**Timeline**: v0.1.0-alpha2

1. ✅ Create `src/discord_mcp/workflows/` module
2. ✅ Create `src/discord_mcp/internal/` module
3. ✅ Create `src/discord_mcp/resources/` module
4. ✅ Implement base classes (`WorkflowResult`, `BaseWorkflow`, `Context`)
5. ✅ Implement internal helpers (`_find_entity`, `_validate_access`)
6. ✅ Implement workflows (discovery, campaign, diagnostics, message)
7. ✅ Register workflows alongside existing tools
8. ✅ Write tests (unit, integration, system)
9. ✅ Update documentation

**Result**: 26 old tools + 7 new workflows (coexist)

### Phase 2: Deprecate Atomic Tools (Soft Deprecation)

**Timeline**: v0.1.0-beta1

1. Mark old tools as deprecated in descriptions
2. Add migration hints: "⚠️ Deprecated: Use `discord_discovery` instead"
3. Update examples to use new workflows
4. Keep old tools functional

**Result**: 26 deprecated tools + 7 workflows (both work)

### Phase 3: Remove Atomic Tools (Hard Removal)

**Timeline**: v0.2.0

1. Remove old tool registrations from `register_tools()`
2. Keep internal functions (workflows still use them)
3. Update all documentation
4. Release breaking change

**Result**: 7-10 workflows only

---

## Summary

This architecture provides:

✅ **Scalability**: Easy to add new workflows (thread, member, context)
✅ **Maintainability**: DRY principle with shared helpers
✅ **Testability**: Three-layer testing (unit, integration, system)
✅ **Flexibility**: Workflows for common use, atomic tools for power users
✅ **Autonomy**: Workflows execute multi-step processes independently
✅ **Resource Management**: Templates and prompts for consistent outputs

The key insight: **Workflows orchestrate, helpers implement**. This prevents monolithic code while consolidating the client API surface.

---

**Next Steps:**

1. Implement internal helpers (`_find_entity`, etc.)
2. Build discovery workflow as proof-of-concept
3. Create resource system with templates
4. Write comprehensive tests
5. Update CLAUDE.md with new patterns

**Questions? See:**

- [WORKFLOWS.md](./WORKFLOWS.md) - Workflow usage guide
- [RESOURCES.md](./RESOURCES.md) - Resource system guide
- [MIGRATION.md](./MIGRATION.md) - Migration from v0.0.x
