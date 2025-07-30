"""Scheduler for daily message sending."""
import asyncio
import logging
from datetime import datetime, date
from typing import Dict, TYPE_CHECKING

import discord

from bot.utils.time_utils import parse_time_string, is_time_to_send

if TYPE_CHECKING:
    from bot.core.bot import DailyMessageBot

logger = logging.getLogger(__name__)

class MessageScheduler:
    """
    Handles the scheduling and sending of daily messages.
    """
    
    def __init__(self, bot: "DailyMessageBot"):
        self.bot = bot
        self.last_sent_dates: Dict[int, date] = {}
        self._task: asyncio.Task = None
        
    async def start(self):
        """Start the message scheduling task."""
        if self._task and not self._task.done():
            return
            
        logger.info("Starting message scheduler")
        self._task = asyncio.create_task(self._scheduler_loop())
        
    async def stop(self):
        """Stop the message scheduling task."""
        if self._task and not self._task.done():
            logger.info("Stopping message scheduler")
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
                
    async def _scheduler_loop(self):
        """Main scheduler loop that runs continuously."""
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            try:
                now_utc = datetime.utcnow()
                await self._check_and_send_messages(now_utc)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
            
            # Wait 60 seconds before next check
            await asyncio.sleep(60)
            
    async def _check_and_send_messages(self, current_time: datetime):
        """Check all guild configurations and send messages if needed."""
        configs = await self.bot.config_manager.get_all_configs()
        
        for guild_id, config in configs.items():
            try:
                await self._process_guild_message(guild_id, config, current_time)
            except Exception as e:
                logger.error(f"Error processing guild {guild_id}: {e}")
                
    async def _process_guild_message(self, guild_id: int, config: dict, current_time: datetime):
        """Process message sending for a single guild."""
        # Skip if disabled or missing required fields
        if not config.get('enabled') or not config.get('channel_id'):
            return
            
        # Check if already sent today
        last_sent_date = self.last_sent_dates.get(guild_id)
        if last_sent_date == current_time.date():
            return
            
        # Parse scheduled time
        scheduled_time = parse_time_string(config.get('time', '07:00'))
        if not scheduled_time:
            logger.warning(f"Invalid time format for guild {guild_id}")
            return
            
        # Check if it's time to send
        if not is_time_to_send(scheduled_time, current_time):
            return
            
        # Send the message
        success = await self._send_message(guild_id, config)
        if success:
            self.last_sent_dates[guild_id] = current_time.date()
            logger.info(f"Daily message sent to guild {guild_id}")
            
    async def _send_message(self, guild_id: int, config: dict) -> bool:
        """Send a message to the configured channel."""
        try:
            channel = self.bot.get_channel(config['channel_id'])
            if not channel:
                logger.error(f"Channel {config['channel_id']} not found for guild {guild_id}")
                return False
                
            await channel.send(config['message'])
            return True
            
        except discord.Forbidden:
            logger.error(f"No permission to send message in channel {config['channel_id']} for guild {guild_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to send message to guild {guild_id}: {e}")
            return False
