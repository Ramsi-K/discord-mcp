# Implementation Guide

## Priority Issues & Resolutions

This document addresses the 5 priority issues identified in the documentation review and provides clear implementation guidance.

---

## 🟥 Priority 1: Implement `ctx.resources` + `ResourceManager`

### Implementation

**File**: `src/discord_mcp/resources/loader.py`

```python
"""Resource management for Discord MCP workflows."""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

class ResourceManager:
    """
    Manage workflow resources (templates, prompts, configs).

    Usage:
        ctx = Context(...)
        template = ctx.resources.get_template("campaign/templates/reminder_default.txt.j2")
        message = template.render(campaign=data, mentions="@user1 @user2")
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize resource manager.

        Args:
            base_path: Base directory for resources. Defaults to src/discord_mcp/resources/
        """
        if base_path is None:
            # Default to resources directory relative to this file
            base_path = Path(__file__).parent

        self.base_path = Path(base_path)

        # Set up Jinja2 environment for templates
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.base_path),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom filters
        self._register_filters()

    def _register_filters(self):
        """Register custom Jinja2 filters."""
        from datetime import datetime

        def datetime_filter(value, format='%Y-%m-%d %H:%M:%S'):
            """Format datetime objects."""
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    return value
            if isinstance(value, datetime):
                return value.strftime(format)
            return value

        self.jinja_env.filters['datetime'] = datetime_filter

    def get_template(self, path: str):
        """
        Load a Jinja2 template.

        Args:
            path: Template path relative to resources/
                  (e.g., "campaign/templates/reminder_default.txt.j2")

        Returns:
            Jinja2 Template object

        Example:
            template = resources.get_template("campaign/templates/reminder_default.txt.j2")
            content = template.render(campaign=data, mentions="@users")
        """
        return self.jinja_env.get_template(path)

    def render_template(self, path: str, **kwargs) -> str:
        """
        Load and render a template in one call.

        Args:
            path: Template path
            **kwargs: Template variables

        Returns:
            Rendered template string
        """
        template = self.get_template(path)
        return template.render(**kwargs)

    def get_prompt(self, path: str) -> Dict[str, Any]:
        """
        Load an LLM prompt configuration.

        Args:
            path: Prompt path relative to resources/
                  (e.g., "discovery/prompts/discovery_intent.yaml")

        Returns:
            Prompt configuration dict with keys:
                - intent: Prompt purpose
                - description: What it does
                - model: LLM model to use
                - temperature: Temperature setting
                - input_vars: List of required variables
                - output_format: Expected output format
                - system_prompt: System instructions
                - template: Jinja2 template string

        Example:
            prompt_cfg = resources.get_prompt("discovery/prompts/discovery_intent.yaml")
            model = prompt_cfg["model"]
            temp = prompt_cfg["temperature"]
        """
        prompt_path = self.base_path / path

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt not found: {path}")

        with open(prompt_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Validate required keys
        required = ['intent', 'model', 'template']
        missing = [k for k in required if k not in config]
        if missing:
            raise ValueError(f"Prompt {path} missing required keys: {missing}")

        return config

    def render_prompt(self, path: str, **kwargs) -> str:
        """
        Load prompt config and render its template.

        Args:
            path: Prompt path
            **kwargs: Variables for prompt template

        Returns:
            Rendered prompt string ready for LLM

        Example:
            prompt = resources.render_prompt(
                "discovery/prompts/discovery_intent.yaml",
                intent="find channel general"
            )
        """
        config = self.get_prompt(path)

        from jinja2 import Template
        prompt_template = Template(config['template'])

        return prompt_template.render(**kwargs)

    def list_templates(self, category: Optional[str] = None) -> list[str]:
        """
        List available templates.

        Args:
            category: Optional category filter (e.g., "campaign", "message")

        Returns:
            List of template paths
        """
        search_path = self.base_path
        if category:
            search_path = search_path / category / "templates"

        templates = []
        for template_file in search_path.rglob("*.j2"):
            rel_path = template_file.relative_to(self.base_path)
            templates.append(str(rel_path))

        return sorted(templates)

    def list_prompts(self, category: Optional[str] = None) -> list[str]:
        """
        List available prompts.

        Args:
            category: Optional category filter

        Returns:
            List of prompt paths
        """
        search_path = self.base_path
        if category:
            search_path = search_path / category / "prompts"

        prompts = []
        for prompt_file in search_path.rglob("*.yaml"):
            rel_path = prompt_file.relative_to(self.base_path)
            prompts.append(str(rel_path))

        return sorted(prompts)


# Workflow resource registry
WORKFLOW_RESOURCES = {
    "campaign": {
        "templates": [
            "campaign/templates/reminder_default.txt.j2",
            "campaign/templates/reminder_tournament.txt.j2",
            "campaign/templates/reminder_event.txt.j2",
            "campaign/templates/reminder_meeting.txt.j2",
            "campaign/templates/campaign_summary.txt.j2",
            "campaign/templates/optin_list.txt.j2",
        ],
        "prompts": [
            "campaign/prompts/campaign_intent.yaml",
            "campaign/prompts/template_suggestion.yaml",
        ]
    },
    "message": {
        "templates": [
            "message/templates/announcement.txt.j2",
            "message/templates/welcome_new_member.txt.j2",
            "message/templates/rule_reminder.txt.j2",
            "message/templates/event_announcement.txt.j2",
            "message/templates/poll_create.txt.j2",
        ],
        "prompts": [
            "message/prompts/message_intent.yaml",
            "message/prompts/mention_suggestion.yaml",
        ]
    },
    "discovery": {
        "prompts": [
            "discovery/prompts/discovery_intent.yaml",
            "discovery/prompts/entity_resolution.yaml",
        ]
    },
    "diagnostics": {
        "templates": [
            "diagnostics/templates/health_report.txt.j2",
            "diagnostics/templates/permission_report.txt.j2",
        ]
    },
    "community": {
        "templates": [
            "community/templates/weekly_digest.txt.j2",
            "community/templates/member_spotlight.txt.j2",
        ],
        "prompts": [
            "community/prompts/community_health.yaml",
        ]
    }
}
```

