"""
Context manager service.
"""

import logging
from typing import Dict, List, Optional, Any

from ..models import ConversationContext
from ..repositories import ContextRepository

logger = logging.getLogger(__name__)


class ContextManagerService:
    """
    Service for managing conversation context.
    """

    def __init__(self, context_repo: ContextRepository = None):
        """
        Initialize the ContextManagerService.

        Args:
            context_repo (ContextRepository, optional): The context repository.
        """
        self.context_repo = context_repo or ContextRepository()
        self._context_cache = {}  # user_id -> ConversationContext

    def get_context(self, user_id: str) -> Optional[ConversationContext]:
        """
        Get the conversation context for a user.

        Args:
            user_id (str): The user ID.

        Returns:
            Optional[ConversationContext]: The conversation context, or None if not found.
        """
        # Check cache first
        if user_id in self._context_cache:
            return self._context_cache[user_id]

        # Get from repository
        context = self.context_repo.get_context_by_user_id(user_id)
        if context:
            self._context_cache[user_id] = context

        return context

    def track_entity(
        self, user_id: str, entity_type: str, entity_id: int
    ) -> bool:
        """
        Track an entity in the conversation context.

        Args:
            user_id (str): The user ID.
            entity_type (str): The entity type ('server', 'channel', or 'role').
            entity_id (int): The entity ID.

        Returns:
            bool: True if the entity was tracked, False otherwise.
        """
        # Get or create context
        context = self.get_context(user_id)
        if not context:
            context = ConversationContext(user_id=user_id)

        # Update context based on entity type
        if entity_type == "server":
            context.server_id = entity_id
        elif entity_type == "channel":
            context.channel_id = entity_id
        elif entity_type == "role":
            context.role_id = entity_id
        else:
            return False

        # Save context
        if context.id:
            self.context_repo.update_context(context)
        else:
            context = self.context_repo.create_context(context)

        # Update cache
        self._context_cache[user_id] = context

        return True

    def clear_context(self, user_id: str) -> bool:
        """
        Clear the conversation context for a user.

        Args:
            user_id (str): The user ID.

        Returns:
            bool: True if the context was cleared, False otherwise.
        """
        # Remove from cache
        if user_id in self._context_cache:
            del self._context_cache[user_id]

        # Remove from repository
        return self.context_repo.delete_context_by_user_id(user_id)
