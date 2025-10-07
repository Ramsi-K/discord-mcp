"""Campaign management tools for Discord MCP server."""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from ..config import Config
from ..database.models import Campaign, OptIn
from ..database.repositories import CampaignRepository, OptInRepository

logger = logging.getLogger(__name__)


def get_campaign_repository() -> CampaignRepository:
    """Get campaign repository instance."""
    config = Config()
    return CampaignRepository(config.database_path)


def get_optin_repository() -> OptInRepository:
    """Get opt-in repository instance."""
    config = Config()
    return OptInRepository(config.database_path)


async def discord_create_campaign(
    channel_id: str,
    message_id: str,
    emoji: str,
    remind_at: str,
    title: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new reaction opt-in reminder campaign.

    Args:
        channel_id: Discord channel ID where the message is located
        message_id: Discord message ID to track reactions on
        emoji: Emoji to track reactions for (e.g., "👍" or ":thumbsup:")
        remind_at: ISO format datetime when to send reminder (e.g., "2024-01-15T10:00:00")
        title: Optional title for the campaign

    Returns:
        Dict containing success status and campaign details
    """
    config = Config()

    if config.dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": "DRY_RUN: Campaign would be created",
            "campaign": {
                "id": 999,
                "title": title or f"Campaign for message {message_id}",
                "channel_id": channel_id,
                "message_id": message_id,
                "emoji": emoji,
                "remind_at": remind_at,
                "status": "active",
            },
        }

    try:
        # Parse remind_at datetime
        try:
            remind_datetime = datetime.fromisoformat(remind_at.replace("Z", "+00:00"))
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid datetime format for remind_at: {e}. Use ISO format like '2024-01-15T10:00:00'",
            }

        # Create campaign object
        campaign = Campaign(
            title=title or f"Campaign for message {message_id}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
            remind_at=remind_datetime,
            status="active",
        )

        # Save to database
        repo = get_campaign_repository()
        campaign_id = repo.create_campaign(campaign)

        if campaign_id:
            campaign.id = campaign_id
            logger.info(f"Created campaign {campaign_id} for message {message_id}")
            return {
                "success": True,
                "message": f"Campaign created successfully with ID {campaign_id}",
                "campaign": campaign.to_dict(),
            }
        else:
            return {
                "success": False,
                "error": "Failed to create campaign in database",
            }

    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        return {
            "success": False,
            "error": f"Error creating campaign: {str(e)}",
        }


async def discord_tally_optins(campaign_id: int) -> Dict[str, Any]:
    """
    Fetch reactions from Discord and store deduplicated opt-ins for a campaign.
    This operation is idempotent - safe to run multiple times.

    Args:
        campaign_id: ID of the campaign to tally opt-ins for

    Returns:
        Dict containing success status and tally results
    """
    config = Config()

    if config.dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": "DRY_RUN: Would fetch reactions and store opt-ins",
            "tally": {
                "campaign_id": campaign_id,
                "total_optins": 15,
                "new_optins": 3,
                "existing_optins": 12,
            },
        }

    try:
        # Get campaign details
        campaign_repo = get_campaign_repository()
        campaign = campaign_repo.get_campaign(campaign_id)

        if not campaign:
            return {
                "success": False,
                "error": f"Campaign {campaign_id} not found",
            }

        # Import Discord bot functionality
        from ..server import discord_bot

        if not discord_bot or discord_bot.is_closed():
            return {"success": False, "error": "Discord bot is not connected"}

        # Get the channel and message
        try:
            channel = discord_bot.get_channel(int(campaign.channel_id))
            if not channel:
                return {
                    "success": False,
                    "error": f"Channel {campaign.channel_id} not found or bot lacks access",
                }

            message = await channel.fetch_message(int(campaign.message_id))
            if not message:
                return {
                    "success": False,
                    "error": f"Message {campaign.message_id} not found",
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching Discord message: {str(e)}",
            }

        # Find the target reaction
        target_reaction = None
        for reaction in message.reactions:
            if str(reaction.emoji) == campaign.emoji:
                target_reaction = reaction
                break

        if not target_reaction:
            return {
                "success": True,
                "message": f"No reactions found for emoji {campaign.emoji}",
                "tally": {
                    "campaign_id": campaign_id,
                    "total_optins": 0,
                    "new_optins": 0,
                    "existing_optins": 0,
                },
            }

        # Get existing opt-ins to avoid duplicates
        optin_repo = get_optin_repository()
        existing_optins = optin_repo.get_optins(
            campaign_id, limit=10000
        )  # Get all existing
        existing_user_ids = {optin.user_id for optin in existing_optins}

        # Fetch users who reacted
        new_optins = 0
        async for user in target_reaction.users():
            if user.bot:  # Skip bot users
                continue

            user_id = str(user.id)
            if user_id not in existing_user_ids:
                # Add new opt-in
                optin = OptIn(
                    campaign_id=campaign_id,
                    user_id=user_id,
                    username=user.display_name or user.name,
                    tallied_at=datetime.now(),
                )

                if optin_repo.add_optin(optin):
                    new_optins += 1
                    existing_user_ids.add(user_id)

        total_optins = len(existing_user_ids)
        existing_count = total_optins - new_optins

        logger.info(
            f"Tallied opt-ins for campaign {campaign_id}: {new_optins} new, {existing_count} existing, {total_optins} total"
        )

        return {
            "success": True,
            "message": f"Successfully tallied opt-ins for campaign {campaign_id}",
            "tally": {
                "campaign_id": campaign_id,
                "total_optins": total_optins,
                "new_optins": new_optins,
                "existing_optins": existing_count,
            },
        }

    except Exception as e:
        logger.error(f"Error tallying opt-ins for campaign {campaign_id}: {e}")
        return {"success": False, "error": f"Error tallying opt-ins: {str(e)}"}


async def discord_list_optins(
    campaign_id: int, limit: int = 100, after_user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List opt-ins for a campaign with pagination support.

    Args:
        campaign_id: ID of the campaign to list opt-ins for
        limit: Maximum number of opt-ins to return (default: 100)
        after_user_id: Return opt-ins after this user ID for pagination

    Returns:
        Dict containing success status and opt-in list
    """
    config = Config()

    if config.dry_run:
        mock_optins = []
        for i in range(min(limit, 10)):
            user_id = str(100000 + i + (int(after_user_id) if after_user_id else 0))
            mock_optins.append(
                {
                    "id": i + 1,
                    "campaign_id": campaign_id,
                    "user_id": user_id,
                    "username": f"User{user_id}",
                    "tallied_at": "2024-01-15T10:00:00",
                }
            )

        return {
            "success": True,
            "dry_run": True,
            "message": "DRY_RUN: Mock opt-ins returned",
            "optins": mock_optins,
            "pagination": {
                "limit": limit,
                "after_user_id": after_user_id,
                "has_more": len(mock_optins) == limit,
            },
        }

    try:
        # Get campaign to verify it exists
        campaign_repo = get_campaign_repository()
        campaign = campaign_repo.get_campaign(campaign_id)

        if not campaign:
            return {
                "success": False,
                "error": f"Campaign {campaign_id} not found",
            }

        # Get opt-ins with pagination
        optin_repo = get_optin_repository()
        optins = optin_repo.get_optins(campaign_id, limit, after_user_id)

        optin_dicts = [optin.to_dict() for optin in optins]

        return {
            "success": True,
            "message": f"Retrieved {len(optins)} opt-ins for campaign {campaign_id}",
            "optins": optin_dicts,
            "pagination": {
                "limit": limit,
                "after_user_id": after_user_id,
                "has_more": len(optins) == limit,
            },
        }

    except Exception as e:
        logger.error(f"Error listing opt-ins for campaign {campaign_id}: {e}")
        return {"success": False, "error": f"Error listing opt-ins: {str(e)}"}


async def discord_build_reminder(
    campaign_id: int, template: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build reminder message with @mention chunking under 2000 characters.

    Args:
        campaign_id: ID of the campaign to build reminder for
        template: Optional custom template for the reminder message

    Returns:
        Dict containing success status and reminder message chunks
    """
    config = Config()

    if config.dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": "DRY_RUN: Reminder message chunks generated",
            "reminder": {
                "campaign_id": campaign_id,
                "total_recipients": 15,
                "message_chunks": [
                    "🔔 Reminder: Test Campaign\n\n@User100001 @User100002 @User100003 @User100004 @User100005",
                    "🔔 Reminder: Test Campaign (continued)\n\n@User100006 @User100007 @User100008 @User100009 @User100010",
                ],
                "chunk_count": 2,
            },
        }

    try:
        # Get campaign details
        campaign_repo = get_campaign_repository()
        campaign = campaign_repo.get_campaign(campaign_id)

        if not campaign:
            return {
                "success": False,
                "error": f"Campaign {campaign_id} not found",
            }

        # Get all opt-ins for the campaign
        optin_repo = get_optin_repository()
        all_optins = []
        after_user_id = None

        while True:
            optins = optin_repo.get_optins(
                campaign_id, limit=1000, after_user_id=after_user_id
            )
            if not optins:
                break
            all_optins.extend(optins)
            if len(optins) < 1000:  # No more results
                break
            after_user_id = optins[-1].user_id

        if not all_optins:
            return {
                "success": True,
                "message": f"No opt-ins found for campaign {campaign_id}",
                "reminder": {
                    "campaign_id": campaign_id,
                    "total_recipients": 0,
                    "message_chunks": [],
                    "chunk_count": 0,
                },
            }

        # Build reminder message template
        if template is None:
            template = "🔔 Reminder: {title}\n\n{mentions}"

        title = campaign.title or f"Campaign {campaign_id}"
        base_message = template.replace("{title}", title)
        base_message_without_mentions = base_message.replace("{mentions}", "").strip()

        # Calculate available space for mentions (Discord limit is 2000 chars)
        max_message_length = 2000
        available_space = (
            max_message_length - len(base_message_without_mentions) - 10
        )  # Buffer

        # Build mention chunks
        message_chunks = []
        current_mentions = []
        current_length = 0

        for optin in all_optins:
            mention = f"<@{optin.user_id}>"
            mention_length = len(mention) + 1  # +1 for space

            if current_length + mention_length > available_space and current_mentions:
                # Create chunk with current mentions
                mentions_text = " ".join(current_mentions)
                chunk_message = base_message.replace("{mentions}", mentions_text)
                message_chunks.append(chunk_message)

                # Start new chunk
                current_mentions = [mention]
                current_length = mention_length
            else:
                current_mentions.append(mention)
                current_length += mention_length

        # Add final chunk if there are remaining mentions
        if current_mentions:
            mentions_text = " ".join(current_mentions)
            chunk_message = base_message.replace("{mentions}", mentions_text)
            message_chunks.append(chunk_message)

        # Add continuation markers for multiple chunks
        if len(message_chunks) > 1:
            for i, chunk in enumerate(message_chunks):
                if i > 0:  # Add continuation marker to subsequent chunks
                    continuation_marker = f" (continued {i+1}/{len(message_chunks)})"
                    # Insert continuation marker after the title
                    lines = chunk.split("\n")
                    if len(lines) > 0:
                        lines[0] += continuation_marker
                        message_chunks[i] = "\n".join(lines)

        logger.info(
            f"Built reminder for campaign {campaign_id}: {len(all_optins)} recipients, {len(message_chunks)} chunks"
        )

        return {
            "success": True,
            "message": f"Built reminder for campaign {campaign_id}",
            "reminder": {
                "campaign_id": campaign_id,
                "total_recipients": len(all_optins),
                "message_chunks": message_chunks,
                "chunk_count": len(message_chunks),
            },
        }

    except Exception as e:
        logger.error(f"Error building reminder for campaign {campaign_id}: {e}")
        return {
            "success": False,
            "error": f"Error building reminder: {str(e)}",
        }


async def discord_send_reminder(
    campaign_id: int, dry_run: bool = True
) -> Dict[str, Any]:
    """
    Send reminder messages with rate limiting and batch processing.

    Args:
        campaign_id: ID of the campaign to send reminder for
        dry_run: If True, don't actually send messages (default: True for safety)

    Returns:
        Dict containing success status and sending results
    """
    config = Config()

    # Force dry_run if global DRY_RUN is enabled
    if config.dry_run:
        dry_run = True

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": "DRY_RUN: Reminder messages would be sent",
            "sending": {
                "campaign_id": campaign_id,
                "messages_sent": 2,
                "total_recipients": 15,
                "rate_limited": False,
                "errors": [],
            },
        }

    try:
        # Get campaign details
        campaign_repo = get_campaign_repository()
        campaign = campaign_repo.get_campaign(campaign_id)

        if not campaign:
            return {
                "success": False,
                "error": f"Campaign {campaign_id} not found",
            }

        # Build reminder messages
        reminder_result = await discord_build_reminder(campaign_id)
        if not reminder_result["success"]:
            return reminder_result

        reminder_data = reminder_result["reminder"]
        message_chunks = reminder_data["message_chunks"]

        if not message_chunks:
            return {
                "success": True,
                "message": "No recipients to send reminder to",
                "sending": {
                    "campaign_id": campaign_id,
                    "messages_sent": 0,
                    "total_recipients": 0,
                    "rate_limited": False,
                    "errors": [],
                },
            }

        # Import Discord bot functionality
        from ..server import discord_bot

        if not discord_bot or discord_bot.is_closed():
            return {"success": False, "error": "Discord bot is not connected"}

        # Get the channel
        try:
            channel = discord_bot.get_channel(int(campaign.channel_id))
            if not channel:
                return {
                    "success": False,
                    "error": f"Channel {campaign.channel_id} not found or bot lacks access",
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error accessing Discord channel: {str(e)}",
            }

        # Send messages with rate limiting
        import asyncio

        messages_sent = 0
        errors = []
        rate_limited = False

        for i, chunk in enumerate(message_chunks):
            try:
                # Rate limiting: wait between messages to avoid Discord limits
                if i > 0:
                    await asyncio.sleep(1)  # 1 second between messages

                await channel.send(chunk)
                messages_sent += 1
                logger.info(
                    f"Sent reminder chunk {i+1}/{len(message_chunks)} for campaign {campaign_id}"
                )

            except Exception as e:
                error_msg = f"Failed to send chunk {i+1}: {str(e)}"
                errors.append(error_msg)
                logger.error(
                    f"Error sending reminder chunk for campaign {campaign_id}: {e}"
                )

                # Check if it's a rate limit error
                if "rate limit" in str(e).lower() or "429" in str(e):
                    rate_limited = True
                    # Wait longer for rate limit errors
                    await asyncio.sleep(5)

        # Log the reminder attempt
        from ..database.models import ReminderLog
        from ..database.repositories import ReminderLogRepository

        log_repo = ReminderLogRepository(config.database_path)
        log_entry = ReminderLog(
            campaign_id=campaign_id,
            sent_at=datetime.now(),
            recipient_count=reminder_data["total_recipients"],
            message_chunks=len(message_chunks),
            success=messages_sent > 0 and len(errors) == 0,
            error_message="; ".join(errors) if errors else None,
        )
        log_repo.log_reminder(log_entry)

        # Update campaign status if fully sent
        if messages_sent == len(message_chunks) and not errors:
            campaign_repo.update_campaign_status(campaign_id, "completed")

        success = messages_sent > 0
        message = f"Sent {messages_sent}/{len(message_chunks)} reminder messages for campaign {campaign_id}"

        if errors:
            message += f" with {len(errors)} errors"

        logger.info(
            f"Reminder sending completed for campaign {campaign_id}: {messages_sent} sent, {len(errors)} errors"
        )

        return {
            "success": success,
            "message": message,
            "sending": {
                "campaign_id": campaign_id,
                "messages_sent": messages_sent,
                "total_recipients": reminder_data["total_recipients"],
                "rate_limited": rate_limited,
                "errors": errors,
            },
        }

    except Exception as e:
        logger.error(f"Error sending reminder for campaign {campaign_id}: {e}")
        return {"success": False, "error": f"Error sending reminder: {str(e)}"}


async def discord_run_due_reminders(
    now: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process scheduled campaigns that are due for reminders.

    Args:
        now: Optional ISO format datetime to use as current time (for testing)

    Returns:
        Dict containing success status and processing results
    """
    config = Config()

    # Parse current time
    if now:
        try:
            current_time = datetime.fromisoformat(now.replace("Z", "+00:00"))
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid datetime format for now: {e}. Use ISO format like '2024-01-15T10:00:00'",
            }
    else:
        current_time = datetime.now()

    if config.dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": "DRY_RUN: Would process due reminders",
            "processing": {
                "current_time": current_time.isoformat(),
                "due_campaigns": 2,
                "processed": 2,
                "successful": 2,
                "failed": 0,
                "errors": [],
            },
        }

    try:
        # Get due campaigns
        campaign_repo = get_campaign_repository()
        due_campaigns = campaign_repo.get_due_campaigns(current_time)

        if not due_campaigns:
            return {
                "success": True,
                "message": f"No campaigns due for reminders at {current_time.isoformat()}",
                "processing": {
                    "current_time": current_time.isoformat(),
                    "due_campaigns": 0,
                    "processed": 0,
                    "successful": 0,
                    "failed": 0,
                    "errors": [],
                },
            }

        # Process each due campaign
        processed = 0
        successful = 0
        failed = 0
        errors = []

        for campaign in due_campaigns:
            try:
                logger.info(f"Processing due campaign {campaign.id}: {campaign.title}")

                # Send reminder for this campaign
                send_result = await discord_send_reminder(campaign.id, dry_run=False)

                processed += 1

                if send_result["success"]:
                    successful += 1
                    logger.info(f"Successfully processed campaign {campaign.id}")
                else:
                    failed += 1
                    error_msg = f"Campaign {campaign.id}: {send_result.get('error', 'Unknown error')}"
                    errors.append(error_msg)
                    logger.error(
                        f"Failed to process campaign {campaign.id}: {send_result.get('error')}"
                    )

                # Rate limiting between campaigns
                import asyncio

                await asyncio.sleep(2)  # 2 seconds between campaigns

            except Exception as e:
                processed += 1
                failed += 1
                error_msg = f"Campaign {campaign.id}: Exception - {str(e)}"
                errors.append(error_msg)
                logger.error(f"Exception processing campaign {campaign.id}: {e}")

        success = successful > 0 or (processed == 0)
        message = f"Processed {processed} due campaigns: {successful} successful, {failed} failed"

        logger.info(f"Due reminders processing completed: {message}")

        return {
            "success": success,
            "message": message,
            "processing": {
                "current_time": current_time.isoformat(),
                "due_campaigns": len(due_campaigns),
                "processed": processed,
                "successful": successful,
                "failed": failed,
                "errors": errors,
            },
        }

    except Exception as e:
        logger.error(f"Error processing due reminders: {e}")
        return {
            "success": False,
            "error": f"Error processing due reminders: {str(e)}",
        }