**File**: `src/discord_mcp/context.py`

```python
"""Context object for workflow execution."""

from dataclasses import dataclass
from typing import Optional, Any
from .config import Config
from .discord_client.bot import DiscordMCPBot

@dataclass
class Context:
    """
    Execution context for workflows and tools.

    Attributes:
        config: Configuration object
        bot: Discord bot instance
        user_id: Optional MCP client user ID
    """

    config: Config
    bot: DiscordMCPBot
    user_id: Optional[str] = None

    # Lazy-loaded properties
    _resources: Optional[Any] = None

    @property
    def resources(self):
        """
        Lazy-load resource manager.

        Returns:
            ResourceManager instance

        Example:
            # In a workflow
            template = ctx.resources.get_template("campaign/templates/reminder_default.txt.j2")
            message = template.render(campaign=data)
        """
        if self._resources is None:
            from .resources.loader import ResourceManager
            self._resources = ResourceManager()
        return self._resources

    @property
    def dry_run(self) -> bool:
        """Shortcut for config.dry_run."""
        return self.config.dry_run

    def with_user(self, user_id: str) -> "Context":
        """
        Create new context with user ID.

        Args:
            user_id: User identifier

        Returns:
            New Context instance
        """
        return Context(
            config=self.config,
            bot=self.bot,
            user_id=user_id,
            _resources=self._resources  # Share resource manager
        )
```

---

## 🟧 Priority 2: Define Helper Function Signatures

### All Helper Functions with Complete Signatures

**File**: `src/discord_mcp/internal/entity_operations.py`

