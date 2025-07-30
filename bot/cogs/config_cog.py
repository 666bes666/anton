"""Configuration cog for Discord bot commands and interactions."""
import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands, ui, Interaction
from discord.ext import commands

from bot.utils.time_utils import parse_time_string

if TYPE_CHECKING:
    from bot.core.bot import DailyMessageBot

logger = logging.getLogger(__name__)

class SettingsModal(ui.Modal, title='Configure Daily Messages'):
    """Modal for configuring bot settings through Discord UI."""
    
    def __init__(self, bot: "DailyMessageBot", guild_id: int):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
        
    async def on_submit(self, interaction: Interaction):
        """Handle modal submission."""
        try:
            # Get form values
            channel_id_str = self.channel_id_input.value
            time_str = self.time_input.value
            message = self.message_input.value

            # Validate channel ID
            try:
                channel_id = int(channel_id_str)
            except ValueError:
                await interaction.response.send_message(
                    "❌ Invalid Channel ID. Please provide a numeric ID.", 
                    ephemeral=True
                )
                return

            # Validate time format
            scheduled_time = parse_time_string(time_str)
            if not scheduled_time:
                await interaction.response.send_message(
                    "❌ Invalid time format. Please use HH:MM (e.g., 07:00).", 
                    ephemeral=True
                )
                return
            
            # Save configuration
            config = {
                'channel_id': channel_id,
                'time': time_str,
                'message': message,
                'enabled': True
            }
            
            await self.bot.config_manager.set_config(self.guild_id, config)

            await interaction.response.send_message(
                f"✅ **Settings updated!**\n"
                f"Daily messages will be sent to <#{channel_id}> at `{time_str}` UTC.\n"
                f"To disable, use the `/toggledaily false` command.",
                ephemeral=True
            )
            
            logger.info(f"Configuration updated for guild {self.guild_id}")

        except Exception as e:
            logger.error(f"Error in modal submission: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while saving your settings. Please try again.",
                ephemeral=True
            )

    async def setup_form_fields(self):
        """Set up form fields with current configuration."""
        current_config = await self.bot.config_manager.get_config(self.guild_id)
        
        self.channel_id_input = ui.TextInput(
            label='Target Channel ID',
            placeholder='Enter the ID of the channel for daily messages',
            default=str(current_config.get('channel_id', '')) if current_config.get('channel_id') else None
        )
        
        self.time_input = ui.TextInput(
            label='Send Time (UTC, 24-hour format)',
            placeholder='e.g., 07:00 for 10:00 MSK',
            default=current_config.get('time', '07:00')
        )
        
        self.message_input = ui.TextInput(
            label='Daily Message Content',
            style=discord.TextStyle.paragraph,
            placeholder='Type the message you want to send daily.',
            default=current_config.get('message', '')
        )
        
        self.add_item(self.channel_id_input)
        self.add_item(self.time_input)
        self.add_item(self.message_input)

class ConfigCog(commands.Cog):
    """Cog containing configuration commands for the bot."""
    
    def __init__(self, bot: "DailyMessageBot"):
        self.bot = bot
        
    @app_commands.context_menu(name="Configure Bot")
    @app_commands.describe()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def configure_bot_context_menu(self, interaction: Interaction, user: discord.Member):
        """Context menu command to configure the bot."""
        try:
            modal = SettingsModal(self.bot, interaction.guild_id)
            await modal.setup_form_fields()
            await interaction.response.send_modal(modal)
            
        except Exception as e:
            logger.error(f"Error in configure_bot_context_menu: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while opening the configuration modal.",
                ephemeral=True
            )

    @app_commands.command(name="toggledaily", description="Enable or disable daily messages for this server.")
    @app_commands.describe(enable="Whether to enable or disable daily messages")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle_daily(self, interaction: Interaction, enable: bool):
        """Slash command to enable/disable daily messages."""
        try:
            config = await self.bot.config_manager.get_config(interaction.guild_id)
            
            if not config or not config.get('channel_id'):
                await interaction.response.send_message(
                    "❌ Please configure the bot first using the 'Configure Bot' context menu.",
                    ephemeral=True
                )
                return
                
            await self.bot.config_manager.update_config(
                interaction.guild_id, 
                {'enabled': enable}
            )
            
            status = "enabled" if enable else "disabled"
            await interaction.response.send_message(
                f"✅ Daily messages have been **{status}**.",
                ephemeral=True
            )
            
            logger.info(f"Daily messages {status} for guild {interaction.guild_id}")
            
        except Exception as e:
            logger.error(f"Error in toggle_daily: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while updating the settings.",
                ephemeral=True
            )

    @app_commands.command(name="status", description="Show current bot configuration for this server.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def show_status(self, interaction: Interaction):
        """Show current bot configuration."""
        try:
            config = await self.bot.config_manager.get_config(interaction.guild_id)
            
            if not config:
                await interaction.response.send_message(
                    "❌ No configuration found. Please configure the bot first.",
                    ephemeral=True
                )
                return
                
            channel_mention = f"<#{config['channel_id']}>" if config.get('channel_id') else "Not set"
            status = "✅ Enabled" if config.get('enabled') else "❌ Disabled"
            
            embed = discord.Embed(
                title="📋 Daily Message Bot Status",
                description=f"Configuration for **{interaction.guild.name}**",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Status", value=status, inline=True)
            embed.add_field(name="Channel", value=channel_mention, inline=True)
            embed.add_field(name="Time (UTC)", value=config.get('time', 'Not set'), inline=True)
            embed.add_field(name="Message Preview", value=config.get('message', 'Not set')[:100] + "..." if len(config.get('message', '')) > 100 else config.get('message', 'Not set'), inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in show_status: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while retrieving the status.",
                ephemeral=True
            )

    @configure_bot_context_menu.error
    @toggle_daily.error
    @show_status.error
    async def command_error_handler(self, interaction: Interaction, error: app_commands.AppCommandError):
        """Handle command errors."""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command. You need 'Manage Server' permission.",
                ephemeral=True
            )
        else:
            logger.error(f"Command error: {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An unexpected error occurred.",
                    ephemeral=True
                )

async def setup(bot: "DailyMessageBot"):
    """Set up the cog."""
    await bot.add_cog(ConfigCog(bot))