async def discord_list_campaigns(
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List all campaigns with optional status filtering.

    Args:
        status: Optional status filter ('active', 'completed', 'cancelled')

    Returns:
        Dict containing success status and campaign list
    """
    config = Config()

    if config.dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": "DRY_RUN: Mock campaigns returned",
            "campaigns": [
                {
                    "id": 1,
                    "title": "Mock Campaign 1",
                    "channel_id": "123456789",
                    "message_id": "987654321",
                    "emoji": "👍",
                    "remind_at": "2024-12-31T23:59:59",
                    "status": "active",
                },
                {
                    "id": 2,
                    "title": "Mock Campaign 2",
                    "channel_id": "123456789",
                    "message_id": "987654322",
                    "emoji": "🎉",
                    "remind_at": "2025-01-01T00:00:00",
                    "status": "completed",
                },
            ],
        }

    try:
        repo = get_campaign_repository()

        if status:
            campaigns = repo.get_campaigns_by_status(status)
        else:
            # Get all campaigns by fetching each status type
            campaigns = []
            for s in ["active", "completed", "cancelled"]:
                campaigns.extend(repo.get_campaigns_by_status(s))

        campaign_dicts = [c.to_dict() for c in campaigns]

        return {
            "success": True,
            "message": f"Retrieved {len(campaigns)} campaigns",
            "campaigns": campaign_dicts,
        }

    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        return {"success": False, "error": f"Error listing campaigns: {str(e)}"}


async def discord_get_campaign(campaign_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific campaign.

    Args:
        campaign_id: ID of the campaign to retrieve

    Returns:
        Dict containing success status and campaign details
    """
    config = Config()

    if config.dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": "DRY_RUN: Mock campaign returned",
            "campaign": {
                "id": campaign_id,
                "title": f"Mock Campaign {campaign_id}",
                "channel_id": "123456789",
                "message_id": "987654321",
                "emoji": "👍",
                "remind_at": "2024-12-31T23:59:59",
                "status": "active",
            },
        }

    try:
        repo = get_campaign_repository()
        campaign = repo.get_campaign(campaign_id)

        if not campaign:
            return {
                "success": False,
                "error": f"Campaign {campaign_id} not found",
            }

        return {
            "success": True,
            "message": f"Retrieved campaign {campaign_id}",
            "campaign": campaign.to_dict(),
        }

    except Exception as e:
        logger.error(f"Error getting campaign {campaign_id}: {e}")
        return {
            "success": False,
            "error": f"Error getting campaign: {str(e)}",
        }