```python
"""Entity discovery and retrieval operations."""

from typing import Dict, Any, List, Optional, Literal
from ..context import Context

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
    Shared entity discovery logic with fuzzy matching.

    Args:
        entity_type: Type of entity to find
        query: Search string (name or partial name)
        ctx: Execution context
        guild_id: Optional guild to scope search
        exact_match: If True, only return exact matches
        limit: Maximum results to return

    Returns:
        {
            "entity_type": str,
            "query": str,
            "matches": [
                {
                    "id": str,
                    "name": str,
                    "match_type": "exact" | "prefix" | "contains"
                }
            ],
            "total_candidates": int,
            "match_count": int
        }
    """
    pass


async def _get_entity_details(
    entity_type: Literal["server", "channel", "role", "member"],
    entity_id: str,
    ctx: Context
) -> Dict[str, Any]:
    """
    Get detailed information about an entity by ID.

    Args:
        entity_type: Type of entity
        entity_id: Entity ID
        ctx: Execution context

    Returns:
        Dict with entity-specific fields
    """
    pass


def _fuzzy_match(
    candidates: List[Any],
    query: str,
    exact_match: bool
) -> List[Dict[str, Any]]:
    """
    Perform fuzzy matching on candidates.

    Args:
        candidates: List of Discord objects to match against
        query: Search query
        exact_match: If True, only exact matches

    Returns:
        List of matched entities with match_type
    """
    pass


def _sort_by_relevance(
    matches: List[Dict[str, Any]],
    query: str
) -> List[Dict[str, Any]]:
    """
    Sort matches by relevance (exact > prefix > contains).

    Args:
        matches: List of matched entities
        query: Original query

    Returns:
        Sorted list
    """
    pass
```

**File**: `src/discord_mcp/internal/access_control.py`

```python
"""Permission validation and access control."""

from typing import List, Optional
from ..context import Context

async def _validate_guild_access(
    guild_id: Optional[str],
    ctx: Context
) -> None:
    """
    Validate bot has access to guild.

    Args:
        guild_id: Guild ID to check
        ctx: Execution context

    Raises:
        PermissionError: If guild not in allowlist
    """
    pass


async def _validate_entity_access(
    entity_type: str,
    entity_id: str,
    ctx: Context,
    *,
    required_permissions: Optional[List[str]] = None
) -> bool:
    """
    Validate user has access to entity.

    Args:
        entity_type: Type of entity
        entity_id: Entity ID
        ctx: Execution context
        required_permissions: List of required Discord permissions

    Returns:
        True if access granted

    Raises:
        PermissionError: If access denied
    """
    pass


async def _check_discord_permissions(
    entity_type: str,
    entity_id: str,
    required_permissions: List[str],
    ctx: Context
) -> bool:
    """
    Check if bot has required Discord permissions.

    Args:
        entity_type: Entity type
        entity_id: Entity ID
        required_permissions: Permission names
        ctx: Execution context

    Returns:
        True if all permissions granted
    """
    pass
```

**File**: `src/discord_mcp/internal/intent_parser.py`

```python
"""Natural language intent parsing."""

from typing import Dict, Any
from ..context import Context

async def parse_discovery_intent(
    intent: str,
    ctx: Context
) -> Dict[str, Any]:
    """
    Parse natural language discovery intent.

    Args:
        intent: User's natural language query
        ctx: Execution context

    Returns:
        {
            "entity_type": "server" | "channel" | "role" | "member",
            "query": str,
            "guild_name": str | None,
            "guild_id": str | None,
            "detailed": bool,
            "limit": int
        }

    Example:
        parse_discovery_intent("find channel general in MyServer", ctx)
        → {
            "entity_type": "channel",
            "query": "general",
            "guild_name": "MyServer",
            "detailed": True,
            "limit": 5
        }
    """
    pass


async def parse_message_intent(
    intent: str,
    ctx: Context,
    *,
    available_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Parse natural language message request.

    Args:
        intent: User's message request
        ctx: Execution context
        available_context: Available channels, roles, etc.

    Returns:
        {
            "channel": str,
            "content": str,
            "mentions": {
                "users": List[str],
                "roles": List[str],
                "everyone": bool,
                "here": bool
            },
            "template": str | None,
            "template_vars": Dict | None
        }
    """
    pass


async def parse_campaign_intent(
    intent: str,
    ctx: Context,
    *,
    channel_context: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Parse natural language campaign creation request.

    Args:
        intent: User's campaign request
        ctx: Execution context
        channel_context: Recent messages for context

    Returns:
        {
            "campaign_type": "tournament" | "event" | "meeting" | "general",
            "title": str,
            "emoji": str,
            "remind_at": str,  # ISO datetime
            "template": str,
            "template_vars": Dict
        }
    """
    pass
```

