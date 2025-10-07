from typing import List, Optional, Dict, Any, Tuple
import re

from ..models import Server, Channel, Role


class AliasGeneratorService:
    """
    Service class for generating aliases for entities.
    """

    def generate_server_aliases(self, server: Server) -> List[str]:
        """
        Generate aliases for a server.

        Args:
            server (Server): The server.

        Returns:
            List[str]: The generated aliases.
        """
        aliases = []

        # Original name (lowercase)
        aliases.append(server.name.lower())

        # Name without "server" suffix (if present)
        if server.name.lower().endswith(" server"):
            aliases.append(server.name[:-7].lower())

        # Name with "server" suffix (if not present)
        if not server.name.lower().endswith(" server"):
            aliases.append(f"{server.name.lower()} server")

        # Common abbreviations
        words = server.name.split()
        if len(words) > 1:
            # Acronym (first letter of each word)
            acronym = "".join(word[0] for word in words).lower()
            aliases.append(acronym)

            # Acronym with "server" suffix
            aliases.append(f"{acronym} server")

        # Remove special characters and spaces
        clean_name = re.sub(r"[^a-zA-Z0-9]", "", server.name).lower()
        if clean_name != server.name.lower():
            aliases.append(clean_name)

        return list(set(aliases))  # Remove duplicates

    def generate_channel_aliases(self, channel: Channel) -> List[str]:
        """
        Generate aliases for a channel.

        Args:
            channel (Channel): The channel.

        Returns:
            List[str]: The generated aliases.
        """
        aliases = []

        # Original name (lowercase)
        aliases.append(channel.name.lower())

        # Name without "channel" suffix (if present)
        if channel.name.lower().endswith(" channel"):
            aliases.append(channel.name[:-8].lower())

        # Name with "channel" suffix (if not present)
        if not channel.name.lower().endswith(" channel"):
            aliases.append(f"{channel.name.lower()} channel")

        # Add # prefix
        aliases.append(f"#{channel.name.lower()}")

        # Purpose-based aliases
        if "announce" in channel.name.lower():
            aliases.append("announcements")
            aliases.append("announce")
            aliases.append("announcement")

        if "general" in channel.name.lower():
            aliases.append("general")
            aliases.append("gen")

        if "welcome" in channel.name.lower():
            aliases.append("welcome")
            aliases.append("greet")
            aliases.append("greeting")

        if "rules" in channel.name.lower():
            aliases.append("rules")
            aliases.append("rule")

        if "help" in channel.name.lower():
            aliases.append("help")
            aliases.append("support")
            aliases.append("helpdesk")

        if "chat" in channel.name.lower():
            aliases.append("chat")
            aliases.append("discussion")
            aliases.append("talk")

        # Remove special characters and spaces
        clean_name = re.sub(r"[^a-zA-Z0-9]", "", channel.name).lower()
        if clean_name != channel.name.lower():
            aliases.append(clean_name)

        return list(set(aliases))  # Remove duplicates

    def generate_role_aliases(self, role: Role) -> List[str]:
        """
        Generate aliases for a role.

        Args:
            role (Role): The role.

        Returns:
            List[str]: The generated aliases.
        """
        aliases = []

        # Original name (lowercase)
        aliases.append(role.name.lower())

        # Name without "role" suffix (if present)
        if role.name.lower().endswith(" role"):
            aliases.append(role.name[:-5].lower())

        # Name with "role" suffix (if not present)
        if not role.name.lower().endswith(" role"):
            aliases.append(f"{role.name.lower()} role")

        # Plural forms
        if not role.name.lower().endswith("s"):
            aliases.append(f"{role.name.lower()}s")

        # Common role aliases
        if role.name.lower() == "admin" or role.name.lower() == "administrator":
            aliases.append("admin")
            aliases.append("administrator")
            aliases.append("admins")

        if role.name.lower() == "mod" or role.name.lower() == "moderator":
            aliases.append("mod")
            aliases.append("moderator")
            aliases.append("mods")
            aliases.append("moderators")

        if role.name.lower() == "member" or role.name.lower() == "members":
            aliases.append("member")
            aliases.append("members")

        # Remove special characters and spaces
        clean_name = re.sub(r"[^a-zA-Z0-9]", "", role.name).lower()
        if clean_name != role.name.lower():
            aliases.append(clean_name)

        return list(set(aliases))  # Remove duplicates

    def learn_aliases_from_usage(
        self, entity_type: str, entity_id: int, reference: str
    ) -> List[str]:
        """
        Learn aliases from user references.

        Args:
            entity_type (str): The entity type ('server', 'channel', or 'role').
            entity_id (int): The entity ID.
            reference (str): The reference used by the user.

        Returns:
            List[str]: The learned aliases.
        """
        # This would require tracking user references and learning from them
        # For now, we'll just return the reference as an alias
        return [reference.lower()]