async def discord_update_campaign_status(
    campaign_id: int, status: str
) -> Dict[str, Any]:
    """
    Update campaign status (active, completed, cancelled).

    Args:
        campaign_id: ID of the campaign to update
        status: New status ('active', 'completed', 'cancelled')

    Returns:
        Dict containing success status and update result
    """
    config = Config()

    if config.dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": f"DRY_RUN: Campaign {campaign_id} status would be updated to '{status}'",
        }

    # Validate status
    valid_statuses = ["active", "completed", "cancelled"]
    if status not in valid_statuses:
        return {
            "success": False,
            "error": f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
        }

    try:
        repo = get_campaign_repository()

        # Verify campaign exists
        campaign = repo.get_campaign(campaign_id)
        if not campaign:
            return {
                "success": False,
                "error": f"Campaign {campaign_id} not found",
            }

        # Update status
        if repo.update_campaign_status(campaign_id, status):
            return {
                "success": True,
                "message": f"Campaign {campaign_id} status updated to '{status}'",
            }
        else:
            return {
                "success": False,
                "error": f"Failed to update campaign {campaign_id} status",
            }

    except Exception as e:
        logger.error(f"Error updating campaign {campaign_id} status: {e}")
        return {
            "success": False,
            "error": f"Error updating campaign status: {str(e)}",
        }