**File**: `src/discord_mcp/internal/campaign_helpers.py`

```python
"""Campaign-specific helper functions."""

from typing import Dict, Any, List
from ..context import Context

async def _campaign_create(
    channel_id: str,
    message_id: str,
    emoji: str,
    remind_at: str,
    ctx: Context,
    *,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a campaign record.

    Args:
        channel_id: Discord channel ID
        message_id: Message ID to track reactions on
        emoji: Emoji to track
        remind_at: ISO datetime for reminder
        ctx: Execution context
        title: Optional campaign title

    Returns:
        {
            "success": bool,
            "campaign_id": int,
            "campaign": Dict
        }
    """
    pass


async def _campaign_tally_optins(
    campaign_id: int,
    ctx: Context
) -> Dict[str, Any]:
    """
    Fetch reactions and store opt-ins.

    Args:
        campaign_id: Campaign ID
        ctx: Execution context

    Returns:
        {
            "total": int,
            "new": int,
            "existing": int
        }
    """
    pass


async def _campaign_build_reminder(
    campaign_id: int,
    ctx: Context,
    *,
    template_name: Optional[str] = None,
    template_vars: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build reminder message with mentions.

    Args:
        campaign_id: Campaign ID
        ctx: Execution context
        template_name: Template to use
        template_vars: Additional template variables

    Returns:
        {
            "chunks": List[str],  # Message chunks under 2000 chars
            "total_optins": int,
            "mentions_per_chunk": List[int]
        }
    """
    pass


async def _campaign_send_reminder(
    campaign_id: int,
    ctx: Context,
    *,
    dry_run: bool = True,
    rate_limit_delay: float = 1.0
) -> Dict[str, Any]:
    """
    Send reminder messages.

    Args:
        campaign_id: Campaign ID
        ctx: Execution context
        dry_run: If True, don't actually send
        rate_limit_delay: Seconds between messages

    Returns:
        {
            "chunks_sent": int,
            "total_users": int,
            "success": bool,
            "errors": List[str]
        }
    """
    pass


async def _campaign_monitor_until_due(
    campaign_id: int,
    ctx: Context,
    *,
    check_interval: int = 300  # 5 minutes
) -> Dict[str, Any]:
    """
    Monitor campaign until remind_at time.

    Args:
        campaign_id: Campaign ID
        ctx: Execution context
        check_interval: Seconds between checks

    Returns:
        {
            "monitoring_stopped": str,  # Reason
            "final_optin_count": int,
            "steps": List[Dict]
        }
    """
    pass
```

---

## 🟨 Priority 3: Add Resource References to Workflow Docs

### Template for Each Workflow Doc

Add this section after "Internal Helpers" in each `*_FLOW.md`:

**Example for CAMPAIGN_FLOW.md**:

```markdown
## Resources Used

### Templates

This workflow uses the following templates from `resources/campaign/templates/`:

#### `reminder_default.txt.j2`
**When used**: Generic reminders for any campaign type
**Variables required**: `campaign`, `mentions`, `total_optins`
**Access**: `ctx.resources.get_template("campaign/templates/reminder_default.txt.j2")`

#### `reminder_tournament.txt.j2`
**When used**: Gaming tournament reminders
**Variables required**: `campaign`, `mentions`, `total_optins`, `tournament_time`, `prize_info`
**Access**: `ctx.resources.get_template("campaign/templates/reminder_tournament.txt.j2")`

#### `reminder_event.txt.j2`
**When used**: Community events (movie night, game night)
**Variables required**: `campaign`, `mentions`, `total_optins`, `event_time`, `event_location`
**Access**: `ctx.resources.get_template("campaign/templates/reminder_event.txt.j2")`

### Prompts

This workflow uses these LLM prompts from `resources/campaign/prompts/`:

#### `campaign_intent.yaml`
**Purpose**: Parse natural language campaign creation requests
**Input**: `intent` (user's request), `channel_context` (recent messages)
**Output**: Structured campaign parameters (type, title, emoji, timing)
**Model**: claude-3-5-sonnet-20250929
**Access**: `ctx.resources.get_prompt("campaign/prompts/campaign_intent.yaml")`

#### `template_suggestion.yaml`
**Purpose**: Suggest best reminder template for campaign
**Input**: `campaign_title`, `campaign_message`, `campaign_context`
**Output**: Recommended template and variables
**Model**: claude-3-5-sonnet-20250929
**Access**: `ctx.resources.get_prompt("campaign/prompts/template_suggestion.yaml")`

### Example Usage in Workflow

```python
async def discord_campaign_workflow(
    action: str,
    *,
    ctx: Context,
    **kwargs
):
    if action == "execute_now":
        # Load template
        template = ctx.resources.get_template(
            "campaign/templates/reminder_default.txt.j2"
        )

        # Render with campaign data
        message = template.render(
            campaign=campaign_data,
            mentions=mention_string,
            total_optins=optin_count
        )

        # Send
        await discord_send(channel_id, message, ctx=ctx)
```
```

---

## 🟩 Priority 4: Merge Overlapping Atomic Tools

### Issue
`discord_ping` and `discord_bot_status` are currently separate but overlap with `discord_diagnostics` workflow.

### Resolution

**Remove as separate atomic tools**, only keep in workflow:

```python
# REMOVE these as standalone tools:
# - discord_ping()
# - discord_bot_status()

# ONLY expose via workflow:
discord_diagnostics(action="ping")
discord_diagnostics(action="status")
```

**Updated Atomic Tool Count**: 3 tools only
1. `discord_send` - Simple message send
2. `discord_get` - Get entity by ID
3. `discord_list` - List entities

**Plus** (not atomic, different categories):
- `discord_get_recent_messages` - Keep as convenience (pagination is common)
- `discord_run_due_reminders` - Automation tool (separate category)

### Updated ATOMIC_TOOLS_ANALYSIS.md

```markdown
## Final Tool Count

### ✅ Pure Atomic Tools (3)
1. `discord_send(channel_id, content)` - Fast, simple send
2. `discord_get(entity_type, entity_id)` - Direct ID lookup
3. `discord_list(entity_type, guild_id?)` - Simple enumeration

### 🔄 Workflow Tools (4)
4. `discord_discovery` - Entity search and exploration
5. `discord_message` - Message operations with templates
6. `discord_campaign` - Campaign lifecycle management
7. `discord_diagnostics` - Health checks (includes ping, status)

### 📊 Convenience Tools (1)
8. `discord_get_recent_messages` - Message history pagination

### ⚙️ Automation Tools (1)
9. `discord_run_due_reminders` - Background campaign processor

**Total**: 9 tools (3 atomic + 4 workflow + 1 convenience + 1 automation)
```

---

## 🟦 Priority 5: Fix Example Call Style

### Issue
Examples show `discord_message(...)` but should show MCP tool invocation pattern.

### Correct Call Patterns

**In workflow documentation**:

```python
# ❌ WRONG - looks like direct function call
discord_discovery("find channel general")

# ✅ CORRECT - MCP tool invocation (user perspective)
# Via Claude Desktop or MCP client:
Use tool: discord_discovery
Parameters:
  intent: "find channel general"

# ✅ CORRECT - Python code (developer perspective)
result = await ctx.call_tool(
    "discord_discovery",
    intent="find channel general"
)

# ✅ CORRECT - In workflow implementation (internal)
from ..tools.atomic import discord_send

async def discord_message_workflow(...):
    # Workflows call atomic tools directly
    result = await discord_send(channel_id, content, ctx=ctx)
```

