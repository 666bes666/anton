"""Main Discord bot implementation."""
import logging
from typing import List

import discord
from discord.ext import commands

from bot.core.config import settings
from bot.core.scheduler import MessageScheduler
from bot.utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class DailyMessageBot(commands.Bot):
    """
    The main class for the Discord Daily Message Bot.
    """
    
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        
        self.config_manager = ConfigManager(settings.config_file_path)
        self.scheduler = MessageScheduler(self)
        
        self.initial_cogs: List[str] = [
            "bot.cogs.config_cog"
        ]
        
    async def setup_hook(self):
        """Asynchronous setup method, called after login."""
        logger.info("Executing setup_hook")
        
        # Load initial cogs
        for cog in self.initial_cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded extension: {cog}")
            except Exception as e:
                logger.error(f"Failed to load extension {cog}: {e}", exc_info=True)
        
        # Sync application commands
        logger.info("Syncing application commands...")
        try:
            synced_commands = await self.tree.sync()
            logger.info(f"Synced {len(synced_commands)} application commands.")
        except Exception as e:
            logger.error(f"Failed to sync application commands: {e}", exc_info=True)
            
        # Start the scheduler
        await self.scheduler.start()
        
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")
        logger.info("Bot is ready.")
        
    async def on_guild_join(self, guild: discord.Guild):
        """Called when the bot joins a new guild."""
        logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
        await self.config_manager.create_default_config(guild.id)
        
    async def close(self):
        """Close the bot and clean up resources."""
        logger.info("Closing bot...")
        await self.scheduler.stop()
        await self.config_manager.close()
        await super().close()