async def discord_delete_campaign(campaign_id: int) -> Dict[str, Any]:
    """
    Delete a campaign and all its associated opt-ins.

    Args:
        campaign_id: ID of the campaign to delete

    Returns:
        Dict containing success status and deletion result
    """
    config = Config()

    if config.dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": f"DRY_RUN: Campaign {campaign_id} and its opt-ins would be deleted",
        }

    try:
        # Verify campaign exists
        campaign_repo = get_campaign_repository()
        campaign = campaign_repo.get_campaign(campaign_id)

        if not campaign:
            return {
                "success": False,
                "error": f"Campaign {campaign_id} not found",
            }

        # Delete opt-ins first
        optin_repo = get_optin_repository()
        optin_repo.clear_optins(campaign_id)

        # Delete campaign (we need to add this method)
        # For now, we'll just set status to 'deleted'
        if campaign_repo.update_campaign_status(campaign_id, "deleted"):
            return {
                "success": True,
                "message": f"Campaign {campaign_id} deleted successfully",
            }
        else:
            return {
                "success": False,
                "error": f"Failed to delete campaign {campaign_id}",
            }

    except Exception as e:
        logger.error(f"Error deleting campaign {campaign_id}: {e}")
        return {
            "success": False,
            "error": f"Error deleting campaign: {str(e)}",
        }