### Updated Example Sections

**For user-facing examples** (in `*_FLOW.md`):

```markdown
## Usage

### Via MCP Client (Claude Desktop, etc.)

```json
{
  "tool": "discord_discovery",
  "parameters": {
    "intent": "find channel general in MyServer"
  }
}
```

### Via Python (Internal/Testing)

```python
# In tests or internal code
result = await discord_discovery_workflow(
    intent="find channel general in MyServer",
    ctx=test_context
)
```
```

**For workflow implementation examples**:

```python
# src/discord_mcp/workflows/discovery.py

async def discord_discovery_workflow(
    intent: str,
    *,
    ctx: Context
) -> WorkflowResult:
    """Discovery workflow implementation."""

    # Parse intent using helper
    parsed = await parse_discovery_intent(intent, ctx)

    # Use atomic tool internally
    from ..tools.atomic import discord_get

    entity = await discord_get(
        entity_type=parsed["entity_type"],
        entity_id=parsed["entity_id"],
        ctx=ctx
    )

    return WorkflowResult(...)
```

---

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Create `src/discord_mcp/resources/` directory structure
- [ ] Implement `ResourceManager` in `resources/loader.py`
- [ ] Extend `Context` class with `resources` property
- [ ] Create `WORKFLOW_RESOURCES` registry

### Phase 2: Internal Helpers
- [ ] Create `src/discord_mcp/internal/` directory
- [ ] Implement `entity_operations.py` helpers
- [ ] Implement `access_control.py` helpers
- [ ] Implement `intent_parser.py` helpers
- [ ] Implement `campaign_helpers.py`

### Phase 3: Templates & Prompts
- [ ] Create all template `.txt.j2` files
- [ ] Create all prompt `.yaml` files
- [ ] Test template rendering
- [ ] Test prompt loading

### Phase 4: Atomic Tools
- [ ] Implement `discord_send`
- [ ] Implement `discord_get`
- [ ] Implement `discord_list`
- [ ] Keep `discord_get_recent_messages`
- [ ] Keep `discord_run_due_reminders` (automation)

### Phase 5: Workflows
- [ ] Implement `discord_discovery` workflow
- [ ] Implement `discord_message` workflow
- [ ] Implement `discord_campaign` workflow
- [ ] Implement `discord_diagnostics` workflow

### Phase 6: Documentation Updates
- [ ] Add resource references to all `*_FLOW.md` files
- [ ] Fix example call styles
- [ ] Update ATOMIC_TOOLS_ANALYSIS.md
- [ ] Update ARCHITECTURE.md with helper signatures

### Phase 7: Testing
- [ ] Unit tests for helpers
- [ ] Integration tests for workflows
- [ ] System tests for MCP tools
- [ ] Test resource loading
- [ ] Test template rendering

---

## Quick Reference

### Resource Loading
```python
# In any workflow
template = ctx.resources.get_template("campaign/templates/reminder_default.txt.j2")
prompt = ctx.resources.get_prompt("discovery/prompts/discovery_intent.yaml")
```

### Helper Functions
```python
# Import from internal
from ..internal.entity_operations import _find_entity, _get_entity_details
from ..internal.access_control import _validate_guild_access
from ..internal.intent_parser import parse_discovery_intent
```

### Atomic Tool Usage
```python
# Import atomic tools
from ..tools.atomic import discord_send, discord_get, discord_list

# Use in workflows
await discord_send(channel_id, content, ctx=ctx)
entity = await discord_get("channel", channel_id, ctx=ctx)
```

### Workflow Registration
```python
# In register_tools.py
from ..workflows.discovery import discord_discovery_workflow

mcp.tool(
    name="discord_discovery",
    description="Find and explore Discord entities"
)(discord_discovery_workflow)
```

---

## Next Steps

1. **Review this implementation guide**
2. **Approve the approach**
3. **Start with Phase 1** (Core Infrastructure)
4. **Build incrementally** (one phase at a time)
5. **Test each phase** before moving forward

All 5 priority issues are now resolved with clear implementation paths!
